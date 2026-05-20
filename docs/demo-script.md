# Demo Recording Script

This is the short walkthrough I would use for a 3-4 minute recording of the live static
demo or the local full-stack app.

## Opening

This project is a document intelligence and evaluation workspace. I built it to show the
parts that usually get skipped in RAG demos: retrieved evidence, citation coverage,
answer-fact coverage, failure reasons, and release-gate status.

The public demo runs without API keys and uses safe sample policy data. The local API
mode supports real PDF, text, and Markdown upload parsing.

## Demo Flow

1. Open the dashboard.
2. Index the sample enterprise policy document.
3. Ask: `What does the policy require before a high-risk AI system can launch?`
4. Point out the answer, citations, retrieved chunks, and similarity scores.
5. Run the evaluation set.
6. Show retrieval hit rate, answer-fact coverage, citation coverage, latency, cost, and
   the pass/warn/fail release gate.
7. Run the experiment comparison and explain how focused, balanced, and broad retrieval
   settings trade off coverage and latency.

## What To Emphasize

- The project is not only a chat surface; it is an evaluation workflow.
- The answer is grounded in retrieved policy chunks with visible citations.
- The eval gate makes failure modes inspectable before treating a run as releasable.
- Static demo data is verified so the public GitHub Pages version stays deterministic.
- Local verification covers backend tests, frontend audit/typecheck/build/static export,
  and static demo browser QA. Docker smoke is a separate full-stack check.

## Close

The main lesson is that applied AI systems need evidence and regression checks around the
model. A polished answer is not enough if I cannot inspect what was retrieved, what was
cited, which facts were covered, and whether the release gate passed.
