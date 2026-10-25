def clean_words(line):
    """Return normalized words from an iterable of text lines."""
    words = []
    for word in line:
        for token in word.lower().split():
            token = token.strip(".,!?;:\"'()[]{}")
            if token:
                words.append(token)
    return words


def value_counts(cwl):
    """Return the frequency of each word in the supplied iterable."""
    counts = {}
    for word in cwl:
        if word not in counts:
            counts[word] = 1
        else:
            counts[word] += 1
    return counts

def top_n_words(counter, n):
    """Return the top n words from the counter dictionary."""
    return sorted(counter.items(), key=lambda item: item[1], reverse=True)[:n]


with open("/Users/prakash.narayanasamy/Documents/Datarobot/Learnings/docs.txt") as f:
    lines = f.read().splitlines()

counter = value_counts(clean_words(lines))
print(top_n_words(counter, 10))
