"""
👤 SISTEMA DE SUPERVISIÓN HUMANA
El bot te consultará a ti para decisiones importantes
"""
import json
import time
from datetime import datetime
from pathlib import Path
import subprocess
import platform

class HumanSupervisor:
    def __init__(self):
        self.supervisor_file = Path("data/human_supervisor.json")
        self.config = self._load_config()
        self.pending_questions = []
        self.last_consultation = 0
        self.cooldown_seconds = 60
        
    def _load_config(self):
        if self.supervisor_file.exists():
            try:
                with open(self.supervisor_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {
            'enabled': True,
            'notify_telegram': True,
            'notify_console': True,
            'auto_consult_on_loss': True,
            'auto_consult_on_low_confidence': True,
            'consult_confidence_threshold': 75,
            'message_template': '🤖 CONSULTA DE SUPERVISIÓN\n\n{question}\n\nResponde con: CONFIRMAR / RECHAZAR / CANCELAR'
        }
    
    def _save_config(self):
        self.supervisor_file.parent.mkdir(exist_ok=True, parents=True)
        with open(self.supervisor_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    def should_consult(self, operation_data):
        """Determina si debe consultarte"""
        if not self.config.get('enabled', True):
            return False
        
        elapsed = time.time() - self.last_consultation
        if elapsed < self.cooldown_seconds:
            return False
        
        profit = operation_data.get('profit', 0)
        confidence = operation_data.get('confidence', 0)
        
        if self.config.get('auto_consult_on_loss', True) and profit <= 0:
            return True
        
        if self.config.get('auto_consult_on_low_confidence', True):
            threshold = self.config.get('consult_confidence_threshold', 75)
            if confidence < threshold:
                return True
        
        return False
    
    def prepare_question(self, operation_data):
        """Prepara la pregunta para ti"""
        asset = operation_data.get('asset', 'N/A')
        direction = operation_data.get('direction', 'N/A')
        confidence = operation_data.get('confidence', 0)
        profit = operation_data.get('profit', 0)
        reason = operation_data.get('reason', 'N/A')
        
        outcome = "GANÓ" if profit > 0 else "PERDIÓ"
        
        question = f"""
📊 ANÁLISIS DE OPERACIÓN

Asset: {asset}
Dirección: {direction}
Confianza: {confidence}%
Resultado: {outcome} (${profit:.2f})
Razón: {reason}

¿Debo ajustar los parámetros del bot según este resultado?
"""
        return question
    
    def notify(self, title, message, urgency='normal'):
        """Te notifica - múltiples canales"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"⏰ {timestamp}\n\n{title}\n\n{message}"
        
        print("\n" + "="*60)
        print("📢 NOTIFICACIÓN DE SUPERVISIÓN")
        print("="*60)
        print(full_message)
        print("="*60 + "\n")
        
        self._log_notification(title, message, urgency)
        
        if self.config.get('notify_telegram', True):
            self._send_telegram_notification(full_message)
        
        if self.config.get('notify_console', True):
            self._show_console_alert(title, message, urgency)
    
    def _log_notification(self, title, message, urgency):
        """Guarda notificación para referencia"""
        log_file = Path("data/supervisor_log.json")
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except: pass
        
        logs.append({
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'message': message[:200],
            'urgency': urgency
        })
        
        if len(logs) > 100:
            logs = logs[-100:]
        
        log_file.parent.mkdir(exist_ok=True, parents=True)
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, default=str)
    
    def _show_console_alert(self, title, message, urgency):
        """Muestra alerta en consola"""
        emojis = {
            'low': 'ℹ️',
            'normal': '🔔',
            'high': '⚠️',
            'critical': '🚨'
        }
        
        print(f"{emojis.get(urgency, '🔔')} {title}")
        print(message)
    
    def _send_telegram_notification(self, message):
        """Envía notificación por Telegram"""
        try:
            import requests
            telegram_config = self._get_telegram_config()
            
            if not telegram_config.get('bot_token') or not telegram_config.get('chat_id'):
                return
            
            url = f"https://api.telegram.org/bot{telegram_config['bot_token']}/sendMessage"
            data = {
                'chat_id': telegram_config['chat_id'],
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                print("✅ Notificación Telegram enviada")
            else:
                print(f"⚠️ Error Telegram: {response.status_code}")
        except ImportError:
            print("⚠️ requests no disponible para Telegram")
        except Exception as e:
            print(f"⚠️ Error enviando Telegram: {e}")
    
    def _get_telegram_config(self):
        """Carga config de Telegram desde .env"""
        try:
            from dotenv import load_dotenv
            import os
            load_dotenv()
            return {
                'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
                'chat_id': os.getenv('TELEGRAM_SUPERVISOR_CHAT_ID', '')
            }
        except:
            return {'bot_token': '', 'chat_id': ''}
    
    def consult_human(self, question, operation_data):
        """Te consulta y espera respuesta"""
        self.last_consultation = time.time()
        
        self.notify(
            "🤔 CONSULTA DE DECISIÓN",
            question,
            urgency='high' if operation_data.get('profit', 0) <= 0 else 'normal'
        )
        
        return self._wait_for_response(question, operation_data)
    
    def _wait_for_response(self, question, operation_data):
        """Espera tu respuesta (modo consola)"""
        print("\n" + "="*60)
        print("⏳ ESPERANDO TU RESPUESTA...")
        print("="*60)
        print("Opciones: [C]onfirmar / [R]echazar / [S]kip / [A]justes")
        print("="*60 + "\n")
        
        print(">> Escribe tu respuesta: ", end="")
        
        try:
            response = input().strip().lower()
        except:
            response = 's'
        
        if response in ['c', 'confirmar', 'confirm', 'si', 's', 'yes', 'y']:
            return {'action': 'CONFIRM', 'message': 'Operación confirmada por supervisor'}
        elif response in ['r', 'rechazar', 'rechazo', 'no', 'n']:
            return {'action': 'REJECT', 'message': 'Operación rechazada por supervisor'}
        elif response in ['a', 'ajustes', 'adjust', 'ajustar']:
            return {'action': 'ADJUST', 'message': 'Se requieren ajustes'}
        else:
            return {'action': 'SKIP', 'message': 'Sin respuesta - continuar'}
    
    def analyze_and_recommend(self, operation_data):
        """Analiza la operación y te pide recomendaciones"""
        asset = operation_data.get('asset')
        direction = operation_data.get('direction')
        profit = operation_data.get('profit', 0)
        confidence = operation_data.get('confidence', 0)
        
        recommendation = f"""
📈 ANÁLISIS POST-OPERACIÓN:

Asset: {asset}
Dirección: {direction}
Ganancia/Perdida: ${profit:.2f}
Confianza: {confidence}%

"""
        
        if profit <= 0:
            recommendation += """
❌ LA OPERACIÓN PERDIÓ

Posibles razones:
- Entrada en sentido contrario a la tendencia
- Señal en zona de resistencia/soporte incorrecta
- RSI en zona extrema sin inversión
- Alta confianza pero señal falsa

Acciones sugeridas:
1. Subir threshold de confianza
2. Evitar este asset temporalmente
3. Bloquear esta dirección
4. Ajustar timing de entrada
"""
        else:
            recommendation += """
✅ LA OPERACIÓN GANÓ

Factores exitosos:
- Rechazo de nivel confirmado
- RSI en zona de reversión
- Con la tendencia principal
- Alta confianza
"""
        
        recommendation += "\n¿Qué ajustes debo hacer? (responde con ajustes específicos)"
        
        return recommendation
    
    def get_daily_summary(self):
        """Te envía resumen del día"""
        from pathlib import Path
        import os
        
        summary_file = Path("data/deep_analysis.json")
        adjustments_file = Path("data/adjustments.json")
        
        summary = "📊 RESUMEN DIARIO DEL BOT\n\n"
        
        if summary_file.exists():
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ops = data.get('operations', [])
                    
                    if ops:
                        recent = ops[-20:]
                        wins = sum(1 for o in recent if o.get('outcome') == 'WIN')
                        total = len(recent)
                        win_rate = (wins / total * 100) if total > 0 else 0
                        
                        summary += f"Operaciones últimas 20: {total}\n"
                        summary += f"Win Rate: {win_rate:.1f}%\n"
                        summary += f"W: {wins} | P: {total - wins}\n\n"
            except: pass
        
        if adjustments_file.exists():
            try:
                with open(adjustments_file, 'r', encoding='utf-8') as f:
                    adj = json.load(f)
                    summary += f"Confidence Threshold: {adj.get('confidence_threshold', 80)}%\n"
                    summary += f"Assets evitados: {len(adj.get('asset_blacklist', []))}\n"
                    summary += f"Assets preferidos: {len(adj.get('asset_whitelist', []))}\n"
            except: pass
        
        return summary
    
    def update_config(self, key, value):
        """Actualiza configuración de supervisión"""
        self.config[key] = value
        self._save_config()
        print(f"✅ Configuración actualizada: {key} = {value}")


supervisor = HumanSupervisor()