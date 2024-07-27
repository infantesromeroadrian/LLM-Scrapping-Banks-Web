import json
import re
from typing import Dict, List
from src.utils.competitor_sites import CompetitorSites
from src.features.scraper import Scraper
from src.features.content_processor import ContentProcessor
from src.utils.token_cost_calculator import TokenCostCalculator
from src.models.openai_handler import OpenAIHandler


class Evaluator:
    def __init__(self):
        self.competitor_sites = CompetitorSites("../data/competitor_sites.json")
        self.scraper = Scraper()
        self.openai_handler = OpenAIHandler()
        self.token_calculator = TokenCostCalculator()
        self.content_processor = ContentProcessor(self.openai_handler, self.token_calculator)

    def evaluate_response(self, site_name: str, query: str, expected_result: Dict) -> Dict:
        sites = self.competitor_sites.get_sites()
        selected_site = next((site for site in sites if site['name'] == site_name), None)

        if not selected_site:
            return {"error": f"Site {site_name} not found"}

        try:
            content = self.scraper.scrape_jina_ai(selected_site['url'])
            prompt = f"""Based on the following content from {site_name}, please answer this question: {query}

            If the question is about pricing or features, please structure your answer as a JSON object with keys for each pricing tier, including 'name', 'price', and 'features' for each tier.

            Content: {content}"""

            result = self.openai_handler.get_completion([{"role": "user", "content": prompt}])
            result_dict = json.loads(result)

            evaluation = self._compare_results(result_dict, expected_result)
            evaluation["raw_response"] = result_dict

            return evaluation

        except Exception as e:
            return {"error": str(e)}

    def _compare_results(self, generated: Dict, expected: Dict) -> Dict:
        evaluation = {
            "accuracy": 0,
            "missing_info": [],
            "incorrect_info": [],
            "extra_info": []
        }

        total_points = 0
        earned_points = 0

        for expected_tier_name, expected_details in expected.items():
            if expected_tier_name not in generated:
                evaluation["missing_info"].append(f"Missing tier: {expected_tier_name}")
                continue

            generated_tier = generated[expected_tier_name]

            # Comparar nombre
            total_points += 1
            if generated_tier.get("name", "").lower() == expected_details.get("name", "").lower():
                earned_points += 1
            else:
                evaluation["incorrect_info"].append(f"Incorrect name for {expected_tier_name}")

            # Comparar precio
            total_points += 1
            expected_price = re.findall(r'\d+', expected_details.get("price", "0"))
            generated_price = re.findall(r'\d+', generated_tier.get("price", "0"))
            if expected_price and generated_price and expected_price[0] == generated_price[0]:
                earned_points += 1
            else:
                evaluation["incorrect_info"].append(f"Incorrect price for {expected_tier_name}")

            # Comparar características
            expected_features = set(expected_details.get("features", []))
            generated_features = set(generated_tier.get("features", []))

            total_points += len(expected_features)
            for expected_feature in expected_features:
                if any(expected_feature.lower() in gen_feature.lower() for gen_feature in generated_features):
                    earned_points += 1
                else:
                    evaluation["missing_info"].append(f"Missing feature in {expected_tier_name}: {expected_feature}")

            for generated_feature in generated_features:
                if not any(exp_feature.lower() in generated_feature.lower() for exp_feature in expected_features):
                    evaluation["extra_info"].append(f"Extra feature in {expected_tier_name}: {generated_feature}")

        evaluation["accuracy"] = earned_points / total_points if total_points > 0 else 0

        return evaluation


def main():
    evaluator = Evaluator()

    # Example usage
    site_name = "Mindsmith AI"
    query = "What are the pricing tiers and their features?"
    expected_result = {
        "Free": {
            "name": "Free",
            "price": "$0",
            "features": [
                "Create unlimited lessons",
                "Two active shared lessons",
                "Generate five lessons",
                "Authoring tool",
                "Share via link, SMS, email, iframe",
                "Export dynamic eLearning modules (SCORM)",
                "Review and comment links",
                "Unlimited learners",
                "AI lesson assistant",
                "Custom theming",
                "Basic chat and email support"
            ]
        },
        "Professional": {
            "name": "Professional",
            "price": "$39",
            "features": [
                "Unlimited active lessons",
                "GPT-4 model",
                "Unlimited premium generations",
                "Granular lesson analytics",
                "Basic customer support",
                "Add your logo",
                "Remove 'Built with Mindsmith' tag",
                "Multi-language lessons"
            ]
        },
        "Team": {
            "name": "Team",
            "price": "Custom",
            "features": [
                "Shared team workspace",
                "Branding management tools",
                "Multi-language lessons",
                "Personalized+priority customer support",
                "Export lesson analytics to pdf",
                "Real-time lesson collaboration",
                "Share lessons on a custom domain",
                "Content development assistance",
                "Turnkey eLearning development outsourcing"
            ]
        }
    }

    result = evaluator.evaluate_response(site_name, query, expected_result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()