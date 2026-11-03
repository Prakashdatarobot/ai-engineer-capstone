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
