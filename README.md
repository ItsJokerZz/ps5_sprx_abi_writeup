# PS5 SPRX ABI Spoofer

## Background / Research

While testing SPRX loading, I noticed something simple:
* Some `libSce*` libraries load fine in PS4 processes
A specific example was `libSceNotification` (used for native toast notifications)

Example error when loading a PS4 SPRX into a PS5 process:
```
### <217> ERROR: ABIVERSION mismatch. /data/etaHEN/fps.prx
[rtld] <217> ERROR self_load_shared_object:2321: B: res 0 (fps.prx)  val 0
```

At that point the goal was just to find *what actually differs* between the SPRX(s).

So I took three types of SPRX:

* PS4-native
* PS5-only
* Backwards-compatible (`libSceNotification`)

Then:

* Removed signatures
* Dumped raw binaries
* Compared ELF headers directly (byte-level)

The thing I had noticed was a variable named:
`EI_ABIVERSION`

From my testing and research I discovered:
```
0 = PlayStation 4
1 = Unknown (Maybe Vita?)
2 = PlayStation 5
3 = Backwards-compatible
```

Changing this value was enough to influence whether a module to load or be rejected by the loader.

---

## Overview

A minimal Python utility for modifying the `EI_ABIVERSION` byte in a PlayStation 5 `.sprx` (ELF) file.

This tool performs a targeted binary patch—changing exactly one byte in the ELF header—without altering any other structure or section.
<br>
This will then allow a PS5 built SPRX to be loaded into a PS4 and 5 application and was used for etaHEN's FPS counter with a single library.

---

## Features

* Minimal and fast (single-byte patch)
* No external dependencies
* Safe output (writes to a new file)
* Works on any ELF-based SPRX

---

## Installation

No installation required beyond Python 3.

```bash
python3 --version
```

---

## Usage

### Default (sets ABI to 3)

```bash
python3 abi_spoof.py yourfile.sprx
```

### Custom ABI Version

```bash
python3 abi_spoof.py yourfile.sprx --abi 4
```

Short flag:

```bash
python3 abi_spoof.py yourfile.sprx -a 2
```

---

## Output

The tool does **not overwrite the original file**.

Instead, it creates a new file:

```
originalname_abiX.sprx
```

Example:

```
libkernel.sprx -> libkernel_abi3.sprx
```

---

## Technical Breakdown

### ELF Header Structure

Every ELF file begins with a 16-byte `e_ident` array:

```
Offset  Size  Description
0x00    4     Magic (0x7F 'ELF')
0x04    1     EI_CLASS
0x05    1     EI_DATA
0x06    1     EI_VERSION
0x07    1     EI_OSABI
0x08    1     EI_ABIVERSION  <-- TARGET
```

### What This Tool Does

1. Scans the file for ELF magic (`\x7fELF`)
2. Calculates offset:

   ```
   abi_offset = elf_start + 8
   ```
3. Reads current ABI value
4. Replaces it with the user-provided value
5. Writes a new file with the modification

### Why Offset +8?

Because `EI_ABIVERSION` is defined as the 9th byte (index 8) in the ELF identification array.

---

## Example Execution

```bash
python3 abi_spoof.py libSceExample.sprx -a 4
```

Output:

```
Changed ABI: 3 -> 4 (offset 0x8)
Saved as: libSceExample_abi4.sprx
Size: 1,234,567 bytes
```

---

## Error Handling

| Error               | Cause                        |
| ------------------- | ---------------------------- |
| ELF magic not found | File is not a valid ELF/SPRX |
| File too short      | Corrupted or truncated file  |
| ABI must be 0-255   | Invalid argument             |
| File not found      | Invalid path                 |
