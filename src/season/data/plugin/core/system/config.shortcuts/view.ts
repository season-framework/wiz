import { AfterViewInit } from '@angular/core';
import { KeyMod, KeyCode } from 'monaco-editor';
import { Service } from '@wiz/service/service';

export class Component implements AfterViewInit {
    public shortcuts: any = [];

    constructor(public service: Service) { }

    public async ngAfterViewInit() {
        this.shortcuts.push({
            key: ["cmd + s", "ctrl + s"],
            monaco: KeyMod.CtrlCmd | KeyCode.KeyS,
            preventDefault: true,
            command: async () => {
                await this.service.editor.update();
            }
        }, {
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
        }, {
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
        }, {
            key: ["alt + w"],
            monaco: KeyMod.Alt | KeyCode.KeyW,
            preventDefault: true,
            command: async () => {
                if (this.service.editor.activated)
                    await this.service.editor.activated.close();
            }
        }, {
            key: ["cmd + 1", "ctrl + 1"],
            monaco: KeyMod.CtrlCmd | KeyCode.Digit1,
            preventDefault: true,
            command: async () => {
                await this.service.leftmenu.toggle(this.service.leftmenu.top[0]);
            }
        }, {
            key: ["cmd + 2", "ctrl + 2"],
            monaco: KeyMod.CtrlCmd | KeyCode.Digit2,
            preventDefault: true,
            command: async () => {
                await this.service.leftmenu.toggle(this.service.leftmenu.top[1]);
            }
        }, {
            key: ["cmd + 3", "ctrl + 3"],
            monaco: KeyMod.CtrlCmd | KeyCode.Digit3,
            preventDefault: true,
            command: async () => {
                await this.service.leftmenu.toggle(this.service.leftmenu.top[2]);
            }
        }, {
            key: ["cmd + 4", "ctrl + 4"],
            monaco: KeyMod.CtrlCmd | KeyCode.Digit4,
            preventDefault: true,
            command: async () => {
                await this.service.leftmenu.toggle(this.service.leftmenu.top[3]);
            }
        }, {
            key: ["cmd + 5", "ctrl + 5"],
            monaco: KeyMod.CtrlCmd | KeyCode.Digit5,
            preventDefault: true,
            command: async () => {
                await this.service.leftmenu.toggle(this.service.leftmenu.top[4]);
            }
        }, {
            key: ["cmd + p", "ctrl + p"],
            monaco: KeyMod.CtrlCmd | KeyCode.KeyP,
            preventDefault: true,
            command: async () => {
                await this.service.rightmenu.toggle(this.service.rightmenu.top[0]);
            }
        }, {
            key: ["cmd + k", "ctrl + k"],
            monaco: KeyMod.CtrlCmd | KeyCode.KeyK,
            preventDefault: true,
            command: async () => {
                await this.service.rightmenu.toggle(this.service.rightmenu.bottom[0]);
            }
        }, {
            key: ["esc"],
            preventDefault: true,
            command: async () => {
                await this.service.rightmenu.toggle();
            }
        }, {
            key: ["alt + t"],
            monaco: KeyMod.Alt | KeyCode.KeyT,
            preventDefault: true,
            command: async () => {
                if (!this.service.editor.activated) return;
                let target = this.service.editor.activated;
                let location = this.service.editor.indexOf(target);
                await target.clone(location + 1);
            }
        }, {
            key: ["alt + m"],
            monaco: KeyMod.Alt | KeyCode.KeyM,
            preventDefault: true,
            command: async () => {
                if (!this.service.editor.activated) return;
                let target = this.service.editor.activated;
                await target.minify();
            }
        });

        for (let i = 0; i < this.shortcuts.length; i++)
            this.shortcuts[i].allowIn = ['TEXTAREA', 'INPUT', 'SELECT'];

        this.service.shortcuts = this.shortcuts;
    }
}