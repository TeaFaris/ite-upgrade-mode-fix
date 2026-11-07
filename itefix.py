#!/usr/bin/env python3
"""
itefix: dump, check and repair the ITE keyboard controller of ASUS ROG laptops
that got stuck in "ITE Upgrade Mode" (USB 048D:89DB, keyboard dead even in BIOS).

Works on Linux (hidraw) and Windows (hid.dll). No dependencies, just Python 3.8+.
The flash protocol is the one used by the official ASUS "ROG Keyboard Firmware Update"
tool (figured out by fosfuchs/kbfw). Read the README before writing anything.

It never erases or writes the bootloader (0x0000-0x1FFF) or the ISP block
(0x1E000-0x1FFFF). As long as those two are alive the controller always comes back
in 048D:89DB mode and can be flashed again.
"""
import argparse
import hashlib
import os
import struct
import sys
import time

VERSION = "0.1.0"

ITE_VID, ITE_PID = 0x048D, 0x89DB
ASUS_VID = 0x0B05
NKEY_PIDS = {0x19B6: "N-KEY Device", 0x1A30: "N-KEY Device (Flow Z13)", 0x1866: "N-KEY Device",
             0x1869: "N-KEY Device", 0x1854: "N-KEY Device", 0x1A0E: "N-KEY Device"}

CHIP_SIZE = 0x40000
SECTOR = 0x400
BLOCK = 56
ISP_BLOCK = (0x1E000, 0x20000)
FGA_HEADER = b"$INVENTEC"
MAX_LEAK_BITS = 8


# ----------------------------------------------------------------------------- output

def say(*a):
    print(*a, flush=True)


def die(msg, code=1):
    print("error: " + msg, file=sys.stderr, flush=True)
    sys.exit(code)


# ----------------------------------------------------------------------------- firmware image parsing

def load_image(path):
    """Accept a raw 256 KiB chip dump or an official ASUS FGA image ($INVENTEC header + chip data)."""
    data = open(path, "rb").read()
    if data[:len(FGA_HEADER)] == FGA_HEADER:
        chip = data[0x100:]
        kind = "ASUS FGA image"
    else:
        chip = data
        kind = "raw dump"
    if len(chip) > CHIP_SIZE:
        die(f"{path}: too big for a 256 KiB chip ({len(chip)} bytes)")
    chip = chip + b"\xff" * (CHIP_SIZE - len(chip))
    return chip, kind


def find_descriptor(img):
    """App slot table: 2 x [start, end, base] (LE u32), then u8 slot select, u8, u16 chip id.
    Seen at 0x3C030 (GU605 .415) and 0x3C400 (Strix G614 images)."""
    for off in range(0x3C000, 0x3D000, 2):
        s0, e0, b0, s1, e1, b1 = struct.unpack_from("<6I", img, off)
        if b0 == 0x2000 and s0 == b0 + 2 and b1 == 0x20000 and s1 == b1 + 2 \
                and 0x4000 < e0 < ISP_BLOCK[0] and 0x22000 < e1 < 0x3C000:
            chip_id = struct.unpack_from("<H", img, off + 0x1A)[0]
            return {"offset": off, "slots": [(s0, e0, b0), (s1, e1, b1)],
                    "select": img[off + 0x18], "chip_id": chip_id}
    return None


def slot_ok(img, slot):
    start, end, base = slot
    stored = (img[base] << 8) | img[base + 1]
    calc = (-sum(img[start:end + 1])) & 0xFFFF
    return stored == calc, stored, calc


def strings_at(img, prefix):
    out, i = [], img.find(prefix)
    while i != -1:
        j = i
        while j < len(img) and 32 <= img[j] < 127:
            j += 1
        out.append((i, img[i:j].decode()))
        i = img.find(prefix, j)
    return out


