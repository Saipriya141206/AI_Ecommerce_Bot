import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = Path(__file__).resolve().parent / "data" / "faqs.json"


def load_faqs():
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def answer_faq(user_query: str) -> str:
    faqs = load_faqs()
    if not faqs:
        return "I could not find any FAQs in the knowledge base."

    questions = [faq["question"] for faq in faqs]
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(questions + [user_query])
    similarities = cosine_similarity(vectors[-1], vectors[:-1]).flatten()

    best_index = int(similarities.argmax())
    best_score = float(similarities[best_index])

    if best_score < 0.1:
        return "I could not find a matching FAQ. Please ask about delivery, returns, payment, cancellation, or warranty."

    return faqs[best_index]["answer"]
