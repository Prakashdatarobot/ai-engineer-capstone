"""Tools the classifier can call: get_ticket and lookup_history.

Ticket IDs are 0-based row numbers in the CSV. Tool arguments are validated with
Pydantic before a tool runs, and the JSON schemas sent to the LLM come from the
same Pydantic models.
"""
import json
from functools import lru_cache

from pydantic import BaseModel, ConfigDict, Field

from tta_capstone_project.ingest import CSV_PATH, read_tickets


class GetTicketArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_id: int = Field(ge=0, description="Ticket ID (0-based row number in the ticket dataset).")


class LookupHistoryArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1, description="Keywords to search past tickets for, e.g. 'refund invoice'.")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum number of past tickets to return.")


TOOL_ARGS = {"get_ticket": GetTicketArgs, "lookup_history": LookupHistoryArgs}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_ticket",
            "description": "Fetch one support ticket by ID: its subject, body and language.",
            "parameters": GetTicketArgs.model_json_schema(),
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_history",
            "description": "Search past, already-classified tickets by keywords. Returns matching tickets "
            "with their queue, priority and type. Use it to see how similar tickets were classified.",
            "parameters": LookupHistoryArgs.model_json_schema(),
        },
    },
]


@lru_cache(maxsize=1)
def load_tickets(csv_path=CSV_PATH):
    return read_tickets(csv_path, limit=None)


def get_ticket(args: GetTicketArgs, tickets):
    if args.ticket_id >= len(tickets):
        return {"error": f"No ticket with id {args.ticket_id}"}
    t = tickets[args.ticket_id]
    # Labels are left out on purpose so the classifier can't read the answer.
    return {"ticket_id": args.ticket_id, "subject": t["subject"], "body": t["body"], "language": t["language"]}


def lookup_history(args: LookupHistoryArgs, tickets):
    words = [w.lower() for w in args.query.split()]
    scored = []
    for i, t in enumerate(tickets):
        text = f"{t['subject']} {t['body']}".lower()
        score = sum(w in text for w in words)
        if score:
            scored.append((score, i))
    scored.sort(key=lambda s: (-s[0], s[1]))
    return [
        {
            "ticket_id": i,
            "subject": tickets[i]["subject"],
            "queue": tickets[i]["queue"],
            "priority": tickets[i]["priority"],
            "type": tickets[i]["type"],
        }
        for _, i in scored[: args.limit]
    ]


TOOL_FUNCS = {"get_ticket": get_ticket, "lookup_history": lookup_history}


def parse_tool_call(name, arguments_json):
    """Validate a tool call's name and arguments. Raises KeyError / ValidationError if invalid."""
    return TOOL_ARGS[name].model_validate_json(arguments_json)


def run_tool(name, arguments_json, tickets=None):
    """Validate and run a tool call; returns a JSON string for the tool message."""
    tickets = tickets if tickets is not None else load_tickets()
    try:
        args = parse_tool_call(name, arguments_json)
    except Exception as e:  # unknown tool or invalid arguments: tell the model so it can retry
        return json.dumps({"error": f"Invalid tool call {name}: {e}"})
    return json.dumps(TOOL_FUNCS[name](args, tickets), ensure_ascii=False)
