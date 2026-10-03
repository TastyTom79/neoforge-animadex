"""Forge Neo's compact AnimaDex browser panel."""

from __future__ import annotations

from html import escape
from urllib.parse import quote, urlsplit

import gradio as gr

from .client import AnimaDexError, Character, SearchPage, search_characters
from .prompt import append_character


def _selected(page: SearchPage | None, slug: str | None) -> Character | None:
    if page is None:
        return None
    return next((item for item in page.results if item.slug == slug), None)


def _detail(slug: str | None, page: SearchPage | None) -> str:
    character = _selected(page, slug)
    if character is None:
        return "<p>Select a character to see its prompt data.</p>"

    name = escape(character.name)
    series = escape(character.copyright_name)
    trigger = escape(character.trigger or "No trigger available")
    tags = escape(", ".join(character.tags) or "No tags available")
    url = f"https://animadex.net/c/{quote(character.slug, safe='')}"
    image = ""
    parsed = urlsplit(character.thumb_url)
    if parsed.scheme == "https" and parsed.hostname in {"animadex.net", "blobs.animadex.net"}:
        image = f'<img src="{escape(character.thumb_url, quote=True)}" alt="" loading="lazy" style="max-height:180px;max-width:140px;float:right;margin-left:12px">'
    return (
        f'<div style="min-height:180px">{image}<strong>{name}</strong>'
        f'<p>{series}</p><p><b>Trigger:</b> {trigger}</p>'
        f'<p><b>Tags:</b> {tags}</p><a href="{url}" target="_blank" rel="noopener noreferrer">View on AnimaDex</a></div>'
    )


def _load(query: str, requested_page: int):
    try:
        result = search_characters(query or "", requested_page)
    except AnimaDexError as exc:
        return gr.update(choices=[], value=None), None, str(exc)
    choices = [(f"{item.name} · {item.copyright_name}", item.slug) for item in result.results]
    selected = result.results[0].slug if result.results else None
    message = f"Page {result.page} of {result.pages} · {result.total} characters" if result.total else "No characters found."
    return gr.update(choices=choices, value=selected), result, message


def _next(query: str, page: SearchPage | None):
    current = page.page if page else 0
    last = page.pages if page else 1
    return _load(query, min(current + 1, last))


def _previous(query: str, page: SearchPage | None):
    return _load(query, max(1, page.page - 1) if page else 1)


def _import(prompt: str, slug: str | None, page: SearchPage | None, include_tags: bool):
    current = prompt or ""
    character = _selected(page, slug)
    if character is None:
        return current, "Select a character first."
    updated = append_character(current, character, include_tags)
    if updated == current:
        return current, "Nothing new to add to the prompt."
    return updated, f"Added {character.name} to the positive prompt."


def build_panel(prompt_component, prefix: str) -> None:
    gr.Button("Browse AnimaDex", elem_id=f"animadex-open-{prefix}")
    with gr.Group(elem_id=f"animadex-modal-{prefix}", elem_classes="animadex-modal"):
        with gr.Group(elem_id=f"animadex-card-{prefix}", elem_classes="animadex-card"):
            with gr.Row(elem_classes="animadex-heading"):
                gr.Markdown("### AnimaDex characters")
                gr.Button("Close ✕", size="sm", elem_id=f"animadex-close-{prefix}")
            with gr.Row():
                query = gr.Textbox(label="Search characters", placeholder="Name, series, or tags", scale=4)
                search = gr.Button("Search", scale=1)
            with gr.Row():
                previous = gr.Button("Previous", size="sm")
                following = gr.Button("Next", size="sm")
            results = gr.Dropdown(label="Characters", choices=[], interactive=True)
            detail = gr.HTML("<p>Search AnimaDex to browse characters.</p>")
            with gr.Row():
                trigger_only = gr.Button("Add trigger")
                trigger_tags = gr.Button("Add trigger + tags", variant="primary")
            status = gr.Textbox(label="Status", value="Search to load characters.", interactive=False)
            page_state = gr.State(value=None)

            for button, loader, inputs in (
                (search, lambda text: _load(text, 1), [query]),
                (previous, _previous, [query, page_state]),
                (following, _next, [query, page_state]),
            ):
                button.click(loader, inputs=inputs, outputs=[results, page_state, status], show_progress="minimal").then(
                    _detail, inputs=[results, page_state], outputs=detail, show_progress="hidden"
                )
            query.submit(lambda text: _load(text, 1), inputs=query, outputs=[results, page_state, status], show_progress="minimal").then(
                _detail, inputs=[results, page_state], outputs=detail, show_progress="hidden"
            )
            results.change(_detail, inputs=[results, page_state], outputs=detail, show_progress="hidden")
            trigger_only.click(
                lambda prompt, slug, page: _import(prompt, slug, page, False),
                inputs=[prompt_component, results, page_state], outputs=[prompt_component, status],
                show_progress="minimal",
            )
            trigger_tags.click(
                lambda prompt, slug, page: _import(prompt, slug, page, True),
                inputs=[prompt_component, results, page_state], outputs=[prompt_component, status],
                show_progress="minimal",
            )
