[
    {
        name: "save",
        key: ["cmd + s", "ctrl + s"],
        monaco: KeyMod.CtrlCmd | KeyCode.KeyS,
        preventDefault: true,
        command: async () => {
            await this.service.editor.update();
        }
    },
    {
        name: "editor.close",
        key: ["alt + w"],
        monaco: KeyMod.Alt | KeyCode.KeyW,
        preventDefault: true,
        command: async () => {
            if (this.service.editor.activated)
                await this.service.editor.activated.close();
        }
    },
    {
        name: "editor.clone",
        key: ["alt + t"],
        monaco: KeyMod.Alt | KeyCode.KeyT,
        preventDefault: true,
        command: async () => {
            if (!this.service.editor.activated) return;
            let target = this.service.editor.activated;
            let location = this.service.editor.indexOf(target);
            await target.clone(location + 1);
        }
    },
    {
        name: "editor.minify",
        key: ["alt + m"],
        monaco: KeyMod.Alt | KeyCode.KeyM,
        preventDefault: true,
        command: async () => {
            if (!this.service.editor.activated) return;
            let target = this.service.editor.activated;
            await target.minify();
        }
    },
    {
        name: "editor.tab.prev",
        key: ["alt + a"],
        monaco: KeyMod.Alt | KeyCode.KeyA,
        preventDefault: true,
        command: async () => {
            if (!this.service.editor.activated) return;
            let target = this.service.editor.activated;
            let current = target.current * 1;
            if (target.tabs[current - 1]) {
                current = target.current - 1;
            } else {
                current = target.tabs.length - 1;
            }
            await target.select(current);
        }
    },
    {
        name: "editor.tab.next",
        key: ["alt + s"],
        monaco: KeyMod.Alt | KeyCode.KeyS,
        preventDefault: true,
        command: async () => {
            if (!this.service.editor.activated) return;
            let target = this.service.editor.activated;
            let current = target.current * 1;
            if (target.tabs[current + 1]) {
                current = target.current + 1;
            } else {
                current = 0;
            }
            await target.select(current);
        }
    }
]