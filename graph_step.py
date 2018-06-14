#!/usr/bin/python3
# coding: utf-8

import serial
import sys
import io
import time

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui 

import numpy as np

class TS_SerialDevice(object):
    UNITS = {1:"°C", 2:str("°F"), 4:str("% RH"), 6:str("%O2"), 19:str("PPM")}
    
    def __init__(self, serpath = None, **kwargs):
        super(TS_SerialDevice, self).__init__();
        
        try:
            self.serial_object = serial.Serial(port=serpath, baudrate=9600, bytesize=serial.EIGHTBITS, timeout=1, exclusive=False)
        except:
            print("Failed to OPEN serial device")
        
        self.ts_reader = io.TextIOWrapper(io.BufferedReader(self.serial_object, 1),  
                               newline = '\r',
                               line_buffering = True) 

    def next_readings(self):

        try:
            self.serial_object.flushInput()
        except:
            print("Failed to FLUSH serial device")
            return #TODO: Raise exception
    
        while True:
        
            try:
                raw_unicode = self.ts_reader.readline()
            except:
                print("Failed to READ from serial device")
                break #TODO: Raise exception

            try:
                raw_bytes = bytes(raw_unicode, encoding='utf-8')
                
                current_probe = int(chr(raw_bytes[2]))
                
                unit_code = int(chr(raw_bytes[3]))*10 +  int(raw_bytes[4])-48
                
                polarity =  int(chr(raw_bytes[5]))
                
                decimal_point = int(chr(raw_bytes[6]))

                try:
                    fixed_width_value = int(str(raw_bytes[7:15], 'utf-8'))
                    value = fixed_width_value * (10.0 ** (-1*decimal_point)) * ((0-polarity)**0)

                except:
                    value = float('nan')

                yield (current_probe, value, self.UNITS[unit_code])
            
            except IndexError as e:
                print(e)

            except ValueError as e:
                print(e)

class DateAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strns = []
        rng = max(values)-min(values)
        #if rng < 120:
        #    return pg.AxisItem.tickStrings(self, values, scale, spacing)
        if rng < 3600*24:
            string = '%H:%M:%S'
            label1 = '%b %d -'
            label2 = ' %b %d, %Y'
        elif rng >= 3600*24 and rng < 3600*24*30:
            string = '%d'
            label1 = '%b - '
            label2 = '%b, %Y'
        elif rng >= 3600*24*30 and rng < 3600*24*30*24:
            string = '%b'
            label1 = '%Y -'
            label2 = ' %Y'
        elif rng >=3600*24*30*24:
            string = '%Y'
            label1 = ''
            label2 = ''
        for x in values:
            try:
                strns.append(time.strftime(string, time.localtime(x)))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        try:
            label = time.strftime(label1, time.localtime(min(values)))+time.strftime(label2, time.localtime(max(values)))
        except ValueError:
            label = ''
        #self.setLabel(text=label)
        return strns

class TS_LiveValuesPlot(pg.GraphicsWindow):
    
    def __init__(self, *args, **kwargs):
        super(TS_LiveValuesPlot, self).__init__();

        self.setWindowTitle('Live Plot of Thermocouple Data')

        self.axis = DateAxis(orientation='bottom')
        self.p1 = self.addPlot(axisItems={'bottom': self.axis})

        keys = [1,2,3,4]
        self.xtime  = {x:[] for x in keys}  #np.empty(0, dtype=float)
        self.data   = {x:[] for x in keys} 
        self.curves = {x:self.p1.plot(self.data[x], pen=(x,2)) for x in keys}

    def update(self, next_time, next_value):

        probe = next_value[0]

        #self.curves[probe].setPos(probe, 0)

        #self.xtime[:-1] = self.xtime[1:]
        #self.data[probe][:-1] = self.data[probe][1:]  # shift data in the array one sample left
        
        self.xtime[probe].append(next_time)
        self.data[probe].append(next_value[1])
        
        self.curves[probe].setData(self.xtime[probe], self.data[probe])

    

def print_output(current_time, current_values):
    print("%f,%d,%f,%s" % (current_time,current_values[0], current_values[1], current_values[2]))

if __name__ == '__main__':

    live_plot_window = TS_LiveValuesPlot()

    data_source = TS_SerialDevice(serpath=sys.argv[1])
    dsg = data_source.next_readings()

    def read_ds_closure():
        for x in range(0,3):
            current_value = next(dsg)
            current_time = time.time()
            live_plot_window.update(current_time, current_value)
            print_output(float(current_time), current_value)

    graph_timer = pg.QtCore.QTimer()
    graph_timer.timeout.connect(read_ds_closure)
    graph_timer.start(30)

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
