#!/usr/local/bin/python

from __future__ import print_function

import serial

class dlmsError(Exception):
	def __init__(self, reason):
		self.reason = reason
	def __str__(self):
		return repr(self.reason)

class dlms(object):

	def __init__(self, serial_port = "/dev/cuaU3"):
		self.ser = serial.Serial(
			port = serial_port,
			baudrate = 300,
			bytesize = serial.SEVENBITS,
			parity = serial.PARITY_EVEN,
			timeout = 3.0)

	def query(self):
		self.ser.write("/?!\r\n")
		state = 0
		id = ""
		cont = ""
		sum = 0
		while True:
			a = self.ser.read(1)
			if len(a) == 0:
				raise dlmsError("Rx Timeout")
			b = bytearray(a)[0]
			if state == 0:
				# Read ID string 
				if b >= 32:
					id += a
				elif b == 13:
					state = 1
				else:
					raise dlmsError(
					    "Illegal char in ident 0x%02x" % b)
					state = 99
			elif state == 1:
				# NL ending ID string
				if b != 10:
					raise dlmsError(
					    "Ident has 0x%02x after CR" % b)
					state = 99
				else:
					state = 2
			elif state == 2:
				# STX
				if b != 2:
					raise dlmsError(
					    "Expected STX not 0x%02x" % b)
					state = 99
				else:
					state = 3
			elif state == 3:
				# message body
				sum ^= b
				if b != 3:
					cont += a
				else:
					state = 4
			elif state == 4:
				# Checksum
				if sum != b:
					raise dlmsError(
					    "Checksum Mismatch")
					state == 99
				else:
					return self.parse(id, cont)
			elif state == 99:
				# Error, flush
				pass
		assert False

	def parse(self, id, cont):
		l = list()
		l.append(id)
		l.append(dict())
		cont = cont.split("\r\n")
		if cont[-1] != "":
			raise dlmsError(
			    "Last data item lacks CRNL")
		if cont[-2] != "!":
			raise dlmsError(
			    "Last data item not '!'")
		for i in cont[:-2]:
			if i[-1] != ")":
				raise dlmsError(
				    "Last char of data item not ')'")
				return None
			i = i[:-1].split("(")
			j = i[1].split("*")
			l[1][i[0]] = j
		return l
			

if __name__ == "__main__":
	foo = dlms()

	a = foo.query()
	print("%16s: %s" % ("identifier", a[0]))
	print("")
	for i in a[1]:
		j = a[1][i]
		if len(j) == 2:
			print("%16s: %s [%s]" % (i, j[0], j[1]))
		else:
			print("%16s: %s" % (i, j[0]))
