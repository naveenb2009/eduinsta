#!/usr/bin/env python3
"""
Patches the Capacitor-generated android/app/build.gradle so the "release"
build type is signed with our production keystore.

Capacitor regenerates android/ from scratch on every CI run (see the
"Add Android platform" step in the workflow), so this file is never
committed with the signing block already in place -- it has to be
injected here every time, the same way AdMob's APPLICATION_ID meta-data
is injected into AndroidManifest.xml.

Reads the actual key material from environment variables at BUILD time
(not from this script), via Gradle's System.getenv(...) -- so no secret
ever gets written into a file that lives in git.
"""
import re
import sys

PATH = "android/app/build.gradle"

with open(PATH, "r") as f:
    src = f.read()

if "signingConfigs" in src:
    print("signingConfigs already present, skipping")
    sys.exit(0)

SIGNING_BLOCK = """    signingConfigs {
        release {
            storeFile file(System.getenv("CI_KEYSTORE_PATH") ?: "release.keystore")
            storePassword System.getenv("CI_KEYSTORE_PASSWORD")
            keyAlias System.getenv("CI_KEY_ALIAS")
            keyPassword System.getenv("CI_KEY_PASSWORD")
        }
    }
"""

# 1) Insert the signingConfigs block right after the top-level "android {" line.
m = re.search(r"^android\s*\{\s*$", src, re.MULTILINE)
if not m:
    print("::error::could not find 'android {' block in build.gradle")
    sys.exit(1)
insert_at = m.end()
src = src[:insert_at] + "\n" + SIGNING_BLOCK + src[insert_at:]

# 2) Inside buildTypes { release { ... } }, add a reference to that signing config
#    as the first line of the release block.
m = re.search(r"(buildTypes\s*\{[\s\S]*?release\s*\{)", src)
if not m:
    print("::error::could not find 'buildTypes { release { ... } }' in build.gradle")
    sys.exit(1)
insert_at = m.end()
src = src[:insert_at] + "\n            signingConfig signingConfigs.release" + src[insert_at:]

with open(PATH, "w") as f:
    f.write(src)

print("Injected release signingConfig into build.gradle")
