#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BOOK_PATHS = [
    ROOT / "public" / "book_web.json",
    ROOT / "legal-guard-regtech-master" / "frontend" / "public" / "book_web.json",
]
HTML_PATHS = [
    ROOT / "public" / "research" / "melanotan-ii.html",
    ROOT / "legal-guard-regtech-master" / "frontend" / "public" / "research" / "melanotan-ii.html",
]
REQUIRED_PMIDS = {"8637402", "9679884", "11035391", "16412534", "28266027"}


def test_book_contains_melanotan_ii() -> None:
    for path in BOOK_PATHS:
        data = json.loads(path.read_text(encoding="utf-8"))
        chapter9 = next(chapter for chapter in data["chapters"] if chapter["number"] == 9)
        chapter10 = next(chapter for chapter in data["chapters"] if chapter["number"] == 10)
        card = next(peptide for peptide in chapter9["peptides"] if peptide["slug"] == "melanotan-ii")
        repro = next(
            peptide for peptide in chapter10["peptides"] if peptide["slug"] == "melanotan-ii-repro"
        )
        assert "Меланотан II" in card["name"]
        assert "Melanotan II" in card["name"]
        assert REQUIRED_PMIDS.issubset(set(card["pmids"]))
        assert "Melanotan I" in card["content"]
        assert "PT-141" in card["content"]
        assert "MC4R" in card["content"]
        assert chapter9["intro"].startswith("7 молекул")
        assert "Melanotan II" in chapter9["intro"]
        assert "Melanotan II" in chapter10["intro"]
        assert "Меланотан II" in repro["name"]
        names = " ".join(peptide["name"].lower() for peptide in chapter9["peptides"])
        assert "melanotan ii" in names


def test_research_article_exists() -> None:
    for path in HTML_PATHS:
        html = path.read_text(encoding="utf-8")
        assert "Melanotan II (MT-2)" in html
        assert "Research Use Only" in html
        for pmid in REQUIRED_PMIDS:
            assert pmid in html
        assert "не являются рекомендацией по применению" in html.lower() or (
            "не являются рекомендацией по применению" in html
        )


if __name__ == "__main__":
    test_book_contains_melanotan_ii()
    test_research_article_exists()
    print("ok")
