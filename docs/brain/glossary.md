# Glossary #glossary

## Provenance

Härkomstlogg: vilken modell, runtime, tidpunkt och resultat varje
AI-anrop gav. En JSONL-rad per anrop i `data/provenance.jsonl`.

Testas: `test_openweight_logs_provenance`, `test_spark_logs_provenance`.

## Telemetry

Svansen av provenansen (sista 20) som boarden visar live
i tabellen Modellanrop.

Provenance = lagret. Telemetry = skyltfönstret.

## NFR

Icke-funktionellt krav (video, repro, licens, freeze).

Karta: `docs/nfr-judging.md`.

## Freeze

Tors 5 nov 03:00: därefter inga pushar till main.

## Open weights

Öppna modellvikter (Spark Open/Glimmer) som kan köras
lokalt eller hos partner. Ger $10k-bonusen om bärande.

## Ladder

Intent-stegen: exact → heuristic → Meta-modell → abstain.

## Rescue / abstain

Rescue: modellen räddar ett missförstått yttrande.
Abstain: avstår hellre än gissar fel (säkerhet).

## Bake

`sh/bake-board.py`: bakar repliker + telemetri till board-filer.

## Board-state

`board-state.json`: allt boarden visar (samtal, kö, karta).

## Autoscore

Portalens robotpoäng (vi: 7.2, plats 135).

## GHCR

GitHubs containerregister (våra Docker-images).

## Bicep

Azures infra-språk (`infra/main.bicep`).
