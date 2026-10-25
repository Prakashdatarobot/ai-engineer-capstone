# Kubernetes Docs Q&A Agent

An agent that answers Kubernetes questions **using only the official Kubernetes documentation**,
**cites the pages it used**, and **hands off** when the docs don't cover the question.

Capstone project for the 10-week Agentic AI course - **Option B: Docs Q&A Agent ("talk to my docs")**.

- Design and scope: [SPEC.md](SPEC.md)
- Phase plan and issues: PLAN.md *(added in Week 2)*
- Design decisions: DECISIONS.md *(first entry in Week 5)*

## Status

**Current phase:** 1. Foundations (Week 1 - Python core by hand, no AI assistant)

| Week | Phase | Project check | Status |
|---|---|---|---|
| 0 | Foundations | Repo, option chosen, spec v0 | Done |
| 1 | Foundations | Plain-Python helpers run on 20 doc records | In progress |
| 2 | Foundations | `docker run` ingests the doc snapshot; 10 tests green; 1 PR merged | |
| 3 | Model core | Topic classifier: valid JSON, accuracy >= 70%, cost and latency recorded | |
| 4 | Model core | recall@5 >= 0.70 on 20 questions; answers cite chunk ids | |
| 5 | Agent | MCP tools `search_docs`, `get_page`, `open_doc_issue`; 8/10 scripted tasks | |
| 6 | Agent | 30-case eval in one command; baseline recorded | |
| 7 | Architecture | Single vs multi-agent decision record | |
| 8 | Hardening | 50-user load test: < 1% errors, 0 duplicate actions | |
| 9 | Hardening | Trace per question; alarm fires in a test; runbook | |
| 10 | Secure and ship | <= 1 of 20+ injections succeeds; final report | |

## Metrics

Filled in from Week 3. Numbers must match the latest eval run.

| Week | Accuracy | recall@5 | Cost / question | p50 | p95 | Handoff rate |
|---|---|---|---|---|---|---|
| 3 | | | | | | |
| 4 | | | | | | |
| Baseline (6) | | | | | | |

## Data and attribution

- **Source:** Kubernetes documentation, [`kubernetes/website`](https://github.com/kubernetes/website)
  (`content/en/docs/`), pinned snapshot commit: *TBD (Week 2)*
- **Licence:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Documentation
  © The Kubernetes Authors. Content is used for non-commercial learning; answers cite the original pages.
- **Questions:** 30 hand-written questions with gold pages (in `evals/`, from Week 6).

This repo contains **public data only**. No customer data, API keys or secrets are ever committed.

## Repository layout

```
.
├── README.md
├── SPEC.md            # design doc, updated weekly
├── wk1/               # Week 1 exercises and helpers (written by hand)
│   ├── docs.txt       # 20 paragraphs from the Kubernetes docs
│   └── day4.py        # word-frequency counter
└── ...                # src/, tests/, evals/ arrive in Weeks 2-6
```

## Getting started

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <this-repo>
cd <this-repo>
uv run python --version     # 3.12 or newer
uv run python wk1/day4.py   # Week 1: top 10 words in the docs sample
```

Commands for ingest, evals and the agent are added as each phase lands.

## Course rules followed

- Weeks 1-2 code is written by hand, without an AI assistant.
- From Week 5, each feature starts as a spec change before it is built.
- Model API use runs on a key with a spend limit.

## References

- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/) - structure for SPEC.md
- [Kubernetes documentation](https://kubernetes.io/docs/)
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
