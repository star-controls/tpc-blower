#!/usr/local/epics/modules/pythonIoc/pythonIoc

#import basic softioc framework
from softioc import softioc, builder

#import the application
from blower import blower

tpc_blower = blower('130.199.61.8',"tpc_blower")

etof_blower = blower('130.199.60.3',"etof_blower")
etof_blower.pv_flow.LOW = 180
etof_blower.pv_flow.LOLO = 120
etof_blower.pv_temp.HSV = "MINOR"
etof_blower.pv_temp.HHSV = "MAJOR"
etof_blower.pv_temp.HIGH = 75
etof_blower.pv_temp.HIHI = 78
etof_blower.pv_humi.HIGH = 50
etof_blower.pv_humi.HIHI = 55

#run the ioc
builder.LoadDatabase()
softioc.iocInit()

tpc_blower.start_monit_loop()
etof_blower.start_monit_loop()


softioc.interactive_ioc(globals())
