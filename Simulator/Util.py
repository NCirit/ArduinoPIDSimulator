import threading, enum

class RaceVariable:
	def __init__(self, var = None):
		self.value = var
		self.lockObj = threading.Lock()

class Error(enum.IntEnum):
	MessageNotFound = 0x0

class Util:
	
	@staticmethod
	def checkCRC(data, size):
		crc = 0; temp = 0; bit = 0
		for i in range(size):
			temp = data[i]
			for j in range(8):
				bit = (crc ^ temp) & 1
				crc >>= 1
				if bit:
					crc ^= 0x8C
				temp >>= 1
		return crc