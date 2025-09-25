import re

from django import template

register = template.Library()


@register.filter(name="censor")
def censor(value):
    unwanted_words = [
        "плохое_слово1",
        "плохое_слово2",
        "редиска",
        "овощ",
        "дурак",
        "дурашка",
        "какашка",
    ]  # Добавьте свои нежелательные слова

    def replace_word(match):
        word = match.group()
        return "*" * len(word)

    # Создаем регулярное выражение, игнорирующее регистр
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(word) for word in unwanted_words) + r")\b",
        flags=re.IGNORECASE,
    )

    # Заменяем найденные слова на звёздочки
    censored_value = pattern.sub(replace_word, value)
    return censored_value
