import cv2
from PIL import Image, ImageTk


def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)


def cvtFrameToTkImg(frame):
    cv2Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    image = Image.fromarray(cv2Image)
    tkImg = ImageTk.PhotoImage(image)
    return tkImg