def slot_sectors(slot):
    start, end, base = slot
    return list(range(base, (end + 1 + SECTOR - 1) // SECTOR * SECTOR, SECTOR))


def describe(img, label=""):
    """Print what is inside an image. Returns the parsed descriptor (or None)."""
    say(f"== {label}")
    boot = strings_at(img[:0x2000], b"IT8")
    fw = strings_at(img, b"FGA")
    say("  bootloader : " + (boot[0][1] if boot else "not recognized"))
    names = sorted({n.strip() for _, n in fw if n.count(".") == 2})
    say("  firmware   : " + (", ".join(names) if names else "no FGA name found"))
    chips = sorted({n for _, n in strings_at(img, b"ITE82")})
    if chips:
        say("  chip       : " + ", ".join(chips))
    d = find_descriptor(img)
    if not d:
        say("  slot table : not found (unknown layout, itefix will not write to this chip)")
        return None
    say(f"  slot table : at {d['offset']:#x}, chip id {d['chip_id']:#06x}, boots slot {'AB'[d['select'] & 1]} first")
    for name, slot in zip("AB", d["slots"]):
        ok, stored, calc = slot_ok(img, slot)
        blank = img[slot[2]:slot[1] + 1] == b"\xff" * (slot[1] + 1 - slot[2])
        state = "blank" if blank else ("checksum OK" if ok else f"checksum BAD (stored {stored:#06x}, calc {calc:#06x})")
        say(f"  app {name}      : {slot[2]:#07x}-{slot[1]:#07x}  {state}")
    return d


def leak_class(cur, ref):
    """Compare one sector. None = equal, ('leak', bits, offsets) = only 0->1 flips, ('other', off) otherwise."""
    if cur == ref:
        return None
    bits, where = 0, []
    for i, (c, r) in enumerate(zip(cur, ref)):
        if c != r:
            if r & ~c & 0xFF:
                return ("other", i)
            bits += bin(c & ~r & 0xFF).count("1")
            where.append(i)
    return ("leak", bits, where)


# ----------------------------------------------------------------------------- HID transports

class LinuxHid:
    def __init__(self, path):
        self.path = path
        self.fd = os.open(path, os.O_RDWR)
        self.flen = self._probe()

    @staticmethod
    def _ioc(nr, size):
        return (3 << 30) | (size << 16) | (ord("H") << 8) | nr

    def _probe(self):
        import fcntl
        for n in (65, 64, 66, 33, 129, 256):
            try:
                fcntl.ioctl(self.fd, self._ioc(7, n), bytearray(n))
                return n
            except OSError:
                pass
        raise OSError("cannot get a feature report from the device")

    def set_feature(self, payload):
        import fcntl
        buf = bytearray(self.flen)
        buf[1:1 + len(payload)] = payload
        fcntl.ioctl(self.fd, self._ioc(6, self.flen), buf)

    def get_feature(self):
        import fcntl
        buf = bytearray(self.flen)
        fcntl.ioctl(self.fd, self._ioc(7, self.flen), buf)
        return bytes(buf[1:])

    def close(self):
        try:
            os.close(self.fd)
        except OSError:
            pass

    @staticmethod
    def enumerate():
        """yield (vid, pid, path, name)"""
        import glob
        for p in sorted(glob.glob("/sys/class/hidraw/hidraw*/device/uevent")):
            vid = pid = None
            name = ""
            for line in open(p):
                if line.startswith("HID_ID="):
                    _, v, d = line.strip().split("=")[1].split(":")
                    vid, pid = int(v, 16), int(d, 16)
                elif line.startswith("HID_NAME="):
                    name = line.strip().split("=", 1)[1]
            if vid is not None:
                yield vid, pid, "/dev/" + p.split("/")[4], name


class WindowsHid:
    def __init__(self, path):
        import ctypes
        self.w = _win()
        self.path = path
        h = self.w.k32.CreateFileW(path, 0xC0000000, 3, None, 3, 0, None)
        if h is None or h == ctypes.c_void_p(-1).value:
            raise OSError(f"cannot open device (error {ctypes.get_last_error()})")
        self.h = h
        caps = _win_caps(self.w, h)
        self.flen = caps.FeatureReportByteLength or 65

    def set_feature(self, payload):
        import ctypes
        buf = (ctypes.c_ubyte * self.flen)()
        for i, b in enumerate(payload[:self.flen - 1]):
            buf[1 + i] = b
        if not self.w.hid.HidD_SetFeature(self.h, buf, self.flen):
            raise OSError(f"HidD_SetFeature failed ({ctypes.get_last_error()})")

    def get_feature(self):
        import ctypes
        buf = (ctypes.c_ubyte * self.flen)()
        if not self.w.hid.HidD_GetFeature(self.h, buf, self.flen):
            raise OSError(f"HidD_GetFeature failed ({ctypes.get_last_error()})")
        return bytes(buf[1:])

    def close(self):
        try:
            self.w.k32.CloseHandle(self.h)
        except Exception:
            pass

    @staticmethod
    def enumerate():
        import ctypes
        w = _win()
        guid = w.GUID()
        w.hid.HidD_GetHidGuid(ctypes.byref(guid))
        hdev = w.sa.SetupDiGetClassDevsW(ctypes.byref(guid), None, None, 0x12)
        if not hdev or hdev == ctypes.c_void_p(-1).value:
            return
        try:
            i = 0
            while True:
                ifd = w.SP_DEVICE_INTERFACE_DATA()
                ifd.cbSize = ctypes.sizeof(ifd)
                if not w.sa.SetupDiEnumDeviceInterfaces(hdev, None, ctypes.byref(guid), i, ctypes.byref(ifd)):
                    break
                i += 1
                need = ctypes.c_ulong(0)
                w.sa.SetupDiGetDeviceInterfaceDetailW(hdev, ctypes.byref(ifd), None, 0, ctypes.byref(need), None)
                if not need.value:
                    continue
                buf = ctypes.create_string_buffer(need.value)
                ctypes.c_ulong.from_buffer(buf).value = 8 if ctypes.sizeof(ctypes.c_void_p) == 8 else 6
                if not w.sa.SetupDiGetDeviceInterfaceDetailW(hdev, ctypes.byref(ifd), buf, need, None, None):
                    continue
                path = ctypes.wstring_at(ctypes.addressof(buf) + 4)
                h = w.k32.CreateFileW(path, 0, 3, None, 3, 0, None)
                if h is None or h == ctypes.c_void_p(-1).value:
                    continue
                try:
                    attr = w.HIDD_ATTRIBUTES()
                    attr.Size = ctypes.sizeof(attr)
                    if not w.hid.HidD_GetAttributes(h, ctypes.byref(attr)):
                        continue
                    name = ctypes.create_unicode_buffer(128)
                    w.hid.HidD_GetProductString(h, name, ctypes.sizeof(name))
                    try:
                        flen = _win_caps(w, h).FeatureReportByteLength
                    except OSError:
                        flen = 0
                    yield attr.VendorID, attr.ProductID, path, name.value + ("" if flen else " (no feature reports)")
                finally:
                    w.k32.CloseHandle(h)
        finally:
            w.sa.SetupDiDestroyDeviceInfoList(hdev)


_WIN = None


def _win():
    global _WIN
    if _WIN:
        return _WIN
    import ctypes
    from ctypes import wintypes

    class GUID(ctypes.Structure):
        _fields_ = [("Data1", ctypes.c_ulong), ("Data2", ctypes.c_ushort),
                    ("Data3", ctypes.c_ushort), ("Data4", ctypes.c_ubyte * 8)]

    class SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD), ("InterfaceClassGuid", GUID),
                    ("Flags", wintypes.DWORD), ("Reserved", ctypes.c_size_t)]

    class HIDD_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("Size", wintypes.ULONG), ("VendorID", wintypes.USHORT),
                    ("ProductID", wintypes.USHORT), ("VersionNumber", wintypes.USHORT)]

    class HIDP_CAPS(ctypes.Structure):
        _fields_ = [("Usage", wintypes.USHORT), ("UsagePage", wintypes.USHORT),
                    ("InputReportByteLength", wintypes.USHORT), ("OutputReportByteLength", wintypes.USHORT),
                    ("FeatureReportByteLength", wintypes.USHORT), ("Reserved", wintypes.USHORT * 17),
                    ("NumberLinkCollectionNodes", wintypes.USHORT),
                    ("NumberInputButtonCaps", wintypes.USHORT), ("NumberInputValueCaps", wintypes.USHORT),
                    ("NumberInputDataIndices", wintypes.USHORT), ("NumberOutputButtonCaps", wintypes.USHORT),
                    ("NumberOutputValueCaps", wintypes.USHORT), ("NumberOutputDataIndices", wintypes.USHORT),
                    ("NumberFeatureButtonCaps", wintypes.USHORT), ("NumberFeatureValueCaps", wintypes.USHORT),
                    ("NumberFeatureDataIndices", wintypes.USHORT)]

    class W:
        pass

    w = W()
    w.GUID, w.SP_DEVICE_INTERFACE_DATA, w.HIDD_ATTRIBUTES, w.HIDP_CAPS = \
        GUID, SP_DEVICE_INTERFACE_DATA, HIDD_ATTRIBUTES, HIDP_CAPS
    w.k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    w.sa = ctypes.WinDLL("setupapi", use_last_error=True)
    w.hid = ctypes.WinDLL("hid", use_last_error=True)
    H = ctypes.c_void_p
    w.k32.CreateFileW.restype = H
    w.k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                                  wintypes.DWORD, wintypes.DWORD, H]
    w.k32.CloseHandle.argtypes = [H]
    w.sa.SetupDiGetClassDevsW.restype = H
    w.sa.SetupDiGetClassDevsW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR, wintypes.HWND, wintypes.DWORD]
    w.sa.SetupDiEnumDeviceInterfaces.argtypes = [H, ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.c_void_p]
    w.sa.SetupDiGetDeviceInterfaceDetailW.argtypes = [H, ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD,
                                                      ctypes.c_void_p, ctypes.c_void_p]
    w.sa.SetupDiDestroyDeviceInfoList.argtypes = [H]
    w.hid.HidD_GetHidGuid.argtypes = [ctypes.c_void_p]
    w.hid.HidD_GetAttributes.argtypes = [H, ctypes.c_void_p]
    w.hid.HidD_GetProductString.argtypes = [H, ctypes.c_void_p, wintypes.ULONG]
    w.hid.HidD_GetPreparsedData.argtypes = [H, ctypes.POINTER(ctypes.c_void_p)]
    w.hid.HidD_FreePreparsedData.argtypes = [ctypes.c_void_p]
    w.hid.HidP_GetCaps.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    w.hid.HidP_GetCaps.restype = ctypes.c_long
    w.hid.HidD_SetFeature.argtypes = [H, ctypes.c_void_p, wintypes.ULONG]
    w.hid.HidD_GetFeature.argtypes = [H, ctypes.c_void_p, wintypes.ULONG]
    _WIN = w
    return w


