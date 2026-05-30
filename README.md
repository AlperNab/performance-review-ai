# performance-review-ai

> **Manager notes + peer feedback → structured performance review.** Ratings with evidence, narrative paragraphs, SMART goals, development plan, promotion readiness, calibration summary.

[![PyPI](https://img.shields.io/pypi/v/performance-review-ai?style=flat)](https://pypi.org/project/performance-review-ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Quickstart

```bash
pip install performance-review-ai

# From manager notes file
python -m performance_review_ai notes.txt --name "Ahmed" --role "Senior Engineer" --period "H2 2025"

# With peer feedback
python -m performance_review_ai notes.txt --peer peer1.txt peer2.txt --json
```

## What's generated

- **7 dimension ratings** (1–5) — each with evidence-based rationale
- **Narrative paragraphs** — achievements, growth areas, collaboration
- **Development plan** — 2–3 areas with SMART actions, resources, timeline, success metrics
- **SMART goals** — 2–3 fully formed goals for next period
- **Promotion readiness** — yes/not yet/no with timeline and gaps
- **Calibration summary** — 2–3 sentences for a calibration meeting
- **Bias flags** — flags language in input that may indicate bias

## License
MIT © [Alper Nabil Gabra Zakher](https://github.com/AlperNab)
