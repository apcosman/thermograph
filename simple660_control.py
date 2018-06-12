#Alin Cosmanescu
#Biocomplexity Institute, Indiana University

import sys
import datetime
import time
import math

#below, not-included-with-python libraries
import cv2 as cv
import usb
from PyQt4 import QtGui
from PyQt4 import QtOpenGL
from PyQt4 import QtCore

class Window(QtGui.QMainWindow):

    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setDockOptions(QtGui.QMainWindow.ForceTabbedDocks)

        self.manual = manualControlWidget()

        #layout of this window and its widgets
        self.setCentralWidget(self.manual)

        self.setWindowTitle("660nm Illuminator Development Platform Software")

class fusionbrainusb(QtCore.QObject):

        def __init__(self, parent = None, **kwargs):

                QtCore.QObject.__init__(self)

                #use pyusb to find endpoint fusion brain
                #self.dev = usb.core.find(idVendor=0x04d8, idProduct=0x000E)

                #self.dev.set_configuration(1)
                #self.dev.set_interface_altsetting(interface = 0, alternate_setting = 0)

                self.bulk_data = bytearray([b'\00' for i in range(0, 64)])
                self.dev_ret = self.bulk_data

        def setOutput(self, output_num = 0, value = b'\01'):
                self.bulk_data[output_num  * 2] = value
                try:
                    self.dev.write(1, self.bulk_data, 0, 500)
                except:
                    print "WOULD HAVE CRASHED -- DIGITAL OUTPUT"
                try:
                    self.dev_ret = self.dev.read(129,64,0,500)
                    self.emit(QtCore.SIGNAL("pinOutSet"), dev_ret)
                except:
                    print "WOULD HAVE CRASHED -- DIGTIAL INPUT"
                return self.dev_ret

        def setAnaOutput(self, output_num = 14, value=0b00000000):
                self.bulk_data[output_num * 2] = value
                self.bulk_data[(output_num *2)+1] = 0b00000001
                try:
                    self.dev.write(1, self.bulk_data, 0, 500)
                    self.dev_ret = self.dev.read(129,64,0,500)
                except:
                    print "WOULD HAVE CRASHED -- ANALOG OUTPUT"
		print self.dev_ret
                return self.dev_ret

        def readAnaOutput(self, ouput_num = 1):
                try:
                    self.dev_ret = self.dev.read(129,64,0,500)
                except:
                    print "WOULD HAVE CRASHED -- ANALOG READ"
                return self.dev_ret

class manualControlWidget(QtGui.QWidget):

        def __init__(self, parent = None, start_pin = 0, stop_pin=3  ):
                QtGui.QWidget.__init__(self, parent)

                self.digital_names = {0:'Pin 0', 1:'Pin 1', 2:'Pin 2'}

                #list comprehension for creating checkboxes
                self.checkboxes = [QtGui.QCheckBox(("%s" % self.digital_names[i]), self) for i in range(start_pin, stop_pin)]

                self.set_time = QtGui.QSpinBox()
                self.set_time.setFocusPolicy(QtCore.Qt.ClickFocus)

                #self.read_analog = QtGui.QLCDNumber()
                self.set_time.setMaximum(3600)
		self.tim = 100 

                self.set_sample = QtGui.QSpinBox()
                self.set_sample.setFocusPolicy(QtCore.Qt.ClickFocus)
		self.set_sample.setMaximum(1000)
		self.sample = 200

                layout = QtGui.QGridLayout()

                layout.addWidget(self.set_time, 0, 1, 1, 1)
		layout.addWidget(self.set_sample, 1, 1, 1,1)
                #layout.addWidget(self.read_analog, 0, 1, 1, 2)

                #map instead of looping to layout checkboxes
                map(layout.addWidget,
                    self.checkboxes,
                    [ i  for i in range( start_pin, stop_pin ) ],
                    [ 0 for i in range( start_pin, stop_pin ) ] )

                self.setLayout(layout)

                self.mapper = QtCore.QSignalMapper()

                #map to connect checkboxes to the signal mapper
                map(self.connect, self.checkboxes, [QtCore.SIGNAL("clicked()") for i in range(start_pin, stop_pin)],
                                                   [self.mapper for i in range(start_pin, stop_pin)],
                                                   [QtCore.SLOT("map()") for i in range(start_pin, stop_pin)])

                #use the signal mapper to emit signal from this widget, which will connect to actual valve control
                map(self.mapper.setMapping, self.checkboxes, range(start_pin, stop_pin))

                self.connect(self.mapper, QtCore.SIGNAL("mapped(int)"), self._pin_click)

                self.connect(self.set_time, QtCore.SIGNAL("valueChanged(int)"), self._spin_change)
                self.connect(self.set_sample, QtCore.SIGNAL("valueChanged(int)"), self._spin_change)
                #use a slot on fusionbrain to listen to valve_click?

                self.output_object = fusionbrainusb()

                #connecting up all the widgets
                self.ana_timer = QtCore.QTimer(self)
                self.connect(self.ana_timer, QtCore.SIGNAL("timeout()"), self._gen_sine)
                self.ana_timer.start(self.tim)

                self.connect(self.output_object, QtCore.SIGNAL("pinOutSet"),  self._sync_check)
                self._sync_check(self.output_object.readAnaOutput())

		self.sine_values = [64 - 64*math.sin(2*math.pi*t/self.sample) for t in range(0, self.sample)]	
		self._gen_sine()

	def _gen_sine(self, omega = 100):
		for sine in self.sine_values:
			self.output_object.setAnaOutput(output_num = 14, value = int(sine))
			time.sleep(0.5)
			
        def _sync_check(self, dev_ret):
                #TODO: this is god-awful ugly
                #print "here: %s" % repr(dev_ret)
                for x,check in enumerate(self.checkboxes):
                        #print dev_ret[(self.digital_names.keys()[x])*2]
                        if dev_ret[(self.digital_names.keys()[x])*2] == 1:
                                check.setChecked(True)
                        else:
                                check.setChecked(False)

        def _pin_click(self, the_no):
                #print "clicked: %s" % the_no
                #TODO: abstract direct access to bulk_data -- ACTUALLY: "bulk data" is a bad way to handle this, the check box should be the state.
                if self.output_object.bulk_data[(the_no) * 2] == 1:
                        self.output_object.setOutput(output_num = the_no, value = b'\00')
                else:
                        self.output_object.setOutput(output_num = the_no, value = b'\01')

        def _spin_change(self, the_value):
                #in_volts = float(the_value) 	

                #in_perc_cycle = int(in_volts)
                #in_perc_cycle = int( ( float(in_volts)  / float(5) ) * float(128) ) -1

                #val = in_perc_cycle << 1
		#val = int(the_value) << 1

                #self.output_object.setAnaOutput(output_num = 14, value = val)
		self.sample =  self.set_sample.value()
		self.time = self.set_time.value()

		

        def _read_analog(self):
                voltage_scale = float(5) / float(1024)

                first_byte = self.output_object.readAnaOutput()[32]
                second_byte = self.output_object.readAnaOutput()[33]

                read_value = first_byte << 8
                #print "              --%s" % read_value
                read_value = read_value + second_byte
                #print "             --%s" % read_value

                self.read_analog.display( read_value*voltage_scale  )

                #TODO: this is BULL, the feedback system needs to be fixed
                self._sync_check(self.output_object.readAnaOutput())

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    #app.setStyle( "cleanlooks" )
    app.setStyle("gtk")
    window = Window()
    window.show()

    sys.exit(app.exec_())
