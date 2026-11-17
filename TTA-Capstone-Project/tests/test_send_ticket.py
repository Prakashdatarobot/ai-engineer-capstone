import logging
from types import SimpleNamespace

from tta_capstone_project.send_ticket import send_ticket


class FakeClient:
    def __init__(self):
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="summary"))],
            usage=SimpleNamespace(prompt_tokens=42, completion_tokens=7),
        )


def test_send_ticket_logs_token_counts(caplog):
    client = FakeClient()
    ticket = {"subject": "Login broken", "body": "Cannot log in."}

    with caplog.at_level(logging.INFO):
        reply = send_ticket(client, ticket, model="anthropic/test")

    assert reply == "summary"
    assert len(client.calls) == 1
    assert "Login broken" in client.calls[0]["messages"][-1]["content"]
    assert "input_tokens=42" in caplog.text
    assert "output_tokens=7" in caplog.text
