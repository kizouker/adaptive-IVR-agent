# Claude Code + Muse Code via AgentChute

Installerat 2026-11-03 för `adaptive-IVR-agent`.

Det här projektet använder AgentChute för lokal kommunikation mellan en
Claude Code-session och en Meta Muse Code-session. Det är en lokal
inkorgsmekanism: agenterna kan meddela varandra om branch, arbetsmapp,
filansvar, blockeringar och handoff utan att människan behöver kopiera mellan
terminalerna.

Det är inte ett hårt fil-lås. Två agenter ska fortfarande inte redigera samma
fil samtidigt.

## Installerat

- AgentChute `v1.7.3` finns i `/Users/raberg/.local/bin/agentchute`.
- `ac`-startkommandot finns i `/Users/raberg/.agentchute/bin/ac` och har lagts
  till i zsh PATH via `/Users/raberg/.zshrc`.
- AgentChute-konfigurationen finns i projektroten:
  `AGENTCHUTE.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/settings.json` och
  `.muse/hooks.json`.
- Den körande inkorgen ligger under `.agentchute/loop/` och är Git-ignorerad.

`agentchute doctor` har kontrollerats med godkänt resultat efter installationen.

## Starta agenterna

Stäng eventuella gamla Claude- och Muse-sessioner som startades direkt med
`claude` eller `muse`. Starta sedan en ny terminal för varje agent med följande
kommando.

Claude Code:

```bash
source /Users/raberg/.zshrc && cd /Users/raberg/kod/001_Meta_Hackathon_w44/adaptive-IVR-agent && ac serve claude
```

Meta Muse Code:

```bash
source /Users/raberg/.zshrc && cd /Users/raberg/kod/001_Meta_Hackathon_w44/adaptive-IVR-agent && ac serve muse
```

`ac serve` registrerar agenten, håller dess lokala inkorg aktiv och ger den ett
meddelande när den andra agenten har skrivit.

## Samordningsregel i IVR-projektet

Innan en agent redigerar ska den använda AgentChute för att berätta för den
andra:

- aktuell Git-branch och arbetsmapp;
- om den läser eller redigerar; och
- exakta filer eller kataloger som den avser att ändra.

En annan agents pågående redigering är ett exklusivt anspråk på de filerna.
Vid ändrad omfattning, paus, blockering eller avslut ska agenten skicka en kort
uppdatering eller handoff.

## Kontrollera läget

Kör detta från valfri terminal för att kontrollera den gemensamma setupen:

```bash
source /Users/raberg/.zshrc && cd /Users/raberg/kod/001_Meta_Hackathon_w44/adaptive-IVR-agent && agentchute doctor
```

När Claude och Muse är startade via `ac serve` kan deras egna sessioner också
köra `agentchute doctor` med sin automatiskt satta identitet.

## Säkerhetsgräns

AgentChute-meddelanden är lokala, vanliga textfiler i projektets kördata. De är
avsedda för agenter och projekt du litar på, inte som säker eller signerad
kommunikation. Följ därför fortfarande projektets vanliga regler för hemligheter,
externa anrop, radering och deployer.
