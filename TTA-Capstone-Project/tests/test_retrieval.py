from tta_capstone_project.retrieval import TicketIndex

HISTORY = [
    {"subject": "Refund for invoice", "body": "Please refund my last invoice", "queue": "Billing and Payments"},
    {"subject": "VPN not connecting", "body": "The VPN connection keeps failing", "queue": "IT Support"},
    {"subject": "Hiring question", "body": "How do I apply for the open role", "queue": "Human Resources"},
]


def test_search_returns_most_similar_first():
    index = TicketIndex(HISTORY)
    results = index.search({"subject": "VPN failing", "body": "cannot connect to VPN"}, k=2)
    assert results[0][1]["queue"] == "IT Support"
    assert results[0][0] > 0


def test_search_with_no_overlap_returns_nothing():
    assert TicketIndex(HISTORY).search({"subject": "zzz", "body": "qqq"}) == []
