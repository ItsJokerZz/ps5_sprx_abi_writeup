#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Change EI_ABIVERSION in PS5 SPRX file")
    parser.add_argument("file")
    parser.add_argument("--abi", "-a", type=int, default=3)
    args = parser.parse_args()

    if not (0 <= args.abi <= 255):
        print("Error: ABI must be 0-255")
        sys.exit(1)

    path = Path(args.file)
    if not path.is_file():
        print(f"Error: File not found: {path}")
        sys.exit(1)

    data = bytearray(path.read_bytes())

    elf_off = data.find(b"\x7fELF")
    if elf_off == -1:
        print("Error: ELF magic not found")
        sys.exit(1)

    abi_pos = elf_off + 8
    if abi_pos >= len(data):
        print("Error: File too short")
        sys.exit(1)

    old_abi = data[abi_pos]
    data[abi_pos] = args.abi

    out_path = path.with_name(f"{path.stem}_abi{args.abi}{path.suffix}")
    out_path.write_bytes(data)

    print(f"Changed ABI: {old_abi} -> {args.abi} (offset 0x{abi_pos:x})")
    print(f"Saved as: {out_path}")
    print(f"Size: {len(data):,} bytes")

if __name__ == "__main__":
    main()
