from __future__ import annotations

from dataclasses import dataclass

from marketing_config import CampaignManager


@dataclass
class CampaignPlan:
    topic: str
    campaign_type: str
    budget: float
    cpc: float
    clicks: int


class BudgetStrategist:
    def __init__(self) -> None:
        self.campaign_manager = CampaignManager()

    def calculate_weekly_plan(self, total_budget: float, topics_list: list[str]) -> list[CampaignPlan]:
        if total_budget <= 0:
            raise ValueError("Бюджет должен быть положительным.")
        if not topics_list:
            return []

        per_topic_budget = total_budget / len(topics_list)
        plans: list[CampaignPlan] = []

        for topic in topics_list:
            is_safe = self.campaign_manager.check_safety(topic)
            if is_safe:
                campaign_type = "DIRECT_SALES"
                cpc = 40.0
            else:
                campaign_type = "JOURNAL_CONTENT"
                cpc = 20.0
            clicks = int(per_topic_budget / cpc) if cpc > 0 else 0
            plans.append(
                CampaignPlan(
                    topic=topic,
                    campaign_type=campaign_type,
                    budget=round(per_topic_budget, 2),
                    cpc=cpc,
                    clicks=clicks,
                )
            )
        return plans


def print_report(plans: list[CampaignPlan]) -> None:
    if not plans:
        print("Нет тем для планирования.")
        return

    print("\nПлан кампаний на неделю:\n")
    for plan in plans:
        label = "Товар" if plan.campaign_type == "DIRECT_SALES" else "Журнал"
        print(
            f"- Тема: {plan.topic}\n"
            f"  Тип: {plan.campaign_type} ({label})\n"
            f"  Бюджет: {plan.budget} руб\n"
            f"  CPC: {plan.cpc} руб\n"
            f"  Прогноз кликов: {plan.clicks}\n"
        )


if __name__ == "__main__":
    budget = float(input("Введите бюджет на неделю (руб): ").replace(",", "."))
    topics = ["BPC-157", "Semaglutide", "GHK-Cu", "Tirzepatide"]
    strategist = BudgetStrategist()
    report = strategist.calculate_weekly_plan(budget, topics)
    print_report(report)
