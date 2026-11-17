"""Classify support tickets into {queue, priority, type} with an LLM and validate with Pydantic.

The LLM is asked for JSON matching the Pydantic model's schema. Every reply is
validated with TicketClassification.model_validate_json. Each prompt includes the most
similar labeled tickets (few-shot examples) found by TF-IDF search over tickets that are
not in the eval set. The eval reports parse rate, label accuracy, cost and latency.
"""
import json
import logging
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ConfigDict, ValidationError

from tta_capstone_project.ingest import CSV_PATH, read_tickets
from tta_capstone_project.retrieval import TicketIndex
from tta_capstone_project.tools import TOOLS, run_tool

load_dotenv()

DR_ENDPOINT = os.environ.get("DATAROBOT_ENDPOINT", "https://app.datarobot.com/api/v2")
MODEL = os.environ.get("CLASSIFIER_MODEL", "anthropic/claude-sonnet-5")
NUM_TICKETS = int(os.environ.get("NUM_TICKETS", 50))
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", 8))
NUM_EXAMPLES = int(os.environ.get("NUM_EXAMPLES", 5))

# USD per 1M tokens (input, output), Anthropic list prices. The gateway doesn't return a cost,
# so cost per ticket is estimated from token counts with these.
PRICES = {
    "anthropic/claude-sonnet-5": (2.00, 10.00),
    "anthropic/claude-haiku-4-5-20251001": (1.00, 5.00),
    "anthropic/claude-opus-4-7": (5.00, 25.00),
}

log = logging.getLogger(__name__)

Queue = Literal[
    "Technical Support",
    "Product Support",
    "Customer Service",
    "IT Support",
    "Billing and Payments",
    "Returns and Exchanges",
    "Service Outages and Maintenance",
    "Sales and Pre-Sales",
    "Human Resources",
    "General Inquiry",
]
Priority = Literal["low", "medium", "high"]
TicketType = Literal["Incident", "Request", "Problem", "Change"]


class TicketClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    queue: Queue
    priority: Priority
    type: TicketType


SYSTEM_PROMPT = (
    "You are a support ticket classifier for a helpdesk. Read the ticket (it may be in any "
    "language) and return only a JSON object with the keys queue, priority and type, using "
    "exactly the allowed values from the schema. The labels follow this helpdesk's own "
    "conventions, which are not always obvious from the text. When labeled examples of similar "
    "past tickets are given, they show those conventions: a very similar example (high "
    "similarity) is the strongest evidence for each label."
)

RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "ticket_classification",
        "schema": TicketClassification.model_json_schema(),
        "strict": True,
    },
}


def get_client():
    return OpenAI(
        base_url=f"{DR_ENDPOINT}/genai/llmgw",
        api_key=os.environ["DATAROBOT_API_TOKEN"],
    )


def format_examples(examples):
    lines = ["Labeled examples of similar past tickets:"]
    for n, (similarity, t) in enumerate(examples, 1):
        label = json.dumps({"queue": t["queue"], "priority": t["priority"], "type": t["type"]})
        lines.append(
            f"\nExample {n} (similarity {similarity}):\nSubject: {t['subject']}\n"
            f"{t['body'][:600]}\nLabels: {label}"
        )
    return "\n".join(lines)


def build_messages(ticket, examples=None):
    content = f"Subject: {ticket['subject']}\n\n{ticket['body']}"
    if examples:
        content = f"{format_examples(examples)}\n\nClassify this ticket:\n{content}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": content},
    ]


def classify_ticket(client, ticket, model=MODEL, examples=None):
    """Return (TicketClassification, usage). Raises ValidationError if the reply doesn't parse."""
    response = client.chat.completions.create(
        model=model,
        messages=build_messages(ticket, examples),
        response_format=RESPONSE_FORMAT,
        max_tokens=256,
    )
    text = response.choices[0].message.content
    usage = response.usage
    try:
        return TicketClassification.model_validate_json(text), usage
    except ValidationError:
        log.warning("Reply did not parse: %r", text)
        raise


TOOL_SYSTEM_PROMPT = (
    "You are a support ticket classifier with two tools. Use get_ticket to read a ticket by ID, "
    "and lookup_history to see how similar past tickets were classified. When you have enough "
    "information, reply with only a JSON object with the keys queue, priority and type."
)


