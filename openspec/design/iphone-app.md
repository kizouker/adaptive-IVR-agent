# Holdmate iOS companion (design for #100)

Vision: Rickard approves BankID himself, sees "you are number 3", takes
over and talks to a person. The app replaces the Mac `osascript` alert
as the last hop. PoC scaffold: `ios/` (SwiftUI ticket, simulator-ready).

## v1 scope

- Live Activity + widget: queue place, countdown, agency name.
- Push at threshold (place <= 2) and at officer-answer.
- Approve-ID screen: "approve in BankID, then tap Resume".
- Take-over button: tells the Mac agent to bridge the call to this phone.

## Build choices

- Native SwiftUI (Live Activities + push + CallKit need native; PWA
  cannot do any of them on iOS).
- Transport v1: poll the Mac board server on LAN; push via a tiny relay
  (Mac posts to APNs, or 46elks SMS as zero-infra fallback).
- Needs: Apple Developer account (Rickard), bundle id, push certs.

## Phases

1. Ticket view polling board-state (PoC exists, first Xcode run Monday).
2. Live Activity for the queue countdown.
3. Push alerts via Mac relay (or SMS fallback).
4. Approve + take-over flows against the 46elks bridge.

## Open questions

- Take-over primitive: carrier call to the iPhone vs VoIP push.
- Pairing/security model Mac <-> phone (PIN? Tailscale?).
- Battery/data budget for polling vs push-only.
