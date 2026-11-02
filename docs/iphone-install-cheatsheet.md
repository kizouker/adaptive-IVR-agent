# iPhone install cheatsheet (Xcode + cable)

## Phone setup (once)
1. Cable → Trust This Computer + passcode.
2. Settings → Privacy & Security → Developer Mode → On → restart → confirm.
3. Xcode → Window → Devices and Simulators → pick the iPhone, wait until ready.
4. Same WiFi on iPhone + Mac (app polls the Mac over LAN).

## Signing (per project)
1. Blue project icon → TARGETS → Holdmate → General → Identity → Bundle Identifier: `com.kizouker.holdmate`.
2. Signing & Capabilities → Automatically manage signing ON → Team: your Apple ID (Xcode → Settings → Accounts → + if missing).
3. First launch on device: Settings → General → VPN & Device Management → trust the developer.

## Info.plist must-haves (custom plist!)
Built .app needs these keys or install fails with CoreDeviceError 3002/3000:
- `CFBundleIdentifier` = `$(PRODUCT_BUNDLE_IDENTIFIER)`
- `CFBundleName` = `$(PRODUCT_NAME)`
- `CFBundleExecutable` = `$(EXECUTABLE_NAME)`

Check: error text → BundleDiagnostics lists present vs ABSENT keys.

## Warnings seen
- `Cannot use ... Autoconnect/Publishers ...` → add `import Combine` (Timer.publish needs it).

## Cache hammer
- Same error after fixing? Delete `~/Library/Developer/Xcode/DerivedData/Holdmate-*`, Product → Clean Build Folder, rebuild.

## Board on LAN (for the device)
- .local URL works on simulator + device: `start` (server always on LAN), allow node in the firewall.
