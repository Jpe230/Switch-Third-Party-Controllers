from enum import Enum
from functools import reduce

import serial
from serial.tools import list_ports

from maths import clamp


class SerialManager:
    def __init__(self, baud: int):
        self.portList = self.getPortList()
        self.baud = baud
        self.ser = serial.Serial(baudrate=self.baud)


    def __enter__(self):
        return self


    def getPortListStr(self) -> list:
        self.portList = self.getPortList()
        return [f"{str(port)}, {i}" for i, port in enumerate(self.portList)]


    def createSerialConnection(self, index: int) -> bool:
        self.portList = self.getPortList()
        if len(self.portList) - 1 < index:
            return False
        self.ser.port = self.portList[index]
        self.ser.open()
        return True


    def writeByteArrayToSer(self, byteArr):
        if type(byteArr) == bytearray:
            self.ser.write(byteArr)
        else:
            print(f"Err:\nValue {byteArr} is not a valid byte array.")


    def writeAsBytes(self, *args) -> None:
        byteArr = bytearray()
        for a in args:
            if type(a) == str:
                for ch in a:
                    byteArr.append(ord(ch))
            elif 0 <= a <= 255:
                byteArr.append(a)
        print(f"Writing byte array ({byteArr}) to port {self.ser.port}")
        self.ser.write(byteArr)


    def readPortAsIntArr(self) -> tuple:
        byts = self.ser.read_all()
        intArr = []

        for byt in byts:
            if type(byt) == int:
                intArr.append(byt)
                continue
            intArr.append(int.from_bytes(byt, byteorder="big"))
        return tuple(intArr)


    @staticmethod
    def getPortList() -> str:
        return [str(portData).split(" ")[0] 
                for ind, portData in enumerate(list(list_ports.grep("")))]


    def __exit__(self, exc_type, exc_value, traceback):
        if self.ser.is_open:
            self.ser.close()


class Button(Enum):
    Y = 0x01
    B = 0x02
    A = 0x04
    X = 0x08
    L = 0x10
    R = 0x20
    ZL = 0x40
    ZR = 0x80
    MINUS = 0x100
    PLUS = 0x200
    LCLICK = 0x400
    RCLICK = 0x800
    HOME = 0x1000
    CAPTURE = 0x2000

    @classmethod
    def hasValue(cls, value):
        return any(value == item.value for item in cls)


class HAT(Enum):
    TOP = 0x00
    TOP_RIGHT = 0x01
    RIGHT = 0x02
    BOTTOM_RIGHT = 0x03
    BOTTOM = 0x04
    BOTTOM_LEFT = 0x05
    LEFT = 0x06
    TOP_LEFT = 0x07
    CENTER = 0x08

    @classmethod
    def hasValue(cls, value):
        return any(value == item.value for item in cls)


class Stick(Enum):
    MIN = 0
    CENTER = 128
    MAX = 255


class Payload:
    """
    Serial data payload class to handle controller serial data in order
    to prevent errors from input.  
    """
    MAX_BUTTON_VALUE = 16383
    def __init__(self):
        self.leftStick = (Stick.CENTER.value, Stick.CENTER.value)
        self.rightStick = (Stick.CENTER.value, Stick.CENTER.value)
        self.hat = HAT.CENTER.value
        self.buttons = 0

    def __repr__(self):
        return f"{self.__dict__}"

    def __str__(self):
        button_list = [button.name 
                        for ind, button in enumerate(Button) 
                        if self.buttons & (1<<ind)]
        st = f"LeftStick: {self.leftStick}, RightStick: {self.rightStick}," + f"HAT: {HAT(self.hat).name}, Buttons: {button_list}"
        return st

    def setLeftX(self, x):
        self.leftStick = (clamp(x, Stick.MIN.value, Stick.MAX.value), 
                        self.leftStick[1])

    def setLeftY(self, y):
        self.leftStick = (self.leftStick[0], 
                        clamp(y, Stick.MIN.value, Stick.MAX.value))


    def setLeftStick(self, x: int, y: int) -> None:
        self.leftStick = (clamp(x, Stick.MIN.value, Stick.MAX.value), 
                            clamp(y, Stick.MIN.value, Stick.MAX.value))


    def setRightX(self, x):
        self.rightStick = (clamp(x, Stick.MIN.value, Stick.MAX.value), 
                        self.rightStick[1])


    def setRightY(self, y):
        self.rightStick = (self.rightStick[0], clamp(y, Stick.MIN.value, Stick.MAX.value))


    def setRightStick(self, x: int, y: int) -> None:
        self.rightStick = (clamp(x, Stick.MIN.value, Stick.MAX.value), 
                            clamp(y, Stick.MIN.value, Stick.MAX.value))


    def setHatFromVector(self, x, y) -> None:
        dPadList = [
            [7,0,1],
            [6,8,2],
            [5,4,3]]
        self.hat = dPadList[y + 1][x + 1]

    def applyButtons(self, *args: Button) -> None:
        if not len(args) > 0:
            return
        enum_values = [item.value for item in args if type(item) == Button]
        nums =  [num for num in args if type(num) == int]
        value_list = enum_values + nums
        self.buttons |= clamp(reduce(lambda acc, val: acc | val, 
                            value_list, 0), 0, self.MAX_BUTTON_VALUE)


    def unapplyAllButtons(self):
        self.buttons = 0


    def resetAllInputs(self):
        self.leftStick = (Stick.CENTER.value, Stick.CENTER.value)
        self.rightStick = (Stick.CENTER.value, Stick.CENTER.value)
        self.buttons = 0
        self.hat = HAT.CENTER.value


    def asByteArray(self):
        buttons2, buttons1  = (b for b in self.buttons.to_bytes(2, byteorder="big"))
        return bytearray([self.leftStick[0], self.leftStick[1],
            self.rightStick[0], self.rightStick[1],
            self.hat, buttons1, buttons2])
