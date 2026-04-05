#!/usr/bin/env python3
"""
================================================================================
                    BOT DE TRADING ULTRA-INTELIGENTE v2.0
                         Para Exnova - Versin Profesional
================================================================================

Caractersticas:
- Motor de Scoring Unificado (reemplaza ~20 filtros dispersos)
- Gestin de Riesgo Avanzada (Kelly Criterion, Drawdown Protection)
- Conexin Asncrona No-Bloqueante
- Circuit Breaker y Rate Limiting
- Explicabilidad Completa de Decisiones

Autores: Equipo de Desarrollo AI
Versin: 2.0.0
"""
import sys
import os
import time
import signal
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import threading

# Pandas para manejo de datos
import pandas as pd
import numpy as np

# Agregar path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports de componentes nuevos
from core.advanced_risk_manager import (
    AdvancedRiskManager,
    RiskConfig,
    get_risk_manager,
    initialize_risk_manager
)
from core.unified_scoring_engine import (
    UnifiedScoringEngine,
    get_scoring_engine,
    SignalType
)
from core.async_exnova_connector import (
    AsyncExnovaConnector,
    get_async_connector
)

# Imports existentes del bot
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.risk import RiskManager
from core.asset_manager import AssetManager
# ExnovaAPI se importa desde el módulo exnovaapi según la estructura del proyecto
try:
    from exnovaapi.api import ExnovaAPI
except ImportError:
    ExnovaAPI = None  # No se usa directamente en este bot


