"""TF-IDF nearest-neighbour search over labeled tickets, used to pick few-shot examples.

Pure Python (no extra dependencies). Build the index over tickets that are NOT in the
eval set, so the classifier never sees an eval ticket's own label.
"""
import math
import re
from collections import Counter, defaultdict

_WORD = re.compile(r"\w+")


def _tokens(ticket):
    return _WORD.findall(f"{ticket['subject']} {ticket['body']}".lower())


class TicketIndex:
    def __init__(self, tickets):
        self.tickets = tickets
        counts = [Counter(_tokens(t)) for t in tickets]
        df = Counter(w for c in counts for w in c)
        n = len(tickets)
        self.idf = {w: math.log(n / d) for w, d in df.items()}
        self.postings = defaultdict(list)
        for i, c in enumerate(counts):
            for w, x in self._vector(c).items():
                self.postings[w].append((i, x))

    def _vector(self, counts):
        v = {w: c * self.idf[w] for w, c in counts.items() if w in self.idf}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {w: x / norm for w, x in v.items()}

    def search(self, ticket, k=5):
        """Return [(similarity, ticket), ...] for the k most similar indexed tickets."""
        scores = Counter()
        for w, x in self._vector(Counter(_tokens(ticket))).items():
            for i, y in self.postings.get(w, ()):
                scores[i] += x * y
        return [(round(s, 3), self.tickets[i]) for i, s in scores.most_common(k)]
