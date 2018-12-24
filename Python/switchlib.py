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

	def processInputs(self, payload: seriallib.Payload,  keysDown: list, leftJoy: list, rightJoy: list, hat: list) -> seriallib.Payload:
		dPadDir = [0, 0]

		payload.setLeftX(leftJoy[0])
		payload.setLeftY(leftJoy[1])
		payload.setRightX(rightJoy[0])
		payload.setRightY(rightJoy[1])

		dPadDir[0] = hat[0]
		dPadDir[1] = hat[1] * -1

		for button, mappedKeys in self.mappingDict.items():
			if any(key in keysDown for key in mappedKeys):
				if button in constants.validButtonValues[12:]:
					payload.applyButtons(1 << (constants.validButtonValues.index(button) - 12))
			
			
		payload.setHatFromVector(dPadDir[0], dPadDir[1])
		return payload
