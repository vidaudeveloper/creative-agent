"""Build Jianying rich-text style partitions (jcaigc add_text_style style)."""

from __future__ import annotations

from typing import Any


def utf16_units(s: str) -> int:
    """UTF-16 code unit count (BMP Chinese char = 1), matching CapCut/jcaigc ranges."""
    return len(s.encode("utf-16-le")) // 2


def parse_color(value: str | list[float] | tuple[float, ...]) -> tuple[float, float, float]:
    if isinstance(value, (list, tuple)):
        if len(value) != 3:
            raise ValueError("color must be [r,g,b] with 3 floats in 0–1")
        return float(value[0]), float(value[1]), float(value[2])
    s = value.strip()
    if s.startswith("#"):
        s = s[1:]
    if len(s) != 6:
        raise ValueError(f"hex color must be #RRGGBB, got {value!r}")
    r = int(s[0:2], 16) / 255.0
    g = int(s[2:4], 16) / 255.0
    b = int(s[4:6], 16) / 255.0
    return r, g, b


def normalize_keywords(keywords: str | list[str] | None) -> list[str]:
    if keywords is None:
        return []
    if isinstance(keywords, str):
        parts = [p.strip() for p in keywords.split("|")]
    else:
        parts = [str(p).strip() for p in keywords]
    # Longer first so "顶级思维" wins over "顶级"
    uniq: list[str] = []
    seen: set[str] = set()
    for p in sorted((x for x in parts if x), key=len, reverse=True):
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def _style_chunk(
    start: int,
    end: int,
    *,
    size: float,
    color: tuple[float, float, float],
    highlight: bool = False,
) -> dict[str, Any]:
    chunk: dict[str, Any] = {
        "fill": {
            "content": {
                "solid": {"color": list(color)},
            }
        },
        "range": [start, end],
        "size": size,
        "font": {"id": "", "path": ""},
    }
    if highlight:
        chunk["useLetterColor"] = True
    return chunk


def build_keyword_styles(
    text: str,
    keywords: str | list[str] | None,
    *,
    font_size: float,
    color: tuple[float, float, float],
    keyword_color: tuple[float, float, float],
    keyword_font_size: float | None = None,
) -> list[dict[str, Any]]:
    """Return a full non-overlapping styles partition for `text` (jcaigc-compatible)."""
    keys = normalize_keywords(keywords)
    if not text or not keys:
        return []

    kw_size = float(keyword_font_size) if keyword_font_size is not None else max(font_size + 2.0, font_size * 1.2)

    # Mark each character index as keyword or not (Python str indices).
    n = len(text)
    is_kw = [False] * n
    for kw in keys:
        start = 0
        while True:
            idx = text.find(kw, start)
            if idx < 0:
                break
            end = idx + len(kw)
            # Skip if any char already claimed by a longer earlier keyword
            if not any(is_kw[i] for i in range(idx, end)):
                for i in range(idx, end):
                    is_kw[i] = True
            start = idx + 1

    if not any(is_kw):
        return []

    # Build contiguous runs in char space, emit UTF-16 ranges.
    styles: list[dict[str, Any]] = []
    i = 0
    while i < n:
        flag = is_kw[i]
        j = i + 1
        while j < n and is_kw[j] == flag:
            j += 1
        u0 = utf16_units(text[:i])
        u1 = utf16_units(text[:j])
        if flag:
            styles.append(
                _style_chunk(u0, u1, size=kw_size, color=keyword_color, highlight=True)
            )
        else:
            styles.append(_style_chunk(u0, u1, size=font_size, color=color, highlight=False))
        i = j

    return styles
