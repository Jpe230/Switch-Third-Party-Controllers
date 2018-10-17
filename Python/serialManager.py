import struct

import serial
from serial.tools import list_ports


class Manager:
    def __init__(self, baud: int):
        self.port_list = self.getPortList()
        self.baud = baud
        self.ser = serial.Serial(baudrate=self.baud)

    def getPortListStr(self) -> list:
        self.port_list = self.getPortList()
        return [f"{str(port)}, {i}" for i, port in enumerate(self.port_list)]

    def createSerialConnection(self, index: int) -> bool:
        self.port_list = self.getPortList()
        if len(self.port_list) - 1 < index:
            return False
        self.ser.port = self.port_list[index]
        self.ser.open()

    def writeAsBytes(self, *args) -> None:
        byte_arr = bytearray()
        for a in args:
            if type(a) == str:
                for ch in a:
                    byte_arr.append(ord(ch))

            elif 0 <= a <= 255:
                byte_arr.append(a)

        print(f"Writing byte array ({byte_arr}) to port {self.ser.port}")
        self.ser.write(byte_arr)

    def readPortAsIntArray(self) -> tuple:
        byts = self.ser.read_all()
        int_arr = []

        for byt in byts:
            if type(byt) == int:
                int_arr.append(byt)
                continue
            int_arr.append(int.from_bytes(byt, byteorder="big"))
        return tuple(int_arr)

    @staticmethod
    def getPortList() -> str:
        return [str(portData).split(" ")[0] for ind, portData in enumerate(list(list_ports.grep("")))]
