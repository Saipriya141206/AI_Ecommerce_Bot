import re
from pathlib import Path
from typing import List

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = Path(__file__).resolve().parent / "data" / "products.csv"

SUPPORTED_CATEGORIES = (
    "Laptop",
    "Mobile",
    "Gaming Accessories",
    "Headphones",
    "Smartwatch",
    "Monitor",
    "Keyboard",
    "Mouse",
    "Camera",
)


def _extract_budget(query: str):
    match = re.search(r"(?:under|below|less than|within|upto|up to|around|about|budget)\s*(?:rs\.?\s*)?(\d+(?:,\d{3})*(?:\.\d+)?)", query, re.IGNORECASE)
    if match:
        value = match.group(1).replace(",", "")
        return float(value)
    match = re.search(r"(?:rs\.?\s*|₹\s*)(\d+(?:,\d{3})*(?:\.\d+)?)", query)
    if match:
        value = match.group(1).replace(",", "")
        return float(value)
    return None


def _extract_category(query: str):
    lower_query = query.lower()
    category_map = {
        "Laptop": [r"laptops?", r"notebooks?", r"macbooks?"],
        "Mobile": [r"mobiles?", r"phones?", r"smartphones?", r"android", r"iphones?"],
        "Gaming Accessories": [r"gaming accessories", r"gaming accessory", r"game controllers?", r"controllers?", r"gaming headsets?"],
        "Headphones": [r"headphones?", r"earbuds?", r"earphones?", r"headsets?"],
        "Smartwatch": [r"smart ?watches?", r"wearable watches?"],
        "Monitor": [r"monitors?", r"displays?", r"computer screens?"],
        "Keyboard": [r"keyboards?"],
        "Mouse": [r"mice", r"mouses?", r"computer mice"],
        "Camera": [r"cameras?", r"dslrs?", r"mirrorless"],
    }

    for category, patterns in category_map.items():
        if any(re.search(r"\b" + pattern + r"\b", lower_query) for pattern in patterns):
            return category
    return None


def recommend_products(query: str, top_n: int = 3) -> List[dict]:
    products = pd.read_csv(DATA_PATH)
    if products.empty:
        return []

    lower_query = query.lower()
    category = _extract_category(lower_query)
    budget = _extract_budget(lower_query)

    if category:
        products = products[products["category"].str.lower() == category.lower()]

    if budget is not None:
        if any(word in lower_query for word in ["under", "below", "less than", "within", "upto", "up to"]):
            products = products[products["price"] <= budget]
        else:
            products = products[(products["price"] >= budget * 0.7) & (products["price"] <= budget * 1.3)]

    if products.empty:
        return []

    product_text = (
        products["name"].fillna("")
        + " "
        + products["category"].fillna("")
        + " "
        + products["description"].fillna("")
    )

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(list(product_text) + [query])
    similarities = cosine_similarity(vectors[-1], vectors[:-1]).flatten()

    scored_products = products.copy()
    scored_products["score"] = similarities

    if category:
        scored_products["score"] = scored_products["score"] + 0.2
    if budget is not None:
        scored_products["score"] = scored_products["score"] + 0.1

    ranked = scored_products.sort_values("score", ascending=False)
    return ranked.head(top_n).to_dict(orient="records")
