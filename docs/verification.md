# Verification

Last local verification: 2026-05-20

Command:

```bash
make verify
```

Result:

- Backend tests: 21 passed
- Frontend audit: 0 vulnerabilities
- Frontend typecheck: passed
- Frontend production build: passed
- Static GitHub Pages export: passed
- Docker Compose config validation: passed
- Docker smoke check: passed

Docker smoke command:

```bash
make docker-check
```

Docker smoke coverage:

- Backend and dashboard images build locally
- Stack starts on temporary local ports
- `/health` returns the expected service
- Sample document indexing succeeds
- Grounded query returns citations and retrieved chunks
- Evaluation run returns a gate verdict
- Report listing returns saved evaluation evidence
- Dashboard CORS preflight passes for the configured frontend port
- Dashboard readiness check passes

This is a local verification artifact. Hosted CI can be added later when Actions minutes
and workflow permissions are available, but the current proof path is intentionally
repeatable from a local checkout.

The evaluation response includes a pass/warn/fail gate with individual checks for
example coverage, retrieval hit rate, expected-answer fact coverage, citation
coverage, failure count, and latency.
Evaluation and experiment runs also write paired JSON/Markdown report artifacts that can
be listed through `/reports` and fetched through the report detail endpoints.
