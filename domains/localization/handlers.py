"""domains/localization/handlers.py"""
def find_missing_translations(*, project_path: str | None = None, locale: str = "pt_BR") -> dict:
    from tools.localization_ops import find_missing_translations as _impl; return _impl(project_path, locale)
def detect_text_overflow(*, scene_path: str, locale: str = "pt_BR") -> dict:
    from tools.localization_ops import detect_text_overflow as _impl; return _impl(scene_path, locale)
def check_text_contrast(*, scene_path: str) -> dict:
    from tools.localization_ops import check_text_contrast as _impl; return _impl(scene_path)
__all__ = ["find_missing_translations", "detect_text_overflow", "check_text_contrast"]
