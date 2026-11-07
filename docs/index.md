---
title: ASUS ROG keyboard not working, stuck in ITE Upgrade Mode (048D:89DB) fix
description: Internal keyboard of an ASUS ROG laptop dead even in BIOS, device 048D:89DB "ITE Upgrade Mode" shows up, or it only wakes up after 10 minutes. Why it happens and a Linux / Windows tool to fix it. Не работает клавиатура ASUS ROG, ITE Upgrade Mode 048D:89DB.
---

# ASUS ROG keyboard stuck in ITE Upgrade Mode (048D:89DB)

the built-in keyboard of an ASUS ROG laptop (Zephyrus, Strix, Flow, older GL series) stops working everywhere, even in BIOS, and instead of `0B05:19B6 N-KEY Device` you see `048D:89DB ITE Upgrade Mode` (`HID\VID_048D&PID_89DB` in Windows Device Manager). sometimes it comes back by itself after about 10 minutes.

that's the keyboard controller sitting in its firmware update mode because its flash leaked a few bits and the firmware checksum fails. I fixed mine (ROG Zephyrus G16 GU605MI) by dumping the chip and writing the same firmware back.

- [the full story and the fix](https://github.com/TeaFaris/ite-upgrade-mode-fix#readme)
- [itefix, the tool for Linux and Windows](https://github.com/TeaFaris/ite-upgrade-mode-fix)
- [how the controller works, flash map, checksum, protocol](how-it-works.md)

---

# Не работает клавиатура ASUS ROG, висит ITE Upgrade Mode (048D:89DB)

встроенная клава ноута ASUS ROG не работает нигде, даже в биосе, а вместо `0B05:19B6 N-KEY Device` в системе висит `048D:89DB ITE Upgrade Mode`. иногда она оживает сама минут через 10.

это контроллер клавы застрял в режиме обновления прошивки: в его флешке утекло несколько бит и не сходится контрольная сумма. свою (ROG Zephyrus G16 GU605MI) я починил: сдампил чип и записал ту же прошивку обратно.

- [история и как починить](https://github.com/TeaFaris/ite-upgrade-mode-fix/blob/main/README.ru.md)
- [itefix, утилита под линукс и винду](https://github.com/TeaFaris/ite-upgrade-mode-fix)