class UltraSmartBot:
    """
    Bot de Trading Ultra-Inteligente

    Orquesta todos los componentes nuevos y existentes
    para tomar decisiones de trading ptimas.
    """

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        demo: bool = True,
        config_file: str = "bot_config.json"
    ):
        self.demo_mode = demo
        self.email = email or Config.EMAIL
        self.password = password or Config.PASSWORD

        # Cargar configuracin
        self.config = self._load_config(config_file)

        # Inicializar componentes de riesgo
        risk_config = RiskConfig(
            max_drawdown_daily=self.config.get('risk', {}).get('max_daily_drawdown', 0.15),
            max_trades_per_hour=self.config.get('limits', {}).get('max_trades_per_hour', 8),
            cooldown_after_loss_seconds=self.config.get('limits', {}).get('cooldown_after_loss', 300),
        )
        self.risk_manager = initialize_risk_manager(100.0, risk_config)  # Balance inicial dummy

        # Inicializar motor de scoring
        self.scoring_engine = get_scoring_engine()

        # Inicializar conector asncrono
        self.connector = get_async_connector()

        # Componentes existentes
        self.market_data = MarketDataHandler(
            broker_name=Config.BROKER_NAME,
            account_type="demo" if demo else "real"
        )
        self.feature_engineer = FeatureEngineer()
        self.asset_manager = AssetManager(self.market_data)

        # Estado
        self.running = False
        self.paused = False
        self.current_asset: Optional[str] = None
        self.last_signal_time: Optional[datetime] = None

        # Mtricas
        self.metrics = {
            'signals_generated': 0,
            'trades_executed': 0,
            'trades_won': 0,
            'trades_lost': 0,
            'total_profit': 0.0,
            'win_rate': 0.0,
        }

        # Configurar signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _load_config(self, config_file: str) -> Dict:
        """Cargar configuracin desde archivo"""
        default_config = {
            'trading_hours': {
                'london': [8, 17],
                'ny': [13, 22],
            },
            'risk': {
                'max_daily_drawdown': 0.15,
                'max_position_size_pct': 0.05,
            },
            'limits': {
                'max_trades_per_hour': 8,
                'max_trades_per_day': 40,
                'cooldown_after_loss': 300,
                'min_confidence': 0.65,
            },
            'assets': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD'],
        }

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    # Merge configs
                    for key in default_config:
                        if key in file_config:
                            if isinstance(default_config[key], dict):
                                default_config[key].update(file_config[key])
                            else:
                                default_config[key] = file_config[key]
            except Exception as e:
                print(f" Error cargando config: {e}. Usando defaults.")

        return default_config

    def _signal_handler(self, sig, frame):
        """Manejar Ctrl+C"""
        print("\n\n Deteniendo bot...")
        self.running = False

    def connect(self) -> bool:
        """Conectar con Exnova"""
        print("=" * 70)
        print(" Conectando con Exnova...")
        print("=" * 70)

        try:
            # Iniciar conector asncrono
            self.connector.set_auth_token(f"{self.email}:{self.password}")
            self.connector.set_callbacks(
                on_connect=self._on_connect,
                on_disconnect=self._on_disconnect,
                on_message=self._on_message,
                on_error=self._on_error
            )
            self.connector.start()

            # Esperar conexin
            time.sleep(2)

            if not self.connector.connection_state.connected:
                print(" No se pudo conectar")
                return False

            # Obtener balance
            balance_info = self.market_data.get_balance()
            if balance_info:
                balance = balance_info.get('balance', 100.0)
                self.risk_manager.initialize(balance)
                print(f" Balance: ${balance:.2f}")

            print(" Conectado exitosamente")
            return True

        except Exception as e:
            print(f" Error de conexin: {e}")
            return False

    def _on_connect(self):
        """Callback de conexin"""
        print(" Conexin establecida")

    def _on_disconnect(self):
        """Callback de desconexin"""
        print(" Desconectado del servidor")

    def _on_message(self, data: Dict):
        """Callback de mensaje recibido"""
        # Procesar mensajes del servidor
        pass

    def _on_error(self, error: Exception):
        """Callback de error"""
        print(f" Error: {error}")

    def analyze_market(self, asset: str) -> Optional[Dict]:
        """
        Analizar mercado y generar seal

        Args:
            asset: Par a analizar (ej. "EUR/USD")

        Returns:
            Dict con anlisis completo o None si no hay seal clara
        """
        try:
            # Obtener datos de mercado
            df = self.market_data.get_candles(asset, timeframe=60, count=100)
            df_m5 = self.market_data.get_candles(asset, timeframe=300, count=50)
            df_m15 = self.market_data.get_candles(asset, timeframe=900, count=30)

            if df is None or len(df) < 50:
                print(f" Datos insuficientes para {asset}")
                return None

            # Calcular indicadores
            df = self.feature_engineer.add_features(df)
            if df_m5 is not None:
                df_m5 = self.feature_engineer.add_features(df_m5)
            if df_m15 is not None:
                df_m15 = self.feature_engineer.add_features(df_m15)

            current_price = df['close'].iloc[-1]

            # Obtener datos adicionales
            smart_money_data = self._analyze_smart_money(df)
            market_structure_data = self._analyze_market_structure(df)

            # Calcular scoring unificado
            scoring_result = self.scoring_engine.score(
                df=df,
                df_m5=df_m5,
                df_m15=df_m15,
                current_price=current_price,
                asset=asset,
                smart_money_data=smart_money_data,
                market_structure_data=market_structure_data
            )

            # Generar reporte
            self.metrics['signals_generated'] += 1

            result = {
                'asset': asset,
                'timestamp': datetime.now(),
                'score': scoring_result.total_score,
                'signal': scoring_result.signal_type.value,
                'confidence': scoring_result.confidence,
                'recommendation': scoring_result.recommendation,
                'expected_winrate': scoring_result.expected_winrate,
                'market_phase': scoring_result.market_phase,
                'reasons': scoring_result.reasons_to_trade,
                'warnings': scoring_result.warnings,
                'category_scores': {
                    k: v.score for k, v in scoring_result.categories.items()
                }
            }

            return result

        except Exception as e:
            print(f" Error analizando {asset}: {e}")
            return None

    def _analyze_smart_money(self, df: pd.DataFrame) -> Dict:
        """Analizar factores de Smart Money"""
        # Implementacin simplificada - usar SmartMoneyAnalyzer existente
        try:
            from core.smart_money_analyzer import SmartMoneyAnalyzer
            analyzer = SmartMoneyAnalyzer()
            return analyzer.analyze(df)
        except:
            return {
                'order_block_hit': False,
                'fvg_detected': False,
                'liquidity_grab': False,
                'premium_discount': 0.5
            }

    def _analyze_market_structure(self, df: pd.DataFrame) -> Dict:
        """Analizar estructura de mercado"""
        # Implementacin simplificada
        try:
            from core.market_structure_analyzer import MarketStructureAnalyzer
            analyzer = MarketStructureAnalyzer()
            return analyzer.analyze(df)
        except:
            return {
                'trend_direction': 'neutral',
                'trend_strength': 0.5,
                'bos_detected': False
            }

    def should_trade(self, analysis: Dict) -> bool:
        """
        Determinar si debemos operar basado en anlisis

        Args:
            analysis: Resultado del anlisis de mercado

        Returns:
            True si debemos operar
        """
        if analysis is None:
            return False

        # Verificar recomendacin
        if analysis['recommendation'] != "TRADE":
            return False

        # Verificar confianza mnima
        min_confidence = self.config['limits'].get('min_confidence', 0.65)
        if analysis['confidence'] < min_confidence:
            print(f" Confianza {analysis['confidence']*100:.1f}% < mnimo {min_confidence*100:.1f}%")
            return False

        # Verificar cooldown despus de prdida
        if self.risk_manager.last_trade_was_loss and self.risk_manager.last_trade_time:
            time_since_loss = (datetime.now() - self.risk_manager.last_trade_time).total_seconds()
            cooldown = self.config['limits'].get('cooldown_after_loss', 300)
            if time_since_loss < cooldown:
                return False

        # Verificar lmites de operaciones
        if not self.risk_manager._can_trade_more():
            return False

        # Verificar si no estamos detenidos por drawdown
        if self.risk_manager.is_stopped:
            print(f" Trading detenido: {self.risk_manager.stop_reason}")
            return False

        return True

    def execute_trade(self, analysis: Dict) -> bool:
        """
        Ejecutar operacin

        Args:
            analysis: Anlisis de mercado

        Returns:
            True si la operacin se ejecut exitosamente
        """
        asset = analysis['asset']
        signal = analysis['signal']
        confidence = analysis['confidence']

        try:
            # Calcular tamao de posicin
            position_size = self.risk_manager.calculate_position_size(
                confidence=confidence
            )

            if position_size <= 0:
                print(" Tamao de posicin invlido")
                return False

            # Obtener ID del activo
            asset_id = self.asset_manager.get_asset_id(asset)
            if not asset_id:
                print(f" Asset ID no encontrado para {asset}")
                return False

            # Determinar direccin y expiracin
            direction = "call" if signal == "CALL" else "put"
            expiration = self.config.get('expiration_seconds', 300)  # 5 minutos

            print(f"\n{'='*60}")
            print(f" EJECUTANDO OPERACIN")
            print(f"{'='*60}")
            print(f"  Activo: {asset}")
            print(f"  Direccin: {direction.upper()}")
            print(f"  Monto: ${position_size:.2f}")
            print(f"  Expiracin: {expiration}s")
            print(f"  Confianza: {confidence*100:.1f}%")
            print(f"  Score: {analysis['score']:.1f}/100")
            print(f"{'='*60}")

            if self.demo_mode:
                # Modo demo - simular
                print(" MODO DEMO - Operacin simulada")
                self.metrics['trades_executed'] += 1
                return True

            # Ejecutar orden real
            loop = self.connector._loop
            if loop and self.connector._running:
                future = asyncio.run_coroutine_threadsafe(
                    self.connector.place_order(
                        asset_id=asset_id,
                        amount=position_size,
                        direction=direction,
                        expiration=expiration
                    ),
                    loop
                )
                result = future.result(timeout=10)

                if result.get('success'):
                    print(f" Orden ejecutada: {result.get('order_id')}")
                    self.metrics['trades_executed'] += 1
                    return True
                else:
                    print(f" Error ejecutando orden: {result.get('error')}")
                    return False
            else:
                print(" Conector no disponible, usando fallback")
                return False

        except Exception as e:
            print(f" Error ejecutando operacin: {e}")
            return False

    def run_loop(self):
        """Loop principal del bot"""
        print("\n" + "=" * 70)
        print(" INICIANDO BOT ULTRA-INTELIGENTE")
        print("=" * 70)
        print(f"Modo: {'DEMO' if self.demo_mode else 'REAL'}")
        print(f"Activos: {', '.join(self.config['assets'])}")
        print(f"Confianza mnima: {self.config['limits']['min_confidence']*100:.1f}%")
        print(f"Mx operaciones/hora: {self.config['limits']['max_trades_per_hour']}")
        print("=" * 70 + "\n")

        self.running = True
        assets = self.config['assets']
        asset_index = 0

        while self.running:
            try:
                # Verificar si estamos en horario de trading
                if not self._is_trading_hours():
                    print(" Fuera de horario de trading - esperando...")
                    time.sleep(60)
                    continue

                # Analizar activo actual
                asset = assets[asset_index % len(assets)]
                print(f"\n Analizando {asset}...")

                analysis = self.analyze_market(asset)

                if analysis:
                    # Imprimir anlisis detallado
                    self._print_analysis(analysis)

                    # Verificar si debemos operar
                    if self.should_trade(analysis):
                        print("\n Seal vlida - Ejecutando operacin...")
                        success = self.execute_trade(analysis)

                        if success:
                            self.last_signal_time = datetime.now()
                            # Cooldown despus de operacin
                            time.sleep(60)  # Esperar 1 minuto
                    else:
                        print(" Esperando mejor oportunidad...")

                # Rotar activos
                asset_index += 1

                # Esperar antes de siguiente anlisis
                time.sleep(30)  # Analizar cada 30 segundos

            except KeyboardInterrupt:
                print("\n\n Interrumpido por usuario")
                break
            except Exception as e:
                print(f" Error en loop principal: {e}")
                time.sleep(10)

        # Cleanup
        self.shutdown()

    def _is_trading_hours(self) -> bool:
        """Verificar si estamos en horario de trading ptimo"""
        now = datetime.now()
        hour_utc = now.hour

        trading_hours = self.config.get('trading_hours', {})

        # Verificar sesin Londres
        london_start, london_end = trading_hours.get('london', [8, 17])
        if london_start <= hour_utc <= london_end:
            return True

        # Verificar sesin NY
        ny_start, ny_end = trading_hours.get('ny', [13, 22])
        if ny_start <= hour_utc <= ny_end:
            return True

        return False

    def _print_analysis(self, analysis: Dict):
        """Imprimir anlisis de forma legible"""
        print("\n" + "-" * 50)
        print(f" ANLISIS: {analysis['asset']}")
        print("-" * 50)
        print(f"  Score Total: {analysis['score']:.1f}/100")
        print(f"  Seal: {analysis['signal']}")
        print(f"  Confianza: {analysis['confidence']*100:.1f}%")
        print(f"  Winrate Esperado: {analysis['expected_winrate']*100:.1f}%")
        print(f"  Recomendacin: {analysis['recommendation']}")
        print(f"  Fase Mercado: {analysis['market_phase']}")

        print("\n  Scores por Categora:")
        for cat, score in analysis['category_scores'].items():
            print(f"    {cat}: {score:.1f}")

        if analysis['reasons']:
            print("\n  Razones para operar:")
            for reason in analysis['reasons'][:5]:  # Mximo 5 razones
                print(f"     {reason}")

        if analysis['warnings']:
            print("\n  Advertencias:")
            for warning in analysis['warnings']:
                print(f"     {warning}")

        print("-" * 50)

    def print_status(self):
        """Imprimir estado actual del bot"""
        risk_status = self.risk_manager.get_status_report()

        print("\n" + "=" * 70)
        print(" ESTADO DEL BOT")
        print("=" * 70)
        print(f"  Balance: ${risk_status['balance']:.2f}")
        print(f"  PnL Total: ${risk_status['total_pnl']:.2f}")
        print(f"  Drawdown: {risk_status['drawdown']*100:.2f}%")
        print(f"  Win Rate: {risk_status['stats']['win_rate']:.1f}%")
        print(f"  Profit Factor: {risk_status['stats']['profit_factor']:.2f}")
        print(f"  Kelly Fraction: {risk_status['kelly_fraction']*100:.1f}%")
        print(f"  Trades Hoy: {risk_status['trades_today']}")
        print(f"  Trades Esta Hora: {risk_status['trades_this_hour']}")

        if risk_status['is_stopped']:
            print(f"\n   TRADING DETENIDO: {risk_status['stop_reason']}")

        print("=" * 70)

    def shutdown(self):
        """Cerrar bot limpiamente"""
        print("\n Cerrando bot...")
        self.running = False
        self.connector.stop()
        self.print_status()
        print(" Bot cerrado")


# Import necesario para place_order
import asyncio


def main():
    """Funcin principal"""
    parser = argparse.ArgumentParser(description='Ultra-Smart Trading Bot')
    parser.add_argument('--email', type=str, help='Email de Exnova')
    parser.add_argument('--password', type=str, help='Password de Exnova')
    parser.add_argument('--demo', action='store_true', help='Modo demo')
    parser.add_argument('--config', type=str, default='bot_config.json', help='Archivo de configuracin')

    args = parser.parse_args()

    # Crear bot
    bot = UltraSmartBot(
        email=args.email,
        password=args.password,
        demo=args.demo,
        config_file=args.config
    )

    # Conectar
    if not bot.connect():
        print(" No se pudo conectar. Verifica credenciales.")
        return

    # Imprimir configuracin
    bot.print_status()

    # Iniciar loop
    try:
        bot.run_loop()
    except KeyboardInterrupt:
        print("\n\n Detenido por usuario")
    finally:
        bot.shutdown()


if __name__ == "__main__":
    main()