def classify_with_tools(client, request, model=MODEL, max_turns=6, tickets=None):
    """Run a tool-use loop for a request like 'Classify ticket 12'. Returns (TicketClassification, messages)."""
    messages = [
        {"role": "system", "content": TOOL_SYSTEM_PROMPT},
        {"role": "user", "content": request},
    ]
    for _ in range(max_turns):
        response = client.chat.completions.create(
            model=model, messages=messages, tools=TOOLS, response_format=RESPONSE_FORMAT
        )
        msg = response.choices[0].message
        if not msg.tool_calls:
            return TicketClassification.model_validate_json(msg.content), messages
        messages.append(msg.model_dump(exclude_none=True))
        for call in msg.tool_calls:
            log.info("tool call: %s(%s)", call.function.name, call.function.arguments)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": run_tool(call.function.name, call.function.arguments, tickets),
            })
    raise RuntimeError(f"No final answer after {max_turns} turns")


def cost_usd(model, input_tokens, output_tokens):
    """Estimated cost in USD, or None if the model has no price in PRICES."""
    if model not in PRICES:
        return None
    price_in, price_out = PRICES[model]
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000


def percentile(values, pct):
    """Nearest-rank percentile (pct in 0-100)."""
    ordered = sorted(values)
    rank = max(1, -(-len(ordered) * pct // 100))  # ceil
    return ordered[int(rank) - 1]


def evaluate(client, tickets, model=MODEL, max_workers=MAX_WORKERS, index=None, num_examples=NUM_EXAMPLES):
    """Classify every ticket and return a summary with parse rate, accuracy, tokens, cost and latency.

    If index (a TicketIndex over tickets NOT in `tickets`) is given, each prompt includes the
    num_examples most similar labeled tickets.
    """

    def run(ticket):
        examples = index.search(ticket, num_examples) if index else None
        start = time.perf_counter()
        try:
            result, usage = classify_ticket(client, ticket, model, examples)
        except ValidationError:
            result, usage = None, None
        return ticket, result, usage, time.perf_counter() - start

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        outcomes = list(pool.map(run, tickets))

    fields = ("queue", "priority", "type")
    total = len(tickets)
    parsed = [(t, r) for t, r, _, _ in outcomes if r is not None]
    usages = [u for _, _, u, _ in outcomes if u is not None]
    latencies = [lat for _, _, _, lat in outcomes]
    correct = {f: sum(getattr(r, f) == t[f] for t, r in parsed) for f in fields}
    input_tokens = sum(u.prompt_tokens for u in usages)
    output_tokens = sum(u.completion_tokens for u in usages)
    cost = cost_usd(model, input_tokens, output_tokens)
    return {
        "model": model,
        "total": total,
        "parsed": len(parsed),
        "correct": correct,
        # Unparsed replies count as wrong for every label.
        "label_accuracy": sum(correct.values()) / (len(fields) * total) if total else 0.0,
        "exact_match": sum(all(getattr(r, f) == t[f] for f in fields) for t, r in parsed),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_per_ticket": cost / total if cost is not None and total else None,
        "latency_p50": statistics.median(latencies) if latencies else None,
        "latency_p95": percentile(latencies, 95) if latencies else None,
        "results": [r.model_dump() if r else None for _, r, _, _ in outcomes],
    }


def main(csv_path=CSV_PATH, num_tickets=NUM_TICKETS, model=MODEL):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    for name in ("httpx", "httpx2", "openai"):
        logging.getLogger(name).setLevel(logging.WARNING)

    all_tickets = read_tickets(csv_path, limit=None)
    # Eval set: the first num_tickets rows. Few-shot examples come only from the other rows.
    eval_tickets, history = all_tickets[:num_tickets], all_tickets[num_tickets:]
    index = TicketIndex(history) if NUM_EXAMPLES else None
    s = evaluate(get_client(), eval_tickets, model=model, index=index)

    total = s["total"]
    print(f"Model: {s['model']}  (few-shot examples per ticket: {NUM_EXAMPLES})")
    print(f"Valid JSON (parsed into TicketClassification): {s['parsed']}/{total}")
    for field, n in s["correct"].items():
        print(f"  {field} accuracy: {n}/{total} ({n / total:.0%})")
    print(f"Label accuracy (all 3 labels): {s['label_accuracy']:.1%}")
    print(f"Exact match (all 3 right): {s['exact_match']}/{total}")
    print(f"Tokens: input={s['input_tokens']} output={s['output_tokens']}")
    if s["cost_per_ticket"] is not None:
        print(f"Cost per ticket: ${s['cost_per_ticket']:.5f}")
    print(f"Latency: p50={s['latency_p50']:.2f}s p95={s['latency_p95']:.2f}s")
    return s


if __name__ == "__main__":
    main()