def _win_caps(w, h):
    import ctypes
    pp = ctypes.c_void_p()
    if not w.hid.HidD_GetPreparsedData(h, ctypes.byref(pp)):
        raise OSError("HidD_GetPreparsedData failed")
    try:
        caps = w.HIDP_CAPS()
        if w.hid.HidP_GetCaps(pp, ctypes.byref(caps)) != 0x00110000:
            raise OSError("HidP_GetCaps failed")
        return caps
    finally:
        w.hid.HidD_FreePreparsedData(pp)


def backend():
    if sys.platform.startswith("linux"):
        return LinuxHid
    if sys.platform == "win32":
        return WindowsHid
    die("only Linux and Windows are supported")


def find_devices():
    found = []
    try:
        for vid, pid, path, name in backend().enumerate():
            if (vid, pid) == (ITE_VID, ITE_PID) or (vid == ASUS_VID and pid in NKEY_PIDS):
                found.append((vid, pid, path, name))
    except PermissionError:
        pass
    return found


def isp_path():
    for vid, pid, path, name in find_devices():
        if (vid, pid) == (ITE_VID, ITE_PID) and "no feature" not in name:
            return path
    return None


# ----------------------------------------------------------------------------- ISP protocol

class Chip:
    """Talks to the ITE ISP block (048D:89DB) with the ASUS updater protocol:
       D1 read 56 bytes, C2 erase one 1 KiB sector, C1/D0 fill the staging buffer
       (D0 replies with its 16 bit sum), C3+C0 program the staged sector."""

    def __init__(self, transport=None, writable=None):
        self.dev = transport or self._open()
        self.writable = writable or set()

    @staticmethod
    def _open(wait=30):
        t = time.time()
        while True:
            p = isp_path()
            if p:
                try:
                    return backend()(p)
                except PermissionError:
                    die("no permission to open the device. Run as root (Linux: sudo itefix ...).")
                except OSError:
                    pass
            if time.time() - t > wait:
                die("keyboard controller is not in ITE Upgrade Mode (048D:89DB), see 'itefix status'")
            time.sleep(0.5)

    def reopen(self):
        try:
            self.dev.close()
        except Exception:
            pass
        say("  device dropped off (the ISP block restarts itself every few minutes), waiting for it ...")
        self.dev = self._open(wait=120)

    def read_block(self, addr, n=BLOCK):
        for _ in range(3):
            try:
                self.dev.set_feature(bytes([0xD1, addr & 0xFF, (addr >> 8) & 0xFF, (addr >> 16) & 0xFF, n]))
                time.sleep(0.004)
                r = self.dev.get_feature()
            except OSError:
                time.sleep(0.05)
                continue
            if r[0] == 0xD1 and r[1:4] == bytes([addr & 0xFF, (addr >> 8) & 0xFF, (addr >> 16) & 0xFF]):
                return r[5:5 + n]
            time.sleep(0.05)
        raise IOError(f"read failed at {addr:#x}")

    def read_range(self, lo, hi):
        out = bytearray()
        a = lo
        while a < hi:
            try:
                out += self.read_block(a)
            except IOError:
                self.reopen()
                out += self.read_block(a)
            a += BLOCK
        return bytes(out[:hi - lo])

    def read_sector(self, s):
        return self.read_range(s, s + SECTOR)

    @staticmethod
    def _chunk(op, off, data):
        return bytes([op, off & 0xFF, off >> 8, len(data)]) + data

    def _guard(self, s):
        if s % SECTOR or s not in self.writable or s < 0x2000 or ISP_BLOCK[0] <= s < ISP_BLOCK[1]:
            raise SystemExit(f"refusing to touch sector {s:#x}")

    def _erase(self, s):
        self._guard(s)
        self.dev.set_feature(bytes([0xC2, s & 0xFF, (s >> 8) & 0xFF, (s >> 16) & 0xFF, 0x01, 0x00]))
        time.sleep(0.03)
        for _ in range(40):
            try:
                if self.read_sector(s) == b"\xff" * SECTOR:
                    return True
            except IOError:
                pass
            time.sleep(0.04)
        return False

    def _stage(self, d):
        for i in range(18):
            off, n = i * 57, (57 if i < 17 else 55)
            self.dev.set_feature(self._chunk(0xC1, off, d[off:off + n]))
            time.sleep(0.005)
        self.dev.set_feature(self._chunk(0xD0, 0x2AC, d[0x2AC:0x2AC + 57]))
        time.sleep(0.008)
        r = self.dev.get_feature()
        return r[1] | (r[2] << 8)

    def _program(self, s, d):
        self._guard(s)
        self.dev.set_feature(bytes([0xC3, s & 0xFF, (s >> 8) & 0xFF, (s >> 16) & 0xFF, 0x00, 0x04]))
        time.sleep(0.005)
        self.dev.set_feature(self._chunk(0xC0, 0x72, d[0x72:0x72 + 57]))
        time.sleep(0.008)
        self.dev.get_feature()

    def write_sector(self, s, d):
        self._guard(s)
        for attempt in range(1, 5):
            try:
                if not self._erase(s):
                    say(f"  {s:#07x}: erase not confirmed (try {attempt})")
                    continue
                if self._stage(d) != (sum(d) & 0xFFFF):
                    say(f"  {s:#07x}: staging checksum mismatch (try {attempt})")
                    continue
                self._program(s, d)
                time.sleep(0.05)
                if self.read_sector(s) == d:
                    return True
                say(f"  {s:#07x}: read-back mismatch (try {attempt})")
            except (OSError, IOError):
                self.reopen()
        return False


