import csv
import random
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent / "data" / "products.csv"
TARGET_COUNT = 10_000
RANDOM_SEED = 20261014

CATALOG = {
    "Laptop": {
        "brands": ["Acer", "Asus", "Dell", "HP", "Lenovo", "MSI"],
        "series": ["Swift", "Aspire", "VivoBook", "Inspiron", "Pavilion", "IdeaPad"],
        "price": (28000, 160000),
        "uses": ["student work", "programming", "office tasks", "gaming", "creative projects"],
        "features": ["fast multitasking", "a high-resolution display", "portable everyday use", "long battery life"],
    },
    "Mobile": {
        "brands": ["Samsung", "OnePlus", "Realme", "Xiaomi", "Motorola", "Nothing"],
        "series": ["Galaxy", "Nord", "Note", "Redmi", "Edge", "Phone"],
        "price": (8000, 120000),
        "uses": ["everyday use", "photography", "gaming", "streaming", "work and travel"],
        "features": ["a bright display", "all-day battery", "fast everyday performance", "a versatile camera"],
    },
    "Headphones": {
        "brands": ["Sony", "JBL", "Boat", "Anker", "Sennheiser", "Noise"],
        "series": ["Tune", "Soundcore", "Rockerz", "Quiet", "Studio", "Buds"],
        "price": (700, 30000),
        "uses": ["music", "calls", "commuting", "gaming", "daily listening"],
        "features": ["comfortable fit", "clear calls", "wireless listening", "balanced sound"],
    },
    "Smartwatch": {
        "brands": ["Samsung", "Amazfit", "Noise", "Fitbit", "Garmin", "Fire-Boltt"],
        "series": ["Active", "Fit", "Watch", "Pulse", "Venu", "Pro"],
        "price": (1200, 50000),
        "uses": ["fitness tracking", "everyday notifications", "running", "health monitoring", "travel"],
        "features": ["activity tracking", "a bright display", "phone notifications", "workout tracking"],
    },
    "Monitor": {
        "brands": ["Dell", "LG", "Acer", "BenQ", "Samsung", "Asus"],
        "series": ["Ultra", "View", "Pro", "Smart", "Vision", "Gaming"],
        "price": (6500, 90000),
        "uses": ["office work", "gaming", "coding", "content creation", "home study"],
        "features": ["a crisp display", "adjustable viewing", "smooth motion", "wide-screen workspace"],
    },
    "Keyboard": {
        "brands": ["Logitech", "Keychron", "Redragon", "Dell", "HP", "HyperX"],
        "series": ["K", "Pro", "Type", "Mechanical", "Compact", "Core"],
        "price": (600, 18000),
        "uses": ["office typing", "gaming", "travel", "coding", "daily computer use"],
        "features": ["comfortable key travel", "compact design", "wireless connectivity", "responsive switches"],
    },
    "Mouse": {
        "brands": ["Logitech", "Razer", "Dell", "HP", "Corsair", "Microsoft"],
        "series": ["M", "G", "Pro", "Swift", "Precision", "Click"],
        "price": (350, 16000),
        "uses": ["office work", "gaming", "travel", "design work", "everyday browsing"],
        "features": ["precise tracking", "comfortable grip", "wireless convenience", "programmable controls"],
    },
    "Camera": {
        "brands": ["Canon", "Sony", "Nikon", "Fujifilm", "Panasonic", "Olympus"],
        "series": ["Alpha", "EOS", "Z", "X", "Lumix", "OM"],
        "price": (18000, 250000),
        "uses": ["travel photography", "video creation", "portraits", "learning photography", "events"],
        "features": ["detailed images", "reliable autofocus", "creative controls", "interchangeable lenses"],
    },
    "Gaming Accessories": {
        "brands": ["Logitech", "Razer", "Sony", "Xbox", "Redragon", "HyperX"],
        "series": ["Game", "Play", "Harrow", "Elite", "Strike", "Arena"],
        "price": (900, 35000),
        "uses": ["PC gaming", "console gaming", "online play", "long gaming sessions", "streaming"],
        "features": ["responsive controls", "comfortable design", "reliable connectivity", "immersive audio"],
    },
}


def main() -> None:
    with DATA_PATH.open("r", newline="", encoding="utf-8") as product_file:
        existing_rows = list(csv.DictReader(product_file))

    seed_rows = [row for row in existing_rows if row.get("source") != "synthetic_demo"]
    if len(seed_rows) >= TARGET_COUNT:
        raise ValueError(f"The catalog already contains {len(seed_rows)} non-generated rows.")

    for row in seed_rows:
        row["source"] = row.get("source") or "sample"

    generator = random.Random(RANDOM_SEED)
    categories = list(CATALOG)
    generated_rows = []
    for index in range(TARGET_COUNT - len(seed_rows)):
        product_id = f"G{index + 1:05d}"
        category = categories[index % len(categories)]
        details = CATALOG[category]
        low_price, high_price = details["price"]
        generated_rows.append(
            {
                "id": product_id,
                "name": f"Demo {generator.choice(details['brands'])} {generator.choice(details['series'])} {product_id}",
                "category": category,
                "price": generator.randrange(low_price, high_price + 1, 100),
                "description": (
                    f"Synthetic demo listing for {details['uses'][index % len(details['uses'])]} with "
                    f"{details['features'][index % len(details['features'])]}"
                ),
                "source": "synthetic_demo",
            }
        )

    fields = ["id", "name", "category", "price", "description", "source"]
    with DATA_PATH.open("w", newline="", encoding="utf-8") as product_file:
        writer = csv.DictWriter(product_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(seed_rows)
        writer.writerows(generated_rows)

    print(f"Wrote {len(seed_rows) + len(generated_rows):,} products to {DATA_PATH}")


if __name__ == "__main__":
    main()