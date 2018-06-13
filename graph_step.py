#!/usr/bin/python3
# coding: utf-8

import serial
import sys
import io

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
                    value = None

                yield (current_probe, value, self.UNITS[unit_code])
            
            except IndexError as e:
                print(e)

            except ValueError as e:
                print(e)


class TS_LiveValuesPlot(pg.GraphicsWindow):
    
    def __init__(self, *args, **kwargs):
        super(TS_LiveValuesPlot, self).__init__();

        self.setWindowTitle('Live Plot of Thermocouple Data')

        self.p1 = self.addPlot()
        
        keys = [1,2,3,4]
        self.data = {x:np.zeros(30, dtype=float) for x in keys} 
        self.curves = {x:self.p1.plot(self.data[x]) for x in keys}

    def update(self, next_value):

        probe = next_value[0]

        self.curves[probe].setPos(probe, 0)

        self.data[probe][:-1] = self.data[probe][1:]  # shift data in the array one sample left
        self.data[probe][-1] = next_value[1]
        
        self.curves[probe].setData(self.data[probe])

def print_output(current_values):
    print("%d,%s,%s" % current_values)

if __name__ == '__main__':

    live_plot_window = TS_LiveValuesPlot()

    data_source = TS_SerialDevice(serpath=sys.argv[1])
    dsg = data_source.next_readings()

    def read_ds_closure():
        current_value = next(dsg)
        live_plot_window.update(current_value)
        print_output(current_value)

    graph_timer = pg.QtCore.QTimer()
    graph_timer.timeout.connect(read_ds_closure)
    graph_timer.start(5)

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
