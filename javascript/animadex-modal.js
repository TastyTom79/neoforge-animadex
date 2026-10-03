(function () {
    let returnFocus = null;

    function closeModal() {
        const open = gradioApp().querySelector(".animadex-modal.animadex-open");
        if (!open) return;
        open.classList.remove("animadex-open");
        open.setAttribute("aria-hidden", "true");
        if (returnFocus && returnFocus.isConnected) returnFocus.focus();
        returnFocus = null;
    }

    function openModal(launcher) {
        const prefix = launcher.id.replace("animadex-open-", "");
        const modal = gradioApp().querySelector(`#animadex-modal-${prefix}`);
        if (!modal) return;
        closeModal();
        returnFocus = launcher.querySelector("button") || launcher;
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
            const launcher = target.closest('[id^="animadex-open-"]');
            if (launcher) {
                openModal(launcher);
                return;
            }
            if (target.closest('[id^="animadex-close-"]') || target.classList.contains("animadex-modal")) {
                closeModal();
            }
        });
        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") closeModal();
        });
        onUiTabChange(closeModal);
    });
})();
