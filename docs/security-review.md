# Security review: OWASP Top 10 (web) + OWASP LLM Top 10 (T-051)

Honest mapping, 2026-11-01. Automated subset runs in `sh/check-security.sh`
and CI (`npm audit`, board lint); the rest is design/process status.

## OWASP Top 10, web (2021)

| ID | Risk | Us | Control / status |
|---|---|---|---|
| A01 | Broken Access Control | Board is a local static page, no users/roles | N/A now; revisit if the board ever goes multi-user |
| A02 | Cryptographic Failures | No secrets in repo; `.env` ignored (checked); no TLS scope locally | `check-security.sh` secret+key scan |
| A03 | Injection | No SQL/LDAP/shell; `say`/`dot` args are constants or repo data, never raw caller input | grep gate: `eval/exec/shell=True/os.system` forbidden in `src` |
| A04 | Insecure Design | Threat model: untrusted party is the phone line, not a web attacker | Design: STT text never executed, only matched; see LLM04/LLM05 |
| A05 | Security Misconfiguration | Vite dev defaults, no prod server yet | Pages deploy is static files only; no headers debate needed |
| A06 | Vulnerable Components | React/Vite/Redux via npm | `npm audit --omit=dev --audit-level=high` in CI (prod clean 2026-11-01); dev-only vite advisories (dev server, Windows) do not ship; Python has no third-party deps |
| A07 | Auth Failures | No login anywhere | N/A |
| A08 | Data/Software Integrity | Deps from npmjs; no webhooks/pipelines executing PR code beyond CI | Lockfile committed (`package-lock.json`); scripts pinned, no `curl\|bash` |
| A09 | Logging Failures | NF-REQ-IVR-002: no personal data in logs/demos/repo | Manual rule today; finding: Skåne transcript holds a staff first name — redact (flagged to Rickard) |
| A10 | SSRF | No URL fetching from user input (scrapes are fixed URLs in reviewed commits) | N/A for runtime paths |

## OWASP Top 10 for LLM Applications (2025)

| ID | Risk | Us | Control / status |
|---|---|---|---|
| LLM01 | Prompt Injection | Spoken caller input reaches matching + (future) LLM parsing | STT text is data: exact-match/keyword lookup only, never concatenated into instructions; no LLM in the loop yet |
| LLM02 | Sensitive Information Disclosure | Call audio/transcripts; personnummer, staff names | NF-REQ-IVR-002 (no PII kept); BankID always human-side; recordings local-only, never committed (`*.wav` ignored) |
| LLM03 | Supply Chain | npm chain (see A06); whisper.cpp binary | Audit gate; models run locally, no training API |
| LLM04 | Data and Model Poisoning | Seeds come from public websites we cite per entry | Sources recorded per topic; seeds can never become observations (evidence policy) |
| LLM05 | Improper Output Handling | Robot speaks fixed lines; board renders repo data | No `dangerouslySetInnerHTML` (grep gate); `say` text from constants/transcripts |
| LLM06 | Excessive Agency | Agent cannot place real calls (no telephony wired; 46elks paused) | Real-line restraint NF-REQ-IVR-003; human-in-the-loop at identity + handover by design |
| LLM07 | System Prompt Leakage | No system prompt exists yet | When an LLM is added: secret-free prompts, output filter for prompt echoes |
| LLM08 | Vector/Embedding Weaknesses | No embeddings/RAG anywhere | N/A |
| LLM09 | Misinformation | Map edges could misroute a caller | Counter: evidence tags + revision rule (FN-REQ-IVR-029); no edge trusted without sources |
| LLM10 | Unbounded Consumption | TTS/whisper.cpp local cost; future API spend | Local-first keeps spend zero; 46elks per-minute cost noted in T-040 before any real call |

## What runs automatically

- `sh/check-security.sh`: `.env` ignored, no private keys/tokens tracked, no dangerous patterns in `src` + `ui/board/src`.
- CI: above + `npm audit --audit-level=high` + `npm run lint`.
- Manual (this file): the mapping above, re-read when telephony or an LLM enters the loop.
