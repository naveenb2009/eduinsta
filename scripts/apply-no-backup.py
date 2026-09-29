#!/usr/bin/env python3
"""
Turns off Android Auto Backup for EduInsta (android:allowBackup="false").

Capacitor's template ships with android:allowBackup="true", so Android backs
the app's local data (including the saved login in localStorage) up to the
user's Google account and silently RESTORES it after an uninstall/reinstall.
The result: a fresh install opens already signed in instead of showing the
sign-in screen. Disabling backup makes a reinstall start clean.

android/ is regenerated on every CI build, so this is applied each time, same
pattern as the other apply-*.py scripts.
"""
import re
import sys
from pathlib import Path

path = Path("android/app/src/main/AndroidManifest.xml")
if not path.is_file():
    print(f"::error::{path} is missing - run `npx cap add android` first")
    sys.exit(1)

text = path.read_text()
if re.search(r'android:allowBackup\s*=\s*"[^"]*"', text):
    text = re.sub(r'android:allowBackup\s*=\s*"[^"]*"', 'android:allowBackup="false"', text)
else:
    text, n = re.subn(r"<application\b", '<application\n        android:allowBackup="false"', text, count=1)
    if n == 0:
        print("::error::could not find <application> in AndroidManifest.xml")
        sys.exit(1)

path.write_text(text)
if 'android:allowBackup="false"' not in text:
    print("::error::failed to set android:allowBackup=\"false\"")
    sys.exit(1)
print(f'Set android:allowBackup="false" in {path}')
