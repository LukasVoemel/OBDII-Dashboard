
import serial 
import time 
import sys
from mainwindow import MainWindow
from PyQt5.QtWidgets import QApplication


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
Gear ratio: A4  Gear is not supported on my OBD for some reason
Actual engine - percent torque PID: 62
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
        'TORQUE' : '0162\r', 
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
        print(f'{key} = {data_parts}')
        response_dic[key] = data_parts
    
    return response_dic


def read_request():
    print("HELLO")

    responses = send_request()
    values = {}

    for key, value in responses.items():

        if key == 'LOAD':
            load_data = b'00'

            for i in range(len(value)):
                print(i,"      " ,value[i])
                
                if 1 < len(value) - 1:
                    
                    if value[i] == b'41' and value[i+1] == b'04':
                        load_data = value[i+2]
                        break

            load = int(load_data, 16) / 2
            values['LOAD'] = load
            #print(f"Engine Load: {load}%")

        elif key == 'TORQUE':
            
            for i in range(len(value)):
                if value[i] == b'41' and value[i+1] == b'62':
                    t_data = value[i+2]
            
            torque = int(t_data, 16) - 125
            values['TORQUE'] = torque
            

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
window = MainWindow(req_func=read_request())
window.showFullScreen()
sys.exit(app.exec())