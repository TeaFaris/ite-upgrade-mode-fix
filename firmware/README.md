# keyboard controller firmware dumps

clean dumps of the keyboard controller, one per model and firmware version. use them when your own dump is already broken (app A checksum BAD in `itefix info`).

[по-русски ниже](#по-русски)

| model | file | firmware | chip | app A | app B | sha256 |
|---|---|---|---|---|---|---|
| ROG Zephyrus G16 GU605MI (2024) | [GU605/FGA00000.GU605.415.bin](GU605/FGA00000.GU605.415.bin) | FGA00000.GU605 .415 | ITE8252 | OK | OK | `899e35fea3dc0d56f41008e36af91cac68aff3ac2a76a2662cbd5ff93c1aa7bc` |

## GU605 .415

dumped from my own GU605MI on 2026-11-07 in ISP mode, two passes, identical. the raw dump had two leaked bits in app B, I fixed them here (`0x36C60` 20 -> 00, `0x2962A` 3E -> 2E, both found by comparing B with A), now both copies pass the checksum. app A is untouched, it's exactly what fixed my keyboard.

how to use it:

```
curl -fsSLO https://github.com/TeaFaris/ite-upgrade-mode-fix/raw/main/firmware/GU605/FGA00000.GU605.415.bin
itefix info FGA00000.GU605.415.bin
sudo itefix refresh --ref FGA00000.GU605.415.bin
```

`refresh` works if your chip runs the same .415 build (it only accepts leaked bits). if itefix says the sectors differ in a way that is not a leak, your chip has another firmware version. then `sudo itefix flash FGA00000.GU605.415.bin` writes .415 over it. itefix still checks that your bootloader and ISP block are byte for byte the same as in this file, otherwise it refuses.

## send me yours

if itefix fixed your keyboard, or your dump shows app A checksum OK, please share it so the next person with your laptop doesn't have to wait for ASUS:

1. `itefix info yourdump.bin`, both apps OK is perfect, A OK is fine too
2. zip it (GitHub doesn't take .bin attachments)
3. open an issue with the "share a dump" template, attach the zip

I'll check it and add it here.

## по-русски

чистые дампы контроллера клавы, по одному на модель и версию прошивки. нужны если твой собственный дамп уже битый (в `itefix info` у app A checksum BAD).

GU605 .415 я сдампил со своего GU605MI 7 ноября 2026 в режиме обновления, два прохода, одинаковые. в сыром дампе в копии B было два утёкших бита, тут я их исправил (`0x36C60` 20 -> 00, `0x2962A` 3E -> 2E, нашёл сравнением B с A), теперь обе копии проходят проверку. копия A не тронута, это ровно то, что починило мою клаву.

как использовать: команды выше. `refresh` работает если у тебя та же версия .415. если itefix скажет что разница не похожа на утечку, значит у тебя другая версия, тогда `sudo itefix flash FGA00000.GU605.415.bin`. загрузчик и блок обновления itefix всё равно сверяет, если не совпадают, писать не будет.

**скинь свой.** если itefix починил тебе клаву или в твоём дампе app A checksum OK, поделись, чтобы следующий человек с таким же ноутом не ждал асус: проверь `itefix info`, запакуй в zip (.bin гитхаб не принимает), открой issue по шаблону "share a dump" и прикрепи. проверю и добавлю сюда.
