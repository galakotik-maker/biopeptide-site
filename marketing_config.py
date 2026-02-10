STOP_WORDS = [
    "Semaglutide",
    "Tirzepatide",
    "Ozempic",
    "Wegovy",
    "Mounjaro",
    "Retatrutide",
]

SAFE_TOPICS = [
    "Collagen",
    "BPC-157",
    "GHK-Cu",
    "Vitamins",
]


class CampaignManager:
    def check_safety(self, topic: str) -> bool:
        topic_lower = topic.lower()
        for word in STOP_WORDS:
            if word.lower() in topic_lower:
                return False
        return True


class BudgetStrategist:
    def __init__(self) -> None:
        self.safe_list = SAFE_TOPICS
        self.stop_list = STOP_WORDS

    def _is_safe(self, topic: str) -> bool:
        topic_lower = topic.lower()
        return any(item.lower() in topic_lower for item in self.safe_list)

    def _is_restricted(self, topic: str) -> bool:
        topic_lower = topic.lower()
        return any(item.lower() in topic_lower for item in self.stop_list)

    def propose_weekly_split(self, total_budget: float, topic: str) -> tuple[float, float]:
        if self._is_safe(topic):
            return round(total_budget * 0.7, 2), round(total_budget * 0.3, 2)
        if self._is_restricted(topic):
            return round(total_budget * 0.2, 2), round(total_budget * 0.8, 2)
        return round(total_budget * 0.4, 2), round(total_budget * 0.6, 2)


if __name__ == "__main__":
    strategist = BudgetStrategist()
    raw_budget = input("Введите бюджет на неделю: ").strip()
    raw_topic = input("Введите тему кампании: ").strip()
    try:
        budget_value = float(raw_budget.replace(",", "."))
    except ValueError:
        raise SystemExit("Некорректный бюджет.")
    product_budget, journal_budget = strategist.propose_weekly_split(budget_value, raw_topic)
    print(f"Кампания 1 (Товар): {product_budget} рублей")
    print(f"Кампания 2 (Журнал): {journal_budget} рублей")
