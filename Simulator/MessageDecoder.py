import threading, struct, enum, datetime
from collections import namedtuple

from Util import *
from PrintManager import *

class MessageTypes(enum.IntEnum):
	constants = 0x15
	controlMsg = 0x20
	pidMsg = 0x19
	sensorMsg = 0x45
	setPointMsg = 0x11
	syncMsg = 0x51


class Message:
	def __init__(self, msgId, msgName, msgSize, msgFormat, msgNamedTuple):
		self.msgId = msgId
		self.Name = msgName
		self.msgSize = msgSize
		self.msgFormat = msgFormat
		self.msgNamedTuple = msgNamedTuple
		self.msgData = msgNamedTuple()
		self.lockObj = threading.Lock()
		

class MessageDecoder(threading.Thread):

	def __init__(self, communicationObject, messageTypes = {}):
		threading.Thread.__init__(self, daemon=True)
		self.communicationObject = communicationObject
		self.messageTypes = messageTypes
		self.printManager = PrintManager.get_instance()
		self.stop = False

	def addNewMessageType(self, msgId, msgName, msgSize, msgFormat, msgNamedTuple):
		self.messageTypes[msgId] = Message(msgId, msgName, msgSize, msgFormat, msgNamedTuple)

	def getMessageData(self, msgId, clear = False):
		temp = None
		if msgId in self.messageTypes:
			self.messageTypes[msgId].lockObj.acquire()
			if self.messageTypes[msgId].msgData:
				temp = self.messageTypes[msgId].msgNamedTuple(**self.messageTypes[msgId].msgData._asdict())
				if clear:
					self.messageTypes[msgId].msgData = None
			self.messageTypes[msgId].lockObj.release()
		return temp

	def run(self):
		while self.stop == False:
			headerTemp = self.communicationObject.read(1)
			header = int.from_bytes(headerTemp, "little")
			if header in self.messageTypes:
				data = self.communicationObject.read(self.messageTypes[header].msgSize - 1)
				#print(type(data))
				self.printManager.addElement("[{}] {} message arrived".format(str(datetime.datetime.now().time())[:-4],
				self.messageTypes[header].Name), PrintColors.RED, 1)
				self.printManager.printObjects()
				self.messageTypes[header].lockObj.acquire()
				try:
					temp =	\
					self.messageTypes[header].msgNamedTuple._make(\
						struct.unpack(self.messageTypes[header].msgFormat, headerTemp + data))
					if(Util.checkCRC(headerTemp + data, self.messageTypes[header].msgSize - 1) == temp.crc):
						self.messageTypes[header].msgData = temp
					else:
						print("Incoming package with errors: " + str(temp))
				finally:
					self.messageTypes[header].lockObj.release()
			else:
				print(chr(header), end=" ")
				print("Unknow message arrived with id: " + str(chr(header)))
		
		for i in self.messageTypes.keys():
			messageTypes[i].lockObj.release()