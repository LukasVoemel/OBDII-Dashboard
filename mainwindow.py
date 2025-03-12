from PyQt5.QtWidgets import QLabel, QApplication, QMainWindow, QGridLayout, QWidget
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt, QTimer

class MainWindow(QWidget):
    def __init__(self, req_func):
        super().__init__()

        self.req_func = req_func
        self.setWindowTitle("OBD-II")

        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        #when driving at night bright coloras are very harsh so black background and light writing 
        self.setStyleSheet('background-color:#0D1B0F;')

        self.labels = {
            "LOAD": QLabel("LOAD: ---"),
            "TORQUE": QLabel("TORQUE: ---"),
            "COOLANT": QLabel("COOLANT: ---"),
            "RPM": QLabel("RPM: ---")
        }
        row, col = 0 ,0 
        for key,label in self.labels.items():
            label.setStyleSheet("border: 2px solid black;"
            "font-size: 32px; "
            "padding: 10px;"
            "font-weight: bold;"
            "color: #A3D9A5;"
            "text-align: center;" )
            label.setMinimumSize(150,100)
            grid_layout.addWidget(label, row, col)   
            col += 1
            if col > 1:
                col = 0 
                row += 1 

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)
    
    def update_data(self):
        data = self.req_func()

        units = {
            "LOAD" : " %", 
            "TORQUE" : "%", 
            "COOLANT" : " °C", 
            "RPM" : ""
        }

        for key,value in data.items():
            self.labels[key].setText(f"{key}: {value}{units.get(key, '')}")

  

    def keyPressEvent(self,event:QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()

