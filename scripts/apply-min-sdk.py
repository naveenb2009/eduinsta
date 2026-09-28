#!/usr/bin/env python3
"""
Raises the app's minSdkVersion to 24 (Android 7.0).

Capacitor 6's Android template ships with minSdkVersion = 22, but Google
Play Console rejects the bundle with:
    "Play automatic protection requires a minimum SDK version of 24 or higher.
     The uploaded App Bundle has a minimum SDK version of 22."

`android/` is regenerated from scratch on every CI build (gitignored), so the
value can't be edited once and committed; this script rewrites it in
android/variables.gradle after the platform is added, same pattern as the
other apply-*.py scripts.
"""
import re
import sys
from pathlib import Path

MIN_SDK = 24
path = Path("android/variables.gradle")

if not path.is_file():
    print(f"::error::{path} is missing - run `npx cap add android` first")
    sys.exit(1)

text = path.read_text()
new_text, n = re.subn(r"minSdkVersion\s*=\s*\d+", f"minSdkVersion = {MIN_SDK}", text)

if n == 0:
    print("::error::could not find 'minSdkVersion = <number>' in variables.gradle")
    sys.exit(1)

path.write_text(new_text)
print(f"Set minSdkVersion = {MIN_SDK} in {path}")
