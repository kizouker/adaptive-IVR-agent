# Baseten TTS-röst-research för Roksolana röstläge 2

Datum: 2026-11-03. Syfte: svensk + engelsk berättarröst, bättre än Apple `say`.
Ingen kod ändrad — ren research.

## Slutsats

Ingen av de fem har verifierat svenskstöd. Fyra saknar svenska bevisat;
MARS6 är den enda med rimlig chans (10 kloningsspråk, lista opublicerad,
CAMB.AI-plattformen stöder sv-se).

## Jämförelse (Baseten-priser okt 2026, per GPU-minut)

| Modell | Svenska | ~Pris/1k tecken | Latens / streaming |
|---|---|---|---|
| MARS6 | Troligen, måste testas | ~$0,001 | Låg / ja |
| Qwen3-TTS 1.7B | Nej, kloning otestad | ~$0,003 | ~97 ms / ja |
| Orpheus 3B | Nej (EN) | ~$0,01 | ~200 ms / ja |
| Kokoro 82M | Nej | ~$0,0002 | Lägst / chunkvis |
| XTTS v2 | Nej, vägrar SV | ~$0,02 | Måttlig / ja |

Priserna är härledda (GPU-pris × genomströmning), ej vendor-offert:
T4 $0,63/h, L4 $0,85/h, A10G $1,21/h, H100 MIG $3,75/h.

API-komplexitet: Orpheus och Kokoro lägst (one-click/Truss-exempel,
preset-röster); MARS6 medel (one-click men kräver referensljud +
`language`-kod); Qwen3-TTS medel (websocket-deploy, klonröster
registreras själv); XTTS v2 högst (referens-wav + språkkod, plus
icke-kommersiell licens).

## Rekommendation

- **Primär: MARS6.** Minst (70–80M, billig/snabb), äkta streaming på
  Baseten (chunked AAC), röst-/prosodikloning — och enda kandidaten där
  svenska plausibelt fungerar. Test: svensk referenssnutt +
  `language`-parameter mot sv. Flagga: kommersiell licens krävs
  (hackathon-demo bör vara OK, verifiera).
- **Fallback: Qwen3-TTS 1.7B.** Ren Apache 2.0, dokumenterad
  korsspråklig kloning och ~97 ms första paket. Större community och
  tydligare deploy än MARS6.

Orpheus är bäst på engelsk berättarkvalitet men oanvändbar för svenska.
Kokoro är billigast/simplast men utan kloning och svenska — bra
EN-only-reserv. XTTS v2 faller bort (vägrar svenska, icke-kommersiell
licens).

## Täcker $100 behovet?

Ja, med marginal vid on-demand-körning. Räkneexempel: 100 fulla
Roksolana-samtal à ~5k tecken = 500k tecken ≈ $0,50–10 beroende på
modell. Risken är inte tecken utan **always-on GPU**: H100 MIG dygnet
runt tömmer $100 på ~27 h. Kör med autoscale/scale-to-zero och stäng
ner deploymenten mellan körningar.

## Källor

- Baseten GPU-priser: https://hokai.io/hub/services/baseten
- Kokoro på Baseten (T4): https://docs.baseten.co/examples/text-to-speech
- Orpheus på Baseten (200 ms TTFB, H100 MIG):
  https://baseten.vercel.app/blog/canopy-labs-selects-baseten-as-preferred-inference-provider-for-orpheus-tts-model/
- MARS6-modellkort: https://ar5iv.labs.arxiv.org/html/2501.05787
- CAMB.AI sv-se-stöd:
  https://help.camb.ai/en/articles/8765503-what-languages-are-supported-for-which-tool
- XTTS v2 språk: https://docs.coqui.ai/en/latest/models/xtts.html
- LiveKit Baseten TTS-plugin: https://docs.livekit.io/agents/models/tts/baseten/
