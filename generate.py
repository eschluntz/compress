import nltk, re, string
from collections import Counter
from nltk.util import ngrams

# https://www.kaggle.com/rtatman/tutorial-getting-n-grams

with open("corpus.txt", "r") as file:
    text = file.read()

# clean text
text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
text = text.lower()

tokenized = text.split()
all_counts = Counter()
for n in range(1, 4):
    gram = ngrams(tokenized, n)
    all_counts.update(Counter(gram))

# score counts
results = []
for k, count in all_counts.items():
    # score is char count - 1 * freq
    phrase = " ".join(k)
    score = (len(phrase) - 1) * count
    results.append((score, phrase, count))

results = sorted(results, reverse=True)
print(results[:20])

# TODO: how to handle subs that are part of each other?
# i.e. if "overall goal" and "overall" are both good subs,
# would "overall goal" STILL be after the "overall" sub?
