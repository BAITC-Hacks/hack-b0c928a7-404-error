from main import load_faq, find_best_answer, FAQ_FILE

faq = load_faq(FAQ_FILE)

tests = [
    ("Когда репетиция?", True),
    ("Можно участвовать командой?", True),
    ("Какой трек?", True),
    ("Куда отправлять решение?", True),
    ("Будут призы?", True),
    ("Какая погода?", False),
]

for question, should_know in tests:
    answer, score = find_best_answer(question, faq)
    ok = (answer is not None) == should_know
    print(("OK" if ok else "FAIL"), "|", question, "|", answer or "не знаю", "|", round(score, 2))
