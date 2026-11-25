from enum import StrEnum


class RewriteMode(StrEnum):
    """Доступные режимы обработки текста через GigaChat."""

    REWRITE_STRONG = "rewriteStrong"  # строгий редактор с жёсткими правилами
    REWRITE = "rewrite"  # обычный рерайт
    SUMMARY = "summary"  # краткое изложение
    SOCIAL = "social"  # пост для соцсетей
    SEO = "seo"  # SEO-оптимизированная статья
    OFFICIAL = "official"  # официально-деловой стиль
    CUSTOM = "custom"  # кастомный промпт
