(function () {
    const prefixes = ["txt2img", "img2img"];
    let returnFocus = null;

    function selectedPreset() {
        const preset = gradioApp().querySelector("#forge_ui_preset");
        const field = preset && preset.querySelector('input:not([type="hidden"]), select');
        return field ? field.value.trim().toLowerCase() : null;
    }

    function syncLaunchers() {
        const root = gradioApp();
        const isAnima = selectedPreset() === "anima";

        for (const prefix of prefixes) {
            const negativeRow = root.querySelector(`#${prefix}_neg_prompt_row`);
            const modal = root.querySelector(`#animadex-modal-${prefix}`);
            let launcher = root.querySelector(`#animadex-launcher-${prefix}`);

            if (!negativeRow || !modal) {
                if (launcher) launcher.remove();
                continue;
            }
            if (!launcher) {
                launcher = document.createElement("button");
                launcher.type = "button";
                launcher.id = `animadex-launcher-${prefix}`;
                launcher.className = "animadex-prompt-launcher";
                launcher.textContent = "Browse AnimaDex";
                launcher.hidden = true;
            }
            if (launcher.previousElementSibling !== negativeRow) {
                negativeRow.after(launcher);
            }
            launcher.hidden = !isAnima;
        }

        if (!isAnima) closeModal();
    }

    function closeModal() {
        const open = gradioApp().querySelector(".animadex-modal.animadex-open");
        if (!open) return;
        open.classList.remove("animadex-open");
        open.setAttribute("aria-hidden", "true");
        if (returnFocus && returnFocus.isConnected) returnFocus.focus();
        returnFocus = null;
    }

    function openModal(launcher) {
        if (selectedPreset() !== "anima") return;
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
