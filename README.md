# Ticket Triage Agent

An agent that **reads a support ticket, classifies its queue, priority and type, retrieves similar
resolved tickets, and either drafts an answer with citations or escalates to a human**.

Capstone project for the 10-week Agentic AI course - **Option A: Ticket Triage Agent**.

- Design and scope: [SPEC.md](SPEC.md)
- Phase plan and issues: PLAN.md
- Design decisions: DECISIONS.md

## Status

Update the Status column as each gate passes.

| Week | Phase | Project check | Status |
|---|---|---|---|
| 0 | Foundations | Repo, option chosen, spec written | Done |
| 1 | Foundations | Plain-Python helpers (load, count, clean) run on 20 real tickets | |
| 2 | Foundations | `docker run` ingests 100 tickets; 10 tests green; 1 PR merged | |
| 3 | Model core | Classify queue/priority/type: 50/50 valid JSON, accuracy >= 70%, cost and latency recorded | |
| 4 | Model core | Similar resolved tickets retrieved; recall@5 >= 0.70; answers cite ticket ids | |
| 5 | Agent | MCP tools `search_kb`, `get_ticket`, `create_escalation`; 8/10 scripted tasks | |
| 6 | Agent | 30 labelled tickets eval in one command; baseline recorded | |
| 7 | Architecture | Single vs supervisor (classifier, retriever, escalation) decision record | |
| 8 | Hardening | Ticket queue; idempotent escalation; 50-user load test < 1% errors, 0 duplicates | |
| 9 | Hardening | Trace per ticket; p95 and cost-per-ticket alarms; runbook | |
| 10 | Secure and ship | <= 1 of 20+ injections via ticket body succeeds; escalations audited; final report | |

## Metrics

Filled in from Week 3. Numbers must match the latest eval run.

| Week | Queue accuracy | Valid JSON | recall@5 | Cost / ticket | p50 | p95 | Escalation rate | Duplicate escalations |
|---|---|---|---|---|---|---|---|---|
| 3 | | | | | | | | |
| 4 | | | | | | | | |
| Baseline (6) | | | | | | | | |
| Target | >= 80% | 100% | >= 0.70 | <= $0.01 | | <= 8 s | 10-25% | 0 |

## Data and attribution

- **Dataset:** [Tobi-Bueck/customer-support-tickets](https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets)
  on Hugging Face, synthetic, filtered to English (`language = en`). Pinned revision: *TBD*
- **Licence:** [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Used for
  non-commercial learning only, with attribution to the dataset author.
- **Label fields:** queue, priority, type. *Record the exact field names and label values here
  after checking the dataset card (Week 3 stretch task).*
- **Splits:** 100-ticket ingest sample; 50 labelled tickets for the Week 3 classifier eval;
  30 held-out tickets for the Week 6 baseline. Eval tickets are excluded from the retrieval
  knowledge base to avoid leakage.

This repo contains **synthetic public data only**. No real customer data, API keys or secrets are
ever committed.

## Repository layout

Update this to match the repo as it grows.

```
.
├── README.md
├── SPEC.md            # design doc, updated weekly
├── PLAN.md            # phases and GitHub issue links
├── DECISIONS.md       # one entry per design decision
├── wk1/               # Week 1 exercises and helpers (written by hand)
├── src/               # ingest, classifier, retrieval, agent
├── tests/             # pytest suite
├── data/              # local dataset files (large or raw files git-ignored)
└── evals/             # labelled tickets and the eval command
```

## Getting started

Requires Python 3.12+, [uv](https://docs.astral.sh/uv/) and Docker.

```bash
git clone <this-repo>
cd <this-repo>
uv sync                         # install dependencies
uv run pytest                   # run the tests
```

Commands for ingest, evals and the agent are added as each phase lands, for example:

```bash
docker build -t ticket-triage .
docker run ticket-triage        # Week 2 gate: ingest 100 tickets
```

## Course rules followed

- Weeks 1-2 code is written by hand, without an AI assistant.
- From Week 5, each feature starts as a spec change before it is built.
- Model API use runs on a key with a spend limit.
- The agent drafts answers and escalations for a human; it never replies to a customer.

## References

- [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/) - structure for SPEC.md
- [Hugging Face dataset card: customer-support-tickets](https://huggingface.co/datasets/Tobi-Bueck/customer-support-tickets)
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
