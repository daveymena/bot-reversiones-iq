"""
Professional Chart Widget - Gráfico profesional con indicadores visuales
Muestra velas, indicadores, señales y análisis en tiempo real
"""
import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtGui import QColor, QPicture, QPainter, QFont
from PySide6.QtCore import QRectF, QPointF, Qt
import numpy as np
import pandas as pd

class CandlestickItem(pg.GraphicsObject):
    """Velas japonesas profesionales - Estilo Exnova"""
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data  # [(time, open, high, low, close), ...]
        self.picture = None
        self.generatePicture()

    def generatePicture(self):
        self.picture = QPicture()
        p = QPainter(self.picture)
        
        if not self.data or len(self.data) == 0:
            p.end()
            return
        
        # Calcular ancho de vela (más ancho para mejor visibilidad)
        if len(self.data) > 1:
            w = (self.data[1][0] - self.data[0][0]) * 0.4
        else:
            w = 0.4
        
        for (t, open_price, high, low, close) in self.data:
            # Validar datos
            if open_price == 0 or close == 0 or high == 0 or low == 0:
                continue
            
            # Color de la vela (estilo Exnova)
            if close >= open_price:
                # Vela alcista (verde brillante)
                pen_color = QColor(0, 255, 100, 255)
                brush_color = QColor(0, 220, 80, 200)
            else:
                # Vela bajista (roja brillante)
                pen_color = QColor(255, 50, 50, 255)
                brush_color = QColor(220, 30, 30, 200)
            
            # Dibujar mecha (línea delgada)
            p.setPen(pg.mkPen(pen_color, width=1.5))
            p.drawLine(QPointF(t, low), QPointF(t, high))
            
            # Dibujar cuerpo de la vela
            p.setPen(pg.mkPen(pen_color, width=1))
            p.setBrush(pg.mkBrush(brush_color))
            
            body_height = abs(close - open_price)
            
            # Si es vela doji (sin cuerpo), dibujar línea horizontal
            if body_height < 0.00001:
                p.drawLine(QPointF(t - w, open_price), QPointF(t + w, open_price))
            else:
                # Dibujar rectángulo del cuerpo
                body_top = max(open_price, close)
                p.drawRect(QRectF(t - w, body_top, w * 2, body_height))
        
        p.end()

    def paint(self, p, *args):
        if self.picture:
            p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        if self.picture:
            return QRectF(self.picture.boundingRect())
        return QRectF()

