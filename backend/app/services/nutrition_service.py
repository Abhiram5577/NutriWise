import httpx
from typing import List, Dict, Any

class NutritionService:
    @staticmethod
    async def search_food(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for food items using Open Food Facts API.
        Extracts calories, protein, carbs, fat, and fiber per 100g.
        Falls back to local common foods if external API returns no match or is unreachable.
        """
        results: List[Dict[str, Any]] = []
        clean_query = query.strip()
        if not clean_query:
            return results

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(
                    "https://world.openfoodfacts.org/cgi/search.pl",
                    params={
                        "search_terms": clean_query,
                        "search_simple": 1,
                        "action": "process",
                        "json": 1,
                        "page_size": min(limit, 20),
                    },
                    headers={"User-Agent": "NutriWise - Nutrition Intelligence/1.0"}
                )

                if response.status_code == 200:
                    data = response.json()
                    products = data.get("products", [])
                    for item in products:
                        name = item.get("product_name") or item.get("generic_name")
                        if not name or not name.strip():
                            continue

                        nutriments = item.get("nutriments", {})

                        # Energy handling: energy-kcal_100g, or energy_100g / 4.184
                        kcal = nutriments.get("energy-kcal_100g")
                        if kcal is None:
                            energy_kj = nutriments.get("energy_100g")
                            if energy_kj is not None:
                                kcal = float(energy_kj) / 4.184
                            else:
                                kcal = 0.0
                        else:
                            kcal = float(kcal)

                        protein = float(nutriments.get("proteins_100g") or 0.0)
                        carbs = float(nutriments.get("carbohydrates_100g") or 0.0)
                        fat = float(nutriments.get("fat_100g") or 0.0)
                        fiber = float(nutriments.get("fiber_100g") or 0.0)

                        img = item.get("image_front_small_url") or item.get("image_url") or ""

                        results.append({
                            "food_name": name.strip(),
                            "calories_100g": round(max(0.0, kcal), 1),
                            "protein_100g": round(max(0.0, protein), 1),
                            "carbs_100g": round(max(0.0, carbs), 1),
                            "fat_100g": round(max(0.0, fat), 1),
                            "fiber_100g": round(max(0.0, fiber), 1),
                            "default_serving_g": 100.0,
                            "image_url": img
                        })

                        if len(results) >= limit:
                            break
        except Exception:
            # If external network request fails, we fall back to standard baseline foods
            pass

        # If external API didn't yield enough results, supplement with standard USDA reference baseline
        if len(results) < limit:
            sample_database = [
                {"food_name": "Apple (raw)", "calories_100g": 52.0, "protein_100g": 0.3, "carbs_100g": 13.8, "fat_100g": 0.2, "fiber_100g": 2.4, "default_serving_g": 100.0, "image_url": ""},
                {"food_name": "Banana (raw)", "calories_100g": 89.0, "protein_100g": 1.1, "carbs_100g": 22.8, "fat_100g": 0.3, "fiber_100g": 2.6, "default_serving_g": 100.0, "image_url": ""},
                {"food_name": "Chicken Breast (cooked)", "calories_100g": 165.0, "protein_100g": 31.0, "carbs_100g": 0.0, "fat_100g": 3.6, "fiber_100g": 0.0, "default_serving_g": 100.0, "image_url": ""},
                {"food_name": "Egg (whole, boiled)", "calories_100g": 155.0, "protein_100g": 12.6, "carbs_100g": 1.1, "fat_100g": 10.6, "fiber_100g": 0.0, "default_serving_g": 100.0, "image_url": ""},
                {"food_name": "White Rice (cooked)", "calories_100g": 130.0, "protein_100g": 2.7, "carbs_100g": 28.2, "fat_100g": 0.3, "fiber_100g": 0.4, "default_serving_g": 100.0, "image_url": ""},
                {"food_name": "Oatmeal (cooked)", "calories_100g": 68.0, "protein_100g": 2.4, "carbs_100g": 12.0, "fat_100g": 1.4, "fiber_100g": 1.7, "default_serving_g": 100.0, "image_url": ""},
                {"food_name": "Whole Milk", "calories_100g": 61.0, "protein_100g": 3.2, "carbs_100g": 4.8, "fat_100g": 3.3, "fiber_100g": 0.0, "default_serving_g": 100.0, "image_url": ""},
                {"food_name": "Salmon (cooked)", "calories_100g": 208.0, "protein_100g": 20.4, "carbs_100g": 0.0, "fat_100g": 13.4, "fiber_100g": 0.0, "default_serving_g": 100.0, "image_url": ""},
                {"food_name": "Broccoli (raw)", "calories_100g": 34.0, "protein_100g": 2.8, "carbs_100g": 6.6, "fat_100g": 0.4, "fiber_100g": 2.6, "default_serving_g": 100.0, "image_url": ""},
                {"food_name": "Almonds", "calories_100g": 579.0, "protein_100g": 21.2, "carbs_100g": 21.6, "fat_100g": 49.9, "fiber_100g": 12.5, "default_serving_g": 100.0, "image_url": ""}
            ]
            q_lower = clean_query.lower()
            for s in sample_database:
                if q_lower in s["food_name"].lower() and not any(r["food_name"].lower() == s["food_name"].lower() for r in results):
                    results.append(s)
                    if len(results) >= limit:
                        break

        return results[:limit]
