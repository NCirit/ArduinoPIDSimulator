import serial, time, threading, struct, signal,sys,os, argparse
from collections import namedtuple
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from itertools import count

from Util import *
from MessageDecoder import MessageDecoder, MessageTypes
from MessageEncoder import MessageEncoder
from MeasurementController import MeasurementController
from PrintManager import *


parser = argparse.ArgumentParser(description="Arduino PID simulator")
required = parser.add_argument_group("required arguments")
optional = parser.add_argument_group("optional arguments")
required.add_argument("--com-port", action="store", type=str, help = "Serial communication port of arduino.", required=True)
required.add_argument("--baud-rate", action="store", type=str, help = "Serial communication baud rate.", required=True)
required.add_argument("--measurement-name", action="store", type=str, help = "Measurement name.", required=True)
required.add_argument("--set-point", action="store", type=float, help = "PID set point.", required=True)
required.add_argument("-kp", action="store", type=float, help = "PID proportional coefficient.", required=True)
required.add_argument("-kd", action="store", type=float, help = "PID deviation coefficient.", required=True)
required.add_argument("-ki", action="store", type=float, help = "PID integration coefficient.", required=True)
optional.add_argument("--system-type", action="store", type=str,nargs='?', const='',\
	help = "The default system is accumulative. If you define this parameter then the system switches to direct type.\
											Update Method:Accumulative: measurement +=  max_increase*(controlSignal/255)-decayVal;\
											Direct: measurement = max_increase*(controlSingal/255)")
optional.add_argument("--start-point", action="store", type=float, default=0, help = "PID start point. Default value is 0.")
optional.add_argument("-v", action="store", type=str, default=None, nargs='?', const='', help = "Enables printing info to console.")
optional.add_argument("--decay-value", action="store", type=float, default=0.05, nargs='?', const='', help = "System decay value. If the system is accumulative then this value is decreased wih the every system update. 0.05 is default value.")
optional.add_argument("--update-frequency", action="store", type=int, default=10, nargs='?', const='', help = "System update frequency(of measurement). Default value is 10.")
optional.add_argument("--max-increase", action="store", type=float, default=0.1, nargs='?', const='', help = "Maximum value applied to measurement according to applied control signal. 0.1 is default value.")
optional.add_argument("--absolute-min", action="store", type=float, default=None, nargs='?', const='', help = "Minimum value that simulated measurement can be.")

args = parser.parse_args()
print(args)
communicationPort = serial.Serial(args.com_port, args.baud_rate)

msgDecoder  = MessageDecoder(communicationPort)
msgEncoder = MessageEncoder(communicationPort, sendingFrequency = 10)
temperatureController = MeasurementController(args.start_point, args.decay_value,\
	 args.update_frequency, args.max_increase, 0, (args.system_type is None), args.absolute_min)

PrintManager.verbose = (args.v is not None)
printManager = PrintManager.get_instance()

start = False
stop = False
index = count()

x_vals = []
y_vals = []
P_vals = []
I_vals = []
D_vals = []

interval = 50

def closeProgram(signum, frame):
	PrintManager.verbose = None
	stop = True
	msgDecoder.stop = True
	msgEncoder.stop = True
	temperatureController.stop = True
	sys.exit(0)


signal.signal(signal.SIGBREAK, closeProgram)
signal.signal(signal.SIGINT, handler=closeProgram)

katsayilar = ""

figure = plt.figure()
ax1 = figure.add_subplot(211)
ax2 = figure.add_subplot(212)
baseTime = time.time()

plotList = []
annotionList = []

