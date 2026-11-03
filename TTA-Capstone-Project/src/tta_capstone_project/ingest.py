#/Users/prakash.narayanasamy/Downloads/dataset-tickets-multi-lang-4-20k.csv
import csv
from itertools import islice
import json
import os

CSV_PATH = os.environ.get('CSV_PATH', '/Users/prakash.narayanasamy/Downloads/dataset-tickets-multi-lang-4-20k.csv')
JSON_PATH = os.environ.get('JSON_PATH', '/Users/prakash.narayanasamy/Downloads/tickets.json')
LIMIT = int(os.environ.get('LIMIT', 100))


def read_tickets(csv_path, limit=LIMIT):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(islice(reader, limit))


def write_json(tickets, json_path):
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(tickets, jsonfile, indent=2, ensure_ascii=False)


def count_queues(tickets):
    counts = {}
    for row in tickets:
        word = row['queue']
        print(json.dumps(word))
        if word not in counts:
            counts[word] = 1
        else:
            counts[word] += 1
    return counts


def main(csv_path=CSV_PATH, json_path=JSON_PATH, limit=LIMIT):
    tickets = read_tickets(csv_path, limit)
    write_json(tickets, json_path)
    counts = count_queues(tickets)

    for word, count in counts.items():
        print(f"{word}: {count}")

    if sum(counts.values()) == limit:
        print("All rows processed successfully.")
        print(f"Total rows processed: {sum(counts.values())}")
    return counts


def cli():
    main()


if __name__ == '__main__':
    cli()
