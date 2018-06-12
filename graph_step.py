import serial
import sys

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QThread

#from PyQt4 import Qt
#import qwt as Qwt
#from PyQt4.Qwt5 import *

import numpy as np

class TS_GetSerialThread(QtCore.QThread):
    """ Runs a function in a thread, and alerts the parent when done. 
    Uses a custom QEvent to alert the main thread of completion.
    """

    def __init__(self, parent = None, *args, **kwargs):
        super(TS_GetSerialThread, self).__init__(parent)
        self.args = args
        self.kwargs = kwargs
        #self.start()

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            print "e is %s" % e
            result = e
        finally:
            CallbackEvent.post_to(self.parent(), self.on_finished, result)


class TS_SerialDevice(QtCore.QObject):
    
    def __init__(self, parent = None, serpath = None, **kwargs):
        super(TS_GetSerialThread, self).__init__(parent)
        #QtCore.QObject.inherits(self)

        try:
	    self.hp_ser = serial.Serial(serparth, baudrate=9600, bytesize=serial.EIGHTBITS, timeout=None)
	except:
	    print "Failed to Open Serial Device"
	    quit()

        self.bulk_data = bytearray([b'\00' for i in range(0, 64)])
        self.dev_ret = self.bulk_data

    def readAnaOutput(self, ouput_num = 1):
        try:
            self.dev_ret = self.dev.read(129,64,0,500)
        except:
            print "WOULD HAVE CRASHED -- ANALOG READ"
        return self.dev_ret


class CallbackEvent(QtCore.QEvent):
    """
    A custom QEvent that contains a callback reference

    Also provides class methods for conveniently executing 
    arbitrary callback, to be dispatched to the event loop.
    """
    EVENT_TYPE = QtCore.QEvent.Type(QtCore.QEvent.registerEventType())

    def __init__(self, func, *args, **kwargs):
        super(CallbackEvent, self).__init__(self.EVENT_TYPE)
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def callback(self):
        """
        Convenience method to run the callable. 

        Equivalent to:  
            self.func(*self.args, **self.kwargs)
        """
        self.func(*self.args, **self.kwargs)

    @classmethod
    def post_to(cls, receiver, func, *args, **kwargs):
        """
        Post a callable to be delivered to a specific
        receiver as a CallbackEvent. 

        It is the responsibility of this receiver to 
        handle the event and choose to call the callback.
        """
        # We can create a weak proxy reference to the
        # callback so that if the object associated with
        # a bound method is deleted, it won't call a dead method
        if not isinstance(func, proxy):
            reference = proxy(func, quiet=True)
        else:
            reference = func
        event = cls(reference, *args, **kwargs)

        # post the event to the given receiver
        QtGui.QApplication.postEvent(receiver, event)