counter = 0
def animate(i):
	global plotList, annotionList, counter
	counter += 1
	x_vals.append(time.time() - baseTime)
	y_vals.append(temperatureController.getTemperatureValue())
	pidObj = msgDecoder.getMessageData(MessageTypes.pidMsg)

	P_vals.append(pidObj.p)
	I_vals.append(pidObj.i)
	D_vals.append(pidObj.d)

	for i in plotList:
		for k in i:
			k.remove()
	for i in annotionList:
		i.remove()
	plotList = []
	annotionList = []


	pMax = max(P_vals[-1], I_vals[-1])
	iMax = max(I_vals[-1], D_vals[-1])
	dMax = max(P_vals[-1], D_vals[-1])

	indexMatris = [	((pMax == P_vals[-1]) & (P_vals[-1] == dMax))*0.3 + ((pMax != P_vals[-1]) & (dMax != P_vals[-1]))*-1 + ((pMax != P_vals[-1]) ^ (dMax != P_vals[-1]))*-0.3,\
									((iMax == I_vals[-1]) & (I_vals[-1] == pMax))*0.3+ ((iMax != I_vals[-1]) & (pMax != I_vals[-1]))*-1 + ((iMax != I_vals[-1]) ^ (pMax != I_vals[-1]))*-0.3,\
									((dMax == D_vals[-1]) & (D_vals[-1] == pMax))*0.3 + ((dMax != D_vals[-1]) & (iMax != D_vals[-1]))*-1 + ((dMax != D_vals[-1]) ^ (iMax != D_vals[-1]))*-0.3]
	y_lims = ax2.get_ylim()
	offsetY = 0.08 * abs(y_lims[0] - y_lims[1])
	offsetX = 0.005 * x_vals[-1]
	
	if(counter % 50 == 0):
		ax1.clear()
		ax1.set_xlabel("sn")
		ax1.set_ylabel(args.measurement_name)
		ax1.axhline(args.set_point, color="darkgreen", linewidth=2)
		ax1.annotate("Set Point", [0, args.set_point], fontweight='bold')
		temp = ax1.plot(x_vals[-1], y_vals[-1], "bo", markersize=5)
		plotList.append(temp)
		temp = ax1.annotate("{:.3f}".format(y_vals[-1]), [x_vals[-1], y_vals[-1]],  fontweight='bold')
		annotionList.append(temp)
		ax1.plot(x_vals, y_vals, "b")
		ax1.set_title(katsayilar, wrap = True)
		#ax1.figure.canvas.draw()

		ax2.clear()
		ax2.set_xlabel("sn")

		temp = ax2.plot( x_vals[-1], P_vals[-1], "ro", markersize=5)
		plotList.append(temp)
		temp = ax2.annotate("{:.2f}".format(P_vals[-1]), [x_vals[-1] + offsetX, P_vals[-1] + offsetY * indexMatris[0]],\
			 color="r", fontweight='bold', annotation_clip=False)
		annotionList.append(temp)
		temp = ax2.plot(x_vals[-1], I_vals[-1], "go", markersize=5)
		plotList.append(temp)
		temp = ax2.annotate("{:.2f}".format(I_vals[-1]), [x_vals[-1] + offsetX, I_vals[-1] + offsetY * indexMatris[1]],\
			 color="g", fontweight='bold', annotation_clip=False)
		annotionList.append(temp)
		temp = ax2.plot(x_vals[-1], D_vals[-1], "bo", markersize=5)
		plotList.append(temp)
		temp = ax2.annotate("{:.2f}".format(D_vals[-1]), [x_vals[-1] + offsetX, D_vals[-1] + offsetY * indexMatris[2]],\
			 color="b", fontweight='bold', annotation_clip=False)
		annotionList.append(temp)

		ax2.plot(x_vals, P_vals, color="r", label="P")
		ax2.plot(x_vals, I_vals, color="g", label="I")
		ax2.plot(x_vals, D_vals, color="b", label="D")
		ax2.set_title("PID Graph", wrap = True)
		#ax2.figure.canvas.draw()
		plt.legend()
		figure.canvas.blit(figure.bbox)
		figure.canvas.flush_events()
		return
	

	#ax1.clear()
	temp = ax1.plot(x_vals[-1], y_vals[-1], "bo", markersize=5)
	plotList.append(temp)
	temp = ax1.annotate("{:.3f}".format(y_vals[-1]), [x_vals[-1] + offsetX, y_vals[-1]],  fontweight='bold')
	annotionList.append(temp)
	ax1.plot(x_vals[-2:], y_vals[-2:], color="b")
	ax1.set_title(katsayilar, wrap = True)
	#ax1.figure.canvas.draw()

	#ax2.clear()
	
	temp = ax2.plot( x_vals[-1], P_vals[-1], "ro", markersize=5)
	plotList.append(temp)
	temp = ax2.annotate("{:.2f}".format(P_vals[-1]), [x_vals[-1] + offsetX, P_vals[-1] + offsetY * indexMatris[0]],\
			color="r", fontweight='bold', annotation_clip=False)
	annotionList.append(temp)
	temp = ax2.plot(x_vals[-1], I_vals[-1], "go", markersize=5)
	plotList.append(temp)
	temp = ax2.annotate("{:.2f}".format(I_vals[-1]), [x_vals[-1] + offsetX, I_vals[-1] + offsetY * indexMatris[1]],\
			color="g", fontweight='bold', annotation_clip=False)
	annotionList.append(temp)
	temp = ax2.plot(x_vals[-1], D_vals[-1], "bo", markersize=5)
	plotList.append(temp)
	temp = ax2.annotate("{:.2f}".format(D_vals[-1]), [x_vals[-1] + offsetX, D_vals[-1] + offsetY * indexMatris[2]],\
			color="b", fontweight='bold', annotation_clip=False)
	annotionList.append(temp)

	ax2.plot(x_vals[-2:], P_vals[-2:], color="r")
	ax2.plot(x_vals[-2:], I_vals[-2:], color="g")
	ax2.plot(x_vals[-2:], D_vals[-2:], color="b")
	figure.canvas.blit(figure.bbox)
	figure.canvas.flush_events()




