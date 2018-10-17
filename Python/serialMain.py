import string
import time
from pprint import pprint

import serial
from serial.tools import list_ports

BAUD = 38400

readable_chars = string.ascii_letters + string.digits

readable_byte_list = [ord(ch) for ch in readable_chars]
print(readable_byte_list)


def read_loop(read_port: serial.Serial) -> list:
	input_bytes = []
	if read_port.in_waiting > 0:
		byte_list = read_port.read_all()
		for single_byte in byte_list:
			if single_byte in readable_byte_list:
				input_bytes.append(chr(single_byte))
			else:
				input_bytes.append(single_byte)
	return input_bytes


def write_loop(write_port: serial.Serial, data: list) -> None:
	byte_arr = bytearray()
	for item in data:
		if type(item) == str:
			for data in item:
				byte_arr.append(ord(data))
		elif type(item) == int:
			if 0 <= item <= 255:
				byte_arr.append(item)
			else:
				print(f"Integer ({item}) is too large")
	write_port.write(byte_arr)


def get_data_from_user() -> list:
	output_data_list = []
	print("Don't type anything to send current data")
	print("And type \"exit\" in order to close program")
	while True:
		print(f"Current data: {output_data_list}")
		output_data = input("Data to send:")
		if output_data == "":
			break
		elif len(output_data) == 1:
			output_data_list.append(ord(output_data))
		elif output_data.isdigit():
			output_data_list.append(int(output_data))
		else:
			output_data_list.append(output_data)
	return output_data_list


def main_loop() -> None:
	avail_ports = list(list_ports.grep(""))

	for ind, port in enumerate(avail_ports):
		avail_ports[ind] = str(port).split(' ')[0].replace('cu.', 'tty.')
		print(f"{ind}, {port}")

	port_index = int(input("Choose port number:"))

	with serial.Serial(avail_ports[port_index], BAUD) as port:
		while True:
			# send outgoing bytes
			dat = get_data_from_user()
			if "exit" in dat:
				break

			write_loop(port, dat)
			time.sleep(0.1)
			# read incoming bytes
			serial_input = read_loop(port)
			if len(serial_input) > 0:
				print(f"Data Received:\n{serial_input}")
			else:
				print("No data received")






if __name__ == "__main__":
	main_loop()