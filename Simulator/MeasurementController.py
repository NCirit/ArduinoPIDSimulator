import threading, time
from Util import RaceVariable


class MeasurementController(threading.Thread):
	def __init__(self, startValue, decayValue, updateFrequency, stepSize, controlSignal, systemType=True, minValue = None):
		threading.Thread.__init__(self, daemon=True)
		self.update = self.accumulative if systemType else self.direct
		self.measurement = RaceVariable(startValue)
		self.decayValue = decayValue
		self.updateFrequency = updateFrequency
		self.stepSize = stepSize
		self.controlSignal = RaceVariable(controlSignal)
		self.stop = False
		self.absoluteMin = minValue

	def accumulative(self):
		self.measurement.value += self.stepSize * (self.controlSignal.value / 255) - self.decayValue

	def direct(self):
		self.measurement.value = self.stepSize * (self.controlSignal.value / 255)
	
	def update(self):
		pass

	def updateControlSignal(self, controlSignal):
		self.controlSignal.lockObj.acquire()
		self.controlSignal.value = controlSignal
		self.controlSignal.lockObj.release()

	def getTemperatureValue(self):
		temp = self.measurement.value
		return temp

	def run(self):
		while self.stop == False:
			self.controlSignal.lockObj.acquire()
			self.measurement.lockObj.acquire()
			self.update()
			if(self.absoluteMin is not None and self.measurement.value < self.absoluteMin):
				self.measurement.value = self.absoluteMin
			self.measurement.lockObj.release()
			self.controlSignal.lockObj.release()
			time.sleep(1/self.updateFrequency)
