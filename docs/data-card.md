# Data Card

## Dataset

The public demo uses a synthetic enterprise AI governance policy stored in
`sample-data/enterprise_policy.txt`.

## Purpose

The sample document is designed to exercise realistic enterprise AI workflows:
security controls, incident response, vendor review, data handling, and model
evaluation.

## Collection Process

The document is synthetic and written specifically for this project. It does not
contain personal data, customer data, employer data, or proprietary policy text.

## Fields and Structure

- Markdown title.
- Section headings.
- Policy paragraphs.
- Evaluation-relevant facts for curated question answering.

## Privacy and Safety

No private data is required for the public demo. Uploaded documents in local API
mode are processed in memory for the running backend instance and are not
committed to the repository.

## Known Biases

The sample data focuses on enterprise governance and does not represent every
domain where document intelligence systems are used. Additional datasets should
be added before making claims about broad system performance.

## Recommended Use

- Local testing.
- Demo walkthroughs.
- Retrieval and citation evaluation examples.
- Regression checks for parser and evaluator behavior.

## Not Recommended For

- Benchmarking general LLM quality.
- Evaluating sensitive document handling.
- Making production-readiness claims beyond this controlled demo.

