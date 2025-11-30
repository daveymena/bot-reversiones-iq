from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, QGroupBox)
from PySide6.QtCore import Qt

class StatusWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        group = QGroupBox("Estado del Bot")
        grid = QGridLayout()
        
        # Labels estáticos
        grid.addWidget(QLabel("Balance:"), 0, 0)
        grid.addWidget(QLabel("Profit Diario:"), 1, 0)
        grid.addWidget(QLabel("Racha:"), 2, 0)
        grid.addWidget(QLabel("Win Rate:"), 3, 0)
        
        # Labels dinámicos
        self.lbl_balance = QLabel("$0.00")
        self.lbl_balance.setStyleSheet("color: #00ff00; font-weight: bold;")
        
        self.lbl_profit = QLabel("$0.00")
        self.lbl_profit.setStyleSheet("color: #00ff00;")
        
        self.lbl_streak = QLabel("0")
        
        self.lbl_winrate = QLabel("0%")
        
        grid.addWidget(self.lbl_balance, 0, 1)
        grid.addWidget(self.lbl_profit, 1, 1)
        grid.addWidget(self.lbl_streak, 2, 1)
        grid.addWidget(self.lbl_winrate, 3, 1)
        
        group.setLayout(grid)
        layout.addWidget(group)
        layout.addStretch()

    def update_balance(self, balance):
        self.lbl_balance.setText(f"${balance:.2f}")

    def update_stats(self, profit, streak, winrate):
        self.lbl_profit.setText(f"${profit:.2f}")
        color = "green" if profit >= 0 else "red"
        self.lbl_profit.setStyleSheet(f"color: {color};")
        
        self.lbl_streak.setText(str(streak))
        self.lbl_winrate.setText(f"{winrate:.1f}%")
