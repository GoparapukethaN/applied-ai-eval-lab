# Verification

Last local verification: 2026-05-20

Command:

```bash
make verify
```

Result:

- Backend tests: 21 passed
- Frontend audit: 0 vulnerabilities
- Static demo data contract: passed
- Frontend typecheck: passed
- Frontend production build: passed
- Static GitHub Pages export: passed
- Static demo browser QA: passed on desktop and mobile

Docker smoke command:

```bash
make docker-check
# or, for the full local + Docker path
make verify-full
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

Static demo data coverage:

- Demo index/upload chunk counts match returned chunk arrays
- Demo corpus chunk IDs are unique
- Starter-question citations point to retrieved chunks
- Demo evaluation item count matches the reported example count

Static demo browser QA command:

```bash
cd frontend
npm run verify:static-demo
```

Static demo browser QA coverage:

- Serves the exported `frontend/out` build under the GitHub Pages base path
- Runs desktop and mobile viewports
- Drives indexing, query, evaluation, and experiment comparison
- Checks cited answer text, release gate output, experiment output, console issues, and
  horizontal overflow

This is a local verification artifact. Hosted CI can be added later when Actions minutes
and workflow permissions are available, but the current proof path is intentionally
repeatable from a local checkout. Docker is optional for the core `make verify` path and
is used only for the separate container smoke checks.

The evaluation response includes a pass/warn/fail gate with individual checks for
example coverage, retrieval hit rate, expected-answer fact coverage, citation
coverage, failure count, and latency.
Evaluation and experiment runs also write paired JSON/Markdown report artifacts that can
be listed through `/reports` and fetched through the report detail endpoints.
