(function () {
    const prefixes = ["txt2img", "img2img"];
    let returnFocus = null;

    function selectedPreset() {
        const preset = gradioApp().querySelector("#forge_ui_preset");
        const field = preset && preset.querySelector('input:not([type="hidden"]), select');
        return field ? field.value.trim().toLowerCase() : null;
    }

    function browserConfig(modal) {
        const config = (modal || gradioApp()).querySelector(".animadex-config");
        return {
            visiblePresets: (config?.dataset.visiblePresets ?? "anima").split(",").map(value => value.trim()),
            autoClose: config?.dataset.autoClose !== "false",
            rememberSearch: config?.dataset.rememberSearch !== "false",
        };
    }

    function presetIsVisible() {
        return browserConfig().visiblePresets.includes(selectedPreset());
    }

    function syncLaunchers() {
        const root = gradioApp();
        const isVisible = presetIsVisible();

        for (const prefix of prefixes) {
            const negativeRow = root.querySelector(`#${prefix}_neg_prompt_row`);
            const modal = root.querySelector(`#animadex-modal-${prefix}`);
            let launcherRow = root.querySelector(`#animadex-launcher-row-${prefix}`);
            let launcher = root.querySelector(`#animadex-launcher-${prefix}`);

            if (!negativeRow || !modal) {
                if (launcherRow) launcherRow.remove();
                continue;
            }
            if (!launcherRow) {
                launcherRow = document.createElement("div");
                launcherRow.id = `animadex-launcher-row-${prefix}`;
                launcherRow.className = "animadex-launcher-row";
            }
            if (!launcher) {
                launcher = document.createElement("button");
                launcher.type = "button";
                launcher.id = `animadex-launcher-${prefix}`;
                launcher.className = "animadex-prompt-launcher";
                launcher.textContent = "Browse AnimaDex";
                launcher.hidden = true;
            }
            if (launcher.parentElement !== launcherRow) {
                launcherRow.append(launcher);
            }
            if (launcherRow.previousElementSibling !== negativeRow) {
                negativeRow.after(launcherRow);
            }
            launcherRow.hidden = !isVisible;
            launcher.hidden = !isVisible;
        }

        if (!isVisible) closeModal();
    }

    function closeModal() {
        const open = gradioApp().querySelector(".animadex-modal.animadex-open");
        if (!open) return;
        open.classList.remove("animadex-open");
        open.setAttribute("aria-hidden", "true");
        if (!browserConfig(open).rememberSearch) {
            const reset = open.querySelector('[id^="animadex-reset-"]');
            (reset?.matches("button") ? reset : reset?.querySelector("button"))?.click();
        }
        if (returnFocus && returnFocus.isConnected) returnFocus.focus();
        returnFocus = null;
    }

    function openModal(launcher) {
        if (!presetIsVisible()) return;
        const prefix = launcher.id.replace("animadex-launcher-", "");
        const modal = gradioApp().querySelector(`#animadex-modal-${prefix}`);
        if (!modal) return;
        closeModal();
        returnFocus = launcher;
        modal.setAttribute("role", "dialog");
        modal.setAttribute("aria-modal", "true");
        modal.setAttribute("aria-label", "AnimaDex character browser");
        modal.setAttribute("aria-hidden", "false");
        modal.classList.add("animadex-open");
        const search = modal.querySelector("textarea, input");
        if (search) search.focus();
    }

    window.animadexImportFinished = function (prefix, success) {
        const modal = gradioApp().querySelector(`#animadex-modal-${prefix}`);
        if (success && modal?.classList.contains("animadex-open") && browserConfig(modal).autoClose) {
            closeModal();
        }
    };

    onUiLoaded(function () {
        const root = gradioApp();
        root.addEventListener("click", function (event) {
            const target = event.target;
            if (!(target instanceof Element)) return;
            const launcher = target.closest(".animadex-prompt-launcher");
            if (launcher) {
                openModal(launcher);
                return;
            }
            if (target.closest('[id^="animadex-close-"]') || target.classList.contains("animadex-modal")) {
                closeModal();
            }
        });
        for (const eventName of ["input", "change"]) {
            root.addEventListener(eventName, function (event) {
                if (event.target instanceof Element && event.target.closest("#forge_ui_preset")) {
                    syncLaunchers();
                    requestAnimationFrame(syncLaunchers);
                }
            });
        }
        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") closeModal();
        });
        onAfterUiUpdate(syncLaunchers);
        onUiTabChange(function () {
            closeModal();
            syncLaunchers();
        });
        syncLaunchers();
    });
})();
