"""Validated AnimaDex preferences read from Forge Neo's settings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserSettings:
    visible_presets: tuple[str, ...] = ("anima",)
    auto_close: bool = True
    preferred_import: str = "Trigger + tags"
    skipped_tags: frozenset[str] = frozenset()
    remember_search: bool = True


def read_settings(options) -> BrowserSettings:
    presets = getattr(options, "animadex_visible_presets", ["anima"])
    if not isinstance(presets, (list, tuple)):
        presets = ["anima"]
    visible_presets = tuple(
        preset.strip().casefold() for preset in presets
        if isinstance(preset, str) and preset.strip()
    )

    skipped = getattr(options, "animadex_skipped_tags", "")
    skipped_tags = frozenset(
        tag.strip().casefold() for tag in skipped.split(",") if tag.strip()
    ) if isinstance(skipped, str) else frozenset()

    preferred = getattr(options, "animadex_preferred_import", "Trigger + tags")
    if preferred not in {"Trigger only", "Trigger + tags"}:
        preferred = "Trigger + tags"

    return BrowserSettings(
        visible_presets=visible_presets,
        auto_close=getattr(options, "animadex_auto_close", True) is True,
        preferred_import=preferred,
        skipped_tags=skipped_tags,
        remember_search=getattr(options, "animadex_remember_search", True) is True,
    )
