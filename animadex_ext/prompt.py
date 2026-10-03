"""Prompt import rules independent of Forge's UI."""

from __future__ import annotations

from .client import Character


def append_character(
    existing: str, character: Character, include_tags: bool,
    skipped_tags: frozenset[str] = frozenset(),
) -> str:
    incoming = [part.strip() for part in character.trigger.split(",") if part.strip()]
    if include_tags:
        incoming.extend(tag for tag in character.tags if tag.strip().casefold() not in skipped_tags)

    seen = {part.strip().casefold() for part in existing.split(",") if part.strip()}
    additions = []
    for part in incoming:
        key = part.strip().casefold()
        if key and key not in seen:
            additions.append(part.strip())
            seen.add(key)
    if not additions:
        return existing
    if not existing.strip():
        return ", ".join(additions)
    separator = " " if existing.rstrip().endswith(",") else ", "
    return existing + separator + ", ".join(additions)
