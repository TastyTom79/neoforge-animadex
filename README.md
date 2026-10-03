# neoforge-animadex

NeoForge extension for browsing AnimaDex characters and instantly importing trigger words and tags into your prompts.

## Install

Place this repository in Forge Neo's `extensions/` directory and restart the WebUI. Select the **anima** UI Preset. The **Browse AnimaDex** button appears directly below the negative prompt in **txt2img** and **img2img**; by default it is hidden for other presets. Click it to open the character browser. Search by name, series, or tags, select a result, then choose **Add trigger** or **Add trigger + tags**. Close the browser with **Close** or Escape. Both import buttons append to that tab's positive prompt. Existing prompt text is retained, and comma-separated terms already present are skipped without reordering imported tags.

## Settings

Open **Settings → AnimaDex** to configure the browser:

- **Show browser on UI presets:** choose any combination of Forge Neo presets. Only **anima** is selected by default. AnimaDex prompt text is inserted as-is on every selected preset.
- **Close browser after a successful import:** enabled by default. Errors and imports that add nothing leave the browser open.
- **Preferred import mode:** highlights either **Add trigger** or **Add trigger + tags**. Both buttons remain available.
- **Tags to skip when importing:** an optional comma-separated list of exact tags, matched without case sensitivity. Trigger phrases are still imported.
- **Remember search when closing the browser:** enabled by default. Turn it off to clear the query and results when the popup closes.

Click **Apply settings**, then **Reload UI** for changes to take effect.

## Data source and compatibility

The extension uses AnimaDex's public JSON search route, `https://animadex.net/api/characters/search`, with `q` and `page` parameters. The site returns `trigger` and an ordered `tags` array for each character, plus names and thumbnail URLs. The adapter is in `animadex_ext/client.py`; prompt merging is in `animadex_ext/prompt.py`. The AnimaDex catalogue requires network access at search time. The extension does not use HTML scraping or require extra Python packages beyond Forge Neo's Gradio installation.

Forge Neo's `scripts.Script` and `script_callbacks.on_after_component` hooks provide the browser and the existing `txt2img_prompt` / `img2img_prompt` fields. The extension's `javascript/` file places the launcher after Forge Neo's negative prompt row and watches the `forge_ui_preset` dropdown; `style.css` presents the browser as a popup. This integration targets the [Forge Neo branch](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo) of Stable Diffusion WebUI. It has not been run in a local Forge Neo installation in this repository.

## Tests

Run `python -m unittest discover -s tests` to check API response parsing, prompt merging, and settings normalization without launching Forge Neo.

## Sources

- [AnimaDex API search route](https://github.com/zetaneko/AnimaDex/blob/main/animadex/routes/api_gallery.py)
- [AnimaDex character serializer](https://github.com/zetaneko/AnimaDex/blob/main/animadex/images.py)
- [AnimaDex character data format](https://github.com/zetaneko/AnimaDex/blob/main/docs/data-format.md)
- [Forge Neo extension example](https://github.com/mikhailfur/sd-webui-ai-wdywfm/blob/master/scripts/ai_wdywfm.py)

MIT licensed; see [LICENSE](LICENSE).
