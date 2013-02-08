import serial
import sys
from PyQt4 import Qt
from PyQt4.Qwt5 import *
from PyQt4.Qwt5.anynumpy import *

class DataPlot(Qwt.QwtPlot):

    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)
	
	try:
		self.hp_ser = serial.Serial('/dev/ttyACM1', baudrate=57600, bytesize=serial.EIGHTBITS, timeout=None)
	except:
		print "Failed to Open Serial Port"
		quit()	

	self.temp_array = []
	self.rs_array = []

        self.setCanvasBackground(Qt.Qt.white)
        self.alignScales()

        # Initialize data
        self.x = arange(0.0, 7200, 1)
	self.z = zeros(len(self.x), Float)
        self.y = zeros(len(self.x), Float)

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

        mY = Qwt.QwtPlotMarker()
        mY.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        mY.setLineStyle(Qwt.QwtPlotMarker.HLine)
        mY.setYValue(20.0)
        mY.attach(self)

        self.setAxisTitle(Qwt.QwtPlot.xBottom, "Time ( 500msec )")
        self.setAxisTitle(Qwt.QwtPlot.yLeft, "Degrees")

	self.grabKeyboard()

        self.startTimer(75)
	self.times = 0
	self.on_time = 16
	self.first = 0

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
		self.times+=1
	else:
		relay_status = 'NS'
		temp = 'NT'
	if not (relay_status == 'NS' and temp == 'NT'):
		if relay_status == 'r':
			self.rs_array.append(0)
		else:
			self.rs_array.append(100)
		self.temp_array.append(float(temp))
	else:
		self.temp_array.append(-1)

	if (self.times > 100) and (self.first == 0):
		self.first = 1
		self.times = 0

	if ( self.times > 2047 ):
		self.times = 0

	if self.first == 1:
		if (self.times <= self.on_time ):
			self.hp_ser.write('R')
		else:
			self.on_time = 16
			self.hp_ser.write(' ')		

	self.y = array(self.temp_array)  
	self.z = array(self.rs_array)      
        self.temp_curve.setData(self.x, self.y)
	self.relay.setData(self.x, self.z)
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

# Admire
if __name__ == '__main__':
    main(sys.argv)

