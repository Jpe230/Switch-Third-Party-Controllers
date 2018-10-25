import sys
import time

import cv2
import pygame

from maths import cvtFrameToTkImg
from switchlib import ControllerApplication, InputManager
from seriallib import Button, HAT

BAUD = 38400

UPDATES_PER_SECOND = 60
winDim = (640, 480)
lockMouse = False
mouseSens = (2, 2)
mouseDelta = (0, 0)

inMan = InputManager("controllerMapping.csv")

def cvImageToPygame(image):
    """Convert cvimage into a pygame image"""
    return pygame.image.frombuffer(image.tostring(), image.shape[1::-1],
                                   "RGB")

pygame.init()

screen = pygame.display.set_mode(winDim)

myFont = pygame.font.SysFont("Arial", 16)

textColor = pygame.Color(255, 255, 255)
screenFillColor = pygame.Color(255, 0, 0)

keysDown = []

with ControllerApplication() as conApp:
	while True:
		conApp.payload.resetAllInputs()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				conApp.man.ser.flush()
				sys.exit()

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.quit()
					conApp.man.ser.flush()
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

		inMan.processInputs(conApp.payload, keysDown, 
				(mouseDelta[0] * mouseSens[0], mouseDelta[1] * mouseSens[1]))

		if lockMouse and pygame.mouse.get_focused():
				pygame.mouse.set_pos(winDim[0] / 2, winDim[1] / 2)
				pygame.event.get(pygame.MOUSEMOTION)
		mouseDelta = (0, 0)
		
		
		
		
		screen.fill(screenFillColor)

		screen.blit(myFont.render(f"Sending:{str(conApp.payload)}", True, textColor), (0,0))
		screen.blit(myFont.render(f"Receiving:{conApp.man.readPortAsIntArr()}", True, textColor), (0,20))

		pygame.display.flip()
		conApp.update()
		time.sleep(1/UPDATES_PER_SECOND)