---
title: How the ASUS ITE keyboard controller works and why it gets stuck in 048D:89DB
description: Flash map, slot table, checksum, boot flow and ISP protocol of the ITE8252 keyboard MCU in ASUS ROG laptops (GU605MI). Why the keyboard ends up in ITE Upgrade Mode.
---

# how it works

everything here is from my GU605MI (controller ITE8252, firmware `FGA00000.GU605  .415`). I read the chip, disassembled the bootloader and compared with official ASUS images for Strix G614. other models may differ in details, itefix checks the layout before it writes anything.

## the chip

the keyboard is not wired to the main EC. it has its own MCU (ITE IT8252, Andes NDS32 core) with 256 KiB of flash, sitting on USB as `0b05:19b6 N-KEY Device` when it runs normally. the main EC of the laptop is a different ITE chip (IT8856 on mine) and its firmware is in the BIOS image. the keyboard firmware is not in the BIOS, so a BIOS reflash doesn't touch it.

## flash map (GU605MI, fw .415)

| range | what |
|---|---|
| `0x00000-0x01FFF` | bootloader, string `IT8297-BOOT-V1.1`, ITE flash signature at `0x80` |
| `0x02000-0x1D7FF` | app A (keyboard firmware), base `0x2000` |
| `0x1E000-0x1FFFF` | ISP block `ITE8297-BBK`, this is what shows up as `048D:89DB ITE Upgrade Mode` |
| `0x20000-0x3B7FF` | app B, same code linked for `+0x1E000` |
| `0x3C000-0x3C3FF` | firmware name + slot table at `0x3C030` |
| `0x3C400-0x3D7FF` | settings the app saves at runtime |
| `0x3E000-0x3FFFF` | empty |

official Strix G614 images use a newer bootloader: slot table at `0x3C400`, apps end at `0x1DFFF` / `0x3BFFF`, plus a `$IEC` record at `0x3F800`.

## slot table

| offset | size | value on my chip |
|---|---|---|
| +0x00 | u32 | app A checksum start `0x2002` |
| +0x04 | u32 | app A end `0x1D7FF` |
| +0x08 | u32 | app A base `0x2000` |
| +0x0C | u32 | app B checksum start `0x20002` |
| +0x10 | u32 | app B end `0x3B7FF` |
| +0x14 | u32 | app B base `0x20000` |
| +0x18 | u8 | which slot to try first (0 = A) |
| +0x1A | u16 | chip id `0x8252` |

## checksum

the first two bytes of each app are a **big endian** u16. the app is valid when

```
stored == (-sum(bytes[start .. end])) & 0xFFFF
```

every official image I checked passes this for both slots.

## boot flow

bootloader (NDS32, disassemble with binutils 2.41 `objdump -b binary -m n1h_v3 -EB`):

1. `0x0000` jumps to `0x0C00`, init, then main at `0x1D32`
2. main reads the table at `0x3C000`, checks the chip id at `+0x4A`, picks the slot from `+0x48`
3. checksum routine at `0x0800`. pass: maps the last 1 KiB of the slot (`end - 0x3FF`, the vector page) to address 0 through registers `0xF01040-0xF01042` and jumps to 0, the keyboard app starts
4. fail: tries the other slot. both fail: jumps to the ISP block at `0x1E000`

ISP block (main at `0x1ED16`): enumerates as `048D:89DB`, waits `600000` ms for an updater, then resets the MCU. that's the 10 minute loop.

the app itself only jumps to the ISP block on HID command `0x09` from the host (the ASUS updater uses it, the app writes `0x99` to `0xF020FF` first so the ISP block knows it was asked).

## what happened to mine

- app B: checksum off by exactly `0x30`, two bits flipped 0 to 1 (one of them at `0x36C60`, `00` became `20`)
- app A: read fine through the ISP block at first. while I was working on it two more bits leaked: `0xAC4E` `d5` to `f5`, `0x11418` `00` to `40`
- every flip is 0 to 1. a programmed cell losing charge reads as 1, so this is charge loss (retention), not wear
- in october the bootloader read A wrong only on a cold start, and after the 10 minute ISP restart (chip warm) it read it fine, that's why the keyboard woke up after 10 minutes. later it failed every time

the ISP block reads slowly enough that weak cells still come out right. so a dump made in ISP mode can be cleaner than what the bootloader sees at boot. that's the whole trick: dump, verify the checksum on the PC, write the same bytes back so every cell gets a full charge again.

## ISP protocol

HID feature reports, report id 0, 64 byte payload. same as the official "ROG Keyboard Firmware Update" tool, worked out by [fosfuchs/kbfw](https://github.com/fosfuchs/kbfw).

| command | payload | meaning |
|---|---|---|
| read | `D1 a0 a1 a2 n` then GET | reply `D1 a0 a1 a2 n data[n]`, n = 56 |
| erase | `C2 a0 a1 a2 01 00` | erase one 1 KiB sector (I checked: neighbours stay intact) |
| stage | `C1 off_lo off_hi n data[n]` x18 | fill the 1 KiB staging buffer, 57 bytes per frame (last one 55) |
| stage check | `D0 AC 02 39 data[0x2AC:+57]` then GET | reply byte 1-2 = 16 bit sum of the staging buffer |
| program | `C3 a0 a1 a2 00 04`, `C0 72 00 39 data[0x72:+57]` then GET | write the staged sector |
| reset | `C4` | restart the MCU (itefix doesn't use it, the 10 minute timeout does the same) |

`a0 a1 a2` is the flash address, low byte first.

## what itefix refresh does

1. reads bootloader and ISP block, must match your dump (otherwise wrong dump or other firmware, it stops)
2. reads every sector of the app slot. accepts only "0 in the dump, 1 on the chip" differences, at most 8 bits per sector
3. per sector: erase, poll until blank, stage, compare the staging sum, program, read back and compare, up to 4 tries
4. reads everything again and verifies
5. never writes below `0x2000` or inside `0x1E000-0x1FFFF`, there is a hard check in the code
