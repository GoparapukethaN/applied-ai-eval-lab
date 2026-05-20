# Model Card

## System

Applied AI Eval Lab uses a local grounded retrieval system for the public demo.
The first release intentionally avoids external model providers so the app can be
reviewed without API keys, private accounts, or hidden infrastructure.

## Intended Use

- Demonstrate document intelligence workflow design.
- Inspect how retrieval results support generated answers.
- Compare retrieval settings against a curated evaluation set.
- Provide a safe baseline before adding private provider-backed generation.

## Out-of-Scope Use

- Legal, medical, financial, or security decisions without human review.
- Processing private customer documents in the public demo.
- Treating local extractive answers as a general-purpose LLM.

## Retrieval Method

The backend chunks documents by section and indexes chunks with deterministic
token-frequency vectors. Query results are ranked with cosine similarity. This
keeps tests repeatable and makes the retrieval behavior inspectable.

## Answering Method

The answer generator is extractive and grounded. It selects the strongest
retrieved evidence sentence and attaches citations back to source chunks. If
retrieval does not find enough evidence, the system declines to answer instead
of fabricating unsupported details.

## Evaluation

The curated evaluation set checks:

- Retrieval hit rate.
- Expected-answer fact coverage.
- Citation coverage.
- Failure category count.
- Average latency.
- Estimated local run cost.
- Release-gate verdict based on evidence coverage, answer-fact coverage,
  citation coverage, failure count, and latency.

The experiment lab compares focused, balanced, and broad retrieval settings over
the same evaluation examples.

## Limitations

- Local token-frequency retrieval is less semantically rich than production
  embedding models.
- Extractive answers are intentionally conservative and may omit synthesis.
- The public static demo uses safe fixed sample responses.
- Persistent storage and authenticated workspaces are not part of this release.

## Planned Improvements

- Add private provider adapters behind environment variables.
- Add reranking and persistent experiment reports.
- Add hosted backend deployment once deployment credentials are available.
