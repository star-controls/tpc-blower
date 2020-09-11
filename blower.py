import pandas as pd
import threading          
import time
from softioc import builder
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import constants
from pyModbusTCP.utils import get_2comp

class blower():
    #_____________________________________________________________________________
    def __init__(self, machine, name):
        builder.SetDeviceName(name)
        self.com = ModbusClient(host=machine, port=4000, auto_open=True) #4000
        self.com.mode(constants.MODBUS_RTU)
        stat = self.com.open()
        self.pv_stat = builder.aIn("stat")
        self.pv_stat.PREC = 1
        self.pv_stat.LOPR = 0
        self.pv_stat.HOPR = 100
        self.pv_temp = builder.aIn("temp")
        self.pv_temp.PREC = 1
        self.pv_temp.LOPR = 0
        self.pv_temp.HOPR = 100
        self.pv_humi = builder.aIn("humidity")
        self.pv_humi.PREC = 1
        self.pv_humi.LOPR = 0
        self.pv_humi.HOPR = 100
        self.pv_humi.HSV = "MINOR"
        self.pv_humi.HHSV = "MAJOR"
        self.pv_humi.HIGH = 45
        self.pv_humi.HIHI = 50
        self.pv_flow = builder.aIn("flow")
        self.pv_flow.PREC = 0
        self.pv_flow.LOPR = 0
        self.pv_flow.HOPR = 600
        self.pv_flow.LOLO = 250
        self.pv_flow.LOW = 300
        self.pv_flow.HIGH = 480
        self.pv_flow.HIHI = 520
        self.pv_flow.LSV = "MINOR"
        self.pv_flow.LLSV = "MAJOR"
        self.pv_flow.HSV = "MINOR"
        self.pv_flow.HHSV = "MAJOR"
        self.stat_pv = builder.boolIn("status", ZNAM="off", ONAM="on", DESC=name)
        self.stat_pv.ZSV = "MAJOR"
	self.pv_on = builder.boolOut("on", ZNAM="0", ONAM="1", HIGH=0.1, on_update = self.turnOn)
	self.pv_off = builder.boolOut("off", ZNAM="0", ONAM="1", HIGH=0.1, on_update = self.turnOff)
        self.busy = False
	self.pv_act = builder.boolOut("activity", ZNAM="0", ONAM="1", HIGH=1)
	self.pv_was_on = builder.boolOut("was_on", ZNAM="0", ONAM="1", HIGH=1.5)
	self.pv_was_off = builder.boolOut("was_off", ZNAM="0", ONAM="1", HIGH=1.5)
        self.id_temp = 0
        self.id_stat = 1

    #_____________________________________________________________________________
    def start_monit_loop(self):                                                                          
        t = threading.Thread(target=self.monitor_loop)
        t.daemon = True
        t.start()
    #_____________________________________________________________________________    
    def monitor_loop(self):
        while True:
            time.sleep(2)
            try:
                if self.busy == False: self.read_YOGOGAWA()
            except TypeError:
                print "monitor_loop: reading skipped due to external write, busy:", self.busy
                self.busy = False

    #_____________________________________________________________________________
    def get_1dig(self, i):
        #print i
        return float(i)*0.1

    #_____________________________________________________________________________  
    def read_YOGOGAWA(self):

        self.busy = True

        self.com.unit_id(1)
        resp = self.com.read_holding_registers(1, 2)
        self.pv_stat.set(self.get_1dig(resp[self.id_stat]))
        self.pv_temp.set(self.get_1dig(resp[self.id_temp]))
        #self.pv_stat.set(resp[0])
        #self.pv_temp.set(resp[1])
        #self.get_1dig(resp[0])
        #self.get_1dig(resp[1])

        self.com.unit_id(2)
        resp = self.com.read_holding_registers(1, 1)[0]
        self.pv_humi.set(self.get_1dig(resp))

        self.com.unit_id(3)
        self.pv_flow.set(get_2comp(self.com.read_holding_registers(1, 1)[0]))

        self.busy = False

        self.pv_act.set(1)

    #_____________________________________________________________________________
    def turnOn(self,val):
        if val == 0: return
        while self.busy == True:
            print "turnOn: waiting for busy to clear"
            time.sleep(0.2)
        self.busy = True
        self.com.unit_id(5)
        self.com.write_single_coil(0,True)
        self.busy = False
        #print("funtion turnOn done")
        self.pv_was_on.set(1)

    #_____________________________________________________________________________                        
    def turnOff(self,val):
        if val == 0: return
        while self.busy == True:
            print "turnOff: waiting for busy to clear"
            time.sleep(0.2)
        self.busy = True
        self.com.unit_id(5)
        self.com.write_single_coil(1,True)
        self.busy = False
        #print("function turnOff done")
        self.pv_was_off.set(1)


