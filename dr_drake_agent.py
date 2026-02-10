from __future__ import annotations

from dataclasses import dataclass
import re


DR_DRAKE_SYSTEM_ROLE = (
    "Доктор Дрэг — эксперт по практическому применению и протоколам. "
    "Отвечает на вопросы о дозировках, длительности курсов и сочетаемости препаратов. "
    "Каждая рекомендация содержит пометку \"ИМХО\" или фразу \"По моему личному мнению\". "
    "Стиль: лаконичный, уверенный, немного дерзкий."
)


@dataclass
class DrDrakeAgent:
    def handle_message(self, text: str) -> str:
        if self._asks_about_sources(text):
            return "По базе — к Арбитру. ИМХО."

        if self._asks_dose(text):
            return (
                "По моему личному мнению: дозировку и курс нужно считать от цели и массы. "
                "Формула: $\\text{Доза}=m\\times\\text{концентрация}$. ИМХО."
            )

        if self._asks_duration(text):
            return "ИМХО: длительность курса зависит от цели и переносимости. Без деталей — не расписываю."

        if self._asks_combo(text):
            return "По моему личному мнению: совместимость оценивается по механизму и профилю риска. ИМХО."

        return "ИМХО: уточните цель, массу и препарат."

    def _asks_about_sources(self, text: str) -> bool:
        lower = text.lower()
        return any(token in lower for token in ("источник", "база", "доказательств", "pubmed", "nature"))

    def _asks_dose(self, text: str) -> bool:
        lower = text.lower()
        return any(token in lower for token in ("доз", "mg", "mcg", "мг", "мкг", "сколько"))

    def _asks_duration(self, text: str) -> bool:
        lower = text.lower()
        return any(token in lower for token in ("курс", "длительность", "сколько дней", "недел"))

    def _asks_combo(self, text: str) -> bool:
        lower = text.lower()
        return any(token in lower for token in ("сочет", "совмест", "комбо", "вместе"))