# ----------------------------------------------------------------------------- commands

def model_name():
    try:
        if sys.platform.startswith("linux"):
            return open("/sys/class/dmi/id/product_name").read().strip()
        if sys.platform == "win32":
            import winreg
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\BIOS")
            return winreg.QueryValueEx(k, "SystemProductName")[0]
    except Exception:
        pass
    return "unknown"


def cmd_status(a):
    say(f"itefix {VERSION}, laptop: {model_name()}")
    devs = find_devices()
    isp = [d for d in devs if (d[0], d[1]) == (ITE_VID, ITE_PID)]
    nkey = [d for d in devs if d[0] == ASUS_VID]
    for vid, pid, path, name in devs:
        say(f"  {vid:04x}:{pid:04x}  {path}  {name}")
    if nkey and not isp:
        say("keyboard controller runs normally. Nothing to fix.")
        return 0
    if isp:
        say("keyboard controller is stuck in ITE Upgrade Mode (048D:89DB).")
        say("next step: 'itefix dump' (read only), then 'itefix info <dump>'.")
        return 3
    if sys.platform.startswith("linux") and os.geteuid() != 0:
        say("nothing found. Try again with sudo.")
    else:
        say("no ASUS N-KEY or ITE Upgrade Mode device found.")
    return 1


def cmd_dump(a):
    chip = Chip()
    passes = []
    for p in range(1, a.passes + 1):
        t = time.time()
        img = chip.read_range(0, CHIP_SIZE)
        passes.append(img)
        say(f"  pass {p}: {time.time() - t:.0f}s sha256 {hashlib.sha256(img).hexdigest()[:16]}...")
    stable = all(x == passes[0] for x in passes)
    out = a.output or time.strftime("kbd-dump-%Y%m%d-%H%M%S.bin")
    with open(out, "wb") as f:
        f.write(passes[0])
    say(f"saved {out}  sha256 {hashlib.sha256(passes[0]).hexdigest()}")
    if not stable:
        say("WARNING: passes differ. Some cells read unstable. Run dump again, compare, keep the copy with valid checksums.")
    describe(passes[0], out)
    say("keep this file somewhere safe (cloud, phone). It is your clean copy for 'itefix refresh'.")
    return 0 if stable else 2


