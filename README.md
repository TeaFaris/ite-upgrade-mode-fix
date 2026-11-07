# ASUS ROG keyboard dead, stuck in "ITE Upgrade Mode" (048D:89DB)? How I fixed mine

[Русская версия](README.ru.md) | **not into computers? [simple step by step guide](GUIDE.md)**

so the built-in keyboard on my ASUS ROG Zephyrus G16 (GU605MI) died. not a few keys, the whole thing, even in BIOS. touchpad and power button still worked. on Linux `lsusb` showed this

```
048d:89db Integrated Technology Express, Inc. ITE Upgrade Mode
```

instead of the normal `0b05:19b6 ASUSTek Computer, Inc. N-KEY Device`. on Windows the same thing is a device with hardware id `HID\VID_048D&PID_89DB` in Device Manager.

I fixed it myself. no service, no new keyboard. here is the story, what actually happens inside that chip, and a small tool called `itefix` (Linux + Windows) so you can check yours and maybe fix it too.

## is this your problem?

- internal keyboard doesn't work anywhere: Windows, Linux, BIOS, boot menu
- keyboard backlight / Aura dead too, touchpad works
- `048D:89DB`, `VID_048D&PID_89DB`, "ITE Upgrade Mode", "ITE Tech. Inc." shows up instead of the keyboard
- big hint: the keyboard comes back by itself about 10 minutes after power on, then works until the next boot (that was me for a whole month)
- the ASUS "ROG Keyboard Firmware Update" tool log says `GetASUSDevice fail` and `GetITEDevice`
- MyASUS, Armoury Crate, Windows Update, BIOS update, power drain, reinstalling drivers: nothing helps

if most of that sounds familiar, keep reading.

## tl;dr

the keyboard has its own little controller (ITE IT8252 in my laptop) with its own flash memory. that flash slowly loses charge, bits flip from 0 to 1. the bootloader checks a checksum of the keyboard firmware on every power on, sees garbage and jumps into update mode (that is the 048D:89DB device) waiting for an updater that never comes. after 10 minutes it gives up, restarts and tries again.

when I read the chip in update mode the firmware still came out correct. so I dumped it and wrote the exact same firmware back. cells charged again, checksum fine, keyboard alive, also from a cold boot.

## quick start

you need an external USB keyboard for this, obviously.

Linux:

```
curl -fsSL https://raw.githubusercontent.com/TeaFaris/ite-upgrade-mode-fix/main/install.sh | sudo sh
sudo itefix status
```

Windows (PowerShell):

```
irm https://raw.githubusercontent.com/TeaFaris/ite-upgrade-mode-fix/main/install.ps1 | iex
itefix status
```

then the easy way, one command that does everything (backup, picks the right firmware, asks before writing):

```
sudo itefix fix        # Linux
itefix fix             # Windows
```

it's one python file, no dependencies. the Windows installer gets Python with winget if you don't have it. below is what `fix` does step by step, if you want to do it by hand.

## what to do if you have this

1. **check it's the same thing.** `itefix status` should say the controller is stuck in ITE Upgrade Mode (048D:89DB).
2. **try the boring safe stuff first.** full shutdown, unplug the charger, hold power 60 s. update BIOS. if ASUS has a "ROG Keyboard Firmware Update tool" for your exact model on its support page (Firmware section), run it in Windows. Strix G614 / G814 / G634 / G834 / G713 / G733 and Flow Z13 GZ302 have one. Zephyrus G16 GU605 doesn't, that's why I ended up here.
3. **dump the chip now.** this is read only and safe:
   ```
   sudo itefix dump -o mykeyboard.bin
   ```
   do it early. the leaks get worse, mine got 2 more bad bits in two hours. put that file in the cloud or on your phone, it's your only clean copy.
4. **look at it:** `itefix info mykeyboard.bin`
   - **app A: checksum OK**: good news, your firmware is still readable. fix:
     ```
     sudo itefix refresh --ref mykeyboard.bin
     ```
     then wait up to 10 minutes or power off and on. that's what fixed mine.
   - **app A bad** (B OK or both bad): don't write your own dump back. check [firmware/](firmware/) for a clean dump of your model and use that one (`refresh --ref` for the same version, `flash` for another one). nothing for your model yet: open an issue with the `itefix info` output, maybe someone has it.
   - **slot table not found**: different controller generation (for example ITE8259 in the 2025 Flow Z13). itefix won't write to it. issue please, with the info output.
