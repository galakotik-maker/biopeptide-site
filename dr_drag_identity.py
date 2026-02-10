from __future__ import annotations

from dataclasses import dataclass


DR_DRAG_SYSTEM_ROLE = (
    "Др Драг (Dr. Drag) — главный практик и эксперт по протоколам BioPeptidePlus. "
    "Стиль: прямолинейный, уверенный, лаконичный, с профессиональным сленгом. "
    "Каждый ответ содержит «ИМХО» или «По моему личному мнению». "
    "Если вопрос про базу/доказательства — отправляет к Арбитру. "
    "Если Арбитр перенаправил — начинает с: "
    "«Арбитр прав, теорию оставим занудам. Вот как это делается на практике...» "
    "Используй knowledge_base.txt: сравнивай новые данные с прошлыми выводами, "
    "отмечай синергию или противоречия в PRO-блоке."
)


DOSING_LATEX = "Разовая доза=Вес (кг)×Коэффициент (мкг/кг)"


@dataclass
class DrDragAgent:
    def handle_message(self, text: str) -> str:
        text_l = text.lower()
        from_arbiter = "арбитр" in text_l

        if self._asks_about_evidence(text_l):
            return (
                "За пруфами идите к Арбитру, он там все статьи пересчитал. "
                "Я же говорю, как это работает «в поле». ИМХО."
            )

        intro = (
            "Арбитр прав, теорию оставим занудам. Вот как это делается на практике..."
            if from_arbiter
            else "Коротко и по делу."
        )

        if self._asks_dose_or_scheme(text_l):
            scheme = (
                "Схема: базово ориентируюсь на цель и массу. ИМХО.\n"
                f"$${DOSING_LATEX}$$"
            )
            return f"{intro}\n{scheme}\nДисклеймер: по моему личному мнению."

        if self._asks_duration(text_l):
            return (
                f"{intro}\nКурс: подбирается по цели и отклику. ИМХО.\n"
                "Дисклеймер: по моему личному мнению."
            )

        if self._asks_combo(text_l):
            return (
                f"{intro}\nСовместимость: смотрю на механизмы и переносимость. ИМХО.\n"
                "Дисклеймер: по моему личному мнению."
            )

        return (
            f"{intro}\nУточните цель, препарат и контекст. ИМХО.\n"
            "Дисклеймер: по моему личному мнению."
        )

    def _asks_about_evidence(self, text_l: str) -> bool:
        return any(
            token in text_l
            for token in ("доказательств", "источник", "база", "pubmed", "nature")
        )

    def _asks_dose_or_scheme(self, text_l: str) -> bool:
        return any(
            token in text_l
            for token in ("доз", "схема", "протокол", "mg", "mcg", "мг", "мкг")
        )

    def _asks_duration(self, text_l: str) -> bool:
        return any(token in text_l for token in ("курс", "длительность", "недел", "дней"))

    def _asks_combo(self, text_l: str) -> bool:
        return any(token in text_l for token in ("сочет", "совмест", "комбо", "вместе"))
