[
    {
        name: "preview",
        key: ["cmd + p", "ctrl + p"],
        monaco: KeyMod.CtrlCmd | KeyCode.KeyP,
        preventDefault: true,
        command: async () => {
            await this.service.rightmenu.toggle(this.service.rightmenu.top[0]);
        }
    },
    {
        name: "command.search",
        key: ["cmd + shift + f", "ctrl + shift + f"],
        monaco: KeyMod.CtrlCmd | KeyMod.Shift | KeyCode.KeyF,
        preventDefault: true,
        command: async () => {
            await this.service.overlay.toggle({ id: "workspace.app.command" });
        }
    }
]