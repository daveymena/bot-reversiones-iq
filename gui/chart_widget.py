import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QColor, QPicture, QPainter
from PySide6.QtCore import QRectF

class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data  # data must have fields: time, open, close, min, max
        self.generatePicture()

    def generatePicture(self):
        self.picture = QPicture()
        p = QPainter(self.picture)
        p.setPen(pg.mkPen('w'))
        w = (self.data[1][0] - self.data[0][0]) / 3.
        for (t, open, close, min, max) in self.data:
            p.drawLine(QPointF(t, min), QPointF(t, max))
            if open > close:
                p.setBrush(pg.mkBrush('r'))
            else:
                p.setBrush(pg.mkBrush('g'))
            p.drawRect(QRectF(t-w, open, w*2, close-open))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())

class ChartWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.plot_widget = pg.PlotWidget(axisItems={'bottom': pg.DateAxisItem()})
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setBackground('#1e1e1e')
        self.plot_widget.setTitle("Gráfico de Mercado (1 Min)")
        
        # Curva de precio simple por ahora (Velas es complejo de implementar en un solo archivo sin helpers)
        # Usaremos una línea amarilla para simplicidad y robustez inicial
        self.curve = self.plot_widget.plot(pen='y')
        
        # Indicadores
        self.bollinger_upper = self.plot_widget.plot(pen=pg.mkPen('b', width=1))
        self.bollinger_lower = self.plot_widget.plot(pen=pg.mkPen('b', width=1))
        
        layout.addWidget(self.plot_widget)
        
        self.data_x = []
        self.data_y = []

    def update_chart(self, timestamp, price):
        self.data_x.append(timestamp)
        self.data_y.append(price)
        
        # Mantener ventana de 200 velas
        if len(self.data_x) > 200:
            self.data_x.pop(0)
            self.data_y.pop(0)
            
        self.curve.setData(self.data_x, self.data_y)
        
        # Simulación de Bollinger (Solo visual)
        import numpy as np
        if len(self.data_y) > 20:
            sma = np.mean(self.data_y[-20:])
            std = np.std(self.data_y[-20:])
            upper = [y + (2*std) for y in self.data_y] # Simplificado para demo
            lower = [y - (2*std) for y in self.data_y]
            # self.bollinger_upper.setData(self.data_x, upper) # Requiere calcular todo el array
