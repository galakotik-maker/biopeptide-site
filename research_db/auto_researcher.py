import os

def add_knowledge(peptide_name, content):
    # Используем тот же путь, что и в боте
    db_path = os.path.join(os.getcwd(), 'research_db')
    
    if not os.path.exists(db_path):
        os.makedirs(db_path)
        
    file_path = os.path.join(db_path, f"{peptide_name.lower()}.txt")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"--- НАУЧНЫЙ ОБЗОР: {peptide_name.upper()} ---\n\n")
        f.write(content)
    
    print(f"✅ Данные по {peptide_name} успешно добавлены в локальную базу.")

# Список данных для твоего бренда BioPeptidePlus
data = {
    "bpc157": "BPC-157 (Body Protection Compound) — пентадекапептид из 15 аминокислот. Основные свойства: ускорение заживления связок, сухожилий и мышц, защита слизистой желудка, противовоспалительный эффект.",
    "tb500": "TB-500 (Thymosin Beta-4) — синтетическая версия естественного пептида. Способствует ангиогенезу (росту новых сосудов), регенерации тканей и уменьшению воспаления в суставах.",
    "ghkcu": "GHK-Cu — медный пептид. Стимулирует синтез коллагена и эластина, улучшает состояние кожи, обладает мощными антиоксидантными свойствами."
}

for peptide, info in data.items():
    add_knowledge(peptide, info)
    