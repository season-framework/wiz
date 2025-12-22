import { OnInit, Input } from '@angular/core';
import { ElementRef, ViewChild } from '@angular/core';
import { ViewContainerRef } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    @Input() config: any = {};

    public tabs: any = [];

    @ViewChild('editor')
    public element: ElementRef;

    constructor(
        public service: Service,
        public viewContainerRef: ViewContainerRef
    ) { }

    public async ngOnInit() {
        await this.service.init();
        await this.service.render();
        this.config.open = this.open.bind(this);
        this.config.find = this.find.bind(this);
        this.config.list = this.list.bind(this);
        this.config.findByIndex = this.findByIndex.bind(this);
        this.config.selected = {};
        if (this.config.onLoad) await this.config.onLoad();
    }

    public sortableOption: any = {
        animation: 0,
        handle: '.view-tab'
    };

    public find(tabId: string, view: any = null) {
        for (let i = 0; i < this.tabs.length; i++)
            if (this.tabs[i].id == tabId)
                if (!view || view == this.tabs[i].view)
                    return this.tabs[i];
        return null;
    }

    public findByIndex(index: number) {
        return this.tabs[index];
    }

    public list() {
        return this.tabs;
    }

    public async open(tab: any, reopen: boolean = false) {
        if (!tab.id) return;
        if (!tab.view) return;
        if (!tab.title) tab.title = id;
        let self = this;

        if (!reopen)
            for (let i = 0; i < self.tabs.length; i++) {
                if (self.tabs[i].id == tab.id && self.tabs[i].view == tab.view) {
                    tab = self.tabs[i];
                    await tab.open();
                    return tab;
                }
            }

        tab.container = this;

        tab.updateTitle = async (_title: string) => {
            tab.title = _title;
            await self.service.render();
        }

        tab.close = async () => {
            let index = self.tabs.indexOf(tab);
            self.tabs.remove(tab);
            if (self.config.selected.id == tab.id) {
                self.element.nativeElement.innerHTML = "";
                self.config.selected = {};
            }
            await self.service.render();
            if (self.config.on) await self.config.on("close");
            if (tab.onClose) await tab.onClose("close");
            if (tab.ref) await tab.ref.destroy();

            let alivetab: any = this.find(tab.id);
            if (alivetab) return await alivetab.open();
            if (self.tabs[index]) return await self.tabs[index].open();
            if (self.tabs[index - 1]) return await self.tabs[index - 1].open();
        }

        tab.open = async () => {
            if (self.config.selected == tab) return;
            let preselected: any = {};
            if (self.config.selected != tab)
                preselected = self.config.selected;
            self.config.selected = tab;
            await self.service.render();

            if (!tab.ref) {
                const ref = self.viewContainerRef.createComponent<NodeComponent>(tab.view);
                ref.instance.tab = tab;
                tab.ref = ref;
            }

            if (tab.onCreatedRef) await tab.onCreatedRef(tab.ref);

            let editorElement = tab.ref.location.nativeElement;
            self.element.nativeElement.innerHTML = "";
            self.element.nativeElement.append(editorElement);
            if (self.config.on) await self.config.on("open");
            await self.service.render();
            if (tab.onOpen) await tab.onOpen("open");

            if (preselected.ref && preselected.ref.instance.wizOnTabHide) await preselected.ref.instance.wizOnTabHide();
            if (tab.ref.instance.wizOnTabInit) await tab.ref.instance.wizOnTabInit();
        }

        self.tabs.push(tab);
        await tab.open();
        return tab;
    }
}