'''

Using Panlong OBDII, when in dev, using pin 16 and 5 for power and ground 
OBD2 Message structure 

Mode $01 is what provides for powertrain diagnostic data, its what I will use
then after that you will use the according PID to access specifc data 

'''

import serial 
import time 
import sys
from PyQt5.QtWidgets import QLabel, QApplication, QMainWindow, QGridLayout, QWidget
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt, QTimer

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OBD-II")

        grid_layout = QGridLayout()
        self.setLayout(grid_layout)

        #when driving at night bright coloras are very harsh so black background and light writing 
        self.setStyleSheet('background-color:#0D1B0F;')

        self.labels = {
            "LOAD": QLabel("LOAD: ---"),
            "GEAR": QLabel("GEAR: ---"),
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
        data = read_request()

        units = {
            "LOAD" : " %", 
            "GEAR" : "", 
            "COOLANT" : " °C", 
            "RPM" : ""
        }

        for key,value in data.items():
            self.labels[key].setText(f"{key}: {value}{units.get(key, '')}")

  

    def keyPressEvent(self,event:QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()



#timeout=2: timeout=0 makes that the program wont wait for any data from the serial device, if no data avialabe, then return immedeialy, timeout=2 makes it wait 2 seconds for data to be received 
ser = serial.Serial('/dev/rfcomm99', 9600, timeout=0.3) #so this seems to be connection at the right guy 

#initilazation function since we have a couple to run 
def init_obd():

    #b sends data as byte string not as unicode string 
    #\r is used to indicate end of command
    commands = [
        b'ATZ\r', #ATZ resets device and returns id 
        b'ATSP0\r', #this is protocol detetection, ATSP0 does auto CAN selection
        b'ATE0\r', #disables echo (OBD sends back command you gave it)
        b'ATH1\r' #ads a \n to the end of line 
    ]

    for command in commands: 

        ser.write(command)
        time.sleep(2)
        response = ser.readline()
        print(response.decode('ascii').strip())

'''
Engine load PID: 04 
     % of availabe engine power being used at a given moment
Gear ratio: A4
Coolant temperature PID: 05 
RPM: 0C (engine speen)


example of output data: b'7E8 03 41 05 61 \r7EA 03 41 05 61 \r>'
41 05 is a response from ECU header responding to 05 PID 
last byte is the important byte which shows the data 61 
this is the same format for each output

RESPONSES FROM ECU:

NAME   :   PID      ==   response
'LOAD' : '0104\r',  == b'7EA 03 41 04 00 \r7E8 03 41 04 00 \r>'
'GEAR' : '01A4\r',  == b'NO DATA\r\r>'
'COOLANT' :'0105\r', == b'7E8 03 41 05 58 \r7EA 03 41 05 58 \r>'
'RPM' : '010C\r'  == b'7E8 04 41 0C 12 0A \r7EA 04 41 0C 12 00 \r>'

formula for coolant and load = byte / 2

RPM returns 2 bytes a high byte and a low byte these are used for the RPM calculation 
formula (high_byte * 256 + low_byte / 4) = rpm

we have to process everything in byte literals b'' which is not the same as str 

'''

def send_request():

    requests = { 
        'LOAD' : '0104\r', 
        'GEAR' : '01A4\r', 
        'COOLANT' :'0105\r', 
        'RPM' : '010C\r'
    }

    response_dic = {} #to store the responses

    for key, value in requests.items():

        ser.write(value.encode())
        #time.sleep(0.5)
        response = ser.readline()
        clean_response = response.replace(b'7E8', b'').replace(b'7EA', b'').replace(b'\r>', b'')
        chunks = clean_response.split(b'\r')
        first_response = chunks[0] #yields first response only 
        data_parts = first_response.split(b' ')
        #print(f'{key} = {data_parts}')
        response_dic[key] = data_parts
    
    return response_dic




def read_request():

    responses = send_request()
    values = {}

    for key, value in responses.items():

        if key == 'LOAD':
            for i in range(len(value)):
                if value[i] == b'41' and value[i+1] ==b'04':
                    load_data = value[i+2]
                else:
                    load_data = b'00'
            load = int(load_data, 16) / 2
            values['LOAD'] = load
            #print(f"Engine Load: {load}%")

        elif key == 'GEAR':
            values['GEAR'] = 0
            #print("GEAR ")

        elif key == 'COOLANT':
            for i in range(len(value)):
                if value[i] == b'41' and value[i+1] == b'05':
                    temp_data = value[i+2]
            
            coolant_temp = int(temp_data, 16) / 2
            values['COOLANT'] = coolant_temp
            #print(f"Coolant temp: {coolant_temp}°C")

        elif key == 'RPM':
            for i in range(len(value)):
                if value[i] == b'41' and value[i+1] ==b'0C':
                    high_byte = int(value[i+2], 16)
                    low_byte = int(value[i+3], 16)

            rpm = (high_byte * 256 + low_byte) / 4
            values['RPM'] = rpm
            #print(f"RPM: {rpm}")

        else:
            print("ERROR NO KEY FOUND")

    return values

init_obd()
app = QApplication(sys.argv)
window = MainWindow()
window.showFullScreen()
sys.exit(app.exec())