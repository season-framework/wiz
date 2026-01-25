import { OnInit } from '@angular/core';
import { Input } from '@angular/core';
import { ContentChild, TemplateRef } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    @ContentChild('fileTemplate') template: TemplateRef<any>;
    @Input() config: any;

    public cache: any = { data: {}, tree: {} };
    public loaded: boolean = false;

    public async ngOnInit() {
        await this.service.init();
        await this.load();
        this.loaded = true;
        this.config.rootNode = this.rootNode.bind(this);
        this.config.info = this.info.bind(this);

        if (!this.config.isShow) this.config.isShow = () => true;

        await this.service.render();
        if (this.config.onInit)
            await this.config.onInit(this.config.info());
    }

    // config bindings
    public rootNode() {
        return this.cache.data[''];
    }

    // tree ui
    public async load(key: any = '') {
        let { code, data } = await this.config.load(key);
        if (code == 200) {
            let { root, children } = data;
            let children_id = [];
            this.cache.data[key] = root;
            this.info(key);
            for (let i = 0; i < children.length; i++) {
                this.cache.data[children[i].id] = children[i];
                children_id.push(children[i].id);
            }
            this.cache.tree[key] = children_id;
        }

        await this.service.render();
        return this.cache[key];
    }

    public getChildren(key: any = '') {
        let targetChildren = this.cache.tree[key];
        if (!targetChildren) return [];
        let children = [];
        for (let i = 0; i < targetChildren.length; i++) {
            let itemkey = targetChildren[i];
            let item = this.info(itemkey);
            if (!item) continue;
            if (!item.rename)
                item.rename = item.title;
            children.push(item);
        }

        if (this.config.sort) {
            this.config.sort(children);
        } else {
            children.sort((a, b) => {
                if (a.type == b.type)
                    return a.title.localeCompare(b.title);
                if (a.type == 'folder') return -1;
                if (b.type == 'folder') return 1;
            });
        }

        return children;
    }

    public info(key: any = '') {
        if (!this.cache.data[key]) return;
        let info = this.cache.data[key];
        info.initialized = true;
        info.isOpen = () => this.cache.tree[key] ? true : false;
        info.parent = () => this.parent.bind(this)(info);
        info.select = async () => await this.select.bind(this)(info);
        info.flush = async () => await this.flush.bind(this)(info.id);
        info.toggle = async () => await this.toggle.bind(this)(info);
        info.update = async () => await this.update.bind(this)(info);
        info.refresh = async () => await this.refresh.bind(this)(info.id);
        info.isActive = () => this.isActive.bind(this)(info);
        info.drop = (event: any) => this.drop.bind(this)(event, info);
        info.dragend = (event: any) => this.dragend.bind(this)(event, info);
        info.dragover = (event: any) => this.dragover.bind(this)(event, info);
        info.getChildren = () => this.getChildren.bind(this)(info.id);
        return info;
    }

    // data bindings
    public async select(node: any) {
        await this.config.select(node);
        await this.service.render();
    }

    public parent(node: any) {
        let parent_id = node.root_id;
        return this.info(parent_id);
    }

    public async refresh(key: any = '') {
        await this.load(key);
    }

    public async toggle(node: any) {
        let node_id = node.id;
        if (this.cache.tree[node_id]) {
            delete this.cache.tree[node_id];
        } else {
            await this.load(node_id);
        }
    }

    public async flush(key: any) {
        let targetChildren = this.cache.tree[key];
        if (targetChildren) {
            for (let i = 0; i < targetChildren.length; i++) {
                let childkey = targetChildren[i];
                await this.flush(childkey);
            }
        }
        delete this.cache.tree[key];
        delete this.cache.data[key];
    }

    public async update(node: any) {
        await this.config.update(node);
        await this.refresh(node.root_id);
    }

    public isActive(node: any) {
        if (this.config.isActive)
            return this.config.isActive(node);
        return false;
    };

    public dragToItem: any = null;

    public async drop(event: any, node: any) {
        event.stopPropagation();
        event.preventDefault();

        let files = await this.service.file.drop(event);
        if (files.length > 0) {
            if (this.config.upload) await this.config.upload(node, files);
            let root_id = this.dragToItem.id ? this.dragToItem.id : '';
            await this.refresh(root_id);
            this.dragToItem = null;
            await this.service.render();
        }
    }

    public async dragend(event: any, node: any) {
        event.stopPropagation();
        event.preventDefault();
        if (!this.dragToItem) return;
        let data = JSON.parse(JSON.stringify(node));
        let root_id = this.dragToItem.id ? this.dragToItem.id : '';
        let org_root_id = data.root_id;
        data.root_id = root_id;
        await this.config.update(data);
        await this.refresh(org_root_id);
        await this.refresh(root_id);
        if (this.config.moved)
            await this.config.moved(event, data);

        this.dragToItem = null;
        await this.service.render();
    }

    public async dragover(event: any, node: any) {
        if (node.type == 'folder') {
            event.preventDefault();
            event.stopPropagation();
            this.dragToItem = node;
        } else {
            this.dragToItem = {};
        }
        this.service.render();
    }

}