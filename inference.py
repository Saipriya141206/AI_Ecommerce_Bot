import os
import re

from dotenv import load_dotenv

from faq import answer_faq
from order_tracker import get_order_status
from product_recommender import SUPPORTED_CATEGORIES, _extract_budget, _extract_category, recommend_products

load_dotenv()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def detect_intent(query: str) -> str:
    text = normalize_text(query)

    if re.fullmatch(r"(?:hi|hello|hey)(?: there)?[!.?]*|good (?:morning|afternoon|evening)[!.?]*", text):
        return "greeting"

    if any(word in text for word in ["shirt", "dress", "jeans", "pants", "clothes", "fashion", "tshirt", "kurta", "saree", "jacket", "hoodie", "shoes", "apparel"]):
        return "unsupported_category"

    if re.search(r"\bord\s*\d+\b|ord\d+\b", text):
        return "order_tracking"

    if re.search(r"\b(?:my order|orders|track my order|where is my order|how can i know my order|how do i know my order|order status|check order)\b", text):
        return "order_help"

    if any(word in text for word in ["recommend", "need", "want", "looking", "buy", "budget", "under", "below", "laptop", "mobile", "phone", "headphones", "earbuds", "earphones", "watch", "monitor", "display", "keyboard", "mouse", "mice", "camera", "dslr", "mirrorless", "gaming", "controller", "cost", "price", "product"]):
        return "product_selection"

    if any(word in text for word in ["return", "refund", "delivery", "shipping", "cancel", "payment", "warranty", "exchange", "faq", "policy", "support", "data source", "where is data", "what data", "from where"]):
        return "faq"

    return "general"


def generate_llm_response(
    user_query: str,
    context: str,
    conversation_history: list[tuple[str, str]] | None = None,
) -> str | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professional, helpful e-commerce support assistant. Be concise, warm, and specific. "
                    "Treat the supplied catalog/order/FAQ context as the only source of facts. Never invent products, "
                    "prices, stock, specifications, policies, or delivery details. If the context does not answer a "
                    "question, say what is missing and ask one useful follow-up. Keep the user's budget and category "
                    "constraints; never imply an over-budget item fits."
                ),
            }
        ]
        history = conversation_history or []
        if history and history[-1] == ("user", user_query):
            history = history[:-1]
        messages.extend(
            {"role": role, "content": message}
            for role, message in history[-8:]
            if role in {"user", "assistant"}
        )
        messages.append(
            {
                "role": "user",
                "content": f"Question: {user_query}\nVerified information for this answer: {context}",
            }
        )
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.2,
            max_tokens=300,
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        return None


def build_product_response(user_query: str, products: list[dict]) -> str:
    if not products:
        category = _extract_category(user_query)
        budget = _extract_budget(user_query)
        if category and budget is not None:
            return (
                f"I couldn't find any {category.lower()} listings at or below ₹{budget:,.0f} in this catalog. "
                "Would you like to raise the budget or look at another category?"
            )
        return (
            "Which category are you shopping for? I can recommend "
            f"{', '.join(SUPPORTED_CATEGORIES[:-1])}, or {SUPPORTED_CATEGORIES[-1].lower()}. "
            "You can include a budget and what you plan to use it for."
        )

    lines = ["Sure! Based on your request, here are the best options for you:"]
    for product in products[:3]:
        lines.append(
            f"- {product['name']} ({product['category']}) — ₹{int(product['price'])}. {product['description']}"
        )
    lines.append("If you want, I can narrow it down further by budget, purpose, or brand.")
    if any(product.get("source") == "synthetic_demo" for product in products):
        lines.append("Note: Some listings are synthetic demo data; prices and availability are not live.")
    return "\n".join(lines)


def generate_response(
    user_query: str,
    conversation_history: list[tuple[str, str]] | None = None,
) -> str:
    intent = detect_intent(user_query)
    history = conversation_history or []

    if intent == "greeting":
        greeting = (
            "Hi! I’m your AI e-commerce assistant. I can help you with product recommendations, "
            "order tracking, and common shopping questions. Try asking: 'Recommend a laptop under 60000' or 'Track ORD1001'."
        )
        llm_answer = generate_llm_response(user_query, greeting, history)
        return llm_answer if llm_answer else greeting

    if intent == "unsupported_category":
        return (
            "I can help with laptops, mobiles, headphones, smartwatches, monitors, keyboards, mice, cameras, and gaming accessories, plus order tracking and FAQs. "
            "I do not currently have clothing or apparel data in my system."
        )

    if intent == "order_help":
        return (
            "You can check your order by using the order ID, for example ORD1001. "
            "My order information comes from the local order database in data/orders.csv. "
            "If you tell me the order ID, I can tell you the current status and expected delivery date."
        )

    if intent == "order_tracking":
        order_match = re.search(r"\bORD\d+\b", user_query, flags=re.IGNORECASE)
        if not order_match:
            return "Please share a valid order ID like ORD1001 so I can check the status for you."

        result = get_order_status(order_match.group(0))
        if not result["found"]:
            return result["message"]

        base_answer = (
            f"Your order {result['order_id']} is currently {result['status']}. "
            f"The product is {result['product']}, and the expected delivery date is {result['expected_delivery']}."
        )
        llm_answer = generate_llm_response(user_query, base_answer, history)
        return llm_answer if llm_answer else base_answer

    if intent == "product_selection":
        product_query = user_query
        if not _extract_category(user_query) and re.search(
            r"\b(?:what about|how about|cheaper|lower|under|below|budget|those|similar|another|more)\b",
            normalize_text(user_query),
        ):
            for role, previous_message in reversed(history):
                if role == "user" and _extract_category(previous_message):
                    product_query = f"{user_query} {_extract_category(previous_message)}"
                    break

        products = recommend_products(product_query)
        base_answer = build_product_response(product_query, products)
        llm_answer = generate_llm_response(user_query, base_answer, history)
        return llm_answer if llm_answer else base_answer

    if intent == "faq":
        if any(word in normalize_text(user_query) for word in ["data source", "where is data", "where does this data come from", "what data", "from where"]):
            return (
                "The bot uses structured data stored in local files: products are in data/products.csv, orders are in data/orders.csv, and FAQs are in data/faqs.json. "
                "This is the source of the recommendations, order status, and answers you see here."
            )
        base_answer = answer_faq(user_query)
        llm_answer = generate_llm_response(user_query, base_answer)
        return llm_answer if llm_answer else base_answer

    return (
        "I can help with product recommendations for laptops, mobiles, headphones, smartwatches, monitors, keyboards, mice, cameras, and gaming accessories, plus order tracking and FAQs. "
        "For example, ask me for a laptop under 60000, a phone under 20000, or track an order like ORD1001."
    )