5. **Linux bonus, auto repair next time:**
   ```
   sudo itefix install-auto --ref mykeyboard.bin
   ```
   when the controller shows up as 048D:89DB again it gets repaired from your dump on its own.
6. **nothing worked**: service. the controller or the keyboard/top case gets replaced.

## is it safe?

honest answer: it writes firmware into a chip, so there is some risk. this is what keeps it small:

- itefix never erases or writes the bootloader (0x0000-0x1FFF) or the update mode block (0x1E000-0x1FFFF). while those two are alive the chip always comes back as 048D:89DB and you can try again
- `refresh` only accepts differences that look like charge leaks (a 0 bit that reads as 1) between the chip and your dump. anything else and it stops before writing
- every sector: erase, check it's blank, write, read back, compare. 4 tries per sector
- it also refuses to write if the bootloader on the chip doesn't match the dump, so you can't flash a dump from a different firmware by accident
- I tested writing on my GU605MI on Linux. the Windows part I only tested for starting up and listing devices (under Wine), I never flashed a real chip from Windows. Linux live USB is the safer bet
- keep the laptop on the charger and don't close the lid while it writes

`itefix selftest` runs all the write logic on a simulated chip, no hardware involved.

## my story

- **2026-10-07.** the laptop hard powered off (got stuck going to sleep with RAM full). after that the keyboard was dead for exactly 10 minutes after every power on, then fine. lived like that for a month, waited or used an external keyboard.
- **2026-11-07, 03:18.** another hard power off. now the keyboard never came back at all. lsusb: 89db, every 10 minutes it reconnects and it's 89db again.
- tried a 60 s power drain. reflashed BIOS 329 with EZ Flash. installed Windows next to Linux just to run ASUS stuff: MyASUS, Armoury Crate, Windows Update. Armoury Crate even downloaded the ROG keyboard firmware tool and ran it. its log: product GU605MI, `GetASUSDevice fail`, `GetITEDevice`, done. there is no GU605 firmware in that package, ASUS just doesn't publish it for this model.
- side quest: Windows setup can't see the SSD when Intel VMD is on and the installer sits on the same disk, and my cheap USB stick turned out to be fake (returns garbage after a few GB). great day.
- found a GL703VD recovery repo, a Reddit post about a GU603ZW and the kbfw tool (links below). dumped my chip read only. inside: firmware `FGA00000.GU605 .415`, controller ITE8252, two copies of the keyboard app, A and B.
- disassembled the bootloader (it's an Andes NDS32 CPU, binutils 2.41 still has the disassembler). the bootloader checks a 16 bit checksum of the app copy. copy B was bad with two flipped bits. copy A was fine when read slowly in update mode, but the chip itself read it wrong at boot. and while I was digging, two more bits leaked in A (0xAC4E `d5` became `f5`, 0x11418 `00` became `40`).
- wrote A back from my dump, 110 sectors, 45 seconds. at the next update mode timeout the chip came back as `0b05:19b6`. rebooted twice, keyboard alive 1.2 seconds after power on. first time since october.
- why the flash leaks I don't know for sure. heat, a weak chip, maybe the cola I spilled on this keyboard a year ago. if it happens again the auto repair kicks in.

technical details (flash map, checksum, boot flow, protocol): [docs/how-it-works.md](docs/how-it-works.md)

## which laptops does itefix work on

**tested on real hardware:** ROG Zephyrus G16 **GU605MI** (2024, ITE8252, firmware .415). the other GU605M variants (GU605MV, GU605MY, GU605MZ, GU605MU) are most likely the same.

**should work, not tested by me:** same ITE8252 chip and same bootloader. `itefix info` reads all 47 official ASUS keyboard images for these and both checksums pass, and kbfw already brought a G614PP back with the same protocol:

ROG Strix G16 / G18 / SCAR: G614FM, G614FP, G614FR, G614JI, G614JJ, G614JU, G614JV, G614JZ, G614PM, G614PP, G614PR, G615JM, G615JMR, G615JPR, G615LM, G615LP, G615LR, G615LW, G634JY, G634JZ, G635LR, G635LW, G635LX, G713PI, G713PU, G713PV, G733PY, G733PZ, G814FM, G814FP, G814JI, G814JU, G814JV, G814JZ, G814PM, G814PP, G815JMR, G815JPR, G815LM, G815LP, G815LR, G815LW, G834JY, G834JZ, G835LR, G835LW, G835LX

the official ASUS keyboard firmware for all of them is in [firmware/asus/](firmware/), taken unchanged from the ASUS "ROG Keyboard Firmware Update" packages. so even if the firmware on your chip is completely dead, `itefix fix` downloads the right file and puts it back, from Linux too, where the ASUS tool doesn't run. it picks the version whose bootloader matches your chip.

**not supported:** the ITE8259 platform: ROG Flow Z13 GZ302 (2025), and going by the Reddit post the Zephyrus M16 GU603ZW. different flash layout, itefix doesn't recognize it and refuses to write, nothing breaks. older GL703VD / GL502VMK: unknown.

## firmware in this repo

[firmware/](firmware/) has the official ASUS keyboard firmware for 47 Strix models plus the GU605 .415 dump from my laptop, 82 files, `itefix fix` picks from them automatically. **if itefix fixed your keyboard, send me your dump**: `itefix info` it, zip it, open an issue with the "share a dump" template and attach the zip. the next person with your model won't have to wait for ASUS.

## laptops with the same 048D:89DB symptom

| model | source | what helped |
|---|---|---|
| ROG Zephyrus G16 GU605MI | this repo | rewrote app A from own dump |
| ROG Zephyrus M16 GU603ZW | Reddit, u/franz13ade | kept own bootloader, app from GZ301 firmware |
| ROG Strix G16 G614PP | fosfuchs/kbfw | reflashed official G614PP firmware from Linux |
| ROG Strix G16 G614PR | ROG forum | official tool doesn't support it |
| ROG Flow Z13 GZ302EA | bazzite issue | official ROG Keyboard Firmware Update tool |
| ROG GL703VD | GitHub + iFixit guide | official tool with GL703GE firmware renamed |
| ROG GL502VMK | kbfw issue | kbfw with an extra erase step |

if yours is not here, open an issue, I'll add it.

## links that helped me

- [fosfuchs/kbfw](https://github.com/fosfuchs/kbfw): Linux flasher for these ITE keyboard chips, the protocol came from here
- [kbfw issue #1](https://github.com/fosfuchs/kbfw/issues/1): GL502VMK, erase before write
- [Reddit, r/ZephyrusM16: GU603ZW keyboard stuck in ITE Upgrade Mode, fixed by cross-flashing the keyboard MCU](https://www.reddit.com/r/ZephyrusM16/comments/1wkctzb/fixed_asus_rog_zephyrus_m16_gu603zw_internal/)
- [cmckenzie236-dot/GL703VD-keyboard-recovery](https://github.com/cmckenzie236-dot/GL703VD-keyboard-recovery) and the [iFixit guide](https://www.ifixit.com/Guide/ASUS+ROG+GL703VD+Dead+Keyboard+&+RGB+Firmware+Recovery/229696)
- [ublue-os/bazzite #4939](https://github.com/ublue-os/bazzite/issues/4939): Flow Z13 GZ302EA stuck in ITE bootloader mode
- [ROG forum: Strix G16 G614PR keyboard stopped working after BIOS 316](https://rog-forum.asus.com/t5/gaming-notebooks/rog-strix-g16-g614pr-built-in-keyboard-stopped-working-after/td-p/1153955)
- [linux-hardware.org: 048d:89db ITE Upgrade Mode](https://linux-hardware.org/?id=usb:048d-89db)

## license

MIT for the code, see [LICENSE](LICENSE). the files in firmware/ are ASUS firmware (official packages and dumps read out of the laptops' own chips), shared only so people can repair their own hardware.