def cmd_info(a):
    img, kind = load_image(a.file)
    describe(img, f"{a.file} ({kind}, sha256 {hashlib.sha256(img).hexdigest()[:16]}...)")
    return 0


def _plan(chip, ref, d, slots, allow_changes):
    """Compare chip with reference. Returns sectors to write or exits on anything unsafe."""
    say("== comparing chip with reference (read only)")
    boot = chip.read_range(0, 0x2000)
    isp = chip.read_range(*ISP_BLOCK)
    bad_protected = []
    for lo, data in ((0, boot), (ISP_BLOCK[0], isp)):
        for off in range(0, len(data), SECTOR):
            c = leak_class(data[off:off + SECTOR], ref[lo + off:lo + off + SECTOR])
            if c:
                bad_protected.append((lo + off, c))
    if any(c[0] == "other" for _, c in bad_protected):
        die("bootloader / ISP block on the chip is different from the reference. Wrong reference "
            "(other model or other firmware build). Nothing written.", 4)
    for s, c in bad_protected:
        say(f"  WARNING: {c[1]} leaked bit(s) in protected sector {s:#x}. itefix will not touch it.")

    sectors, report = [], []
    for name in slots:
        slot = d["slots"]["AB".index(name)]
        ok, _, _ = slot_ok(ref, slot)
        if not ok:
            die(f"app {name} in the reference has a bad checksum, can't use it as a source.", 4)
        for s in slot_sectors(slot):
            cur, want = chip.read_sector(s), ref[s:s + SECTOR]
            c = leak_class(cur, want)
            if c and c[0] == "other" and not allow_changes:
                die(f"sector {s:#x} differs from the reference in a way that is not a charge leak. "
                    "Different firmware on chip? Nothing written. (use 'flash' if you really mean it)", 4)
            if c and c[0] == "leak" and c[1] > MAX_LEAK_BITS and not allow_changes:
                die(f"sector {s:#x} has {c[1]} leaked bits, too many to trust. Nothing written.", 4)
            if c:
                report.append((s, c))
            sectors.append(s)
    for s, c in report:
        if c[0] == "leak":
            say(f"  {s:#07x}: {c[1]} leaked bit(s) at " + ", ".join(f"{s + i:#x}" for i in c[2][:6]))
        else:
            say(f"  {s:#07x}: different content")
    if not report:
        say("  chip matches the reference (still rewriting, weak cells can read fine here and fail at boot)")
    return sectors


