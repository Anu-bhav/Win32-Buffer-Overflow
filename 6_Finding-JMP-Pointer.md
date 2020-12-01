# Finding JMP Pointer

Once all the bad characters are found, we’ll find the JMP ESP pointer from the Immunity Debugger itself using mona. By example, the bad characters that I will be avoiding are - *0x00 0x0a 0x0d*

`!mona jmp -r esp -cpb "\x00\x0a\x0d"`

By executing the above command you will not only find the addresses, without protection mechanisms, that would perform JMP ESP but also ensure that none of the addresses has any of the bad characters in itself.

**Please ensure you select an address from the applications’ DLL ONLY, and NOT from OS DLLs**. Application DLLs will be constant across operating systems, but we can NOT say the same for OS DLLs.
* * *

If mona module is not found by Immunity Debbuger, copy the `mona.py` file to the moudules folder in Immunity Debugger install path.


