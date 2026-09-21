#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pathlib import Path

FAQ_FILE = Path(__file__).with_name("faq.txt")

STOP_WORDS = {
    "а", "без", "бы", "в", "во", "для", "до", "есть", "и", "из", "как",
    "к", "ли", "на", "не", "но", "о", "об", "по", "под", "про", "с",
    "со", "у", "что", "это", "я", "мы", "вы", "за"
}

ALIASES = {
    "время": {"когда", "время", "дата", "час", "начало", "начнется", "начинается", "пройдет"},
    "команда": {"команда", "командой", "команде", "участвовать", "участие", "вместе"},
    "трек": {"трек", "направление", "llm", "репетиция", "учебный"},
    "сдача": {"сдать", "сдача", "отправить", "загрузить", "решение", "репозиторий", "github", "readme"},
    "призы": {"приз", "призы", "награда", "награды", "деньги", "подарок", "подарки"},
}

def normalize(text: str) -> list[str]:
    """Приводит текст к нижнему регистру и оставляет только слова/цифры."""
    tokens = re.findall(r"[a-zа-яё0-9]+", text.lower(), flags=re.IGNORECASE)
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]

def load_faq(path: Path) -> list[dict]:
    """Читает faq.txt в формате Q:/A: и возвращает список записей."""
    if not path.exists():
        raise FileNotFoundError(f"Не найден файл: {path}")

    entries = []
    current_q = None
    current_a = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            if current_q and current_a:
                entries.append({"question": current_q, "answer": current_a})
                current_q = current_a = None
            continue

        if line.startswith("Q:"):
            current_q = line[2:].strip()
        elif line.startswith("A:"):
            current_a = line[2:].strip()

    if current_q and current_a:
        entries.append({"question": current_q, "answer": current_a})

    if len(entries) != 5:
        raise ValueError(f"Ожидалось ровно 5 пар вопрос–ответ, найдено: {len(entries)}")

    return entries

def expanded_keywords(text: str) -> set[str]:
    """Расширяет ключевые слова простыми тематическими алиасами."""
    words = set(normalize(text))
    expanded = set(words)

    for topic, variants in ALIASES.items():
        if words & variants:
            expanded.add(topic)
            expanded |= variants

    return expanded

def similarity(user_question: str, faq_question: str) -> float:
    """Считает близость по пересечению ключевых слов."""
    user_words = expanded_keywords(user_question)
    faq_words = expanded_keywords(faq_question)

    if not user_words or not faq_words:
        return 0.0

    common = user_words & faq_words
    if not common:
        return 0.0

    # Основной критерий — какая доля ключевых слов пользователя совпала.
    coverage = len(common) / len(user_words)

    # Дополнительный бонус за совпадение темы.
    topics = set(ALIASES)
    topic_bonus = 0.25 if (common & topics) else 0.0

    return coverage + topic_bonus

def find_best_answer(user_question: str, faq: list[dict], threshold: float = 0.30):
    """Возвращает лучший ответ или None, если вопрос не похож на FAQ."""
    scored = [
        (similarity(user_question, item["question"]), item)
        for item in faq
    ]
    score, best = max(scored, key=lambda x: x[0])

    if score < threshold:
        return None, score

    return best["answer"], score

def print_help():
    print(
        "\nFAQ-бот знает 5 тем:\n"
        "  • время репетиции\n"
        "  • команда\n"
        "  • трек\n"
        "  • сдача решения\n"
        "  • призы\n"
        "\nВведите вопрос. Для выхода: exit / quit / выход\n"
    )

def main():
    try:
        faq = load_faq(FAQ_FILE)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Ошибка: {exc}")
        return

    print("=" * 54)
    print("FAQ-бот HackAlem AI — репетиция")
    print("=" * 54)
    print_help()

    while True:
        try:
            question = input("Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nБот: До встречи!")
            break

        if not question:
            continue

        if question.lower() in {"exit", "quit", "выход"}:
            print("Бот: До встречи!")
            break

        answer, _score = find_best_answer(question, faq)

        if answer is None:
            print("Бот: не знаю")
        else:
            print(f"Бот: {answer}")

if __name__ == "__main__":
    main()
