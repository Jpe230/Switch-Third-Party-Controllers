import seriallib
import constants

class InputManager:
	def __init__(self, configCSVPath):
		self.mappingDict = {button: [] for button in constants.validButtonValues}
		f = open(configCSVPath, "r")
		f.readline()
		for line in f.readlines():
			seperatedLine = line.strip().replace(" ", "").split(",")
			if len(seperatedLine) == 1:
				continue
			
			button = seperatedLine[0].upper()
			if not button in constants.validButtonValues:
				print(f"Invalid Button Name ({button})")
				continue
			
			keys = seperatedLine[1:]
			for key in keys:
				if key.lower() in constants.nameKeyValDict:
					self.mappingDict[button].append(constants.nameKeyValDict[key])
				else:
					print(f"Received incorrect key value ({key}). Please refer to keys.txt for list of valid keys")
		print(self.mappingDict)

	def processInputs(self, payload: seriallib.Payload,  keysDown: list, mouseDiff: tuple) -> seriallib.Payload:
		dPadDir = [0, 0]
		for button, mappedKeys in self.mappingDict.items():
			if "mx" in mappedKeys or "my" in mappedKeys:
				if button in ["-LX","+LX"]:
					payload.setLeftX(128 + mouseDiff[0])
				elif button in ["-LY","+LY"]:
					payload.setLeftY(128 + mouseDiff[1])
				elif button in ["-RX","+RX"]:
					payload.setRightX(128 + mouseDiff[0])
				elif button in ["-RY","+RY"]:
					payload.setRightY(128 + mouseDiff[1])

			if any(key in keysDown for key in mappedKeys):
				if button in constants.validButtonValues[12:]:
					payload.applyButtons(1 << (constants.validButtonValues.index(button) - 12))

				elif button == "-LX":
					payload.setLeftX(0)
				elif button == "+LX":
					payload.setLeftX(255)

				elif button == "-LY":
					payload.setLeftY(0)
				elif button == "+LY":
					payload.setLeftY(255)

				elif button == "-RX":
					payload.setRightX(0)
				elif button == "+RX":
					payload.setRightX(255)

				elif button == "-RY":
					payload.setRightX(0)
				elif button == "+RY":
					payload.setRightX(255)

				elif button == "DLEFT":
					dPadDir[0] += -1
				elif button == "DRIGHT":
					dPadDir[0] += 1
				elif button == "DUP":
					dPadDir[1] += -1
				elif button == "DDOWN":
					dPadDir[1] += 1
				
		
		payload.setHatFromVector(dPadDir[0], dPadDir[1])
		return payload





class ControllerApplication:
	def __init__(self, serialBaud=38400):
		self.man = seriallib.SerialManager(serialBaud)
		self.verifySerialConnection()
		self.payload = seriallib.Payload()
		self.frame = 0

	def __enter__(self):
		return self

	def verifySerialConnection(self):
		if not len(self.man.getPortList()) > 0:
			raise LookupError("Unable to detect a connected serial device")
		
		print(self.man.getPortListStr())
		while True:
			portIndex = input("Select a port:")
			if not str.isdecimal(portIndex):
				print(f"Value {portIndex} is not an integer")
				continue
			if self.man.createSerialConnection(int(portIndex)):
				break
			print(f"Value {portIndex} was not valid.")

	def didReceiveFeedback(self):
		return self.man.ser.in_waiting > 0

	def submitData(self):
		self.man.writeByteArrayToSer(self.payload.asByteArray())

	def update(self):
		self.man.ser.read_all()
		self.submitData()
		
	def __exit__(self, exc_type, exc_value, traceback):
		self.man.__exit__(exc_type, exc_value, traceback)