def watchThread():
	global katsayilar, msgDecoder, msgEncoder,start,stop
	
	Constants = namedtuple("Constants", "msgId kp ki kd crc", defaults=(MessageTypes.constants,0,0,0,0))
	ControlSignal = namedtuple("ControlSignal", "msgId signal crc", defaults=(MessageTypes.controlMsg,0,0))
	PIDSignals = namedtuple("PIDSignals", "msgId p i d crc", defaults=(MessageTypes.pidMsg,0,0,0,0))
	SensorData = namedtuple("SensorData", "msgId data crc", defaults=(MessageTypes.sensorMsg,0,0))
	SetPoint = namedtuple("SetPoint", "msgId setPoint crc", defaults=(MessageTypes.setPointMsg,0,0))
	SyncObject = namedtuple("SyncObject", "msgId crc", defaults=(MessageTypes.syncMsg,0))

	# msgId, msgName, msgSize, msgFormat, msgNamedTuple
	msgDecoder.addNewMessageType(MessageTypes.constants, "Constants", 14, "<BfffB", Constants)
	msgDecoder.addNewMessageType(MessageTypes.controlMsg, "ControlSignal", 6, "<BfB", ControlSignal)
	msgDecoder.addNewMessageType(MessageTypes.pidMsg, "PIDSignals", 14, "<BfffB", PIDSignals)
	msgDecoder.addNewMessageType(MessageTypes.sensorMsg, "SensorData", 6, "<BfB", SensorData)
	msgDecoder.addNewMessageType(MessageTypes.syncMsg, "SyncObject", 2, "<BB", SyncObject)
	msgDecoder.addNewMessageType(MessageTypes.setPointMsg, "SetPoint", 6, "<BfB", SetPoint)

	msgEncoder.messageTypes = msgDecoder.messageTypes

	msgDecoder.getMessageData(MessageTypes.syncMsg, True)

	msgDecoder.start()
	msgEncoder.start()
	temperatureController.start()
	start = True
	while stop == False:
		#printManager.flush()
		if msgDecoder.getMessageData(MessageTypes.syncMsg, True):
			msgDecoder.getMessageData(MessageTypes.setPointMsg,True)
			msgDecoder.getMessageData(MessageTypes.constants, True)

			data = msgDecoder.getMessageData(MessageTypes.setPointMsg) or SetPoint()
			temp = struct.pack(msgDecoder.messageTypes[MessageTypes.setPointMsg].msgFormat[:-1], data.msgId, data.setPoint)
			while Util.checkCRC(temp, len(temp)) != data.crc:
				msgEncoder.putMessage([MessageTypes.setPointMsg, args.set_point])
				time.sleep(0.1)
				data = msgDecoder.getMessageData(MessageTypes.setPointMsg) or SetPoint()
				temp = struct.pack(msgDecoder.messageTypes[MessageTypes.setPointMsg].msgFormat[:-1], data.msgId, data.setPoint)
			
			data = msgDecoder.getMessageData(MessageTypes.constants) or Constants()
			temp = struct.pack(msgDecoder.messageTypes[MessageTypes.constants].msgFormat[:-1], data.msgId, data.kp, data.ki, data.kd)
			while Util.checkCRC(temp, len(temp)) != data.crc:
				msgEncoder.putMessage([MessageTypes.constants, args.kp, args.ki, args.kd])
				time.sleep(0.1)
				data = msgDecoder.getMessageData(MessageTypes.constants) or Constants()
				temp = struct.pack(msgDecoder.messageTypes[MessageTypes.constants].msgFormat[:-1], data.msgId, data.kp, data.ki, data.kd)
		control = msgDecoder.getMessageData(MessageTypes.controlMsg)
		katsayilar = str(msgDecoder.getMessageData(MessageTypes.constants))
		pid = msgDecoder.getMessageData(MessageTypes.pidMsg)

		temperatureController.updateControlSignal(control.signal)
		currentTemp = temperatureController.getTemperatureValue()
		msgEncoder.putMessage([MessageTypes.sensorMsg, currentTemp])
		sensor = msgDecoder.getMessageData(MessageTypes.sensorMsg)
		
		printManager.addElement(control, PrintColors.GREEN, 2)
		printManager.addElement(sensor, PrintColors.GREEN, 3)
		printManager.addElement(pid, PrintColors.GREEN, 4)
		printManager.printObjects()
		time.sleep(0.1)

x = threading.Thread(target=watchThread, args=tuple())
x.setDaemon(True)

def main():
	global start, x
	x.start()
	while(not start):
		pass
	figure.canvas.set_window_title("PID Simulator by Nurullah Cirit")
	ax1.set_xlabel("sn")
	ax1.set_ylabel(args.measurement_name)
	ax1.axhline(args.set_point, color="darkgreen", linewidth=2)
	ax1.annotate("Set Point", [0, args.set_point], fontweight='bold')

	ax2.set_xlabel("sn")
	ax2.plot(0, 0, color="r", label="P")
	ax2.plot(0, 0, color="g", label="I")
	ax2.plot(0, 0, color="b", label="D")
	ax2.set_title("PID Graph", wrap = True)
	figure.canvas.draw()
	plt.legend()
	plt.subplots_adjust(top=0.9, right=0.945, bottom = 0.1, left= 0.125, wspace= 0.2, hspace= 0.405)
	ani = FuncAnimation(plt.gcf(), animate, interval = interval)
	plt.show()


if __name__ == "__main__":

	#plt.show(block = False)
	main()
	#input("Press enter to exit.")
