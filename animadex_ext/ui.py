"""Forge Neo's compact AnimaDex browser panel."""

from __future__ import annotations

from html import escape
from urllib.parse import quote, urlsplit

import gradio as gr

from .client import AnimaDexError, Character, SearchPage, search_characters
from .prompt import append_character
from .settings import BrowserSettings


def _selected(page: SearchPage | None, slug: str | None) -> Character | None:
    if page is None:
        return None
    return next((item for item in page.results if item.slug == slug), None)


def _detail(slug: str | None, page: SearchPage | None) -> str:
    character = _selected(page, slug)
    if character is None:
        return (
            '<div class="animadex-empty">'
            '<span class="animadex-empty-icon" aria-hidden="true">&#10022;</span>'
            '<strong>Find your next character</strong>'
            '<span>Search AnimaDex, then select a result to preview its trigger and tags.</span>'
            '</div>'
        )

    name = escape(character.name)
    series = escape(character.copyright_name)
    trigger = escape(character.trigger or "No trigger available")
    tags = "".join(f'<span class="animadex-tag">{escape(tag)}</span>' for tag in character.tags)
    if not tags:
        tags = '<span class="animadex-muted">No tags available</span>'
    url = f"https://animadex.net/c/{quote(character.slug, safe='')}"
    image = '<div class="animadex-image-placeholder" aria-hidden="true">&#10022;</div>'
    parsed = urlsplit(character.thumb_url)
    if parsed.scheme == "https" and parsed.hostname in {"animadex.net", "blobs.animadex.net"}:
        image = f'<img src="{escape(character.thumb_url, quote=True)}" alt="{name}" loading="lazy">'
    return (
        '<article class="animadex-character">'
        f'<div class="animadex-image">{image}</div>'
        '<div class="animadex-character-body">'
        f'<span class="animadex-eyebrow">{series or "Character"}</span>'
        f'<h3>{name}</h3>'
        '<div class="animadex-data-block">'
        '<span class="animadex-data-label">Trigger phrase</span>'
        f'<div class="animadex-trigger">{trigger}</div>'
        '</div>'
        '<div class="animadex-data-block">'
        f'<span class="animadex-data-label">Character tags <small>{len(character.tags)}</small></span>'
        f'<div class="animadex-tags">{tags}</div>'
        '</div>'
        f'<a class="animadex-source" href="{url}" target="_blank" rel="noopener noreferrer">View on AnimaDex &rarr;</a>'
        '</div></article>'
    )


def _status(message: str, kind: str = "info") -> str:
    return f'<div class="animadex-status animadex-status-{kind}">{escape(message)}</div>'


def _load(query: str, requested_page: int):
    try:
        result = search_characters(query or "", requested_page)
    except AnimaDexError as exc:
        return gr.update(choices=[], value=None), None, _status(str(exc), "error")
    choices = [(f"{item.name} · {item.copyright_name}", item.slug) for item in result.results]
    selected = result.results[0].slug if result.results else None
    message = f"Page {result.page} of {result.pages} · {result.total} characters" if result.total else "No characters found."
    return gr.update(choices=choices, value=selected), result, _status(message)


def _next(query: str, page: SearchPage | None):
    current = page.page if page else 0
    last = page.pages if page else 1
    return _load(query, min(current + 1, last))


def _previous(query: str, page: SearchPage | None):
    return _load(query, max(1, page.page - 1) if page else 1)


def _import(
    prompt: str, slug: str | None, page: SearchPage | None,
    include_tags: bool, skipped_tags: frozenset[str],
):
    current = prompt or ""
    character = _selected(page, slug)
    if character is None:
        return current, _status("Select a character first.", "error"), ""
    updated = append_character(current, character, include_tags, skipped_tags)
    if updated == current:
        return current, _status("Nothing new to add to the prompt."), ""
    return updated, _status(f"Added {character.name} to the positive prompt.", "success"), "success"


def _reset_browser():
    return (
        gr.update(value=""), gr.update(choices=[], value=None), None,
        _detail(None, None), _status("Search to load characters."),
    )


def build_panel(prompt_component, prefix: str, settings: BrowserSettings) -> None:
    with gr.Group(elem_id=f"animadex-modal-{prefix}", elem_classes="animadex-modal"):
        gr.HTML(
            '<div class="animadex-config"'
            f' data-visible-presets="{escape(",".join(settings.visible_presets), quote=True)}"'
            f' data-auto-close="{str(settings.auto_close).lower()}"'
            f' data-remember-search="{str(settings.remember_search).lower()}"></div>',
            elem_classes="animadex-config-wrap",
        )
        with gr.Group(elem_id=f"animadex-card-{prefix}", elem_classes="animadex-card"):
            with gr.Row(elem_classes="animadex-heading"):
                gr.HTML(
                    '<div class="animadex-brand"><span class="animadex-brand-mark" aria-hidden="true">&#10022;</span>'
                    '<div><strong>AnimaDex</strong><span>Character browser</span></div></div>'
                )
                gr.Button("Close", size="sm", elem_id=f"animadex-close-{prefix}", elem_classes="animadex-close")
            with gr.Column(elem_classes="animadex-content"):
                with gr.Row(elem_classes="animadex-search-row"):
                    query = gr.Textbox(
                        label="Search characters", show_label=False, lines=1, max_lines=1,
                        placeholder="Search characters, series, or tags...", scale=5,
                        elem_classes="animadex-search-input",
                    )
                    search = gr.Button("Search", variant="primary", scale=0, min_width=100, elem_classes="animadex-search-button")
                gr.HTML('<div class="animadex-section-label">Characters <span>Choose one to preview</span></div>')
                results = gr.Dropdown(label="Characters", show_label=False, choices=[], interactive=True, elem_classes="animadex-results")
                detail = gr.HTML(_detail(None, None), elem_classes="animadex-detail")
                with gr.Row(elem_classes="animadex-pagebar"):
                    previous = gr.Button("Previous", size="sm", scale=0, min_width=90)
                    status = gr.HTML(_status("Search to load characters."), elem_classes="animadex-status-wrap")
                    following = gr.Button("Next", size="sm", scale=0, min_width=90)
            with gr.Row(elem_classes="animadex-actions"):
                trigger_only = gr.Button(
                    "Add trigger", variant="primary" if settings.preferred_import == "Trigger only" else "secondary",
                )
                trigger_tags = gr.Button(
                    "Add trigger + tags", variant="primary" if settings.preferred_import == "Trigger + tags" else "secondary",
                )
            page_state = gr.State(value=None)
            import_result = gr.Textbox(value="", show_label=False, interactive=False, elem_classes="animadex-import-result")
            reset = gr.Button("Reset browser", elem_id=f"animadex-reset-{prefix}", elem_classes="animadex-reset")

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

            def import_handler(include_tags: bool):
                def run(prompt: str, slug: str | None, page: SearchPage | None):
                    return _import(prompt, slug, page, include_tags, settings.skipped_tags)

                return run

            for button, include_tags in ((trigger_only, False), (trigger_tags, True)):
                button.click(
                    import_handler(include_tags),
                    inputs=[prompt_component, results, page_state],
                    outputs=[prompt_component, status, import_result],
                    show_progress="minimal",
                ).then(
                    fn=None, inputs=[import_result], outputs=[],
                    _js=f"(result) => window.animadexImportFinished('{prefix}', result === 'success')",
                )
            reset.click(
                _reset_browser, inputs=[], outputs=[query, results, page_state, detail, status],
                queue=False, show_progress="hidden",
            )
