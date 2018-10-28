import sys
import time

import pygame
from serial.tools import list_ports

from switchlib import InputManager
from seriallib import SerialManager, Payload

BAUD = 38400

UPDATES_PER_SECOND = 60

payload = Payload()

def getPortFromUser():
	portList = list(list_ports.grep(""))
	if len(portList) == 0:
		raise LookupError("Unable to detect Serial Device.")
	indexPortListString = [f"Index: {index}, Port: {port.device}, Description: {port.description}"
						   for index, port in enumerate(portList)]
	print(indexPortListString)
	while True:
		ind = input("What port index should be used? ")
		if not str.isdigit(ind):
			print(f"Value given is not a digit")
		elif not (0 <= int(ind) < len(portList)):
			print("Value given is not an index in the list")
		else:
			return portList[int(ind)].device




winDim = (640, 480)
lockMouse = False
mouseSens = (2, 2)
mouseDelta = (0, 0)

inMan = InputManager("controllerMapping.csv")

pygame.init()

screen = pygame.display.set_mode(winDim)

myFont = pygame.font.SysFont("Arial", 16, bold=True)

textColor = pygame.Color(255, 255, 255)
screenFillColor = pygame.Color(0, 0, 0)

keysDown = []

with SerialManager(getPortFromUser(), BAUD) as serialMan:
	while True:
		payload.resetAllInputs()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				serialMan.flush()
				sys.exit()

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					serialMan.flush()
					sys.exit()
				elif event.key == pygame.K_TAB:
					lockMouse = not lockMouse
				elif not event.key in keysDown:
					keysDown.append(event.key)

			elif event.type == pygame.KEYUP:
				if event.key in keysDown:
					keysDown.remove(event.key)
			
			elif event.type == pygame.MOUSEMOTION:
				mouseDelta = event.rel

			elif event.type == pygame.MOUSEBUTTONDOWN:
				keyStr = f"m{event.button}"
				if not keyStr in keysDown:
					keysDown.append(keyStr)

			elif event.type == pygame.MOUSEBUTTONUP:
				keyStr = f"m{event.button}"
				if keyStr in keysDown:
					keysDown.remove(keyStr)

		inMan.processInputs(payload, keysDown,
				(mouseDelta[0] * mouseSens[0], -mouseDelta[1] * mouseSens[1]))

		if lockMouse and pygame.mouse.get_focused():
				pygame.mouse.set_pos(winDim[0] / 2, winDim[1] / 2)
				pygame.event.get(pygame.MOUSEMOTION)
		mouseDelta = (0, 0)

		screen.fill(screenFillColor)

		screen.blit(myFont.render(f"Sending:{str(payload)}", True, textColor), (0,0))
		screen.blit(myFont.render(f"Receiving:{serialMan.readPortAsIntArr()}", True, textColor), (0,20))

		pygame.display.flip()
		serialMan.write(payload.asByteArray())
		time.sleep(1/UPDATES_PER_SECOND)
