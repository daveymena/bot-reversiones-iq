"""
Gestor de Base de Datos para Bot de Trading Inteligente
Maneja todas las operaciones con PostgreSQL
"""
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.pool import ThreadedConnectionPool
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os
from dotenv import load_dotenv
import signal
from functools import wraps

load_dotenv()

def timeout_handler(signum, frame):
    raise TimeoutError("Operación de BD excedió el timeout")

def db_operation_with_timeout(timeout_seconds=2):
    """Decorador para operaciones de BD con timeout"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # En Windows, signal.alarm no funciona, usar threading
                import threading
                result = [None]
                exception = [None]
                
                def target():
                    try:
                        result[0] = func(*args, **kwargs)
                    except Exception as e:
                        exception[0] = e
                
                thread = threading.Thread(target=target, daemon=True)
                thread.start()
                thread.join(timeout=timeout_seconds)
                
                if thread.is_alive():
                    print(f"⚠️ Timeout en {func.__name__}, continuando sin BD")
                    return None
                
                if exception[0]:
                    print(f"⚠️ Error en {func.__name__}: {exception[0]}")
                    return None
                
                return result[0]
            except Exception as e:
                print(f"⚠️ Error en {func.__name__}: {e}")
                return None
        return wrapper
    return decorator

class DatabaseManager:
    """Gestor profesional de base de datos con pool de conexiones"""
    
    def __init__(self):
        self.pool = None
        self.db_available = False
        self.db_enabled = os.getenv('ENABLE_DATABASE', 'False').lower() == 'true'
        
        if not self.db_enabled:
            print("⚠️ Base de datos DESHABILITADA (para evitar congelamientos)")
            print("   El bot funcionará sin guardar en BD")
            return
        self.connect()
    
    def connect(self):
        """Crear pool de conexiones con timeouts agresivos"""
        try:
            # Soportar DATABASE_URL de Easypanel o variables individuales
            database_url = os.getenv('DATABASE_URL')
            
            if database_url:
                # Usar URL completa (formato Easypanel/Heroku)
                self.pool = ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=database_url,
                    connect_timeout=2,  # Timeout de 2 segundos para conectar (reducido)
                    options='-c statement_timeout=2000'  # Timeout de 2s para queries (reducido)
                )
                print("✅ Pool de conexiones creado (usando DATABASE_URL)")
            else:
                # Usar variables individuales con fallback a Easypanel
                db_host = os.getenv('DB_HOST') or '157.173.97.41'
                db_port = os.getenv('DB_PORT') or '15432'
                db_name = os.getenv('DB_NAME') or 'trading_bot'
                db_user = os.getenv('DB_USER') or 'postgres'
                db_password = os.getenv('DB_PASSWORD') or '6715320D'
                
                self.pool = ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,
                    host=db_host,
                    port=db_port,
                    database=db_name,
                    user=db_user,
                    password=db_password,
                    connect_timeout=5,  # Timeout de 5 segundos para conectar
                    options='-c statement_timeout=10000'  # Timeout de 10s para queries
                )
                print(f"✅ Pool de conexiones creado ({db_host}:{db_port})")
        except Exception as e:
            print(f"❌ Error conectando a la base de datos: {e}")
            print("⚠️  El bot continuará sin base de datos")
            self.pool = None
            raise
    
    def get_connection(self):
        """Obtener conexión del pool"""
        if not self.pool:
            return None
        return self.pool.getconn()
    
    def return_connection(self, conn):
        """Devolver conexión al pool"""
        if self.pool and conn:
            self.pool.putconn(conn)
    
    def close_all(self):
        """Cerrar todas las conexiones"""
        if self.pool:
            self.pool.closeall()
    
    # ============================================
    # TRADES
    # ============================================
    
    def save_trade(self, trade_data: Dict) -> str:
        """
        Guardar operación en la base de datos
        
        Args:
            trade_data: Diccionario con datos del trade
            
        Returns:
            UUID del trade guardado
        """
        if not self.db_enabled or not self.pool:
            return None
        
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO trades (
                        trade_id, asset, direction, amount, duration,
                        entry_price, exit_price, result, profit, profit_pct,
                        entry_time, exit_time, market_context,
                        rl_confidence, llm_analysis, decision_score,
                        broker, account_type, session_id
                    ) VALUES (
                        %(trade_id)s, %(asset)s, %(direction)s, %(amount)s, %(duration)s,
                        %(entry_price)s, %(exit_price)s, %(result)s, %(profit)s, %(profit_pct)s,
                        %(entry_time)s, %(exit_time)s, %(market_context)s,
                        %(rl_confidence)s, %(llm_analysis)s, %(decision_score)s,
                        %(broker)s, %(account_type)s, %(session_id)s
                    )
                    RETURNING id
                """, trade_data)
                
                trade_uuid = cur.fetchone()[0]
                conn.commit()
                return str(trade_uuid)
        finally:
            self.return_connection(conn)
    
    def update_trade_result(self, trade_id: str, result: str, exit_price: float, 
                           profit: float, exit_time: datetime):
        """Actualizar resultado de un trade"""
        if not self.db_enabled or not self.pool:
            return None
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                profit_pct = (profit / exit_price) * 100 if exit_price > 0 else 0
                
                cur.execute("""
                    UPDATE trades
                    SET result = %s, exit_price = %s, profit = %s, 
                        profit_pct = %s, exit_time = %s, updated_at = NOW()
                    WHERE trade_id = %s
                """, (result, exit_price, profit, profit_pct, exit_time, trade_id))
                
                conn.commit()
        finally:
            self.return_connection(conn)
    
    def get_recent_trades(self, limit: int = 50, asset: Optional[str] = None) -> List[Dict]:
        """Obtener trades recientes"""
        if not self.db_enabled or not self.pool:
            return []
        
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT * FROM trades
                    WHERE 1=1
                """
                params = []
                
                if asset:
                    query += " AND asset = %s"
                    params.append(asset)
                
                query += " ORDER BY entry_time DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]
        finally:
            self.return_connection(conn)
    
    # ============================================
    # MARKET CONDITIONS
    # ============================================
    
    def save_market_conditions(self, conditions: Dict):
        """Guardar condiciones del mercado"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO market_conditions (
                        asset, timeframe, timestamp,
                        rsi, macd, macd_signal, macd_hist,
                        sma_20, sma_50, sma_200, ema_12, ema_26,
                        bb_upper, bb_middle, bb_lower, bb_width,
                        atr, volatility, volume, momentum, roc,
                        open, high, low, close,
                        patterns, order_blocks, fair_value_gaps, liquidity_zones
                    ) VALUES (
                        %(asset)s, %(timeframe)s, %(timestamp)s,
                        %(rsi)s, %(macd)s, %(macd_signal)s, %(macd_hist)s,
                        %(sma_20)s, %(sma_50)s, %(sma_200)s, %(ema_12)s, %(ema_26)s,
                        %(bb_upper)s, %(bb_middle)s, %(bb_lower)s, %(bb_width)s,
                        %(atr)s, %(volatility)s, %(volume)s, %(momentum)s, %(roc)s,
                        %(open)s, %(high)s, %(low)s, %(close)s,
                        %(patterns)s, %(order_blocks)s, %(fair_value_gaps)s, %(liquidity_zones)s
                    )
                """, conditions)
                conn.commit()
        finally:
            self.return_connection(conn)
    
    def get_market_history(self, asset: str, hours: int = 24) -> List[Dict]:
        """Obtener historial de condiciones del mercado"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM market_conditions
                    WHERE asset = %s
                        AND timestamp >= NOW() - INTERVAL '%s hours'
                    ORDER BY timestamp DESC
                """, (asset, hours))
                return [dict(row) for row in cur.fetchall()]
        finally:
            self.return_connection(conn)
    
    # ============================================
    # LEARNING EXPERIENCES
    # ============================================
    
    def save_experience(self, experience: Dict) -> str:
        """Guardar experiencia de aprendizaje"""
        if not self.db_enabled or not self.pool:
            return None
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO learning_experiences (
                        trade_id, state, action, action_confidence,
                        reward, next_state, was_correct, error_type,
                        lesson, should_avoid, model_version
                    ) VALUES (
                        %(trade_id)s, %(state)s, %(action)s, %(action_confidence)s,
                        %(reward)s, %(next_state)s, %(was_correct)s, %(error_type)s,
                        %(lesson)s, %(should_avoid)s, %(model_version)s
                    )
                    RETURNING id
                """, experience)
                
                exp_id = cur.fetchone()[0]
                conn.commit()
                return str(exp_id)
        finally:
            self.return_connection(conn)
    
    def get_learning_experiences(self, limit: int = 1000, 
                                 action: Optional[str] = None) -> List[Dict]:
        """Obtener experiencias para entrenamiento"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT * FROM learning_experiences WHERE 1=1"
                params = []
                
                if action:
                    query += " AND action = %s"
                    params.append(action)
                
                query += " ORDER BY timestamp DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]
        finally:
            self.return_connection(conn)
    
    # ============================================
    # PATTERN PERFORMANCE
    # ============================================
    
    def update_pattern_performance(self, pattern_type: str, asset: str, 
                                   won: bool, profit: float, conditions: Dict):
        """Actualizar rendimiento de un patrón"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Verificar si el patrón existe
                cur.execute("""
                    SELECT id, total_occurrences, wins, losses, avg_profit
                    FROM pattern_performance
                    WHERE pattern_type = %s AND asset = %s
                """, (pattern_type, asset))
                
                row = cur.fetchone()
                
                if row:
                    # Actualizar existente
                    pattern_id, total, wins, losses, avg_profit = row
                    new_total = total + 1
                    new_wins = wins + (1 if won else 0)
                    new_losses = losses + (0 if won else 1)
                    new_win_rate = (new_wins / new_total) * 100
                    new_avg_profit = ((avg_profit * total) + profit) / new_total
                    
                    cur.execute("""
                        UPDATE pattern_performance
                        SET total_occurrences = %s, wins = %s, losses = %s,
                            win_rate = %s, avg_profit = %s, last_seen = NOW(),
                            last_updated = NOW()
                        WHERE id = %s
                    """, (new_total, new_wins, new_losses, new_win_rate, 
                          new_avg_profit, pattern_id))
                else:
                    # Crear nuevo
                    win_rate = 100.0 if won else 0.0
                    cur.execute("""
                        INSERT INTO pattern_performance (
                            pattern_type, asset, timeframe,
                            total_occurrences, wins, losses, win_rate, avg_profit,
                            first_seen, last_seen
                        ) VALUES (
                            %s, %s, 60, 1, %s, %s, %s, %s, NOW(), NOW()
                        )
                    """, (pattern_type, asset, 1 if won else 0, 0 if won else 1,
                          win_rate, profit))
                
                conn.commit()
        finally:
            self.return_connection(conn)
    
    def get_best_patterns(self, asset: Optional[str] = None, 
                         min_occurrences: int = 10) -> List[Dict]:
        """Obtener mejores patrones"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT * FROM pattern_performance
                    WHERE total_occurrences >= %s
                """
                params = [min_occurrences]
                
                if asset:
                    query += " AND asset = %s"
                    params.append(asset)
                
                query += " ORDER BY win_rate DESC, avg_profit DESC LIMIT 20"
                
                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]
        finally:
            self.return_connection(conn)
    
    # ============================================
    # DECISION LOGS
    # ============================================
    
    def log_decision(self, decision_data: Dict) -> str:
        """Registrar decisión del bot"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO decision_logs (
                        asset, timestamp,
                        rl_prediction, rl_confidence, rl_reasoning,
                        technical_signals, technical_score,
                        llm_recommendation, llm_confidence, llm_reasoning,
                        validator_approved, validator_score, validator_reasons,
                        final_decision, decision_executed, execution_reason,
                        trade_id
                    ) VALUES (
                        %(asset)s, %(timestamp)s,
                        %(rl_prediction)s, %(rl_confidence)s, %(rl_reasoning)s,
                        %(technical_signals)s, %(technical_score)s,
                        %(llm_recommendation)s, %(llm_confidence)s, %(llm_reasoning)s,
                        %(validator_approved)s, %(validator_score)s, %(validator_reasons)s,
                        %(final_decision)s, %(decision_executed)s, %(execution_reason)s,
                        %(trade_id)s
                    )
                    RETURNING id
                """, decision_data)
                
                decision_id = cur.fetchone()[0]
                conn.commit()
                return str(decision_id)
        finally:
            self.return_connection(conn)
    
    # ============================================
    # ERROR PATTERNS
    # ============================================
    
    def record_error(self, error_type: str, description: str, 
                    conditions: Dict, trade_id: str, loss: float):
        """Registrar patrón de error"""
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Verificar si el error ya existe
                cur.execute("""
                    SELECT id, occurrences, total_loss, affected_trades
                    FROM error_patterns
                    WHERE error_type = %s
                """, (error_type,))
                
                row = cur.fetchone()
                
                if row:
                    # Actualizar existente
                    error_id, occurrences, total_loss, affected_trades = row
                    new_occurrences = occurrences + 1
                    new_total_loss = total_loss + loss
                    new_avg_loss = new_total_loss / new_occurrences
                    
                    # Agregar trade_id al array
                    cur.execute("""
                        UPDATE error_patterns
                        SET occurrences = %s, total_loss = %s,
                            avg_loss_per_occurrence = %s,
                            affected_trades = array_append(affected_trades, %s::uuid),
                            last_occurrence = NOW(), updated_at = NOW()
                        WHERE id = %s
                    """, (new_occurrences, new_total_loss, new_avg_loss, 
                          trade_id, error_id))
                else:
                    # Crear nuevo
                    cur.execute("""
                        INSERT INTO error_patterns (
                            error_type, error_description, occurrences,
                            common_conditions, affected_trades,
                            total_loss, avg_loss_per_occurrence,
                            first_occurrence, last_occurrence
                        ) VALUES (
                            %s, %s, 1, %s, ARRAY[%s::uuid], %s, %s, NOW(), NOW()
                        )
                    """, (error_type, description, Json(conditions), 
                          trade_id, loss, loss))
                
                conn.commit()
        finally:
            self.return_connection(conn)
    
    def get_common_errors(self, limit: int = 10) -> List[Dict]:
        """Obtener errores más comunes"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM error_patterns
                    ORDER BY occurrences DESC, total_loss DESC
                    LIMIT %s
                """, (limit,))
                return [dict(row) for row in cur.fetchall()]
        finally:
            self.return_connection(conn)
    
    # ============================================
    # ANALYTICS
    # ============================================
    
    def get_performance_stats(self, days: int = 7, 
                             asset: Optional[str] = None) -> Dict:
        """Obtener estadísticas de rendimiento"""
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT 
                        COUNT(*) as total_trades,
                        SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
                        SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses,
                        ROUND(AVG(CASE WHEN result = 'win' THEN 1.0 ELSE 0.0 END) * 100, 2) as win_rate,
                        ROUND(SUM(profit), 2) as total_profit,
                        ROUND(AVG(profit), 2) as avg_profit,
                        MAX(profit) as best_trade,
                        MIN(profit) as worst_trade,
                        ROUND(AVG(rl_confidence), 2) as avg_confidence
                    FROM trades
                    WHERE entry_time >= NOW() - INTERVAL '%s days'
                        AND result IS NOT NULL
                """
                params = [days]
                
                if asset:
                    query += " AND asset = %s"
                    params.append(asset)
                
                cur.execute(query, params)
                return dict(cur.fetchone())
        finally:
            self.return_connection(conn)
    
    def get_performance_by_asset(self, days: int = 30) -> List[Dict]:
        """Obtener rendimiento por activo"""
        if not self.db_enabled or not self.pool:
            return []
        
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM performance_by_asset
                """)
                return [dict(row) for row in cur.fetchall()]
        finally:
            self.return_connection(conn)
    
    def get_performance_by_hour(self) -> List[Dict]:
        """Obtener rendimiento por hora del día"""
        if not self.db_enabled or not self.pool:
            return []
        
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM performance_by_hour")
                return [dict(row) for row in cur.fetchall()]
        finally:
            self.return_connection(conn)

# Instancia global
db = DatabaseManager()
