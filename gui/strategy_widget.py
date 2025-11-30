from PySide6.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QPushButton, 
                               QGroupBox, QProgressBar, QLabel)
from PySide6.QtCore import Signal

class StrategyWidget(QWidget):
    toggle_bot_signal = Signal(bool) # True=Start, False=Stop

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Estrategias Activas
        strat_group = QGroupBox("Estrategias Activas")
        strat_layout = QVBoxLayout()
        self.chk_scalping = QCheckBox("Scalping (1 min)")
        self.chk_reversal = QCheckBox("Reversión")
        self.chk_rl = QCheckBox("Aprendizaje por Refuerzo (RL)")
        self.chk_rl.setChecked(True)
        
        strat_layout.addWidget(self.chk_scalping)
        strat_layout.addWidget(self.chk_reversal)
        strat_layout.addWidget(self.chk_rl)
        strat_group.setLayout(strat_layout)
        
        # Info RL
        rl_group = QGroupBox("Estado RL")
        rl_layout = QVBoxLayout()
        self.lbl_epsilon = QLabel("Exploración (Epsilon): 1.00")
        self.prog_reward = QProgressBar()
        self.prog_reward.setFormat("Recompensa Media: %v")
        self.prog_reward.setRange(-100, 100)
        self.prog_reward.setValue(0)
        
        rl_layout.addWidget(self.lbl_epsilon)
        rl_layout.addWidget(self.prog_reward)
        rl_group.setLayout(rl_layout)
        
        # Botón Principal
        self.btn_toggle = QPushButton("INICIAR BOT")
        self.btn_toggle.setCheckable(True)
        self.btn_toggle.setStyleSheet("background-color: green; color: white; font-size: 16px; font-weight: bold; padding: 10px;")
        self.btn_toggle.clicked.connect(self.on_toggle)
        
        layout.addWidget(strat_group)
        layout.addWidget(rl_group)
        layout.addWidget(self.btn_toggle)
        layout.addStretch()

    def on_toggle(self):
        if self.btn_toggle.isChecked():
            self.btn_toggle.setText("DETENER BOT")
            self.btn_toggle.setStyleSheet("background-color: red; color: white; font-size: 16px; font-weight: bold; padding: 10px;")
            self.toggle_bot_signal.emit(True)
        else:
            self.btn_toggle.setText("INICIAR BOT")
            self.btn_toggle.setStyleSheet("background-color: green; color: white; font-size: 16px; font-weight: bold; padding: 10px;")
            self.toggle_bot_signal.emit(False)
