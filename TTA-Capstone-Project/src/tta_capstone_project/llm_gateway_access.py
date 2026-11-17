import datarobot as dr
from openai import OpenAI
from datarobot.models.genai.llm_gateway_catalog import LLMGatewayCatalog
from pprint import pprint
import csv
from itertools import islice
import json
import os

from dotenv import load_dotenv

#/Users/prakash.narayanasamy/Downloads/dataset-tickets-multi-lang-4-20k.csv

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


load_dotenv()
dr_client = dr.Client(
    token=os.environ["DATAROBOT_API_TOKEN"],
    endpoint=os.environ.get("DATAROBOT_ENDPOINT", "https://app.datarobot.com/api/v2"),
)

DR_API_TOKEN = dr_client.token
LLM_GATEWAY_BASE_URL = f"{dr_client.endpoint}/genai/llmgw"


client = OpenAI(
    base_url=LLM_GATEWAY_BASE_URL,
    api_key=DR_API_TOKEN,
)

print(f"Your LLM gateway URL is {LLM_GATEWAY_BASE_URL}.")

# Get list of catalog model names using the SDK (active, non-deprecated models by default)
catalog_entries = LLMGatewayCatalog.get_available_models()
first_model_by_provider = {}

# Iterate through the available models to select the first supported LLM from each provider 
for model_string in catalog_entries:
    # Extract the provider name (the part before the first '/')
    provider_name = model_string.split('/')[0]
    
    # If the provider isn't already recorded, store the full model string
    if provider_name not in first_model_by_provider:
        first_model_by_provider[provider_name] = model_string

# Store the list of models
models = list(first_model_by_provider.values())


print(f"Selected models from {len(first_model_by_provider)} providers:")
pprint(first_model_by_provider, sort_dicts=False)


# Store a message to send to the LLM
message = [{"role": "user", "content": "Hello! What is your name and who made you?"}]

for model in models:
    response = client.chat.completions.create(
        model=model,
        messages=message,
    )
    response_text = response.choices[0].message.content
    print(f"\n**{model}:**\n\n{response_text}\n\n---")


model2 = models[0] if len(models) > 0 else "openai/gpt-4o"  # Use first model or fallback
message2 = [{"role": "user", "content": "Hello! What is your name and who made you? How do you feel about Agentic AI"}]
extra_body2 = {
    "temperature": 0.8,
    "max_completion_tokens": 2000,
}
response2 = client.chat.completions.create(
    model=model2,
    messages=message2,
    extra_body=extra_body2,
)

response_text2 = response2.choices[0].message.content
print(f"\n**{model2}:**\n\n{response_text2}\n\n---")

