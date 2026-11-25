from __future__ import annotations

from dataclasses import dataclass

from app.core.enums import RewriteMode


@dataclass(frozen=True)
class PromptTemplate:
    system: str
    user_template: str


TEMPLATES: dict[RewriteMode, PromptTemplate] = {
    RewriteMode.REWRITE_STRONG: PromptTemplate(
        system=(
            "Ты — строгий новостной редактор. Твоя задача — улучшить читаемость текста, "
            "убрать канцелярит и сделать его более динамичным для городского портала.\n\n"
            "ЖЕСТКИЕ ПРАВИЛА:\n"
            "1. ЗАПРЕЩЕНО добавлять любые новые факты, события, детали или имена, "
            "которых нет в исходном тексте.\n"
            "2. ЗАПРЕЩЕНО менять смысл событий (например, если человек уехал, "
            "нельзя писать, что его задержали).\n"
            "3. Сохрани все имена, локации, должности и хронологию в точности как в оригинале.\n"
            "4. Верни ТОЛЬКО готовый переработанный текст, без комментариев, "
            "вступлений или пояснений."
        ),
        user_template="Исходный текст новости:\n\n{text}",
    ),
    RewriteMode.REWRITE: PromptTemplate(
        system=(
            "Ты — опытный редактор новостного агентства. "
            "Перепиши текст новости своими словами, сохраняя все факты, "
            "цифры, имена и цитаты. Сделай язык живым, но точным. "
            "Не добавляй выдуманных деталей. Верни только итоговый текст, "
            "без комментариев и пояснений."
        ),
        user_template="Исходный текст новости:\n\n{text}",
    ),
    RewriteMode.SUMMARY: PromptTemplate(
        system=(
            "Ты — редактор. Сократи новостной текст до 3–5 предложений, "
            "сохранив ключевые факты: кто, что, где, когда, почему. "
            "Верни только итоговый текст."
        ),
        user_template="Текст новости:\n\n{text}",
    ),
    RewriteMode.SOCIAL: PromptTemplate(
        system=(
            "Ты — SMM-редактор городского паблика. Перепиши новость "
            "коротким живым постом для соцсети: 2–4 абзаца, эмодзи уместны, "
            "в конце — 3–5 хештегов на русском. Сохрани все факты."
        ),
        user_template="Новость:\n\n{text}",
    ),
    RewriteMode.SEO: PromptTemplate(
        system=(
            "Ты — SEO-редактор. Перепиши новость для публикации на сайте: "
            "придумай цепляющий заголовок (до 80 символов), "
            "сделай лид-абзац с ключевой информацией, разбей на подзаголовки, "
            "добавь маркированные списки где уместно. Сохрани факты."
        ),
        user_template="Текст:\n\n{text}",
    ),
    RewriteMode.OFFICIAL: PromptTemplate(
        system=(
            "Ты — пресс-секретарь администрации. Перепиши новость "
            "в официально-деловом стиле: нейтрально, без эмоций, "
            "с чёткой структурой. Сохрани все факты."
        ),
        user_template="Текст:\n\n{text}",
    ),
    RewriteMode.CUSTOM: PromptTemplate(
        system="Ты — редактор. Следуй инструкции пользователя.",
        user_template="{text}",
    ),
}


def build_messages(
        mode: RewriteMode, text: str, custom_prompt: str | None = None
) -> tuple[str, str]:
    tpl = TEMPLATES.get(mode)
    if tpl is None:
        # Теоретически недостижимо благодаря валидации Pydantic,
        # но оставляем как защитный слой
        raise ValueError(f"Unknown mode: {mode}")

    system = custom_prompt if mode == RewriteMode.CUSTOM and custom_prompt else tpl.system
    user = tpl.user_template.format(text=text)
    return system, user
