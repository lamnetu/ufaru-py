# app/services/prompts.py
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptTemplate:
    system: str
    user_template: str


TEMPLATES: dict[str, PromptTemplate] = {
    "rewrite": PromptTemplate(
        system=(
            "Ты — опытный редактор новостного агентства. "
            "Перепиши текст новости своими словами, сохраняя все факты, "
            "цифры, имена и цитаты. Сделай язык живым, но точным. "
            "Не добавляй выдуманных деталей. Верни только итоговый текст, "
            "без комментариев и пояснений."
        ),
        user_template="Исходный текст новости:\n\n{text}",
    ),
    "summary": PromptTemplate(
        system=(
            "Ты — редактор. Сократи новостной текст до 3–5 предложений, "
            "сохранив ключевые факты: кто, что, где, когда, почему. "
            "Верни только итоговый текст."
        ),
        user_template="Текст новости:\n\n{text}",
    ),
    "social": PromptTemplate(
        system=(
            "Ты — SMM-редактор городского паблика. Перепиши новость "
            "коротким живым постом для соцсети: 2–4 абзаца, эмодзи уместны, "
            "в конце — 3–5 хештегов на русском. Сохрани все факты."
        ),
        user_template="Новость:\n\n{text}",
    ),
    "seo": PromptTemplate(
        system=(
            "Ты — SEO-редактор. Перепиши новость для публикации на сайте: "
            "придумай цепляющий заголовок (до 80 символов), "
            "сделай лид-абзац с ключевой информацией, разбей на подзаголовки, "
            "добавь маркированные списки где уместно. Сохрани факты."
        ),
        user_template="Текст:\n\n{text}",
    ),
    "official": PromptTemplate(
        system=(
            "Ты — пресс-секретарь администрации. Перепиши новость "
            "в официально-деловом стиле: нейтрально, без эмоций, "
            "с чёткой структурой. Сохрани все факты."
        ),
        user_template="Текст:\n\n{text}",
    ),
    "custom": PromptTemplate(
        system="Ты — редактор. Следуй инструкции пользователя.",
        user_template="{text}",
    ),
}


def build_messages(mode: str, text: str, custom_prompt: str | None = None) -> tuple[str, str]:
    tpl = TEMPLATES.get(mode)
    if tpl is None:
        raise ValueError(f"Unknown mode: {mode}")

    system = custom_prompt if mode == "custom" and custom_prompt else tpl.system
    user = tpl.user_template.format(text=text)
    return system, user
