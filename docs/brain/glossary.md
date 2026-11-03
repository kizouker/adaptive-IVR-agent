# Glossary #glossary

- **Provenance** — härkomstlogg: vilken modell, runtime, tidpunkt och resultat
  varje AI-anrop gav. En JSONL-rad per anrop i `data/provenance.jsonl`.
  Testas: `test_openweight_logs_provenance`, `test_spark_logs_provenance`.
- **Telemetry** — svansen av provenansen (sista 20) som boarden visar live
  i tabellen Modellanrop.
- **NFR** — icke-funktionellt krav (video, repro, licens, freeze). Karta: `docs/nfr-judging.md`.
- **Freeze** — tors 5 nov 03:00: därefter inga pushar till main.
- **Open weights** — öppna modellvikter (Spark Open/Glimmer) som kan köras
  lokalt eller hos partner. Ger $10k-bonusen om bärande.
- **Ladder** — intent-stegen: exact → heuristic → Meta-modell → abstain.
- **Rescue/abstain** — rescue: modellen räddar ett missförstått yttrande;
  abstain: avstår hellre än gissar fel (säkerhet).
- **Bake** — `sh/bake-board.py`: bakar repliker + telemetri till board-filer.
- **Board-state** — `board-state.json`: allt boarden visar (samtal, kö, karta).
- **Autoscore** — portalens robotpoäng (vi: 7.2, plats 135).
- **GHCR** — GitHubs containerregister (våra Docker-images).
- **Bicep** — Azures infra-språk (`infra/main.bicep`).
