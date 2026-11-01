# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | Yes       |

This is a hackathon project; only the latest release line gets fixes.

## Reporting a Vulnerability

Use
[private vulnerability reporting](https://github.com/kizouker/adaptive-IVR-agent/security/advisories/new)
so details stay private until a fix is out. You can also
[open a public issue](https://github.com/kizouker/adaptive-IVR-agent/issues)
for non-sensitive security improvements.

What happens next:

1. We confirm receipt within a few days.
2. We fix on a branch, cut a release, and credit you (unless you prefer
   to stay anonymous).

## Scope notes

- Call recordings and transcripts in this repo are simulated or redacted;
  real personal data (personnummer, names) must never be committed —
  `sh/check-security.sh` and secret scanning guard this in CI.
- Phone credentials (46elks/Twilio) belong in `.env`, never in the repo.

See `docs/security-review.md` for the OWASP Top 10 + LLM Top 10 mapping.
