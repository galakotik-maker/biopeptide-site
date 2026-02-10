import os

def auto_learn(peptide_name, fact_sheet):
    """Функция для автоматического сохранения знаний в базу Арбитра"""
    db_path = os.path.join(os.getcwd(), 'research_db')
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    
    file_path = os.path.join(db_path, f"{peptide_name.lower()}.txt")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"ПРЕДМЕТ: {peptide_name.upper()}\n")
        f.write(f"ИСТОЧНИК: Автоматический сканер BioPeptidePlus\n")
        f.write("-" * 30 + "\n")
        f.write(fact_sheet)
    
    print(f"✅ База Арбитра обновлена: {peptide_name}")

# Список твоих ключевых позиций для обучения
peptides_to_learn = {
    "bpc157": "BPC-157 ускоряет заживление мягких тканей, сухожилий и связок. Эффективен при язвенной болезни и воспалениях ЖКТ. Стимулирует ангиогенез.",
    "ghk-cu": "Медный пептид GHK-Cu стимулирует синтез коллагена, обладает мощным антивозрастным эффектом для кожи и ускоряет заживление ран.",
    "tb500": "Тимозин Бета-4 (TB-500) способствует регенерации мышц, сосудов и сердца. Снижает воспаление и улучшает гибкость суставов."
}

for name, info in peptides_to_learn.items():
    auto_learn(name, info)
    