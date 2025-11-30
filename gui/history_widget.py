from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                               QHeaderView)
from PySide6.QtGui import QColor
from datetime import datetime

class HistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Hora", "Activo", "Tipo", "Resultado", "Profit"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.table)

    def add_trade(self, asset, direction, profit):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        time_str = datetime.now().strftime("%H:%M:%S")
        result = "GANADA" if profit > 0 else "PERDIDA"
        color = QColor(0, 255, 0) if profit > 0 else QColor(255, 0, 0)
        
        self.table.setItem(row, 0, QTableWidgetItem(time_str))
        self.table.setItem(row, 1, QTableWidgetItem(asset))
        self.table.setItem(row, 2, QTableWidgetItem(direction.upper()))
        
        item_res = QTableWidgetItem(result)
        item_res.setForeground(color)
        self.table.setItem(row, 3, item_res)
        
        item_prof = QTableWidgetItem(f"${profit:.2f}")
        item_prof.setForeground(color)
        self.table.setItem(row, 4, item_prof)
