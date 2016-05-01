import http.server
import ReadTemp
import time

address = ('', 8000)

class WebHandler(http.server.BaseHTTPRequestHandler):
	baseDir = '/sys/bus/w1/devices/'
	writeFile = '/opt/LightingSystem/webServer/TempReadings.txt'
	sensor = ReadTemp.initializeSensor()
	def do_GET(self):
		print('Received {0:s} request from {1:s}'.format(self.command, self.client_address[0]))
		if self.path.endswith('/get_temp'):
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			[tempC, tempF] = self.sensor.temp
			timeString = time.strftime("%m/%d/%Y %H:%M:%S", time.localtime())
			retString = ('{0:s} tempC={1:f}, tempF={2:f}'.format(timeString, tempC, tempF))
			print("Response: <{0}>".format(retString))
			self.wfile.write(retString.encode('utf-8'))
	
if __name__ == '__main__':
	tempAPI = http.server.HTTPServer(address, WebHandler)
	try:
		print('Serving at port {0:d}'.format(address[1]))
		tempAPI.serve_forever()
	except KeyboardInterrupt:
		print('Closing socket.')
		tempAPI.socket.close()
		exit()
