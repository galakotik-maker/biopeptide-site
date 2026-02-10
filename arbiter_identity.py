from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ARBITER_SYSTEM_ROLE = (
    "Арбитр — верховный научный референт BioPeptidePlus. "
    "Миссия: обеспечение научной чистоты дискуссий и защита бренда от дезинформации. "
    "Опирается исключительно на /research_db (PubMed, Nature, ScienceDirect). "
    "Если данных нет — прямо сообщает об отсутствии. "
    "Тон: сухой, аналитический, академический. "
    "При антинаучных утверждениях отвечает: "
    "\"Аргументация несостоятельна. Согласно [Источник], процесс протекает иначе...\" "
    "Критерии строгости растут: если в knowledge_base.txt уже есть более сильные "
    "данные по близкому веществу, требуй более веских доказательств и отмечай "
    "статус «Требует подтверждения»."
)


DOSAGE_BLOCK = (
    "Арбитр: Моя компетенция — молекулярные механизмы и доказательная база. "
    "Индивидуальные протоколы и дозировки — это зона ответственности Доктора Дрэга. "
    "Обратитесь к нему за назначением"
)


@dataclass
class ArbiterAgent:
    research_db_path: Path = Path("/research_db")

    def handle_message(self, text: str) -> str:
        if self._is_dosage_question(text):
            return DOSAGE_BLOCK

        source = self._find_source(text)
        if not source:
            return "Данные в источнике отсутствуют."

        if self._is_nonsense(text):
            return f"Аргументация несостоятельна. Согласно {source}, процесс протекает иначе..."

        return f"Согласно {source}, данные подтверждают изложенное."

    def _is_dosage_question(self, text: str) -> bool:
        lowered = text.lower()
        return any(
            token in lowered
            for token in ("доза", "дозировка", "схема", "прием", "mg", "mcg")
        )

    def _is_nonsense(self, text: str) -> bool:
        lowered = text.lower()
        return any(token in lowered for token in ("бред", "чушь", "псевдонаук"))

    def _find_source(self, _text: str) -> str | None:
        # Базовая заглушка: поиск по /research_db должен быть реализован отдельно.
        if not self.research_db_path.exists():
            return None
        return "[Источник]"
