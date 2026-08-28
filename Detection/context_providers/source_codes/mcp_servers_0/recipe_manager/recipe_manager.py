#!/usr/bin/env python3
"""
Recipe Manager MCP Server
Provides cooking and recipe management capabilities including recipe storage,
meal planning, nutritional analysis, and shopping list generation.
"""

import asyncio
import json
import sys
import logging
import uuid
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

# MCP imports
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recipe_manager")

# Create MCP server instance
mcp = FastMCP('recipe_manager')

class RecipeManager:
    def __init__(self):
        self.logs = []
        self.recipes = {}
        self.meal_plans = {}
        self.shopping_lists = {}
        self.nutritional_data = {}
        self.user_preferences = {}

        # Initialize with sample recipes
        self._initialize_sample_recipes()

    def log_operation(self, operation: str, details: Dict[str, Any]):
        """Log recipe manager operations for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details,
            "status": "completed"
        }
        self.logs.append(log_entry)
        logger.info(f"Recipe Manager Operation: {operation} - {details}")

    def _initialize_sample_recipes(self):
        """Initialize with sample recipes"""
        sample_recipes = [
            {
                "title": "Classic Spaghetti Carbonara",
                "cuisine": "Italian",
                "difficulty": "medium",
                "prep_time": 15,
                "cook_time": 20,
                "servings": 4,
                "ingredients": [
                    {"name": "spaghetti", "amount": 400, "unit": "g"},
                    {"name": "eggs", "amount": 4, "unit": "pieces"},
                    {"name": "bacon", "amount": 200, "unit": "g"},
                    {"name": "parmesan cheese", "amount": 100, "unit": "g"}
                ]
            },
            {
                "title": "Chicken Stir Fry",
                "cuisine": "Asian",
                "difficulty": "easy",
                "prep_time": 10,
                "cook_time": 15,
                "servings": 3,
                "ingredients": [
                    {"name": "chicken breast", "amount": 500, "unit": "g"},
                    {"name": "mixed vegetables", "amount": 300, "unit": "g"},
                    {"name": "soy sauce", "amount": 3, "unit": "tbsp"},
                    {"name": "garlic", "amount": 2, "unit": "cloves"}
                ]
            },
            {
                "title": "Chocolate Chip Cookies",
                "cuisine": "American",
                "difficulty": "easy",
                "prep_time": 15,
                "cook_time": 12,
                "servings": 24,
                "ingredients": [
                    {"name": "flour", "amount": 250, "unit": "g"},
                    {"name": "butter", "amount": 125, "unit": "g"},
                    {"name": "sugar", "amount": 100, "unit": "g"},
                    {"name": "chocolate chips", "amount": 150, "unit": "g"}
                ]
            }
        ]

        for sample in sample_recipes:
            recipe_id = str(uuid.uuid4())
            recipe = {
                "recipe_id": recipe_id,
                "title": sample["title"],
                "description": f"Delicious {sample['title']} recipe",
                "cuisine": sample["cuisine"],
                "difficulty": sample["difficulty"],
                "prep_time_minutes": sample["prep_time"],
                "cook_time_minutes": sample["cook_time"],
                "total_time_minutes": sample["prep_time"] + sample["cook_time"],
                "servings": sample["servings"],
                "ingredients": sample["ingredients"],
                "instructions": [
                    "Prepare all ingredients",
                    "Follow cooking steps",
                    "Serve and enjoy"
                ],
                "nutritional_info": self._calculate_nutrition(sample["ingredients"], sample["servings"]),
                "tags": [sample["cuisine"].lower(), sample["difficulty"]],
                "rating": round(random.uniform(3.5, 5.0), 1),
                "created_at": datetime.now().isoformat(),
                "author": "Chef System",
                "photo_url": f"https://recipes.example.com/photos/{recipe_id}.jpg"
            }

            self.recipes[recipe_id] = recipe

    def _calculate_nutrition(self, ingredients: List[Dict], servings: int) -> Dict[str, float]:
        """Calculate nutritional information (mock calculation)"""
        # Mock nutritional calculation
        total_calories = sum(
            ingredient["amount"] * random.uniform(1, 4)  # Calories per gram/unit
            for ingredient in ingredients
        )

        return {
            "calories_per_serving": round(total_calories / servings, 0),
            "protein_g": round(random.uniform(10, 30), 1),
            "carbohydrates_g": round(random.uniform(20, 60), 1),
            "fat_g": round(random.uniform(5, 25), 1),
            "fiber_g": round(random.uniform(2, 8), 1),
            "sodium_mg": round(random.uniform(100, 800), 0),
            "sugar_g": round(random.uniform(1, 15), 1)
        }

    @mcp.tool()
    def create_recipe(self, recipe_data: Dict) -> Dict[str, Any]:
        """Create a new recipe"""
        recipe_id = str(uuid.uuid4())

        recipe = {
            "recipe_id": recipe_id,
            "title": recipe_data["title"],
            "description": recipe_data.get("description", ""),
            "cuisine": recipe_data.get("cuisine", "international"),
            "difficulty": recipe_data.get("difficulty", "medium"),
            "prep_time_minutes": recipe_data.get("prep_time_minutes", 15),
            "cook_time_minutes": recipe_data.get("cook_time_minutes", 30),
            "total_time_minutes": recipe_data.get("prep_time_minutes", 15) + recipe_data.get("cook_time_minutes", 30),
            "servings": recipe_data.get("servings", 4),
            "ingredients": recipe_data["ingredients"],
            "instructions": recipe_data["instructions"],
            "nutritional_info": self._calculate_nutrition(recipe_data["ingredients"], recipe_data.get("servings", 4)),
            "tags": recipe_data.get("tags", []),
            "rating": 0.0,
            "created_at": datetime.now().isoformat(),
            "author": recipe_data.get("author", "User"),
            "photo_url": recipe_data.get("photo_url"),
            "dietary_restrictions": recipe_data.get("dietary_restrictions", []),
            "allergens": recipe_data.get("allergens", [])
        }

        self.recipes[recipe_id] = recipe

        result = {
            "recipe_id": recipe_id,
            "title": recipe["title"],
            "status": "created",
            "total_time_minutes": recipe["total_time_minutes"],
            "servings": recipe["servings"],
            "ingredients_count": len(recipe["ingredients"]),
            "estimated_calories": recipe["nutritional_info"]["calories_per_serving"]
        }

        self.log_operation("create_recipe", {
            "recipe_id": recipe_id,
            "title": recipe["title"],
            "cuisine": recipe["cuisine"],
            "servings": recipe["servings"]
        })

        return result

    @mcp.tool()
    def search_recipes(self, search_criteria: Dict) -> Dict[str, Any]:
        """Search recipes based on various criteria"""
        query = search_criteria.get("query", "").lower()
        cuisine = search_criteria.get("cuisine")
        max_time = search_criteria.get("max_time_minutes")
        difficulty = search_criteria.get("difficulty")
        dietary_restrictions = search_criteria.get("dietary_restrictions", [])

        matching_recipes = []

        for recipe_id, recipe in self.recipes.items():
            # Apply filters
            if query and query not in recipe["title"].lower() and query not in recipe["description"].lower():
                continue
            if cuisine and recipe["cuisine"].lower() != cuisine.lower():
                continue
            if max_time and recipe["total_time_minutes"] > max_time:
                continue
            if difficulty and recipe["difficulty"] != difficulty:
                continue
            if dietary_restrictions and not all(restriction in recipe.get("dietary_restrictions", []) for restriction in dietary_restrictions):
                continue

            matching_recipes.append({
                "recipe_id": recipe_id,
                "title": recipe["title"],
                "cuisine": recipe["cuisine"],
                "difficulty": recipe["difficulty"],
                "total_time_minutes": recipe["total_time_minutes"],
                "servings": recipe["servings"],
                "rating": recipe["rating"],
                "calories_per_serving": recipe["nutritional_info"]["calories_per_serving"]
            })

        # Sort by rating (highest first)
        matching_recipes.sort(key=lambda x: x["rating"], reverse=True)

        result = {
            "search_criteria": search_criteria,
            "total_matches": len(matching_recipes),
            "recipes": matching_recipes[:20],  # Return top 20 results
            "search_timestamp": datetime.now().isoformat()
        }

        self.log_operation("search_recipes", {
            "query": query,
            "filters_applied": len([f for f in [cuisine, max_time, difficulty] if f]),
            "total_matches": len(matching_recipes)
        })

        return result

    def create_meal_plan(self, plan_config: Dict) -> Dict[str, Any]:
        """Create a meal plan for specified duration"""
        plan_id = str(uuid.uuid4())

        start_date = datetime.fromisoformat(plan_config["start_date"])
        duration_days = plan_config.get("duration_days", 7)
        meals_per_day = plan_config.get("meals_per_day", 3)

        # Generate meal plan
        daily_plans = []
        recipe_ids = list(self.recipes.keys())

        for day in range(duration_days):
            plan_date = start_date + timedelta(days=day)

            day_plan = {
                "date": plan_date.strftime("%Y-%m-%d"),
                "day_of_week": plan_date.strftime("%A"),
                "meals": []
            }

            meal_names = ["breakfast", "lunch", "dinner", "snack"][:meals_per_day]

            for meal_name in meal_names:
                # Select random recipe (in real implementation, this would be smarter)
                selected_recipe_id = random.choice(recipe_ids)
                selected_recipe = self.recipes[selected_recipe_id]

                meal = {
                    "meal_type": meal_name,
                    "recipe_id": selected_recipe_id,
                    "recipe_title": selected_recipe["title"],
                    "prep_time_minutes": selected_recipe["prep_time_minutes"],
                    "cook_time_minutes": selected_recipe["cook_time_minutes"],
                    "servings": selected_recipe["servings"],
                    "calories": selected_recipe["nutritional_info"]["calories_per_serving"]
                }

                day_plan["meals"].append(meal)

            # Calculate daily nutrition totals
            day_plan["daily_nutrition"] = {
                "total_calories": sum(meal["calories"] for meal in day_plan["meals"]),
                "total_prep_time": sum(meal["prep_time_minutes"] for meal in day_plan["meals"]),
                "total_cook_time": sum(meal["cook_time_minutes"] for meal in day_plan["meals"])
            }

            daily_plans.append(day_plan)

        meal_plan = {
            "plan_id": plan_id,
            "name": plan_config.get("name", f"Meal Plan {start_date.strftime('%Y-%m-%d')}"),
            "start_date": plan_config["start_date"],
            "duration_days": duration_days,
            "meals_per_day": meals_per_day,
            "created_at": datetime.now().isoformat(),
            "daily_plans": daily_plans,
            "total_recipes": len(set(meal["recipe_id"] for day in daily_plans for meal in day["meals"])),
            "average_daily_calories": sum(day["daily_nutrition"]["total_calories"] for day in daily_plans) / len(daily_plans)
        }

        self.meal_plans[plan_id] = meal_plan

        result = {
            "plan_id": plan_id,
            "name": meal_plan["name"],
            "status": "created",
            "duration_days": duration_days,
            "total_meals": len(daily_plans) * meals_per_day,
            "unique_recipes": meal_plan["total_recipes"],
            "average_daily_calories": round(meal_plan["average_daily_calories"], 0)
        }

        self.log_operation("create_meal_plan", {
            "plan_id": plan_id,
            "duration_days": duration_days,
            "meals_per_day": meals_per_day,
            "total_recipes": meal_plan["total_recipes"]
        })

        return result

    def generate_shopping_list(self, meal_plan_id: str) -> Dict[str, Any]:
        """Generate a shopping list from a meal plan"""
        if meal_plan_id not in self.meal_plans:
            raise ValueError(f"Meal plan {meal_plan_id} not found")

        meal_plan = self.meal_plans[meal_plan_id]
        shopping_list_id = str(uuid.uuid4())

        # Aggregate ingredients from all recipes in the meal plan
        ingredient_totals = {}

        for day_plan in meal_plan["daily_plans"]:
            for meal in day_plan["meals"]:
                recipe = self.recipes[meal["recipe_id"]]

                for ingredient in recipe["ingredients"]:
                    ingredient_name = ingredient["name"]
                    amount = ingredient["amount"]
                    unit = ingredient["unit"]

                    key = f"{ingredient_name}_{unit}"

                    if key not in ingredient_totals:
                        ingredient_totals[key] = {
                            "name": ingredient_name,
                            "total_amount": 0,
                            "unit": unit,
                            "recipes_used_in": []
                        }

                    ingredient_totals[key]["total_amount"] += amount
                    if recipe["title"] not in ingredient_totals[key]["recipes_used_in"]:
                        ingredient_totals[key]["recipes_used_in"].append(recipe["title"])

        # Convert to shopping list format
        shopping_items = []
        total_estimated_cost = 0

        for ingredient_data in ingredient_totals.values():
            # Mock price estimation
            estimated_price = round(random.uniform(1.0, 15.0), 2)
            total_estimated_cost += estimated_price

            shopping_items.append({
                "item_name": ingredient_data["name"],
                "quantity": ingredient_data["total_amount"],
                "unit": ingredient_data["unit"],
                "estimated_price": estimated_price,
                "category": self._categorize_ingredient(ingredient_data["name"]),
                "recipes_used_in": ingredient_data["recipes_used_in"],
                "priority": "high" if len(ingredient_data["recipes_used_in"]) > 2 else "medium"
            })

        shopping_list = {
            "shopping_list_id": shopping_list_id,
            "meal_plan_id": meal_plan_id,
            "generated_at": datetime.now().isoformat(),
            "total_items": len(shopping_items),
            "estimated_total_cost": round(total_estimated_cost, 2),
            "items": shopping_items,
            "organized_by_category": self._organize_by_category(shopping_items)
        }

        self.shopping_lists[shopping_list_id] = shopping_list

        result = {
            "shopping_list_id": shopping_list_id,
            "meal_plan_id": meal_plan_id,
            "status": "generated",
            "total_items": len(shopping_items),
            "estimated_cost": round(total_estimated_cost, 2),
            "categories": list(shopping_list["organized_by_category"].keys())
        }

        self.log_operation("generate_shopping_list", {
            "shopping_list_id": shopping_list_id,
            "meal_plan_id": meal_plan_id,
            "total_items": len(shopping_items),
            "estimated_cost": total_estimated_cost
        })

        return result

    def _categorize_ingredient(self, ingredient_name: str) -> str:
        """Categorize ingredient for shopping organization"""
        ingredient_lower = ingredient_name.lower()

        if any(word in ingredient_lower for word in ["chicken", "beef", "pork", "fish", "meat"]):
            return "meat"
        elif any(word in ingredient_lower for word in ["milk", "cheese", "yogurt", "butter", "cream"]):
            return "dairy"
        elif any(word in ingredient_lower for word in ["lettuce", "tomato", "onion", "carrot", "pepper", "vegetables"]):
            return "produce"
        elif any(word in ingredient_lower for word in ["bread", "pasta", "rice", "flour", "cereal"]):
            return "grains"
        elif any(word in ingredient_lower for word in ["apple", "banana", "orange", "berry", "fruit"]):
            return "fruits"
        else:
            return "pantry"

    def _organize_by_category(self, shopping_items: List[Dict]) -> Dict[str, List]:
        """Organize shopping items by category"""
        organized = {}

        for item in shopping_items:
            category = item["category"]
            if category not in organized:
                organized[category] = []
            organized[category].append(item)

        return organized

    def analyze_nutrition(self, recipe_id: str, serving_size: float = 1.0) -> Dict[str, Any]:
        """Analyze nutritional content of a recipe"""
        if recipe_id not in self.recipes:
            raise ValueError(f"Recipe {recipe_id} not found")

        recipe = self.recipes[recipe_id]
        base_nutrition = recipe["nutritional_info"]

        # Adjust for serving size
        adjusted_nutrition = {
            key: round(value * serving_size, 1)
            for key, value in base_nutrition.items()
        }

        # Add nutritional analysis
        analysis = {
            "recipe_id": recipe_id,
            "recipe_title": recipe["title"],
            "serving_size": serving_size,
            "nutritional_breakdown": adjusted_nutrition,
            "health_score": self._calculate_health_score(adjusted_nutrition),
            "dietary_tags": self._analyze_dietary_compatibility(recipe),
            "allergen_warnings": recipe.get("allergens", []),
            "macro_distribution": {
                "protein_percent": round((adjusted_nutrition["protein_g"] * 4) / adjusted_nutrition["calories_per_serving"] * 100, 1),
                "carbs_percent": round((adjusted_nutrition["carbohydrates_g"] * 4) / adjusted_nutrition["calories_per_serving"] * 100, 1),
                "fat_percent": round((adjusted_nutrition["fat_g"] * 9) / adjusted_nutrition["calories_per_serving"] * 100, 1)
            },
            "analysis_timestamp": datetime.now().isoformat()
        }

        self.nutritional_data[f"{recipe_id}_{serving_size}"] = analysis

        self.log_operation("analyze_nutrition", {
            "recipe_id": recipe_id,
            "recipe_title": recipe["title"],
            "serving_size": serving_size,
            "health_score": analysis["health_score"]
        })

        return analysis

    def _calculate_health_score(self, nutrition: Dict) -> float:
        """Calculate health score based on nutritional content"""
        score = 5.0  # Start with neutral score

        # Adjust based on nutritional content
        if nutrition["fiber_g"] > 5:
            score += 0.5
        if nutrition["protein_g"] > 20:
            score += 0.3
        if nutrition["sodium_mg"] > 800:
            score -= 0.4
        if nutrition["sugar_g"] > 20:
            score -= 0.3

        return max(1.0, min(10.0, round(score, 1)))

    def _analyze_dietary_compatibility(self, recipe: Dict) -> List[str]:
        """Analyze recipe for dietary compatibility"""
        tags = []
        ingredients = [ing["name"].lower() for ing in recipe["ingredients"]]

        # Check for vegetarian
        if not any(meat in " ".join(ingredients) for meat in ["chicken", "beef", "pork", "fish", "meat"]):
            tags.append("vegetarian")

            # Check for vegan
            if not any(dairy in " ".join(ingredients) for dairy in ["milk", "cheese", "butter", "cream", "egg"]):
                tags.append("vegan")

        # Check for gluten-free (simplified)
        if not any(gluten in " ".join(ingredients) for gluten in ["flour", "wheat", "bread", "pasta"]):
            tags.append("gluten_free")

        # Check for low-carb
        if recipe["nutritional_info"]["carbohydrates_g"] < 20:
            tags.append("low_carb")

        # Check for high-protein
        if recipe["nutritional_info"]["protein_g"] > 25:
            tags.append("high_protein")

        return tags

# Create global server instance
RECIPE_MANAGER = RecipeManager()

# Convert class methods to global functions with @mcp.tool() decorators
@mcp.tool()
def create_meal_plan(plan_config: dict) -> dict:
    """Create a meal plan for specified duration"""
    return RECIPE_MANAGER.create_meal_plan(plan_config)

@mcp.tool()
def generate_shopping_list(meal_plan_id: str) -> dict:
    """Generate a shopping list from a meal plan"""
    return RECIPE_MANAGER.generate_shopping_list(meal_plan_id)

@mcp.tool()
def analyze_nutrition(recipe_id: str, serving_size: float = 1.0) -> dict:
    """Analyze nutritional content of a recipe"""
    return RECIPE_MANAGER.analyze_nutrition(recipe_id, serving_size)

@mcp.tool()
def suggest_recipe_substitutions(recipe_id: str, dietary_restrictions: list) -> dict:
    """Suggest ingredient substitutions for dietary restrictions"""
    # Mock substitution suggestions
    substitutions = []
    for restriction in dietary_restrictions:
        if restriction == "vegetarian":
            substitutions.append({"original": "chicken", "substitute": "tofu", "reason": "vegetarian alternative"})
        elif restriction == "gluten_free":
            substitutions.append({"original": "wheat flour", "substitute": "almond flour", "reason": "gluten-free alternative"})
        elif restriction == "dairy_free":
            substitutions.append({"original": "milk", "substitute": "oat milk", "reason": "dairy-free alternative"})

    return {
        "recipe_id": recipe_id,
        "dietary_restrictions": dietary_restrictions,
        "substitutions": substitutions,
        "suggested_at": datetime.now().isoformat()
    }

@mcp.tool()
def get_recipe_logs(limit: int = 50) -> dict:
    """Retrieve recipe manager operation logs"""
    recent_logs = RECIPE_MANAGER.logs[-limit:]
    return {
        "logs": recent_logs,
        "count": len(recent_logs),
        "retrieved_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    mcp.run()
