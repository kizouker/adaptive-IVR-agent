# Use of Meta products — Holdmate (2026-11-04)

Sources: `meta-cost models --project adaptive-IVR-agent` (Meta Cost Center, local Muse logs;
estimates, not bills) and `data/provenance*.jsonl` (Holdmate's own runtime calls).

## 1. Runtime — inside Holdmate (what the app calls)

| Model | Role in Holdmate | Calls logged |
|---|---|---|
| **Muse Spark 1.3** (`api.meta.ai`) | Intent stage: maps the caller's own words onto the robot's closed keyword list, or abstains | 144 |
| **Muse Wonder 1.0** | Review / evaluation runs | 13 |

Every call is logged with model, runtime, latency, prompt hash (`data/provenance.jsonl`).
Daily call cap in code (`SPARK_DAILY_MAX_CALLS`). Median latency ≈ 8.3 s.

## 2. Build time — Muse used to build the project (Oct 26 – Nov 4)

| Model | Use | Input tokens | Output tokens | API-equivalent USD* | Events |
|---|---|---|---|---|---|
| muse-spark-1.3-contributor | Coding agent (Muse Code) | 1,198,012,150 | 5,212,498 | 8.35 | 6,686 |
| muse-wonder-1.0 | Code review | 14,666,190 | 62,538 | 6.64 | 181 |
| muse-spark-1.3 | Direct / API | 1,025,858 | 49,295 | 0.99 | 44 |
| unknown (not priced) | — | 70,072,322 | 954,031 | unknown | 1,329 |
| **Total (known)** | | | | **≈ 15.94+** | 8,213 |

\* Meta Cost Center estimate at public API rates; most input was cached. Not a bill.

## For the form ("Use of Meta products")

> Holdmate calls **Muse Spark 1.3** (api.meta.ai) at runtime as its intent stage: it maps what
> the caller says onto the phone robot's closed keyword list, or abstains — it never invents a
> keyword. Every call is logged with model, latency and prompt hash; a daily cap limits spend.
> **Muse Wonder 1.0** was used for evaluation and code review. The project itself was built with
> **Muse Code** (Muse Spark 1.3 contributor): ~8,200 logged events, ≈ USD 16 API-equivalent,
> tracked with Meta Cost Center.
