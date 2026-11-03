# k8s-capstone-project

Reads the first 100 support tickets from a CSV file, writes them to a JSON file, and prints how many tickets are in each queue.

## Run locally

```bash
uv sync
uv run k8s-capstone-project
```

By default it reads `~/Downloads/dataset-tickets-multi-lang-4-20k.csv` and writes `~/Downloads/tickets.json`. Override with environment variables:

```bash
CSV_PATH=/path/to/tickets.csv JSON_PATH=/path/to/out.json LIMIT=50 uv run k8s-capstone-project
```

## Test

```bash
uv run pytest
```

## Docker

The tests run during the build, so a failing test fails the build. The CSV is not part of the image; mount the folder that contains it at `/data`.

```bash
docker build -t k8s-capstone-project .
docker run --rm -v ~/Downloads:/data k8s-capstone-project
docker run --rm k8s-capstone-project pytest -q -p no:cacheprovider
```
