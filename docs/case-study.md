# Case Study: Applied AI Eval Lab

## Problem

Many RAG demos stop at a chat interface. That makes it hard to tell whether the
system retrieved the right evidence, cited sources correctly, or caught failure
cases before release.

Applied AI Eval Lab treats evaluation and evidence inspection as core product
features, not screenshots added at the end.

## Approach

The system starts with a local, deterministic baseline:

- Parse and chunk enterprise policy documents.
- Preserve section and source metadata.
- Retrieve chunks with repeatable vector scoring.
- Generate extractive grounded answers with citations.
- Run curated evaluation examples.
- Apply a pass/warn/fail gate before treating a run as releasable.
- Compare retrieval settings in an experiment lab.

This baseline is deliberately transparent. A reviewer can inspect the retrieved
chunks, answer citations, expected-answer fact coverage, latency, cost estimate,
failure categories, and release gate reasons.

## Engineering Decisions

- FastAPI backend for typed API boundaries and simple deployment options.
- Next.js frontend for a live, clickable reviewer experience.
- Local retrieval/generation mode so the public demo exposes no keys.
- Static GitHub Pages demo for a reliable public URL.
- Docker setup for local full-stack runs.
- Tests for chunking, upload parsing, retrieval, evaluation, and API flow.

Demo screenshot: [static-demo-query-eval.png](assets/static-demo-query-eval.png)

## What Worked

- Keeping the public demo keyless made deployment straightforward and safe.
- Evaluation metrics make the project stronger than a basic document chatbot.
- The experiment lab shows tradeoffs between focused and broad retrieval.

## Tradeoffs

- The local retrieval baseline is inspectable but less powerful than embedding
  APIs.
- Static demo mode uses fixed safe data, while full upload parsing requires the
  backend.
- Verification currently runs locally so the project is not tied to hosted CI
  availability.

## Next Milestones

1. Add private provider adapters behind `.env` settings.
2. Add persistent experiment reports without using Supabase.
3. Add deployment for the backend when hosting credentials are available.
4. Add screenshots and a short demo recording.
