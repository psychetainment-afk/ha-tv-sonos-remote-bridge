# Build the companion APK

The matching preferred source is android/app/src/main (Java, AndroidManifest.xml and resource XML). scripts/build-apk.ps1 builds the app on Windows with PowerShell, without Gradle or access to personal HA data.

Requirements: JDK 21, Android platform 34 (android.jar), Android Build Tools 34.0.0 (aapt, d8, zipalign, apksigner), and your own private signing keystore. Obtain tools from the official Android SDK and JDK distributions; they are not bundled.

Set TVBRIDGE_KEYSTORE_PASSWORD in your process environment securely; never commit it. Run, with your own paths:

```powershell
./scripts/build-apk.ps1 `
  -JdkPath 'C:/Tools/jdk-21' `
  -AndroidJar 'C:/Android/platforms/android-34/android.jar' `
  -BuildToolsPath 'C:/Android/build-tools/34.0.0' `
  -KeyStorePath 'C:/PRIVATE/tvbridge.p12' `
  -KeyAlias 'tvbridge'
```

The script compiles Java, generates DEX, packages/aligns/signs the APK and verifies its signature. It creates a unique ignored build directory and dist/tv-sonos-remote-bridge-1.7.1.apk. It does not install the app. Generated output is not claimed to be byte-for-byte reproducible.

The release APK is signed with the project's existing private key. An independently signed build cannot directly update that installation; uninstalling would lose app settings and accessibility authorization. Keep private keys/passwords outside Git. Future changed APK releases must increase versionCode and retain the project signer for direct updates. APK downgrades are not guaranteed.

To test gesture logic without Android, compile GestureTracker.java and tests/GestureTrackerTest.java with javac --release 8 into a temporary classes directory, then run java -cp <classes> GestureTrackerTest. Full HA tests and known hardware limits: [PRUEFUNG.md](PRUEFUNG.md). German build instructions: [BUILD.md](BUILD.md).
