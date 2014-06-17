"""
ReadTemp for Raspberry Pi

James Dryden and Brett Nelson
OSIsoft

Reads temperature values from a DS18B20 sensor and writes the timestamp 
and values to a .txt file
"""

import os
import glob
import time
import sys
import re


baseDir = '/sys/bus/w1/devices/'
writeFile = '/opt/LightingSystem/webServer/TempReadings.txt'


def findSensorDir():
	try:
		deviceFolder = glob.glob(baseDir + '28-*')[0]
		return deviceFolder
	except IndexError:
		print('DS18B20 temperature sensor not detected. Retrying in 10 seconds.')
		time.sleep(10)
		return findSensorDir()

def writeToFile(tempC, tempF):
	with open(writeFile, mode='w') as f:
		f.write(time.strftime("%m/%d/%Y %H:%M:%S", time.localtime()) + 
			' tempC=' + str(tempC) + ', tempF=' + str(tempF) + '\n')
	
def initializeSensor():
	os.system('sudo modprobe w1-gpio')
	os.system('sudo modprobe w1-therm')
	deviceFolder = findSensorDir()
	return TempSensor(deviceFolder + '/w1_slave')
	
class TempSensor(object):
	yesPattern = re.compile(r'YES')
	tempPattern = re.compile(r't=(\d+)')
	
	def __init__(self, path):
		self.path = path
		self._ready = False
		self._temp = []
	
	def _getData(self):
		with open(self.path) as f:
			data = f.read()
		if self.yesPattern.search(data):
			self._ready = True
		else:
			self._ready = False
		return data

	@property
	def temp(self):
		while not self._ready:
			data = self._getData()
		self._ready = False
		tempString = self.tempPattern.search(data).group(1)
		tempC = float(tempString) / 1000.0
		tempF = tempC * 9.0 / 5.0 + 32.0
		self._temp = [tempC, tempF]
		return self._temp
			
if __name__ == '__main__':
	try:
		DEBUG = sys.argv[1] == '-d'
	except IndexError:
		DEBUG = False

	sensor = initializeSensor()
	while True:
		[tempC, tempF] = sensor.temp
		if DEBUG: print('tempC=' + str(tempC), 'tempF=' + str(tempF))
		writeToFile(tempC, tempF)
		time.sleep(2)
	