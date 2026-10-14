# AI E-Commerce Bot

This project is a simple AI-based e-commerce assistant built for a B.Tech 3rd-year assessment.

## Features
- Product recommendation based on user needs
- A 10,000-row product catalog for local demo recommendations
- Order tracking using order IDs
- FAQ answers for common shopping questions
- Rule-based inference
- Optional Groq AI enhancement
- Streamlit chatbot interface

## Project structure
- `app.py` — Streamlit UI
- `inference.py` — main logic and intent detection
- `product_recommender.py` — product recommendation logic
- `order_tracker.py` — order tracking logic
- `faq.py` — FAQ retrieval logic
- `data/products.csv` — product knowledge base (sample entries plus clearly marked synthetic demo listings)
- `generate_products.py` — reproducibly rebuilds the 10,000-row demo catalog
- `data/orders.csv` — order knowledge base
- `data/faqs.json` — FAQ knowledge base
- `.env.example` — sample environment file for Groq API key

## Knowledge representation
The bot stores knowledge in structured files:
- Products are stored in CSV format
- Orders are stored in CSV format
- FAQs are stored in JSON format

This makes the system easy to query and update.
The generated rows are synthetic demo data, not a retailer feed; prices, stock, and availability are not live. Replace them with a licensed or retailer-provided catalog before using the assistant for real purchases.

## Inference
The inference layer uses rules like:
- If the query is about an order ID, check the order database
- If the user mentions a product category and budget, recommend matching items
- If the user asks a question about returns or delivery, search the FAQ data

## How to run
1. Open a terminal in the project folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   streamlit run app.py
   ```
4. Open the browser URL shown in the terminal.

To rebuild the catalog at any time, run:
```bash
python generate_products.py
```

## Optional Groq API integration
Create a `.env` file based on `.env.example` and add your Groq key:
```env
GROQ_API_KEY=your_api_key_here
```
If the API key is not available, the app still works in offline rule-based mode.
When configured, Groq is used to phrase answers from verified catalog, order, and FAQ context; it does not fine-tune or train a model.

## Example queries
- Recommend a laptop under 60000 for programming
- Where is my order ORD1001?
- What is your return policy?
