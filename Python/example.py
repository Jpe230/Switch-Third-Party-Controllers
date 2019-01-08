import sys
import time

import pygame
from serial.tools import list_ports

from switchlib import InputManager
from seriallib import SerialManager, Payload

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

payload = Payload()

BAUD = 38400



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


pygame.init()
size = [800, 700]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Xbox Controller")

done = False
clock = pygame.time.Clock()
pygame.joystick.init()

textPrint = textPrint()

inMan = InputManager("controllerMapping.csv")

keysDown = []

leftJoy  = [128, 128]
rightJoy = [128, 128]


with SerialManager(getPortFromUser(), BAUD) as serialMan: 
	while done == False:
		payload.resetAllInputs()
		# EVENT PROCESSING STEP
		for event in pygame.event.get(): 
			if event.type == pygame.QUIT: 
				done = True 

			# Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
			if event.type == pygame.JOYBUTTONDOWN:
				keysDown.append(event.button)
			if event.type == pygame.JOYBUTTONUP:
				keysDown.remove(event.button)

	
		screen.fill(WHITE)
		joystick = pygame.joystick.Joystick(0)
        	joystick.init()
		LJX = ((joystick.get_axis(0) + 1.0) / 2.0)
		LJY = ((joystick.get_axis(1) + 1.0) / 2.0)
		RJX = ((joystick.get_axis(3) + 1.0) / 2.0)
		RJY = ((joystick.get_axis(4) + 1.0) / 2.0)

		if(LJX < .55 and LJX > .45):
			LJX = 0.5
		if(LJY < .55 and LJY > .45):
			LJY = 0.5
		if(RJX < .55 and RJX > .45):
			RJX = 0.5
		if(RJY < .55 and RJY > .45):
			RJY = 0.5


		leftJoy[0] = int(LJX*256)
		leftJoy[1] = int(LJY*256)

		rightJoy[1] = int(RJX*256)
		rightJoy[0] = int(RJY*256)

		textPrint.unindent()

		hat = joystick.get_hat(0)


		inMan.processInputs(payload, keysDown, leftJoy, rightJoy, hat)	

		textPrint.print(screen, "Sending:{}".format(str(payload)))
	
		pygame.display.flip()

		serialMan.write(payload.asByteArray())
		serialMan.reset_input_buffer()
		serialMan.reset_output_buffer()

		clock.tick(60)

	pygame.quit()
	serialMan.flush()
	sys.exit()
