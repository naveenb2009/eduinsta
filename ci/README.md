# ci/android-debug.keystore

A fixed, **non-secret** Android debug-signing key (standard debug alias
`androiddebugkey`, password `android` — the same defaults Android Studio
itself uses for local debug builds).

It is committed to the repo on purpose. Without it, every GitHub Actions
run would generate its own throwaway debug certificate, so each new debug
APK would have a different signature than the last one — and Android
blocks installing an "update" whose signing certificate doesn't match
what's already on the device. The build workflow copies this file to
`~/.android/debug.keystore` before building the debug APK, so every debug
build ever produced by this pipeline is signed identically and can be
installed over an older one without uninstalling first.

This key is never used for the signed Play Store release build — that
one uses your own private release keystore, supplied only via GitHub
Actions secrets and never committed anywhere.
