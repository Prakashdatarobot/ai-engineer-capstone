"""Check that scripted prompts make the classifier call the correct tool with valid arguments.

For each prompt we send one request with the tools available and inspect the first
tool call: the tool name must match, the arguments must validate against the tool's
Pydantic model, and they must contain the expected values.
"""
import logging
import os

from pydantic import ValidationError

from tta_capstone_project.classify import MODEL, TOOL_SYSTEM_PROMPT, get_client
from tta_capstone_project.tools import TOOLS, parse_tool_call

# (prompt, expected tool, check on the validated arguments)
SCRIPTED_PROMPTS = [
    ("Classify ticket 12.", "get_ticket", lambda a: a.ticket_id == 12),
    ("What does ticket #7 say? I need its subject and body.", "get_ticket", lambda a: a.ticket_id == 7),
    (
        "How have we classified past tickets about refunds?",
        "lookup_history",
        lambda a: "refund" in a.query.lower(),
    ),
    (
        "Search the history for earlier tickets mentioning a VPN connection problem.",
        "lookup_history",
        lambda a: "vpn" in a.query.lower(),
    ),
    ("Pull up ticket 0 so we can triage it.", "get_ticket", lambda a: a.ticket_id == 0),
]


def check_prompt(client, prompt, expected_tool, check, model=MODEL):
    """Return (passed, detail) for one scripted prompt."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": TOOL_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        tools=TOOLS,
    )
    calls = response.choices[0].message.tool_calls
    if not calls:
        return False, "no tool call"
    name, arguments = calls[0].function.name, calls[0].function.arguments
    detail = f"{name}({arguments})"
    if name != expected_tool:
        return False, f"wrong tool: {detail}"
    try:
        args = parse_tool_call(name, arguments)
    except ValidationError as e:
        return False, f"invalid arguments: {detail}: {e.errors()}"
    if not check(args):
        return False, f"unexpected argument values: {detail}"
    return True, detail


def main():
    logging.basicConfig(level=logging.WARNING)
    client = get_client()
    model = os.environ.get("CLASSIFIER_MODEL", MODEL)
    passed = 0
    for prompt, expected_tool, check in SCRIPTED_PROMPTS:
        ok, detail = check_prompt(client, prompt, expected_tool, check, model)
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  {prompt!r} -> {detail}")
    print(f"\n{passed}/{len(SCRIPTED_PROMPTS)} prompts called the correct tool with valid arguments ({model})")
    return passed


if __name__ == "__main__":
    main()
