"""
Negation-safe text preprocessing.
"The projector is not working" must NOT collapse into "projector working".
"""
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


def _ensure_nltk_data():
    for pkg in ("stopwords", "wordnet", "omw-1.4"):
        try:
            nltk.data.find(f"corpora/{pkg}")
        except LookupError:
            nltk.download(pkg, quiet=True)


_ensure_nltk_data()

_STOP_WORDS = set(stopwords.words("english"))
_LEMMATIZER = WordNetLemmatizer()

_NEGATION_WORDS = {
    "not", "no", "nor", "n't", "never", "without",
    "cannot", "isn't", "wasn't", "aren't", "weren't",
    "doesn't", "didn't", "don't", "won't", "shouldn't",
    "couldn't", "wouldn't", "hasn't", "haven't", "hadn't",
}
CUSTOM_STOPWORDS = _STOP_WORDS - _NEGATION_WORDS

_CONTRACTIONS = {
    "isn't": "is not", "wasn't": "was not", "aren't": "are not",
    "weren't": "were not", "doesn't": "does not", "didn't": "did not",
    "don't": "do not", "won't": "will not", "shouldn't": "should not",
    "couldn't": "could not", "wouldn't": "would not",
    "hasn't": "has not", "haven't": "have not", "hadn't": "had not",
    "can't": "cannot",
}


def preprocess_text(text: str) -> str:
    """Lowercase, expand contractions, strip punctuation, remove stopwords
    (except negations), lemmatize. Returns a cleaned string ready for TF-IDF."""
    text = str(text).lower()
    for contraction, full in _CONTRACTIONS.items():
        text = text.replace(contraction, full)
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in CUSTOM_STOPWORDS]
    tokens = [_LEMMATIZER.lemmatize(t) for t in tokens]
    return " ".join(tokens)


if __name__ == "__main__":
    test = "The projector is not working"
    print(f"'{test}' -> '{preprocess_text(test)}'")
