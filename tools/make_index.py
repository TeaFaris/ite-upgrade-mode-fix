#!/usr/bin/env python3
"""rebuild firmware/index.json and the table in firmware/README.md from the files in firmware/.
run it after adding a dump:  python3 tools/make_index.py"""
import hashlib
import importlib.util
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("itefix", os.path.join(ROOT, "itefix.py"))
itefix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(itefix)

FW = os.path.join(ROOT, "firmware")
PACKAGES = {"206": "ROGNkeyFWupdate V3.8.3.007", "315": "ROGNkeyFWupdate V3.8.3.007",
            "214": "ROGNkeyFWupdate V4.8.3.003", "317": "ROGNkeyFWupdate V4.8.3.003"}

entries = []
for dirpath, _, files in os.walk(FW):
    for name in sorted(files):
        if name.endswith((".md", ".json")):
            continue
        path = os.path.join(dirpath, name)
        rel = os.path.relpath(path, FW).replace(os.sep, "/")
        raw = open(path, "rb").read()
        img, kind = itefix.load_image(path)
        d = itefix.find_descriptor(img)
        model, version = itefix.chip_firmware(img)
        if not d or not model:
            print(f"skip {rel}: layout or name not recognized")
            continue
        official = raw[:len(itefix.FGA_HEADER)] == itefix.FGA_HEADER
        slots = ["OK" if itefix.slot_ok(img, s)[0] else "BAD" for s in d["slots"]]
        entries.append({
            "model": model, "version": version, "file": rel,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "boot_sha256": hashlib.sha256(img[:0x2000]).hexdigest(),
            "source": f"ASUS {PACKAGES.get(version, 'package')}" if official else "dump from a real laptop",
            "app_a": slots[0], "app_b": slots[1],
        })

entries.sort(key=lambda e: (e["model"], e["version"]))
with open(os.path.join(FW, "index.json"), "w") as f:
    json.dump(entries, f, indent=1)
    f.write("\n")

rows = ["| model | firmware | file | source | app A | app B |", "|---|---|---|---|---|---|"]
for e in entries:
    rows.append(f"| {e['model']} | .{e['version']} | [{e['file'].split('/')[-1]}]({e['file']}) | {e['source']} | {e['app_a']} | {e['app_b']} |")
table = "\n".join(rows)

readme = os.path.join(FW, "README.md")
text = open(readme).read()
start, end = "<!-- index:start -->", "<!-- index:end -->"
if start in text and end in text:
    text = text[:text.index(start) + len(start)] + "\n" + table + "\n" + text[text.index(end):]
    open(readme, "w").write(text)
print(f"{len(entries)} entries, {len({e['model'] for e in entries})} models")
