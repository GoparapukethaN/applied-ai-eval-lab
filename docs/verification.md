# Verification

Last local verification: 2026-05-20

Command:

```bash
make verify
```

Result:

- Backend tests: 16 passed
- Frontend audit: 0 vulnerabilities
- Frontend typecheck: passed
- Frontend production build: passed
- Static GitHub Pages export: passed
- Docker Compose config validation: passed

This is a local verification artifact. Hosted CI can be added later when Actions minutes
and workflow permissions are available, but the current proof path is intentionally
repeatable from a local checkout.

The evaluation response includes a pass/warn/fail gate with individual checks for
example coverage, retrieval hit rate, citation coverage, failure count, and latency.
