#!/usr/bin/env python3
"""
Bot de Trading Headless (sin GUI) para EasyPanel
Ejecuta el bot en modo consola con logging completo
"""

import sys
import os
import signal
import logging
import time
from pathlib import Path
from datetime import datetime

# Configurar logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"bot_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Importar configuración
from config import Config
from core.trader import LiveTrader
from data.market_data import MarketDataManager

class HeadlessBot:
    """Bot de trading en modo headless"""
    
    def __init__(self):
        self.trader = None
        self.running = False
        self.logger = logging.getLogger(__name__)
        
        # Registrar manejadores de señales
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
    def _handle_signal(self, signum, frame):
        """Manejar señales de terminación"""
        self.logger.info(f"Señal recibida: {signum}. Deteniendo bot...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Iniciar el bot"""
        try:
            self.logger.info("=" * 60)
            self.logger.info("🚀 INICIANDO BOT DE TRADING HEADLESS")
            self.logger.info("=" * 60)
            
            # Validar configuración
            self._validate_config()
            
            # Inicializar trader
            self.logger.info("Inicializando trader...")
            self.trader = LiveTrader()
            
            # Crear flag de ejecución
            Path("data/bot_running.flag").touch()
            
            self.running = True
            self.logger.info("✅ Bot iniciado correctamente")
            self.logger.info(f"Broker: {Config.BROKER_NAME}")
            self.logger.info(f"Tipo de cuenta: {Config.ACCOUNT_TYPE}")
            self.logger.info(f"Activo por defecto: {Config.DEFAULT_ASSET}")
            
            # Loop principal
            self._run_loop()
            
        except Exception as e:
            self.logger.error(f"❌ Error al iniciar bot: {e}", exc_info=True)
            self.stop()
            sys.exit(1)
    
    def _validate_config(self):
        """Validar configuración necesaria"""
        if not Config.EXNOVA_EMAIL or Config.EXNOVA_EMAIL == "tu@email.com":
            raise ValueError("❌ EXNOVA_EMAIL no configurado en .env")
        if not Config.EXNOVA_PASSWORD or Config.EXNOVA_PASSWORD == "tupassword":
            raise ValueError("❌ EXNOVA_PASSWORD no configurado en .env")
    
    def _run_loop(self):
        """Loop principal del bot"""
        self.logger.info("Entrando en loop principal...")
        
        try:
            while self.running:
                try:
                    # El trader se ejecuta en su propio thread
                    time.sleep(1)
                except KeyboardInterrupt:
                    self.logger.info("Interrupción del usuario detectada")
                    break
                except Exception as e:
                    self.logger.error(f"Error en loop principal: {e}", exc_info=True)
                    time.sleep(5)  # Esperar antes de reintentar
                    
        except Exception as e:
            self.logger.error(f"Error crítico en loop: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Detener el bot"""
        if self.running:
            self.logger.info("Deteniendo bot...")
            self.running = False
            
            if self.trader:
                try:
                    self.trader.stop()
                except Exception as e:
                    self.logger.error(f"Error al detener trader: {e}")
            
            # Remover flag de ejecución
            try:
                Path("data/bot_running.flag").unlink(missing_ok=True)
            except Exception as e:
                self.logger.error(f"Error al remover flag: {e}")
            
            self.logger.info("✅ Bot detenido")

def main():
    """Punto de entrada principal"""
    bot = HeadlessBot()
    bot.start()

if __name__ == "__main__":
    main()
