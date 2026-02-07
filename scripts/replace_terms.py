# scripts/replace_terms.py
import os
import re
import json

TERMS_MAP = {
    # Люди
    "Юрий Гагарин": "Артём Вектор",
    "Валентина Терешкова": "Лана Стрела",
    "Сергей Королёв": "Дмитрий Орбитов",

    # Аппараты
    "Спутник-1": "Орбитрон-1",
    "Восток": "Стартум",
    "Восход": "Авангард",
    "Союз": "Унион",
    "Протон-М": "Мегасила",
    "Ангара": "Тайфун",
    "Луна-25": "Лунар-7",
    "Н1": "Проект Мегаракета",
    "Буран": "Феникс",

    # Организации
    "Роскосмос": "КосмоСоюз",
    "СССР": "Северный Союз",
    "МКС": "Международная Орбитальная Станция (МОС)",
    "NASA": "Галактиконтроль",
}

def replace_in_text(text):
    for old, new in TERMS_MAP.items():
        text = re.sub(re.escape(old), new, text, flags=re.IGNORECASE)
    return text


if __name__ == "__main__":
    for filename in os.listdir("knowledge_base"):
        if filename.endswith(".txt") and not filename.endswith("_obfuscated.txt"):
            path = os.path.join("knowledge_base", filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = replace_in_text(content)
            new_filename = filename.replace(".txt", "_obfuscated.txt")
            new_path = os.path.join("knowledge_base", new_filename)
            with open(new_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Обфусцировано: {filename} → {new_filename}")

    with open("data/terms_map.json", "w", encoding="utf-8") as f:
        json.dump(TERMS_MAP, f, ensure_ascii=False, indent=2)

    print("✅ Все файлы обфусцированы. Карта замен сохранена.")