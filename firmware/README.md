# keyboard controller firmware

[по-русски ниже](#по-русски)

two kinds of files here:

- **`asus/`**: official ASUS keyboard firmware, taken unchanged out of the ASUS "ROG Keyboard Firmware Update" packages (ROGNkeyFWupdate V3.8.3.007 and V4.8.3.003, ASUS support pages, Firmware section). 47 Strix models. the official updater only runs on Windows, with these files itefix can do the same from Linux
- **everything else**: dumps from real laptops, for models where ASUS doesn't publish the keyboard firmware (my GU605)

you don't have to pick anything by hand. `sudo itefix fix` (Windows: `itefix fix`) reads your chip, and only if your own firmware is broken it downloads a file from here: same model, and the bootloader of the file has to match the bootloader on your chip byte for byte, newest version first. ASUS changed the bootloader between some versions (the 2025 Strix .214 and .317 have different ones), that's why older versions are kept too.

<!-- index:start -->
| model | firmware | file | source | app A | app B |
|---|---|---|---|---|---|
| G614FM | .214 | [FGA00000.G614FM.214](asus/G614FM/FGA00000.G614FM.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G614FM | .317 | [FGA00000.G614FM.317](asus/G614FM/FGA00000.G614FM.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G614FP | .214 | [FGA00000.G614FP.214](asus/G614FP/FGA00000.G614FP.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G614FP | .317 | [FGA00000.G614FP.317](asus/G614FP/FGA00000.G614FP.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G614FR | .214 | [FGA00000.G614FR.214](asus/G614FR/FGA00000.G614FR.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G614FR | .317 | [FGA00000.G614FR.317](asus/G614FR/FGA00000.G614FR.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G614JI | .206 | [FGA00000.G614JI.206](asus/G614JI/FGA00000.G614JI.206) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G614JI | .315 | [FGA00000.G614JI.315](asus/G614JI/FGA00000.G614JI.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G614JJ | .206 | [FGA00000.G614JJ.206](asus/G614JJ/FGA00000.G614JJ.206) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G614JU | .206 | [FGA00000.G614JU.206](asus/G614JU/FGA00000.G614JU.206) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G614JU | .315 | [FGA00000.G614JU.315](asus/G614JU/FGA00000.G614JU.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G614JV | .206 | [FGA00000.G614JV.206](asus/G614JV/FGA00000.G614JV.206) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G614JV | .315 | [FGA00000.G614JV.315](asus/G614JV/FGA00000.G614JV.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G614JZ | .206 | [FGA00000.G614JZ.206](asus/G614JZ/FGA00000.G614JZ.206) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G614JZ | .315 | [FGA00000.G614JZ.315](asus/G614JZ/FGA00000.G614JZ.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G614PM | .214 | [FGA00000.G614PM.214](asus/G614PM/FGA00000.G614PM.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G614PM | .317 | [FGA00000.G614PM.317](asus/G614PM/FGA00000.G614PM.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G614PP | .214 | [FGA00000.G614PP.214](asus/G614PP/FGA00000.G614PP.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G614PP | .317 | [FGA00000.G614PP.317](asus/G614PP/FGA00000.G614PP.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G614PR | .214 | [FGA00000.G614PR.214](asus/G614PR/FGA00000.G614PR.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G614PR | .317 | [FGA00000.G614PR.317](asus/G614PR/FGA00000.G614PR.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615JM | .214 | [FGA00000.G615JM.214](asus/G615JM/FGA00000.G615JM.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615JM | .317 | [FGA00000.G615JM.317](asus/G615JM/FGA00000.G615JM.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615JMR | .214 | [FGA00000.G615JMR.214](asus/G615JMR/FGA00000.G615JMR.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615JMR | .317 | [FGA00000.G615JMR.317](asus/G615JMR/FGA00000.G615JMR.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615JPR | .214 | [FGA00000.G615JPR.214](asus/G615JPR/FGA00000.G615JPR.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615JPR | .317 | [FGA00000.G615JPR.317](asus/G615JPR/FGA00000.G615JPR.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615LM | .214 | [FGA00000.G615LM.214](asus/G615LM/FGA00000.G615LM.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615LM | .317 | [FGA00000.G615LM.317](asus/G615LM/FGA00000.G615LM.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615LP | .214 | [FGA00000.G615LP.214](asus/G615LP/FGA00000.G615LP.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615LP | .317 | [FGA00000.G615LP.317](asus/G615LP/FGA00000.G615LP.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615LR | .214 | [FGA00000.G615LR.214](asus/G615LR/FGA00000.G615LR.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615LR | .317 | [FGA00000.G615LR.317](asus/G615LR/FGA00000.G615LR.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615LW | .214 | [FGA00000.G615LW.214](asus/G615LW/FGA00000.G615LW.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G615LW | .317 | [FGA00000.G615LW.317](asus/G615LW/FGA00000.G615LW.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G634JY | .315 | [FGA00000.G634JY.315](asus/G634JY/FGA00000.G634JY.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G634JZ | .315 | [FGA00000.G634JZ.315](asus/G634JZ/FGA00000.G634JZ.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G635LR | .317 | [FGA00000.G635LR.317](asus/G635LR/FGA00000.G635LR.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G635LW | .317 | [FGA00000.G635LW.317](asus/G635LW/FGA00000.G635LW.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G635LX | .317 | [FGA00000.G635LX.317](asus/G635LX/FGA00000.G635LX.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G713PI | .206 | [FGA00000.G713PI.206](asus/G713PI/FGA00000.G713PI.206) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G713PI | .315 | [FGA00000.G713PI.315](asus/G713PI/FGA00000.G713PI.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G713PU | .206 | [FGA00000.G713PU.206](asus/G713PU/FGA00000.G713PU.206) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G713PU | .315 | [FGA00000.G713PU.315](asus/G713PU/FGA00000.G713PU.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G713PV | .206 | [FGA00000.G713PV.206](asus/G713PV/FGA00000.G713PV.206) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G713PV | .315 | [FGA00000.G713PV.315](asus/G713PV/FGA00000.G713PV.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G733PY | .315 | [FGA00000.G733PY.315](asus/G733PY/FGA00000.G733PY.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G733PZ | .315 | [FGA00000.G733PZ.315](asus/G733PZ/FGA00000.G733PZ.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G814FM | .214 | [FGA00000.G814FM.214](asus/G814FM/FGA00000.G814FM.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G814FM | .317 | [FGA00000.G814FM.317](asus/G814FM/FGA00000.G814FM.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G814FP | .214 | [FGA00000.G814FP.214](asus/G814FP/FGA00000.G814FP.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G814FP | .317 | [FGA00000.G814FP.317](asus/G814FP/FGA00000.G814FP.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G814JI | .206 | [FGA00000.G814JI.206](asus/G814JI/FGA00000.G814JI.206) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G814JI | .315 | [FGA00000.G814JI.315](asus/G814JI/FGA00000.G814JI.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G814JU | .206 | [FGA00000.G814JU.206](asus/G814JU/FGA00000.G814JU.206) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G814JU | .315 | [FGA00000.G814JU.315](asus/G814JU/FGA00000.G814JU.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G814JV | .206 | [FGA00000.G814JV.206](asus/G814JV/FGA00000.G814JV.206) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G814JV | .315 | [FGA00000.G814JV.315](asus/G814JV/FGA00000.G814JV.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G814JZ | .206 | [FGA00000.G814JZ.206](asus/G814JZ/FGA00000.G814JZ.206) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G814JZ | .315 | [FGA00000.G814JZ.315](asus/G814JZ/FGA00000.G814JZ.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G814PM | .214 | [FGA00000.G814PM.214](asus/G814PM/FGA00000.G814PM.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G814PM | .317 | [FGA00000.G814PM.317](asus/G814PM/FGA00000.G814PM.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G814PP | .214 | [FGA00000.G814PP.214](asus/G814PP/FGA00000.G814PP.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G814PP | .317 | [FGA00000.G814PP.317](asus/G814PP/FGA00000.G814PP.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G815JMR | .214 | [FGA00000.G815JMR.214](asus/G815JMR/FGA00000.G815JMR.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G815JMR | .317 | [FGA00000.G815JMR.317](asus/G815JMR/FGA00000.G815JMR.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G815JPR | .214 | [FGA00000.G815JPR.214](asus/G815JPR/FGA00000.G815JPR.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G815JPR | .317 | [FGA00000.G815JPR.317](asus/G815JPR/FGA00000.G815JPR.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G815LM | .214 | [FGA00000.G815LM.214](asus/G815LM/FGA00000.G815LM.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G815LM | .317 | [FGA00000.G815LM.317](asus/G815LM/FGA00000.G815LM.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G815LP | .214 | [FGA00000.G815LP.214](asus/G815LP/FGA00000.G815LP.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G815LP | .317 | [FGA00000.G815LP.317](asus/G815LP/FGA00000.G815LP.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G815LR | .214 | [FGA00000.G815LR.214](asus/G815LR/FGA00000.G815LR.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G815LR | .317 | [FGA00000.G815LR.317](asus/G815LR/FGA00000.G815LR.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G815LW | .214 | [FGA00000.G815LW.214](asus/G815LW/FGA00000.G815LW.214) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G815LW | .317 | [FGA00000.G815LW.317](asus/G815LW/FGA00000.G815LW.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G834JY | .315 | [FGA00000.G834JY.315](asus/G834JY/FGA00000.G834JY.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G834JZ | .315 | [FGA00000.G834JZ.315](asus/G834JZ/FGA00000.G834JZ.315) | ASUS ROGNkeyFWupdate V3.8.3.007 | OK | OK |
| G835LR | .317 | [FGA00000.G835LR.317](asus/G835LR/FGA00000.G835LR.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G835LW | .317 | [FGA00000.G835LW.317](asus/G835LW/FGA00000.G835LW.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| G835LX | .317 | [FGA00000.G835LX.317](asus/G835LX/FGA00000.G835LX.317) | ASUS ROGNkeyFWupdate V4.8.3.003 | OK | OK |
| GU605 | .415 | [FGA00000.GU605.415.bin](GU605/FGA00000.GU605.415.bin) | dump from a real laptop | OK | BAD |
<!-- index:end -->

## GU605 .415

dumped from my own GU605MI on 2026-11-07 in ISP mode, two passes, identical. app A is exactly what fixed my keyboard.

app B is left as it was in the dump: two leaked bits, bad checksum. I could guess which bits (one of them for sure), but a checksum match doesn't prove the guess, and a wrong B that still passes the checksum is worse than a broken one. with B broken the bootloader can only ever run A, and if A dies the chip goes back to 048D:89DB where you can flash it again. so only app A from this file is used, itefix refuses to write a slot whose checksum is bad.

## by hand

```
curl -fsSLO https://github.com/TeaFaris/ite-upgrade-mode-fix/raw/main/firmware/asus/G614JI/FGA00000.G614JI.315
itefix info FGA00000.G614JI.315
sudo itefix flash FGA00000.G614JI.315
```

`flash` refuses if the bootloader in the file is not the one on your chip, try the other version of your model then. `refresh --ref` instead of `flash` if the file has the same version as your chip.

## send me yours

if itefix fixed your keyboard, or your dump shows app A checksum OK, and your model is not here yet: `itefix info` it, zip it (GitHub doesn't take .bin attachments), open an issue with the "share a dump" template, attach the zip. I'll add it, `python3 tools/make_index.py` rebuilds the list.

## по-русски

тут два вида файлов:

- **`asus/`**: официальные прошивки клавы от асуса, вытащенные без изменений из асусовских пакетов "ROG Keyboard Firmware Update" (ROGNkeyFWupdate V3.8.3.007 и V4.8.3.003, сайт поддержки асус, раздел Firmware). 47 моделей Strix. асусовская утилита работает только на винде, с этими файлами itefix делает то же самое из линукса
- **остальное**: дампы с живых ноутов, для моделей где асус прошивку клавы не выкладывает (мой GU605)

выбирать руками ничего не надо. `sudo itefix fix` (на винде `itefix fix`) читает твой чип и только если твоя прошивка битая, качает файл отсюда: та же модель, и загрузчик в файле должен побайтно совпасть с загрузчиком в чипе, сначала самая новая версия. асус между некоторыми версиями менял загрузчик (у Strix 2025 года .214 и .317 разные), поэтому старые версии тоже лежат.

**GU605 .415** я сдампил со своего GU605MI 7 ноября 2026 в режиме обновления, два прохода, одинаковые. копия A это ровно то, что починило мою клаву. копию B я оставил как была в дампе: два утёкших бита, контрольная сумма не сходится. какие биты утекли можно угадать (один точно), но сошедшаяся сумма догадку не доказывает, а неправильная B с правильной суммой хуже битой. пока B битая, загрузчик может запустить только A, а если A умрёт, чип вернётся в 048D:89DB и его можно перешить. поэтому из этого файла используется только A.

**руками:** команды выше. `flash` откажется если загрузчик в файле не такой как в чипе, тогда бери другую версию своей модели. если версия та же что в чипе, вместо `flash` можно `refresh --ref`.

**скинь свой.** если itefix починил тебе клаву или в твоём дампе app A checksum OK, а твоей модели тут ещё нет: проверь `itefix info`, запакуй в zip (.bin гитхаб не принимает), открой issue по шаблону "share a dump" и прикрепи. добавлю, `python3 tools/make_index.py` пересобирает список.
