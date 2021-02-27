import threading, time
import queue
import struct
from Util import *

class MessageEncoder(threading.Thread):
	def __init__(self, communicationObject, sendingFrequency = 10, messageTypes = {}):
		threading.Thread.__init__(self, daemon=True)
		self.communicationObject = communicationObject
		self.messageTypes = messageTypes
		self.queue = queue.Queue()
		self.frequency = sendingFrequency
		self.stop = False

	def putMessage(self, vars):
		if vars[0] not in self.messageTypes.keys():
			return Error.MessageNotFound
		msgFormat = self.messageTypes[vars[0]].msgFormat
		data = struct.pack(msgFormat[:-1], *vars)
		crc = Util.checkCRC(data, len(data))
		data = struct.pack(msgFormat, *vars, crc)
		self.queue.put(data)
	

	def run(self):
		while self.stop == False:
			data = self.queue.get()
			self.communicationObject.write(data)
			time.sleep(1/self.frequency)
			

	