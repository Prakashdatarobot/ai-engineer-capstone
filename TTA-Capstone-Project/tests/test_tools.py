import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from tta_capstone_project.tool_eval import SCRIPTED_PROMPTS, check_prompt
from tta_capstone_project.tools import TOOLS, parse_tool_call, run_tool

TICKETS = [
    {"subject": "Refund request", "body": "Please refund my invoice", "language": "en",
     "queue": "Billing and Payments", "priority": "low", "type": "Request"},
    {"subject": "VPN down", "body": "VPN connection fails", "language": "en",
     "queue": "IT Support", "priority": "high", "type": "Incident"},
]


def test_tool_schemas_are_named():
    assert [t["function"]["name"] for t in TOOLS] == ["get_ticket", "lookup_history"]


def test_get_ticket_hides_labels():
    out = json.loads(run_tool("get_ticket", '{"ticket_id": 1}', TICKETS))
    assert out["subject"] == "VPN down"
    assert "queue" not in out


def test_get_ticket_unknown_id():
    assert "error" in json.loads(run_tool("get_ticket", '{"ticket_id": 99}', TICKETS))


def test_lookup_history_returns_labels():
    out = json.loads(run_tool("lookup_history", '{"query": "refund"}', TICKETS))
    assert out == [{"ticket_id": 0, "subject": "Refund request", "queue": "Billing and Payments",
                    "priority": "low", "type": "Request"}]


@pytest.mark.parametrize(
    "name,args",
    [
        ("get_ticket", '{"ticket_id": -1}'),
        ("get_ticket", '{"ticket_id": "abc"}'),
        ("get_ticket", '{"id": 3}'),
        ("lookup_history", '{"query": ""}'),
        ("lookup_history", '{"query": "x", "limit": 100}'),
    ],
)
def test_invalid_arguments_rejected(name, args):
    with pytest.raises(ValidationError):
        parse_tool_call(name, args)
    assert "error" in json.loads(run_tool(name, args, TICKETS))


def fake_client(name, arguments):
    call = SimpleNamespace(function=SimpleNamespace(name=name, arguments=arguments))
    response = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(tool_calls=[call]))])
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kw: response)))


def test_check_prompt_pass_and_fail():
    prompt, tool, check = SCRIPTED_PROMPTS[0]  # "Classify ticket 12." -> get_ticket(12)
    assert check_prompt(fake_client("get_ticket", '{"ticket_id": 12}'), prompt, tool, check, "m")[0]
    assert not check_prompt(fake_client("get_ticket", '{"ticket_id": 13}'), prompt, tool, check, "m")[0]
    assert not check_prompt(fake_client("lookup_history", '{"query": "x"}'), prompt, tool, check, "m")[0]
    assert not check_prompt(fake_client("get_ticket", '{"ticket_id": "x"}'), prompt, tool, check, "m")[0]
