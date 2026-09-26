#!/usr/bin/env python3
"""
Injects the intent-filters that let a shared reel link open EduInsta
directly, instead of a browser -- the same trick Instagram/TikTok use for
their reel share links.

Capacitor's default AndroidManifest.xml only has a MAIN/LAUNCHER
intent-filter (how the app icon opens the app). It knows nothing about
opening a specific https://.../reel/<id> link, so without this, sharing a
reel just hands out a bare video-file URL that WhatsApp shows as a plain
"website address" and that opens in a browser, not the app.

This adds, right after that intent-filter, on the same <activity>:
  1. An Android App Link (autoVerify) for https://<API host>/reel/* --
     the real fix. Android intercepts this BEFORE it ever reaches a
     browser, once /.well-known/assetlinks.json on that host (served by
     server.js) confirms this app is authorized for the domain.
  2. A custom-scheme fallback (eduinsta://reel/<id>) the landing page's
     "Open in EduInsta" button can always use, for the rare case App Link
     verification hasn't completed yet on a given device.

Capacitor regenerates android/ on every CI build, so -- like the AdMob
meta-data and the version/signing patches -- this has to be reapplied
every time, not committed into a generated folder.
"""
import re
import sys

PATH = "android/app/src/main/AndroidManifest.xml"

# Must match the host used in shareReel()'s link (index.html) and the
# assetlinks.json served by server.js -- keep all three in sync.
APP_LINK_HOST = "eduinsta-api.onrender.com"

with open(PATH, "r") as f:
    src = f.read()

if "android:host=\"" + APP_LINK_HOST + "\"" in src:
    print("App Links intent-filter already present, skipping")
    sys.exit(0)

old_filter = (
    '            <intent-filter>\n'
    '                <action android:name="android.intent.action.MAIN" />\n'
    '                <category android:name="android.intent.category.LAUNCHER" />\n'
    '            </intent-filter>\n'
)

new_block = old_filter + f'''
            <!-- App Links: tapping a shared https://{APP_LINK_HOST}/reel/<id>
                 link (see the server's GET /reel/:id route) opens straight
                 into the app instead of a browser, once
                 /.well-known/assetlinks.json on that host verifies this app
                 owns the domain. -->
            <intent-filter android:autoVerify="true">
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="https" android:host="{APP_LINK_HOST}" android:pathPrefix="/reel" />
            </intent-filter>

            <!-- Custom-scheme fallback (eduinsta://reel/<id>) for the rare
                 case App Link verification hasn't completed on a device yet -
                 the landing page's "Open in EduInsta" button uses this. -->
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="eduinsta" />
            </intent-filter>
'''

n = src.count(old_filter)
if n != 1:
    print(f"::error::expected exactly one MAIN/LAUNCHER intent-filter in {PATH}, found {n}")
    sys.exit(1)

src2 = src.replace(old_filter, new_block, 1)
with open(PATH, "w") as f:
    f.write(src2)

print(f"Injected App Links + custom-scheme intent-filters for {APP_LINK_HOST}")
