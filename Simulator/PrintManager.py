import os
from Util import RaceVariable

class PrintColors:
    HEADER 	= "\033[95m"
    BLUE 		= "\033[94m"
    GREEN 	= "\033[92m"
    RED 		= "\033[91m"
    ENDC 		= "\033[0m"

class PrintManager:
	__instance__ = RaceVariable()
	__construction__ = RaceVariable()
	verbose = False
	def __init__(self):
		os.system("color")
		PrintManager.__construction__.lockObj.acquire()
		if PrintManager.__instance__.value is None:
			self.buffer = RaceVariable({})
			self.counter = RaceVariable()
			self.counter.lockObj.acquire()
			self.counter.value = 2
			self.counter.lockObj.release()
			PrintManager.__instance__.value = self
		else:
			PrintManager.__construction__.lockObj.release()
			raise Exception("Attempting to create multiple Print Manager instance.")
		PrintManager.__construction__.lockObj.release()
		
	@staticmethod
	def get_instance():
		PrintManager.__instance__.lockObj.acquire()
		if PrintManager.__instance__.value is None:
			PrintManager()
		PrintManager.__instance__.lockObj.release()
		
		return PrintManager.__instance__.value

	def getCounter(self):
		self.counter.lockObj.acquire()
		temp = self.counter.value
		self.counter.value += 1
		self.counter.lockObj.release()
		return temp

	def addElement(self, obj, color = PrintColors.HEADER ,index = 0):
		self.buffer.lockObj.acquire()
		if index != 0:
			self.buffer.value[index] = [obj,color]
		else:
			self.buffer.value[self.getCounter()] = [obj,color]
		self.buffer.lockObj.release()

	def flush(self):
		self.buffer.lockObj.acquire()
		self.counter.lockObj.acquire()
		self.buffer.value = {}
		if not PrintManager.verbose:
			print("\033[2J", end = "")
		self.counter.value = 2
		self.counter.lockObj.release()
		self.buffer.lockObj.release()

	def printObjects(self):
		if not PrintManager.verbose:
			return
		self.buffer.lockObj.acquire()
		maxIndex = 0
		print("\033[2J", end = "")
		for i in self.buffer.value.keys():
			if maxIndex < i:
				maxIndex = i
			print("\033[{};{}H".format(i, 0) + self.buffer.value[i][1] +str(self.buffer.value[i][0]) + PrintColors.ENDC)
			print("\033[{};{}H".format(maxIndex, 0))
		self.buffer.lockObj.release()
