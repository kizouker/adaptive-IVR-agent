#!/usr/bin/env bash
# Two-voice demo: AF Agda (Alva) vs the caller (Oskar). Live audio, Mac only.
# Lines come from data/doorkeeper-lines.json (L01, L02, L03); caller line is
# the ny-arbetslos role opening. Part of T-039 (#41).
set -euo pipefail

ROBOT_VOICE="Alva"
CALLER_VOICE="Oskar"

L01="Välkommen till Arbetsförmedlingen för arbetssökande. For English, press 0."
L02="Beskriv vad du vill ha hjälp med. Vad gäller ditt ärende?"
CALLER="Hej. Jag heter Rickard, jag vill anmäla mig som arbetssökande."
L03="Förlåt, jag uppfattade inte. Du kan till exempel säga aktivitetsrapport, ersättning eller hjälp med att söka arbete."

say -v "$ROBOT_VOICE" "$L01"
say -v "$ROBOT_VOICE" "$L02"
say -v "$CALLER_VOICE" "$CALLER"
say -v "$ROBOT_VOICE" "$L03"
echo "Dialogue done."
