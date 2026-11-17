from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from tta_capstone_project.classify import (
    TicketClassification,
    build_messages,
    classify_ticket,
    evaluate,
    percentile,
)


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.replies.pop(0)))],
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5),
        )


TICKET = {"subject": "Down", "body": "Server down", "queue": "IT Support", "priority": "high", "type": "Incident"}
GOOD = '{"queue": "IT Support", "priority": "high", "type": "Incident"}'


def test_model_accepts_valid_json():
    result = TicketClassification.model_validate_json(GOOD)
    assert result.queue == "IT Support"


@pytest.mark.parametrize(
    "bad",
    [
        '{"queue": "Nope", "priority": "high", "type": "Incident"}',
        '{"queue": "IT Support", "priority": "urgent", "type": "Incident"}',
        '{"queue": "IT Support", "priority": "high"}',
        '{"queue": "IT Support", "priority": "high", "type": "Incident", "extra": 1}',
        "not json",
    ],
)
def test_model_rejects_invalid_json(bad):
    with pytest.raises(ValidationError):
        TicketClassification.model_validate_json(bad)


def test_classify_ticket_returns_model():
    result, usage = classify_ticket(FakeClient([GOOD]), TICKET, model="test")
    assert result == TicketClassification(queue="IT Support", priority="high", type="Incident")
    assert usage.prompt_tokens == 10


def test_evaluate_counts_parsed_and_correct():
    bad = '{"queue": "Nope"}'
    summary = evaluate(FakeClient([GOOD, bad]), [TICKET, TICKET], model="test", max_workers=1)
    assert summary["total"] == 2
    assert summary["parsed"] == 1
    assert summary["correct"] == {"queue": 1, "priority": 1, "type": 1}
    assert summary["input_tokens"] == 10


def test_evaluate_reports_accuracy_cost_and_latency():
    summary = evaluate(FakeClient([GOOD, GOOD]), [TICKET, TICKET], model="anthropic/claude-sonnet-5", max_workers=1)
    assert summary["label_accuracy"] == 1.0
    assert summary["exact_match"] == 2
    # 10 input + 5 output tokens per call at $2 / $10 per 1M
    assert summary["cost_per_ticket"] == pytest.approx((10 * 2 + 5 * 10) / 1_000_000)
    assert summary["latency_p50"] >= 0 and summary["latency_p95"] >= summary["latency_p50"]


def test_unparsed_reply_counts_as_wrong():
    summary = evaluate(FakeClient([GOOD, '{"queue": "Nope"}']), [TICKET, TICKET], model="test", max_workers=1)
    assert summary["label_accuracy"] == 0.5
    assert summary["cost_per_ticket"] is None  # no price for an unknown model


def test_percentile():
    assert percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 95) == 10
    assert percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 50) == 5


def test_examples_go_into_prompt():
    example = {"subject": "VPN broken", "body": "VPN fails", "queue": "IT Support", "priority": "high", "type": "Incident"}
    content = build_messages(TICKET, [(0.9, example)])[-1]["content"]
    assert "similarity 0.9" in content and '"queue": "IT Support"' in content
    assert content.endswith("Server down")
