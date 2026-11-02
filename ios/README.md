# Holdmate iOS PoC (#146, full app: #100)

Minimal SwiftUI ticket: polls the Mac board server and shows the queue
place big. No signing team needed for the simulator.

## Run

1. Start the board on the Mac (`start` in this repo).
2. Open `ios/Holdmate.xcodeproj` in Xcode.
3. Pick an iPhone simulator, press Run.

The app fetches `http://localhost:5173/board-state.json` every 5 seconds
(simulator shares the Mac network, so localhost works; cleartext local
traffic is allowed via `NSAllowsLocalNetworking` in Info.plist).

## Status

- Swift sources parse clean (`swiftc -parse`, verified in sandbox).
- First full `xcodebuild`/simulator run happens on Rickard's Xcode —
  the sandbox blocks the Swift macro + simulator services.
- Next (per #100): Live Activity, push alerts, approve + take-over flows.