def _write(chip, ref, sectors):
    say(f"== writing {len(sectors)} sectors")
    t, failed = time.time(), []
    for i, s in enumerate(sectors, 1):
        if not chip.write_sector(s, ref[s:s + SECTOR]):
            failed.append(s)
        if i % 10 == 0 or i == len(sectors):
            say(f"  {i}/{len(sectors)}  {time.time() - t:.0f}s  failed: {len(failed)}")
    say("== verify")
    bad = [s for s in sectors if chip.read_sector(s) != ref[s:s + SECTOR]]
    prot = chip.read_range(0, 0x2000) + chip.read_range(*ISP_BLOCK)
    say(f"  written sectors : {'OK' if not bad else 'MISMATCH ' + ', '.join(hex(s) for s in bad[:8])}")
    say(f"  bootloader + ISP block untouched: {'yes' if prot == ref[:0x2000] + ref[ISP_BLOCK[0]:ISP_BLOCK[1]] else 'they differ from the reference (they did before too)'}")
    if bad or failed:
        say("some sectors failed. Run the same command again, nothing is lost while the ISP block is alive.")
        return 5
    say("done. The controller loads the new app at its next restart: wait up to 10 minutes or power the laptop off and on.")
    return 0


def _ref_and_layout(path):
    ref, kind = load_image(path)
    d = describe(ref, f"reference {path} ({kind})")
    if not d:
        die("reference layout not recognized, refusing to write.", 4)
    return ref, d


def _confirm(a, text):
    if a.yes:
        return
    say(text)
    if input("type YES to continue: ").strip() != "YES":
        die("cancelled")