class ProfessionalChartWidget(QWidget):
    """
    Gráfico profesional con:
    - Velas japonesas
    - Indicadores técnicos (RSI, MACD, BB, SMAs)
    - Señales de trading (flechas)
    - Zonas de soporte/resistencia
    - Panel de análisis
    """
    def __init__(self):
        super().__init__()
        self.candles_data = []
        self.df = None
        self.last_signal = None
        self.support_zones = []
        self.resistance_zones = []
        self.candle_items = []  # Para almacenar items de velas dibujadas
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Panel superior: Información del activo y análisis
        self.info_panel = self.create_info_panel()
        main_layout.addWidget(self.info_panel)
        
        # Gráfico principal con velas
        self.main_plot = pg.PlotWidget()
        self.main_plot.setBackground('#0a0a0a')
        self.main_plot.showGrid(x=True, y=True, alpha=0.3)
        self.main_plot.setLabel('left', 'Precio')
        self.main_plot.setLabel('bottom', 'Tiempo')
        self.main_plot.setTitle("📊 Gráfico de Trading Profesional", color='#00ff00', size='14pt')
        
        # Velas japonesas
        self.candlestick = None
        
        # Indicadores en el gráfico principal
        self.sma_20_curve = self.main_plot.plot(pen=pg.mkPen('#FFA500', width=2), name='SMA 20')
        self.sma_50_curve = self.main_plot.plot(pen=pg.mkPen('#FF1493', width=2), name='SMA 50')
        self.bb_upper_curve = self.main_plot.plot(pen=pg.mkPen('#00BFFF', width=1, style=Qt.DashLine), name='BB Superior')
        self.bb_lower_curve = self.main_plot.plot(pen=pg.mkPen('#00BFFF', width=1, style=Qt.DashLine), name='BB Inferior')
        self.bb_mid_curve = self.main_plot.plot(pen=pg.mkPen('#00BFFF', width=1, style=Qt.DotLine), name='BB Media')
        
        # Zonas de soporte/resistencia
        self.support_lines = []
        self.resistance_lines = []
        
        # Señales de trading (flechas)
        self.signal_arrows = []
        
        # Leyenda
        legend = self.main_plot.addLegend(offset=(10, 10))
        
        main_layout.addWidget(self.main_plot, stretch=3)
        
        # Subgráfico: RSI
        self.rsi_plot = pg.PlotWidget()
        self.rsi_plot.setBackground('#0a0a0a')
        self.rsi_plot.showGrid(x=True, y=True, alpha=0.3)
        self.rsi_plot.setLabel('left', 'RSI')
        self.rsi_plot.setYRange(0, 100)
        self.rsi_plot.setMaximumHeight(150)
        
        # Líneas de referencia RSI
        self.rsi_plot.addLine(y=70, pen=pg.mkPen('#FF0000', width=1, style=Qt.DashLine))
        self.rsi_plot.addLine(y=30, pen=pg.mkPen('#00FF00', width=1, style=Qt.DashLine))
        self.rsi_plot.addLine(y=50, pen=pg.mkPen('#FFFFFF', width=1, style=Qt.DotLine))
        
        self.rsi_curve = self.rsi_plot.plot(pen=pg.mkPen('#FFFF00', width=2), name='RSI')
        
        main_layout.addWidget(self.rsi_plot, stretch=1)
        
        # Subgráfico: MACD
        self.macd_plot = pg.PlotWidget()
        self.macd_plot.setBackground('#0a0a0a')
        self.macd_plot.showGrid(x=True, y=True, alpha=0.3)
        self.macd_plot.setLabel('left', 'MACD')
        self.macd_plot.setMaximumHeight(150)
        
        # Línea de referencia MACD
        self.macd_plot.addLine(y=0, pen=pg.mkPen('#FFFFFF', width=1, style=Qt.DashLine))
        
        self.macd_curve = self.macd_plot.plot(pen=pg.mkPen('#00FF00', width=2), name='MACD')
        self.macd_signal_curve = self.macd_plot.plot(pen=pg.mkPen('#FF0000', width=1), name='Signal')
        self.macd_histogram = None  # Barras del histograma
        
        main_layout.addWidget(self.macd_plot, stretch=1)
        
        # Panel inferior: Análisis de decisión
        self.analysis_panel = self.create_analysis_panel()
        main_layout.addWidget(self.analysis_panel)

    def create_info_panel(self):
        """Panel superior con información del activo"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #00ff00;
                border-radius: 5px;
                padding: 5px;
            }
            QLabel {
                color: #ffffff;
                font-size: 12pt;
                font-weight: bold;
            }
        """)
        panel.setMaximumHeight(80)
        
        layout = QHBoxLayout(panel)
        
        self.asset_label = QLabel("Activo: --")
        self.price_label = QLabel("Precio: --")
        self.change_label = QLabel("Cambio: --")
        self.trend_label = QLabel("Tendencia: --")
        self.score_label = QLabel("Score: --")
        
        layout.addWidget(self.asset_label)
        layout.addWidget(self.price_label)
        layout.addWidget(self.change_label)
        layout.addWidget(self.trend_label)
        layout.addWidget(self.score_label)
        layout.addStretch()
        
        return panel

    def create_analysis_panel(self):
        """Panel inferior con análisis de decisión"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #00bfff;
                border-radius: 5px;
                padding: 10px;
            }
            QLabel {
                color: #ffffff;
                font-size: 11pt;
            }
        """)
        panel.setMaximumHeight(120)
        
        layout = QVBoxLayout(panel)
        
        title = QLabel("📋 ANÁLISIS DE DECISIÓN")
        title.setStyleSheet("font-size: 13pt; font-weight: bold; color: #00bfff;")
        layout.addWidget(title)
        
        self.decision_label = QLabel("Esperando análisis...")
        self.decision_label.setWordWrap(True)
        layout.addWidget(self.decision_label)
        
        return panel

    def update_full_chart(self, df, asset_name=""):
        """
        Actualiza el gráfico completo con DataFrame
        
        Args:
            df: DataFrame con columnas: open, high, low, close, rsi, macd, etc.
            asset_name: Nombre del activo
        """
        if df is None or df.empty:
            return
        
        self.df = df.copy()
        
        # Actualizar información del activo
        if asset_name:
            self.asset_label.setText(f"📊 Activo: {asset_name}")
        
        last_price = df.iloc[-1]['close']
        self.price_label.setText(f"💰 Precio: {last_price:.5f}")
        
        # Calcular cambio
        if len(df) >= 2:
            prev_price = df.iloc[-2]['close']
            change = ((last_price - prev_price) / prev_price) * 100
            color = "#00ff00" if change >= 0 else "#ff0000"
            symbol = "▲" if change >= 0 else "▼"
            self.change_label.setText(f"{symbol} Cambio: {change:.3f}%")
            self.change_label.setStyleSheet(f"color: {color};")
        
        # Determinar tendencia
        if 'sma_20' in df.columns and 'sma_50' in df.columns:
            sma_20 = df.iloc[-1]['sma_20']
            sma_50 = df.iloc[-1]['sma_50']
            if sma_20 > sma_50 and last_price > sma_20:
                trend = "📈 ALCISTA"
                trend_color = "#00ff00"
            elif sma_20 < sma_50 and last_price < sma_20:
                trend = "📉 BAJISTA"
                trend_color = "#ff0000"
            else:
                trend = "↔️ LATERAL"
                trend_color = "#ffff00"
            
            self.trend_label.setText(f"Tendencia: {trend}")
            self.trend_label.setStyleSheet(f"color: {trend_color};")
        
        # 🎯 DIBUJAR VELAS USANDO MÉTODO DIRECTO (más confiable)
        # Limpiar velas anteriores
        if hasattr(self, 'candle_items'):
            for item in self.candle_items:
                try:
                    self.main_plot.removeItem(item)
                except:
                    pass
        self.candle_items = []
        
        # Validar columnas OHLC
        required_cols = ['open', 'high', 'low', 'close']
        if not all(col in df.columns for col in required_cols):
            print("[WARNING] Faltan columnas OHLC en el DataFrame")
            return
        
        # Dibujar cada vela individualmente
        times = list(range(len(df)))
        for i, (idx, row) in enumerate(df.iterrows()):
            try:
                self._draw_single_candle(
                    times[i],
                    float(row['open']),
                    float(row['high']),
                    float(row['low']),
                    float(row['close'])
                )
            except Exception as e:
                print(f"[WARNING] Error dibujando vela {i}: {e}")
                continue
        
        print(f"[DEBUG] Dibujadas {len(self.candle_items)//2} velas")
        
        # Actualizar indicadores
        closes = df['close'].values
        
        # SMAs
        if 'sma_20' in df.columns:
            self.sma_20_curve.setData(times, df['sma_20'].values)
        
        if 'sma_50' in df.columns:
            self.sma_50_curve.setData(times, df['sma_50'].values)
        
        # Bollinger Bands
        if 'bb_high' in df.columns and 'bb_low' in df.columns:
            self.bb_upper_curve.setData(times, df['bb_high'].values)
            self.bb_lower_curve.setData(times, df['bb_low'].values)
            
            # BB media
            bb_mid = (df['bb_high'] + df['bb_low']) / 2
            self.bb_mid_curve.setData(times, bb_mid.values)
            
            # Rellenar área entre bandas
            # (Opcional: requiere FillBetweenItem)
        
        # RSI
        if 'rsi' in df.columns:
            self.rsi_curve.setData(times, df['rsi'].values)
        
        # MACD
        if 'macd' in df.columns:
            self.macd_curve.setData(times, df['macd'].values)
            
            if 'macd_signal' in df.columns:
                self.macd_signal_curve.setData(times, df['macd_signal'].values)
        
        # Actualizar zonas de soporte/resistencia
        self.update_support_resistance_zones(df)
        
        # Auto-ajustar vista
        self.main_plot.autoRange()

    def update_support_resistance_zones(self, df):
        """Actualiza zonas de soporte y resistencia en el gráfico"""
        # Limpiar líneas anteriores
        for line in self.support_lines:
            self.main_plot.removeItem(line)
        for line in self.resistance_lines:
            self.main_plot.removeItem(line)
        
        self.support_lines = []
        self.resistance_lines = []
        
        if len(df) < 50:
            return
        
        # Identificar niveles de soporte (mínimos locales)
        lows = df['low'].values
        for i in range(2, len(lows) - 2):
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
               lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                # Dibujar línea de soporte
                line = pg.InfiniteLine(
                    pos=lows[i],
                    angle=0,
                    pen=pg.mkPen('#00FF00', width=1, style=Qt.DashLine),
                    label='Soporte'
                )
                self.main_plot.addItem(line)
                self.support_lines.append(line)
        
        # Identificar niveles de resistencia (máximos locales)
        highs = df['high'].values
        for i in range(2, len(highs) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
               highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                # Dibujar línea de resistencia
                line = pg.InfiniteLine(
                    pos=highs[i],
                    angle=0,
                    pen=pg.mkPen('#FF0000', width=1, style=Qt.DashLine),
                    label='Resistencia'
                )
                self.main_plot.addItem(line)
                self.resistance_lines.append(line)
        
        # Limitar a las 3 más relevantes de cada tipo
        if len(self.support_lines) > 3:
            for line in self.support_lines[3:]:
                self.main_plot.removeItem(line)
            self.support_lines = self.support_lines[:3]
        
        if len(self.resistance_lines) > 3:
            for line in self.resistance_lines[3:]:
                self.main_plot.removeItem(line)
            self.resistance_lines = self.resistance_lines[:3]

    def add_trade_signal(self, signal_type, price, reason=""):
        """
        Agrega una señal de trading al gráfico
        
        Args:
            signal_type: 'CALL' o 'PUT'
            price: Precio de entrada
            reason: Razón de la señal
        """
        if self.df is None or self.df.empty:
            return
        
        # Posición en el eje X (última vela)
        x_pos = len(self.df) - 1
        
        # Color y símbolo según tipo
        if signal_type == 'CALL':
            color = '#00FF00'
            symbol = '▲'
            arrow_angle = 90
        else:  # PUT
            color = '#FF0000'
            symbol = '▼'
            arrow_angle = -90
        
        # Agregar flecha
        arrow = pg.ArrowItem(
            pos=(x_pos, price),
            angle=arrow_angle,
            brush=color,
            pen=pg.mkPen(color, width=2),
            headLen=20,
            headWidth=20
        )
        self.main_plot.addItem(arrow)
        self.signal_arrows.append(arrow)
        
        # Agregar texto con razón
        text = pg.TextItem(
            f"{symbol} {signal_type}\n{reason}",
            color=color,
            anchor=(0.5, 1 if signal_type == 'CALL' else 0)
        )
        text.setPos(x_pos, price)
        self.main_plot.addItem(text)
        self.signal_arrows.append(text)
        
        # Limitar a últimas 5 señales
        if len(self.signal_arrows) > 10:  # 5 señales × 2 items (flecha + texto)
            for item in self.signal_arrows[:2]:
                self.main_plot.removeItem(item)
            self.signal_arrows = self.signal_arrows[2:]

    def update_decision_analysis(self, validation_result, profitability_score=None):
        """
        Actualiza el panel de análisis con la decisión
        
        Args:
            validation_result: Resultado de decision_validator
            profitability_score: Score de filtros de rentabilidad
        """
        if not validation_result:
            return
        
        # Actualizar score
        if profitability_score is not None:
            color = "#00ff00" if profitability_score >= 70 else "#ff0000"
            self.score_label.setText(f"🎯 Score: {profitability_score:.0f}/100")
            self.score_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # Construir texto de análisis
        recommendation = validation_result.get('recommendation', 'HOLD')
        confidence = validation_result.get('confidence', 0) * 100
        valid = validation_result.get('valid', False)
        
        if valid:
            status_emoji = "✅"
            status_color = "#00ff00"
            status_text = "EJECUTAR"
        else:
            status_emoji = "⏸️"
            status_color = "#ffff00"
            status_text = "ESPERAR"
        
        analysis_text = f"""
<span style='color: {status_color}; font-size: 14pt; font-weight: bold;'>
{status_emoji} {status_text}: {recommendation}
</span>
<br>
<span style='color: #00bfff;'>
📊 Confianza: {confidence:.0f}%
</span>
<br>
"""
        
        # Agregar razones principales (máximo 3)
        reasons = validation_result.get('reasons', [])
        if reasons:
            analysis_text += "<span style='color: #ffffff;'>"
            for reason in reasons[:3]:
                analysis_text += f"• {reason}<br>"
            analysis_text += "</span>"
        
        self.decision_label.setText(analysis_text)

    def _draw_single_candle(self, x, open_price, high, low, close):
        """
        Dibuja una vela japonesa individual usando el método directo
        (más confiable que QPicture)
        """
        try:
            # Determinar color (alcista o bajista)
            is_bullish = close >= open_price
            
            if is_bullish:
                # Verde brillante para velas alcistas
                color = QColor(0, 255, 100, 255)
            else:
                # Rojo brillante para velas bajistas
                color = QColor(255, 50, 50, 255)
            
            # Ancho de la vela
            width = 0.6
            
            # 1. Dibujar mecha (high-low) como línea
            wick = pg.PlotDataItem(
                [x, x],
                [low, high],
                pen=pg.mkPen(color=color, width=1.5)
            )
            self.main_plot.addItem(wick)
            self.candle_items.append(wick)
            
            # 2. Dibujar cuerpo (open-close) como rectángulo
            body_height = abs(close - open_price)
            body_y = min(open_price, close)
            
            # Si es vela doji (sin cuerpo), dibujar línea horizontal
            if body_height < 0.00001:
                doji_line = pg.PlotDataItem(
                    [x - width/2, x + width/2],
                    [open_price, open_price],
                    pen=pg.mkPen(color=color, width=2)
                )
                self.main_plot.addItem(doji_line)
                self.candle_items.append(doji_line)
            else:
                # Crear rectángulo para el cuerpo
                from PySide6.QtWidgets import QGraphicsRectItem
                body = QGraphicsRectItem(
                    x - width/2,
                    body_y,
                    width,
                    body_height
                )
                
                # Configurar color y borde
                body.setPen(pg.mkPen(color=color, width=1))
                body.setBrush(pg.mkBrush(color=color))
                
                self.main_plot.addItem(body)
                self.candle_items.append(body)
        
        except Exception as e:
            print(f"[ERROR] Error dibujando vela: {e}")
    
    def clear_signals(self):
        """Limpia todas las señales del gráfico"""
        for item in self.signal_arrows:
            self.main_plot.removeItem(item)
        self.signal_arrows = []
