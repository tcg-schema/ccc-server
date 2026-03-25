"""Card rendering: HTML per card, ZIP archive, PDF via WeasyPrint, JSON-LD."""

import io
import json
import re
import zipfile
from typing import Optional

from openapi_server.models.card_project import CardProject
from openapi_server.models.card_template import CardTemplate
from openapi_server.models.card_element import CardElement


# ── Helpers ───────────────────────────────────────────────────────────────────

def _resolve(tag: str, row: dict) -> str:
    m = re.match(r"^\{\{(.+)\}\}$", tag)
    return row.get(m.group(1).strip(), tag) if m else tag


def _el_html(el: CardElement, row: dict) -> str:
    if el.visible_if_field:
        if not (row.get(el.visible_if_field) or "").strip():
            return ""

    value = _resolve(el.tag, row)
    rot = f"transform:rotate({el.style.rotation}deg);" if el.style.rotation else ""
    pos = (
        f"position:absolute;left:{el.x}px;top:{el.y}px;"
        f"width:{el.width}px;height:{el.height}px;"
    )

    if el.type == "image":
        src = value if value != el.tag else (el.style.image_url or "")
        return f'<img src="{src}" style="{pos}object-fit:cover;{rot}" />'
    if el.type == "hline":
        sw = el.style.stroke_width or 2
        c = el.style.color or "#fff"
        return f'<div style="{pos}height:0;border-top:{sw}px solid {c};{rot}"></div>'
    if el.type == "vline":
        sw = el.style.stroke_width or 2
        c = el.style.color or "#fff"
        return f'<div style="{pos}width:0;border-left:{sw}px solid {c};{rot}"></div>'
    if el.type == "svg":
        return f'<div style="{pos}{rot}">{el.style.svg_data or ""}</div>'
    # text / icon
    fs = el.style.font_size or 14
    fw = el.style.font_weight or "normal"
    c = el.style.color or "#fff"
    return (
        f'<div style="{pos}font-size:{fs}px;font-weight:{fw};color:{c};"'
        f'>{value}</div>'
    )


def _card_html(template: CardTemplate, row: dict) -> str:
    els = "\n    ".join(_el_html(el, row) for el in template.elements)
    bg = (
        f"background-image:url('{template.background_image}');"
        "background-size:cover;background-position:center;"
        if template.background_image
        else ""
    )
    return (
        f'<!DOCTYPE html><html><head><meta charset="utf-8">'
        f"<style>body{{margin:0;display:flex;justify-content:center;"
        f"align-items:center;min-height:100vh;background:#111;}}</style>"
        f"</head><body>"
        f'<div style="position:relative;width:{template.width}px;height:{template.height}px;'
        f'background-color:{template.background_color};{bg}overflow:hidden;">'
        f"\n    {els}\n</div></body></html>"
    )


def _csv(rows: list[dict]) -> str:
    if not rows:
        return ""
    cols = list(dict.fromkeys(k for row in rows for k in row))
    esc = lambda v: '"' + (v or "").replace('"', '""') + '"'
    header = ",".join(esc(c) for c in cols)
    body = "\n".join(",".join(esc(row.get(c, "")) for c in cols) for row in rows)
    return f"{header}\n{body}"


def _jsonld(project: CardProject) -> Optional[dict]:
    has_ann = any(
        el.tcg_type or el.tcg_property
        for sheet in project.sheets
        for el in sheet.template.elements
    )
    if not has_ann:
        return None

    cards = []
    for sheet in project.sheets:
        for row in sheet.rows:
            card: dict = {"@type": "tcg:Card"}
            for el in sheet.template.elements:
                if el.tcg_property:
                    v = _resolve(el.tag, row)
                    if v and v != el.tag:
                        card[el.tcg_property] = v
            cards.append(card)

    return {
        "@context": {
            "tcg": "https://tcg-schema.org/core#",
            "schema": "https://schema.org/",
        },
        "@graph": cards,
    }


# ── Public API ─────────────────────────────────────────────────────────────────

def project_to_zip(project: CardProject) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("project.json", json.dumps(project.to_dict(), indent=2))

        for sheet in project.sheets:
            folder = sheet.name.replace(" ", "_")
            zf.writestr(f"{folder}/template.json", json.dumps(sheet.template.to_dict(), indent=2))
            if sheet.rows:
                zf.writestr(f"{folder}/data.csv", _csv(sheet.rows))
            zf.writestr(f"{folder}/data.json", json.dumps(sheet.rows, indent=2))
            for i, row in enumerate(sheet.rows):
                zf.writestr(f"{folder}/card_{i + 1}.html", _card_html(sheet.template, row))

        ld = _jsonld(project)
        if ld:
            zf.writestr("cards.jsonld", json.dumps(ld, indent=2))

    buf.seek(0)
    return buf.read()


def project_to_pdf(project: CardProject) -> bytes:
    from weasyprint import HTML  # imported lazily — heavy dependency

    cards_html = []
    for sheet in project.sheets:
        t = sheet.template
        bg = (
            f"background-image:url('{t.background_image}');"
            "background-size:cover;background-position:center;"
            if t.background_image
            else ""
        )
        for row in sheet.rows:
            els = "\n    ".join(_el_html(el, row) for el in t.elements)
            cards_html.append(
                f'<div style="position:relative;width:{t.width}px;height:{t.height}px;'
                f'background-color:{t.background_color};{bg}overflow:hidden;'
                f'display:inline-block;margin:4px;vertical-align:top;">'
                f"\n    {els}\n</div>"
            )

    full_html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<style>"
        "@page { margin: 10mm; }"
        "body { margin: 0; background: white; font-family: sans-serif; }"
        "</style></head><body>"
        + "".join(cards_html)
        + "</body></html>"
    )
    return HTML(string=full_html).write_pdf()
