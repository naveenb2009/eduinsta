#!/usr/bin/env python3
"""
Replaces Capacitor's default blue "cap" launcher icon with EduInsta's real
brand mark (the same play-triangle + graduation-cap logo used in-app).

`android/` is regenerated from scratch by `npx cap add android` on every CI
build (it's gitignored - see .gitignore), so its default icon can't just be
edited once and committed. Instead the FINISHED icon files (already
generated for every density, legacy + adaptive) are committed under
android-icon/, and this script copies them into android/app/src/main/res
after the platform is added, same pattern as apply-applinks.py and the
AdMob meta-data injection.

android-icon/ was produced with @capacitor/assets from assets/icon.png,
assets/icon-foreground.png and assets/icon-background.png. If you ever want
to change the icon, regenerate it with:
    npm install -D @capacitor/assets
    npx cap add android   # if android/ doesn't already exist
    npx @capacitor/assets generate --android --assetPath assets \\
        --iconBackgroundColor '#7c6cf6' --iconBackgroundColorDark '#7c6cf6'
then copy the mipmap-*/ic_launcher*.png and mipmap-anydpi-v26/ic_launcher*.xml
files it produces back into android-icon/, replacing what's there.
"""
import shutil
import sys
from pathlib import Path

SRC = Path("android-icon")
DEST = Path("android/app/src/main/res")

if not SRC.is_dir():
    print(f"::error::{SRC} is missing - nothing to copy")
    sys.exit(1)
if not DEST.is_dir():
    print(f"::error::{DEST} is missing - run `npx cap add android` first")
    sys.exit(1)

copied = 0
for src_file in SRC.rglob("*"):
    if src_file.is_dir():
        continue
    rel = src_file.relative_to(SRC)
    dest_file = DEST / rel
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src_file, dest_file)
    copied += 1

print(f"Copied {copied} app icon files into {DEST}")
