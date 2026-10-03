"""Forge Neo extension entry point for the AnimaDex browser."""

from modules import script_callbacks, scripts

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
            build_panel(prompt, prefix)
        return []


script_callbacks.on_after_component(_capture_prompt)
