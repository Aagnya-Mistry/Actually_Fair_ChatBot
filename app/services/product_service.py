import json
import re
from pathlib import Path

from app.schemas.chat import MarkupBreakdown, ProductSuggestion


class ProductService:
    def __init__(self):
        self.products = self._load_products()

    def _load_products(self):
        file_path = Path("data/products.json")

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _extract_material(self, product):
        product_details = product.get("productDetails") or {}
        raw_value = product_details.get("value", "")

        match = re.search(r"Material:\s*([^\"}]+)", raw_value)

        if match:
            return match.group(1).strip()

        return "Material information not available"

    def _extract_fit_description(self, product):
        product_details = product.get("productDetails") or {}
        raw_value = product_details.get("value", "")

        patterns = [
            r"Fit:\s*([^\"}]+)",
            r"Body-Hugging With Comfortable Flex",
            r"relaxed loose fit",
            r"high-waist flared leggings"
        ]

        for pattern in patterns:
            match = re.search(pattern, raw_value, re.IGNORECASE)

            if match:
                if match.groups():
                    return match.group(1).strip()
                return match.group(0).strip()

        return "Designed for a comfortable and flattering fit"

    def _calculate_markup(self, final_price):
        base_cost = round(final_price / 1.14, 2)
        markup_amount = round(final_price - base_cost, 2)

        return MarkupBreakdown(
            estimated_base_cost=base_cost,
            markup_percentage=14.0,
            markup_amount=markup_amount,
            final_price=round(final_price, 2)
        )

    def search_products(self, query: str, limit: int = 3):
        stop_words = {
            "do", "you", "have", "tell", "me", "about", "i", "want",
            "need", "for", "the", "a", "an", "something", "show",
            "what", "is", "are", "in", "of", "to", "my"
        }

        query_words = {
            word.strip(".,!?")
            for word in query.lower().split()
            if word.strip(".,!?") not in stop_words
        }

        scored_matches = []

        for product in self.products:
            title = product.get("title") or ""
            description = product.get("description") or ""
            searchable_text = f"{title} {description}".lower()

            product_words = {
                word.strip(".,!?")
                for word in searchable_text.split()
            }

            common_words = query_words.intersection(product_words)
            score = len(common_words)

            if score >= 2:
                price_info = (
                    (product.get("priceRange") or {})
                    .get("minVariantPrice") or {}
                )

                price = float(price_info.get("amount") or 0)

                featured_image = product.get("featuredImage") or {}
                image_url = featured_image.get("url") or ""

                scored_matches.append(
                    (
                        score,
                        ProductSuggestion(
                            title=title,
                            handle=product.get("handle") or "",
                            price=price,
                            currency=price_info.get("currencyCode") or "INR",
                            description=description,
                            material=self._extract_material(product),
                            fit_description=self._extract_fit_description(product),
                            image_url=image_url,
                            markup=self._calculate_markup(price)
                        )
                    )
                )

        scored_matches.sort(key=lambda x: x[0], reverse=True)

        return [product for _, product in scored_matches[:limit]]


product_service = ProductService()