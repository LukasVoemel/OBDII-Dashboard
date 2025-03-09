'''

Using Panlong OBDII, when in dev, using pin 16 and 5 for power and ground 
OBD2 Message structure 

Mode $01 is what provides for powertrain diagnostic data, its what I will use
then after that you will use the according PID to access specifc data 

'''



#this is the start of the project 

# send the obd2 initializaion commands 
# I guess make sure the bluetooth is connected 
# make graphical interafece 
# read the data 
# read data in teh right intervals 
# be able to do the whole thing at bootup
# make it seem like the shole softwar


# how to set uo the files could be a good thing to know and potetnally set up git repo to practice that 

import serial 
import time 

#timeout=2: timeout=0 makes that the program wont wait for any data from the serial device, if no data avialabe, then return immedeialy, timeout=2 makes it wait 2 seconds for data to be received 
ser = serial.Serial('/dev/rfcomm99', 9600, timeout=2) #so this seems to be connection at the right guy 

print(ser.name)

ser.write(b'ATZ\r')
#in python3 you have to send data as byte string not unicode string, thats whre the b comes from 
#\r is a carraige return 
#ATZ resets the OBD-II adapter and sends its id back 

time.sleep(2)
response = ser.readline()
print(response.decode('ascii').strip())

#ASP0 Does atomatic protocol selection, this is somce sort os CAN protocol 
ser.write(b'ATSP0')
time.sleep(2)
response = ser.readline()
print(response.decode('ascii').strip())

ser.close()
