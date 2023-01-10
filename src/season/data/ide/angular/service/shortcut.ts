import Service from './service';
import { KeyMod, KeyCode } from 'monaco-editor';
import * as shortcuts from "./shortcut.plugin";
import CustomShortcut from "./shortcut.custom";

export default class Shortcut {
    public data: any = [];
    public keymap: any = {};

    constructor(private service: Service) { }

    public bind(namespace: string, value: any) {
        if (this.keymap[namespace]) {
            this.data.remove(this.keymap[namespace]);
        }
        value.allowIn = ['TEXTAREA', 'INPUT', 'SELECT'];
        this.keymap[namespace] = value;
        this.data.push(value);
        return this;
    }

    public async bindDefault() {
        this.bind("menu.main1", {
            key: ["cmd + 1", "ctrl + 1"],
            monaco: KeyMod.CtrlCmd | KeyCode.Digit1,
            preventDefault: true,
            command: async () => {
                await this.service.leftmenu.toggle(this.service.leftmenu.top[0]);
            }
        });

        this.bind("menu.main2", {
            key: ["cmd + 2", "ctrl + 2"],
            monaco: KeyMod.CtrlCmd | KeyCode.Digit2,
            preventDefault: true,
            command: async () => {
                await this.service.leftmenu.toggle(this.service.leftmenu.top[1]);
            }
        });

        this.bind("menu.main3", {
            key: ["cmd + 3", "ctrl + 3"],
            monaco: KeyMod.CtrlCmd | KeyCode.Digit3,
            preventDefault: true,
            command: async () => {
                await this.service.leftmenu.toggle(this.service.leftmenu.top[2]);
            }
        });

        this.bind("menu.main4", {
            key: ["cmd + 4", "ctrl + 4"],
            monaco: KeyMod.CtrlCmd | KeyCode.Digit4,
            preventDefault: true,
            command: async () => {
                await this.service.leftmenu.toggle(this.service.leftmenu.top[3]);
            }
        });

        this.bind("menu.main5", {
            key: ["cmd + 5", "ctrl + 5"],
            monaco: KeyMod.CtrlCmd | KeyCode.Digit5,
            preventDefault: true,
            command: async () => {
                await this.service.leftmenu.toggle(this.service.leftmenu.top[4]);
            }
        });

        this.bind("esc", {
            key: ["esc"],
            preventDefault: true,
            command: async () => {
                if (this.service.overlay.mode) {
                    await this.service.overlay.toggle();
                }
            }
        });

        for (let key in shortcuts) {
            try {
                let cls = new shortcuts[key](this.service);
                cls.bind();
            } catch (e) {
            }
        }

        try {
            let cls = new CustomShortcut(this.service);
            cls.bind();
        } catch (e) {
        }
    }
}