class DataPlot(Qwt.QwtPlot):

    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)
	
	self.temp_array = []
	self.rs_array = []
	self.temp_avg = []
	self.errors = []

        self.setCanvasBackground(Qt.Qt.white)
        self.alignScales()

        # Initialize data
        self.x = np.arange(0.0, 100000, 1)
	self.z = np.zeros(len(self.x), np.float)
        self.y = np.zeros(len(self.x), np.float)
	self.w = np.zeros(len(self.x), np.float)
	self.v = np.zeros(len(self.x), np.float)

        self.setTitle("Teflonator")
        self.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend);

	self.grid = Qwt.QwtPlotGrid()
        self.grid.attach(self)

        self.temp_curve = Qwt.QwtPlotCurve("Temperature")
        self.temp_curve.attach(self) 
        self.temp_curve.setPen(Qt.QPen(Qt.Qt.red, 3, Qt.Qt.DashDotLine, Qt.Qt.RoundCap, Qt.Qt.RoundJoin))

        self.relay = Qwt.QwtPlotCurve("Relay Status")
        self.relay.attach(self)
        self.relay.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                        Qt.QBrush(),
                                        Qt.QPen(Qt.Qt.yellow),
                                        Qt.QSize(7, 7)))
        self.relay.setPen(Qt.QPen(Qt.Qt.blue))

	self.avg_curve = Qwt.QwtPlotCurve("Avg Temp")
        self.avg_curve.attach(self)
        self.avg_curve.setPen(Qt.QPen(Qt.Qt.green, 3))

	self.error_curve = Qwt.QwtPlotCurve("Error")
        self.error_curve.attach(self)
        self.error_curve.setPen(Qt.QPen(Qt.Qt.green, 3))

        mY = Qwt.QwtPlotMarker()
        mY.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        mY.setLineStyle(Qwt.QwtPlotMarker.HLine)
        mY.setYValue(100.0)
        mY.attach(self)

        self.setAxisTitle(Qwt.QwtPlot.xBottom, "Time ( 200msec )")
        self.setAxisTitle(Qwt.QwtPlot.yLeft, "Degrees")

	self.grabKeyboard()

        self.startTimer(75)

	self.cycles = 0
	self.on_cycles = 45
	self.start = 0

    def alignScales(self):
        self.canvas().setFrameStyle(Qt.QFrame.Box | Qt.QFrame.Plain)
        self.canvas().setLineWidth(1)
        for i in range(Qwt.QwtPlot.axisCnt):
            scaleWidget = self.axisWidget(i)
            if scaleWidget:
                scaleWidget.setMargin(0)
            scaleDraw = self.axisScaleDraw(i)
            if scaleDraw:
                scaleDraw.enableComponent(
                    Qwt.QwtAbstractScaleDraw.Backbone, False)

    
    def timerEvent(self, e):
	rx_data = ''
	while not rx_data == '\r':
		rx_data = self.hp_ser.read(size=1)
	if rx_data == '\r':
		relay_status = self.hp_ser.read(size=1)
		self.hp_ser.read(size=1) #throw out tab
		temp = self.hp_ser.read(size=6)
		self.cycles+=1
	else:
		relay_status = 'NS'
		temp = 'NT'
	if not (relay_status == 'NS' and temp == 'NT'):
		if relay_status == 'r':
			self.rs_array.append(0)
		elif relay_status == 'R':
			self.rs_array.append(100)
		else:
			self.rs_array.append(self.rs_array[-1])		
		self.temp_array.append(float(temp))
		self.temp_avg.append(sum(self.temp_array[-101:-1])/100.)
		error = 80 - self.temp_avg[-1]
                if (len(self.errors) > 0) and (abs(error - self.errors[-1]) > 25):
                    self.errors.append(self.errors[-1])
                else:
                    self.errors.append(error)
	#else:
	#	self.temp_array.append(-1)
	
	if (self.cycles > 300) and (self.start == 0):
		self.start = 1
		self.cycles = 0

	if ( self.cycles > 512 ):
		self.cycles = 0

	if self.start == 1:
			
		#error = 80 - self.temp_avg[-1]
		#self.errors.append(error)
		
		prop_pwr = error*0.0045 #0.0035 seems to work alright with cover and 0.0025 deriv (@ 512)

		deriv = (self.errors[-1] - self.errors[-100])/2. #change in error in degrees per second?
		deriv_pwr = deriv*0.003

		self.on_cycles = (prop_pwr + deriv_pwr)*512
 
                if (self.cycles <= self.on_cycles and self.on_cycles > 0):
                    if relay_status != 'R':
                            self.hp_ser.write('R')
                else:
                    if relay_status == 'R':
                        self.hp_ser.write(' ')

		print "%s: %s (%s. %s), cycles: %s, error: %s, prop_pwr: %s, deriv_pwr: %s, on_cycles: %s. deriv: %s" % (relay_status, temp, self.temp_avg[-1], self.errors[-1], self.cycles, error, prop_pwr, deriv_pwr, self.on_cycles, deriv)


	self.y = array(self.temp_array)  
	self.z = array(self.rs_array)
	self.w = array(self.temp_avg)
	self.v = array(self.errors)     
        self.temp_curve.setData(self.x, self.y)
	self.relay.setData(self.x, self.z)
	self.avg_curve.setData(self.x, self.w)
	self.error_curve.setData(self.x, self.v)
        self.replot()

    def to_file(self):
    	f = open('output_data.txt', 'w')
    	f.write("Temperature\n")
    	for item in self.temp_array:
		f.write("%s\n" % item)
    	f.write("Relay\n")
    	for item in self.rs_array:
		f.write("%s\n" % item)

    def keyPressEvent(self,event):
        if event.key() == Qt.Qt.Key_Right:
            self.to_file()
	if event.key() == Qt.Qt.Key_Left:
            self.temp_array = []
            self.rs_array = []


def make():
    demo = DataPlot()
    demo.resize(500, 300)
    demo.show()
    return demo

def main(args): 
    app = Qt.QApplication(args)
    demo = make()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)

