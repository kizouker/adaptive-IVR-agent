# IVR BlackHole-felsökning (2026-11-04)

```mermaid
flowchart TD
    A[BlackHole installerad] --> B[Syns i SwitchAudioSource]
    B --> C[Aggregat hela - Spotify funkar]
    C --> D[record-call --check grön]
    D --> E[Samtal kopplas fram]
    E --> F{Motpart hörs?}
    F -->|Ja, i AirPods| G[FaceTime matar AirPods direkt]
    G --> H[Inspelning tyst -91dB]
    H --> I[Fix: FaceTime-högtalare till IVR_Agent_Airpods]
    I --> J[Kör --airpods --call]
    J --> K{check-recording.sh exit 0?}
    K -->|Ja| L[Riktigt testsamtal]
    K -->|Nej| M[Ping --airpods GRÖN -24.8dB: aggregatet helt]
    M --> N{FaceTime-inställning aktiv under samtalet?}
    N -->|Nej| I
    N -->|Ja| P[Ljudet stannar på iPhone - svara/lägg på Macen]
    L --> Q[#140 Upptaget-nod PR 234]
    Q --> O[v0.4.3 release]

    classDef done fill:#2d6a2d,color:#fff
    classDef now fill:#8a6d1b,color:#fff
    class A,B,C,D,E,F,G,K,M done
    class H,I,J,N,P now
```

## Logg

- 13:52 Graf skapad, kedjan tyst (-91 dB).
- ~14:05 `--airpods --check` helt grön, ping når BlackHole (-24,8 dB). Aggregatet frikänt — felet ligger i själva samtalets ljudväg (FaceTime-inställning eller svarsenhet).

