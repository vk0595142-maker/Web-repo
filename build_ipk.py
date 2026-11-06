#!/usr/bin/env python3
"""Builds com.usbplayer.app_1.0.0_all.ipk (same layout ares-package makes). No Node needed."""
import tarfile, io, os, time, json
ID, VER = "com.usbplayer.app", "1.0.0"
APP = ["appinfo.json", "index.html", "icon.png"]
def tgz(entries):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz", format=tarfile.GNU_FORMAT) as t:
        for name, data, mode in entries:
            ti = tarfile.TarInfo(name); ti.size = len(data); ti.mode = mode
            ti.uid = ti.gid = 0; ti.uname = ti.gname = "root"; ti.mtime = int(time.time())
            if data is None: ti.type = tarfile.DIRTYPE
            t.addfile(ti, io.BytesIO(data))
    return buf.getvalue()
def d(name):
    ti = None
    return (name, b"", 0o755)
files = []
base = f"./usr/palm/applications/{ID}"
for f in APP: files.append((f"{base}/{f}", open(f, "rb").read(), 0o644))
files.append((f"./usr/palm/packages/{ID}/packageinfo.json",
    json.dumps({"app": ID, "id": ID, "loadable": True, "version": VER}).encode(), 0o644))
size = sum(len(x[1]) for x in files)
control = (f"Package: {ID}\nVersion: {VER}\nSection: misc\nPriority: optional\nArchitecture: all\n"
           f"Installed-Size: {size}\nMaintainer: N/A <nobody@example.com>\nDescription: USB Player\n"
           f"webOS-Package-Format-Version: 2\nwebOS-Packager-Version: x.y.x\n").encode()
members = [("debian-binary", b"2.0\n"), ("control.tar.gz", tgz([("./control", control, 0o644)])),
           ("data.tar.gz", tgz(files))]
os.makedirs("dist", exist_ok=True)
out = f"dist/{ID}_{VER}_all.ipk"
with open(out, "wb") as o:
    o.write(b"!<arch>\n")
    for n, data in members:
        o.write(f"{n+'/':<16}{int(time.time()):<12}{0:<6}{0:<6}{100644:<8}{len(data):<10}`\n".encode())
        o.write(data)
        if len(data) % 2: o.write(b"\n")
print("built", out, os.path.getsize(out), "bytes")