def cmd_refresh(a):
    ref, d = _ref_and_layout(a.ref)
    slots = a.slots.upper()
    chip = Chip(writable=set(s for n in slots for s in slot_sectors(d["slots"]["AB".index(n)])))
    sectors = _plan(chip, ref, d, slots, allow_changes=False)
    _confirm(a, f"about to erase and rewrite app {', '.join(slots)} ({len(sectors)} sectors) from the reference. "
                "Laptop on AC power, don't close the lid.")
    return _write(chip, ref, sectors)


def cmd_flash(a):
    ref, d = _ref_and_layout(a.image)
    slots = a.slots.upper()
    chip = Chip(writable=set(s for n in slots for s in slot_sectors(d["slots"]["AB".index(n)])))
    sectors = _plan(chip, ref, d, slots, allow_changes=True)
    _confirm(a, "flash writes app code that is DIFFERENT from what is on the chip. Only use an official "
                "ASUS image for your exact model. Bootloader and ISP block matched, so the layout fits.")
    return _write(chip, ref, sectors)


def cmd_check(a):
    ref, d = _ref_and_layout(a.ref)
    chip = Chip()
    _plan(chip, ref, d, "A", allow_changes=True)
    return 0


def cmd_auto(a):
    """for udev / scheduled task: refresh from the stored reference if the controller is stuck"""
    if not isp_path():
        say("controller is not in ITE Upgrade Mode, nothing to do")
        return 0
    a.slots, a.yes = "A", True
    return cmd_refresh(a)


UDEV = 'ACTION=="add", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="048d", ATTRS{idProduct}=="89db", ' \
       'TAG+="systemd", ENV{SYSTEMD_WANTS}+="itefix-auto.service"\n'
UNIT = """[Unit]
Description=itefix: repair the ASUS keyboard controller stuck in ITE Upgrade Mode

[Service]
Type=oneshot
ExecStart={exe} auto --ref {ref}
TimeoutStartSec=15min
"""


def cmd_install_auto(a):
    if not sys.platform.startswith("linux"):
        die("install-auto is Linux only for now. On Windows run 'itefix refresh' by hand.")
    if os.geteuid() != 0:
        die("run as root")
    ref, d = _ref_and_layout(a.ref)
    if not slot_ok(ref, d["slots"][0])[0]:
        die("app A in this reference has a bad checksum, it can't be used for auto repair")
    os.makedirs("/var/lib/itefix", exist_ok=True)
    dst = "/var/lib/itefix/reference.bin"
    with open(dst, "wb") as f:
        f.write(ref)
    os.chmod(dst, 0o444)
    exe = os.path.realpath(sys.argv[0])
    with open("/etc/systemd/system/itefix-auto.service", "w") as f:
        f.write(UNIT.format(exe=exe, ref=dst))
    with open("/etc/udev/rules.d/99-itefix.rules", "w") as f:
        f.write(UDEV)
    os.system("systemctl daemon-reload; udevadm control --reload")
    say(f"installed. When the controller shows up as 048D:89DB, {exe} refreshes app A from {dst}.")
    say("log: journalctl -u itefix-auto")
    return 0


# ----------------------------------------------------------------------------- self test (no hardware)

class SimChip:
    """In-memory model of the ISP block, to test the write logic without hardware."""

    def __init__(self, img):
        self.mem = bytearray(img)
        self.buf = bytearray(b"\xff" * SECTOR)
        self.reply = b""
        self.flen = 65
        self.erased, self.programmed = [], []

    def set_feature(self, p):
        op = p[0]
        if op == 0xD1:
            a, n = p[1] | p[2] << 8 | p[3] << 16, p[4]
            self.reply = bytes([0xD1, p[1], p[2], p[3], n]) + bytes(self.mem[a:a + n])
        elif op in (0xC1, 0xD0, 0xC0):
            off, n = p[1] | p[2] << 8, p[3]
            self.buf[off:off + n] = p[4:4 + n]
            s = sum(self.buf) & 0xFFFF
            self.reply = bytes([op, s & 0xFF, s >> 8])
        elif op == 0xC2:
            a = p[1] | p[2] << 8 | p[3] << 16
            self.mem[a:a + SECTOR] = b"\xff" * SECTOR
            self.erased.append(a)
        elif op == 0xC3:
            self.pending = p[1] | p[2] << 8 | p[3] << 16
        if op == 0xC0:
            a = self.pending
            self.mem[a:a + SECTOR] = bytes(x & y for x, y in zip(self.mem[a:a + SECTOR], self.buf))
            self.programmed.append(a)

    def get_feature(self):
        return self.reply + bytes(64)

    def close(self):
        pass


