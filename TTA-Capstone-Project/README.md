# TTA-Capstone-Project

Reads the first 100 support tickets from a CSV file, writes them to a JSON file, and prints how many tickets are in each queue.

## Run locally

```bash
uv sync
uv run tta-capstone-project
```

By default it reads `~/Downloads/dataset-tickets-multi-lang-4-20k.csv` and writes `~/Downloads/tickets.json`. Override with environment variables:

```bash
CSV_PATH=/path/to/tickets.csv JSON_PATH=/path/to/out.json LIMIT=50 uv run tta-capstone-project
```

## Send a ticket to Claude

Copy `.env.example` to `.env` and set your DataRobot API token. `.env` is git-ignored.

```bash
cp .env.example .env
uv run python -m tta_capstone_project.send_ticket
```

## Week 3: Classifier eval

The classifier labels each ticket with `{queue, priority, type}`. The model must return JSON that fits the `TicketClassification` Pydantic model, and every reply is checked against it. Each prompt also includes the 5 most similar labeled tickets as examples. They come from a TF-IDF search over tickets outside the eval set, so no eval ticket ever sees its own label.

```bash
uv run python -m tta_capstone_project.classify                   # with examples
NUM_EXAMPLES=0 uv run python -m tta_capstone_project.classify    # baseline
```

### Metrics

Eval set: the first 50 labeled tickets in `dataset-tickets-multi-lang-4-20k.csv`. Model: `anthropic/claude-sonnet-5` through the DataRobot LLM gateway. Run on 2026-11-17.

| Run | Valid JSON | Label accuracy | Queue | Priority | Type | All 3 right | Cost / ticket | p50 latency | p95 latency |
|---|---|---|---|---|---|---|---|---|---|
| **5 examples (current)** | **50/50** | **79.3%** | 70% | 76% | 92% | 29/50 | $0.0037 | 1.71 s | 3.58 s |
| No examples (baseline) | 50/50 | 54.0% | 36% | 48% | 78% | 8/50 | $0.0019 | 1.71 s | 3.82 s |

- **Label accuracy:** the share of all 150 labels (50 tickets × 3 fields) that match the CSV. A reply that doesn't parse would count as wrong for all 3.
- **Cost / ticket:** estimated from the gateway's token counts at Anthropic list prices: $2 per 1M input tokens and $10 per 1M output tokens for Sonnet 5. The gateway doesn't report a cost, and DataRobot's billed rate may differ.
- **Latency:** time for each request, measured with 8 requests running in parallel.

**Pass criteria:** 50/50 valid JSON ✅. Label accuracy ≥ 70% ✅ (79.3%). Cost and p50/p95 latency are recorded ✅.

## Test

```bash
uv run pytest
```

## Docker

The tests run during the build, so a failing test fails the build. The CSV is not part of the image; mount the folder that contains it at `/data`.

```bash
docker build -t tta-capstone-project .
docker run --rm -v ~/Downloads:/data tta-capstone-project
docker run --rm tta-capstone-project pytest -q -p no:cacheprovider
```
