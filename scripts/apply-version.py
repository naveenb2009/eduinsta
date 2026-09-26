#!/usr/bin/env python3
"""
Makes versionCode / versionName come from CI env vars instead of the
hardcoded values Capacitor's template ships with (versionCode 1,
versionName "1.0" forever).

Why this matters: Android refuses to install an "update" over an existing
app unless the new APK has a STRICTLY HIGHER versionCode than what's already
on the device (same or lower versionCode = install blocked, or Play Console
rejects the upload outright). If every CI build keeps versionCode 1, no
build can ever update a previous one -- the user has to uninstall the old
app first every single time.

Reads CI_VERSION_CODE / CI_VERSION_NAME from the environment at BUILD time
(set by the workflow from the run number), so every CI run gets a unique,
increasing versionCode automatically -- no manual bumping required.
"""
import re
import sys

PATH = "android/app/build.gradle"

with open(PATH, "r") as f:
    src = f.read()

if "CI_VERSION_CODE" in src:
    print("version already wired to CI env vars, skipping")
    sys.exit(0)

src2, n1 = re.subn(
    r"versionCode\s+\d+",
    # NOTE: deliberately NOT "versionCode (getenv(...) ?: "1").toInteger()".
    # In Groovy, "methodName (expr).foo()" parses as "(methodName(expr)).foo()"
    # -- the trailing .toInteger() would land on versionCode()'s return value
    # (null), not on the env var expression, causing a build-time
    # NullPointerException ("Value is null"). Integer.parseInt(...) as a
    # single self-contained argument avoids the ambiguity entirely.
    'versionCode Integer.parseInt(System.getenv("CI_VERSION_CODE") ?: "1")',
    src,
    count=1,
)
if n1 != 1:
    print("::error::could not find 'versionCode <number>' in build.gradle")
    sys.exit(1)

src3, n2 = re.subn(
    r'versionName\s+"[^"]*"',
    'versionName (System.getenv("CI_VERSION_NAME") ?: "1.0")',
    src2,
    count=1,
)
if n2 != 1:
    print("::error::could not find 'versionName \"...\"' in build.gradle")
    sys.exit(1)

with open(PATH, "w") as f:
    f.write(src3)

print("Wired versionCode/versionName to CI_VERSION_CODE/CI_VERSION_NAME")