def cmd_selftest(a):
    import random
    rnd = random.Random(1)
    img = bytearray(rnd.getrandbits(8) for _ in range(CHIP_SIZE))
    img[0x3C000:0x40000] = b"\xff" * 0x4000
    for base, end in ((0x2000, 0x1D7FF), (0x20000, 0x3B7FF)):
        img[base:base + 2] = b"\0\0"
        s = (-sum(img[base + 2:end + 1])) & 0xFFFF
        img[base], img[base + 1] = s >> 8, s & 0xFF
    struct.pack_into("<6I", img, 0x3C030, 0x2002, 0x1D7FF, 0x2000, 0x20002, 0x3B7FF, 0x20000)
    img[0x3C048] = 0
    struct.pack_into("<H", img, 0x3C04A, 0x8252)
    ref = bytes(img)
    d = find_descriptor(ref)
    assert d and d["offset"] == 0x3C030 and all(slot_ok(ref, s)[0] for s in d["slots"])

    chip_img = bytearray(ref)
    for addr in (0x2C4E, 0x11418):          # two charge leaks, like on my laptop
        chip_img[addr] |= 0x20 if chip_img[addr] & 0x20 == 0 else 0x40
    sim = SimChip(chip_img)
    chip = Chip(transport=sim, writable=set(slot_sectors(d["slots"][0])))
    old = say
    globals()["say"] = lambda *x: None
    try:
        sectors = _plan(chip, ref, d, "A", allow_changes=False)
        rc = _write(chip, ref, sectors)
    finally:
        globals()["say"] = old
    assert rc == 0 and bytes(sim.mem[0x2000:0x1D800]) == ref[0x2000:0x1D800]
    assert not [x for x in sim.erased + sim.programmed if x < 0x2000 or ISP_BLOCK[0] <= x < ISP_BLOCK[1]]
    try:
        chip._guard(0x1000)
        raise AssertionError("guard did not stop a bootloader write")
    except SystemExit:
        pass
    sim2 = SimChip(chip_img)
    sim2.mem[0x5000] ^= 0xFF             # not a leak: must refuse
    chip2 = Chip(transport=sim2, writable=set(slot_sectors(d["slots"][0])))
    globals()["say"] = lambda *x: None
    err, sys.stderr = sys.stderr, open(os.devnull, "w")
    try:
        _plan(chip2, ref, d, "A", allow_changes=False)
        raise AssertionError("non-leak difference was not refused")
    except SystemExit:
        pass
    finally:
        globals()["say"] = old
        sys.stderr = err
    say("selftest OK: leaks repaired, bootloader and ISP block never touched, foreign data refused")
    return 0


# ----------------------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(prog="itefix", description="ASUS ROG keyboard stuck in ITE Upgrade Mode (048D:89DB): dump, check, repair.")
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("status", help="what the keyboard controller shows up as right now")
    s = sub.add_parser("dump", help="read the whole 256 KiB flash (read only, safe)")
    s.add_argument("-o", "--output")
    s.add_argument("--passes", type=int, default=2)
    s = sub.add_parser("info", help="show what is inside a dump or an ASUS FGA image (offline)")
    s.add_argument("file")
    s = sub.add_parser("check", help="compare the chip with a reference dump (read only)")
    s.add_argument("--ref", required=True)
    for name, hlp in (("refresh", "rewrite app sectors from your own good dump (fixes leaked bits)"),
                      ("flash", "write app sectors from an official ASUS image of the SAME model")):
        s = sub.add_parser(name, help=hlp)
        if name == "refresh":
            s.add_argument("--ref", required=True)
        else:
            s.add_argument("image")
        s.add_argument("--slots", default="A", choices=["A", "B", "AB", "a", "b", "ab"])
        s.add_argument("-y", "--yes", action="store_true")
    s = sub.add_parser("auto", help="non interactive refresh, for udev/systemd")
    s.add_argument("--ref", required=True)
    s = sub.add_parser("install-auto", help="Linux: repair automatically whenever 048D:89DB shows up")
    s.add_argument("--ref", required=True)
    sub.add_parser("selftest", help="test the write logic on a simulated chip (no hardware)")
    a = p.parse_args()
    cmds = {"status": cmd_status, "dump": cmd_dump, "info": cmd_info, "check": cmd_check,
            "refresh": cmd_refresh, "flash": cmd_flash, "auto": cmd_auto,
            "install-auto": cmd_install_auto, "selftest": cmd_selftest}
    if not a.cmd:
        p.print_help()
        return 0
    return cmds[a.cmd](a)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        die("interrupted")
