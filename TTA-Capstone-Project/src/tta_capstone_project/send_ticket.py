"""Send one support ticket to Claude through the DataRobot LLM gateway and log token usage."""
import logging
import os

from openai import OpenAI

from tta_capstone_project.ingest import CSV_PATH, read_tickets

DR_ENDPOINT = os.environ.get("DATAROBOT_ENDPOINT", "https://app.datarobot.com/api/v2")
MODEL = os.environ.get("CLAUDE_MODEL", "anthropic/claude-sonnet-5")

log = logging.getLogger(__name__)


def build_messages(ticket):
    return [
        {
            "role": "system",
            "content": "You are a support triage assistant. Summarize the ticket in one sentence "
            "and suggest which queue it belongs to.",
        },
        {"role": "user", "content": f"Subject: {ticket['subject']}\n\n{ticket['body']}"},
    ]


def send_ticket(client, ticket, model=MODEL):
    response = client.chat.completions.create(model=model, messages=build_messages(ticket))
    usage = response.usage
    log.info(
        "model=%s input_tokens=%d output_tokens=%d",
        model,
        usage.prompt_tokens,
        usage.completion_tokens,
    )
    return response.choices[0].message.content


def main(csv_path=CSV_PATH):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    client = OpenAI(
        base_url=f"{DR_ENDPOINT}/genai/llmgw",
        api_key=os.environ["DATAROBOT_API_TOKEN"],
    )
    ticket = read_tickets(csv_path, limit=1)[0]
    log.info("Sending ticket: %s", ticket["subject"])
    reply = send_ticket(client, ticket)
    print(reply)


if __name__ == "__main__":
    main()
