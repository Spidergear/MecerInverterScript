#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, time
import timeout_decorator
import warnings
#ignore depecated warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

from crc16 import crc16xmodem
from struct import pack
from traceback import format_exc


inverter_port ='/dev/hidraw0'
        

@timeout_decorator.timeout(40, use_signals=False)
def command(cmd):
   
    encoded_cmd = cmd.encode()
    try:
        
        if encoded_cmd == b"ERROR":
            while True:
                time.sleep(1)

        if encoded_cmd == b"POP02":   # ERROR firmware - CRC correcto es: 0xE2 0x0A
            cmd_crc = b'\x50\x4f\x50\x30\x32\xe2\x0b\x0d'

        elif encoded_cmd[:9] == b'^S007POP1':
                cmd_crc = b'^S007POP1\x0e\x10\r'
                
        elif encoded_cmd[:9] == b'^S007LON0':
                cmd_crc = b'^S007LON0\x69\xd8\r'
                        
        else:
            checksum = crc16xmodem(encoded_cmd)
            cmd_crc = encoded_cmd + pack('>H', checksum) + b'\r'

        #print ('Comando con CRC=',repr(cmd_crc))
        if os.path.exists(inverter_port):
            fd = open(inverter_port,'rb+')
            time.sleep(.20)
            ee = 30
            #print ('Byte1=',repr(cmd_crc[:8]))
            fd.write(cmd_crc[:8])
            
            ee = 40
            if len(cmd_crc) > 8:
                #print ('Byte2=',repr(cmd_crc[8:16]))
                fd.flush()
                fd.write(cmd_crc[8:16])

            ee = 45
            if len(cmd_crc) > 16:
                #print ('Byte3=',repr(cmd_crc[16:]))
                fd.flush()
                fd.write(cmd_crc[16:])
            
            ee = 50
            time.sleep(.5)
           
            r = fd.read(5)
            
            while r.find(b'\r') == -1 :
                time.sleep(.05)
                r = r + fd.read(1)
            
            return r[0:len(r)-3][1:].decode("utf-8")
           
                      
    
    except Exception as e:
        #Error occured
        print(e)
       
        
    finally:
        try:
            fd.close()
        except:
            pass

def colorprint(string, text_color = 'default', bold = False, underline = False):
    if underline == True:
            string = '\033[4m' + string
    if bold == True:
            string = '\033[1m' + string
    if text_color == 'default' or text_color in colors:
            for color in colors:
                    if text_color == color:
                            string = colors[color] + string
    else:
            raise ValueError ("Colors not in:", colors.keys())

    print(string + '\033[0m')

while True:
    
    #Get inverter status
    inverter_status =command('QMOD')
    print("Inverter Status:", end =" ")
    if inverter_status =='P':
        print('Power On')
    elif inverter_status =='S':
        print('Standby')
    elif inverter_status =='L':
        colorprint('Online','green',True)
    elif inverter_status =='B':
        colorprint('On Battery','red',True)
    elif inverter_status =='F':
        colorprint('Fault','red',True)
    elif inverter_status =='H':
        print('Power Saving')
            
    #Get values from inverter
    data = command('QPIGS').split()
    print('Mains Voltage = '+ data[0])
    print('Mains Frequency = '+ data[1])
    print('Output Voltage = '+ data[2])
    print('Output Frequency = '+ data[3])
    print('OutputApparentPower = '+ data[4])
    print('OutputActivePower = '+ data[5])
    print('OutputLoadPercent = '+ data[6])
    print('BusVoltage = '+ data[7])
    print('BatteryVoltage = '+ data[8])
    print('BatteryChargingCurrent = '+ data[9])
    print('BatteryCapacity = '+ data[10])
    print('InverterHeatSinkTemperature = '+ str(int(data[11])/10))
    print('PV Input Current = '+ data[12])
    print('PV Input Voltage = '+ data[13])
    print('BatteryVoltageFromSCC = '+ data[14])
    print('BatteryDischargeCurrent = '+ data[15])
    print('DeviceStatus = '+ data[16])

    #Device Warning Status inquiry
    #print(command('QPIWS'))
    
    #sleep 5 seconds before next query
    time.sleep(5)
