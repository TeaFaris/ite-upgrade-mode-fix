# simple guide: ASUS ROG laptop keyboard died

for people who aren't into computers. step by step, about 15 minutes. if something is unclear, ask in [issues](https://github.com/TeaFaris/ite-upgrade-mode-fix/issues/new/choose), I'll help.

[по-русски](GUIDE.ru.md) | [detailed version](README.md)

## what you need

- any USB keyboard, plug it into the laptop (the built-in one doesn't work, right)
- the charger, keep the laptop plugged in the whole time
- internet

## step 1. install the program

**Windows:**

1. right click the **Start** button (the Windows logo at the bottom)
2. pick **Terminal** (on older Windows it's called **Windows PowerShell**)
3. a window with text opens. copy this line:
   ```
   irm https://raw.githubusercontent.com/TeaFaris/ite-upgrade-mode-fix/main/install.ps1 | iex
   ```
4. right click inside the terminal window, the line gets pasted. press **Enter**
5. if it asks about installing Python, say yes and wait. at the end it says `installed`
6. close the window and open the terminal again (like in 1 and 2)

**Linux:** open a terminal and paste
```
curl -fsSL https://raw.githubusercontent.com/TeaFaris/ite-upgrade-mode-fix/main/install.sh | sudo sh
```

## step 2. check it's this exact problem

type this and press Enter:
```
itefix status
```
on Linux: `sudo itefix status`

- it says **`stuck in ITE Upgrade Mode`**: that's it, go on
- it says **`runs normally`**: the keyboard controller is alive, so the problem is somewhere else (the keyboard itself, the cable). this program won't help, better go to a repair shop
- it says **`no ASUS N-KEY or ITE Upgrade Mode device found`**: also not this case

## step 3. fix it

type this and press Enter:
```
itefix fix
```
on Linux: `sudo itefix fix`

the program will:
1. read the keyboard chip and save a copy into your user folder (file `itefix-backup-...bin`)
2. decide what to write: your own firmware if it's still fine, or a clean one from this project if there is one for your model
3. ask for permission. type **`YES`** in capitals and press Enter

while it writes (less than a minute): **don't close the lid, don't turn it off, don't pull the charger.**

## step 4. restart

when it says **`DONE`**: shut the laptop down completely (Start, Shut down, not Restart), wait 30 seconds, turn it on.

keyboard works? fixed. one more thing: don't delete `itefix-backup-...bin`, put it in the cloud or on your phone. and if you can, [share it here](https://github.com/TeaFaris/ite-upgrade-mode-fix/issues/new/choose) ("share a dump" template, zip the file first), it helps the next person with the same laptop.

## if it didn't work

- **`no clean dump for ... yet`**: there is no clean firmware for your model yet. nothing was written, nothing broke. open an [issue](https://github.com/TeaFaris/ite-upgrade-mode-fix/issues/new/choose) and paste all the text from the window
- **`layout itefix doesn't know`**: you have a different controller, the program doesn't know it and leaves it alone on purpose. paste the text into an issue too
- **any other error, or the keyboard still doesn't work**: paste all the text from the window into an issue

## can it break my laptop?

the program never touches the part of the chip that is responsible for flashing it. so even if something goes wrong the chip stays in the same mode and you can try again. I tested writing on my own laptop on Linux. on Windows it does the same thing but I tested it less, so if you have a Linux USB stick, that's the safer way.
