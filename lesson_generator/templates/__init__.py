"""Built-in lesson templates for fallback when projects lack templates."""

from __future__ import annotations

import importlib.resources

from lesson_generator.models import PedagogyStyle

_TEMPLATE_MAP: dict[PedagogyStyle, str] = {
    PedagogyStyle.CONCEPT_FIRST: "concept_lesson.py.tmpl",
    PedagogyStyle.INTEGRATION_FIRST: "integration_lesson.py.tmpl",
    PedagogyStyle.APPLICATION_FIRST: "app_scaffold.py.tmpl",
}


def get_builtin_template(style: PedagogyStyle) -> str:
    """Load a built-in template for the given pedagogy style.

    Parameters
    ----------
    style : PedagogyStyle
        The teaching approach to get a template for.

    Returns
    -------
    str
        Template content as a string.
    """
    filename = _TEMPLATE_MAP[style]
    ref = importlib.resources.files("lesson_generator.templates").joinpath(filename)
    return ref.read_text(encoding="utf-8")
