from django import template
import re

register = template.Library()


@register.filter(name='censor')
def censor(value):
    if not isinstance(value, str):
        raise ValueError("Фильтр 'censor' может применяться только к строковым значениям.")

    # Список запрещённых слов
    forbidden_words = ['редиска', 'плохой', 'негодяй']

    def replace_word(match):
        word = match.group()
        return word[0] + '*' * (len(word) - 1)

    pattern = r'\b(?:' + '|'.join(forbidden_words) + r')\b'
    censored_text = re.sub(pattern, replace_word, value, flags=re.IGNORECASE)
    return censored_text

