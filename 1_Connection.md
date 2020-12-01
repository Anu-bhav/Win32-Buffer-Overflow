## connect.py

Making sure connection and all the operations are successfully performed is crucial as everything will be built on this script/step.

```
import socket
import sys

rhost = "192.168." 	# edit remote host here
rport = 6969		# edit remote port here


try:
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((rhost,rport))
	print s.recv(1024)
	s.send('USER test\r\n')
	print s.recv(1024)
	s.send('PASS asdf\r\n')
	print s.recv(1024)
	s.send('QUIT\r\n')
	s.close()
except:
	print "Oops! Something went wrong!"
	sys.exit()
```

OR use net-cat (recommended)
Command: `nc -nv $RHOST $RPORT`
Example: `nc -nv 192.168.69.5 6969`
