"""Forge Neo extension entry point for the AnimaDex browser."""

import gradio as gr

from modules import script_callbacks, scripts, shared
from modules_forge.presets import PresetArch

from animadex_ext.settings import read_settings
from animadex_ext.ui import build_panel


PROMPTS = {}


def _capture_prompt(component, **kwargs):
    elem_id = kwargs.get("elem_id") or getattr(component, "elem_id", None)
    if elem_id in {"txt2img_prompt", "img2img_prompt"}:
        PROMPTS[elem_id] = component


class Script(scripts.Script):
    def title(self):
        return "AnimaDex characters"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        prefix = "img2img" if is_img2img else "txt2img"
        prompt = PROMPTS.get(f"{prefix}_prompt")
        if prompt is not None:
            build_panel(prompt, prefix, read_settings(shared.opts))
        return []


def _register_settings():
    section = ("animadex", "AnimaDex")
    shared.opts.add_option(
        "animadex_visible_presets",
        shared.OptionInfo(
            ["anima"], "Show browser on UI presets", gr.CheckboxGroup,
            {"choices": PresetArch.choices()}, section=section,
        ).info("Select the presets where the Browse AnimaDex button appears.").needs_reload_ui(),
    )
    shared.opts.add_option(
        "animadex_auto_close",
        shared.OptionInfo(True, "Close browser after a successful import", section=section).needs_reload_ui(),
    )
    shared.opts.add_option(
        "animadex_preferred_import",
        shared.OptionInfo(
            "Trigger + tags", "Preferred import mode", gr.Dropdown,
            {"choices": ["Trigger only", "Trigger + tags"]}, section=section,
        ).info("Highlights the preferred button; both import buttons remain available.").needs_reload_ui(),
    )
    shared.opts.add_option(
        "animadex_skipped_tags",
        shared.OptionInfo(
            "", "Tags to skip when importing", gr.Textbox,
            {"lines": 2}, section=section,
        ).info("Comma-separated tags. Trigger phrases are always kept.").needs_reload_ui(),
    )
    shared.opts.add_option(
        "animadex_remember_search",
        shared.OptionInfo(True, "Remember search when closing the browser", section=section).needs_reload_ui(),
    )


script_callbacks.on_after_component(_capture_prompt)
script_callbacks.on_ui_settings(_register_settings)
