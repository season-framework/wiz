import Service from './service';

export class EditorTab {
    public editor: Editor;
    public name: string;         // tab display name
    public path: string;         // real file path
    public viewref: any;         // class for render editor view
    public updater: any;
    public loader: any;
    public cache: any = null;
    public meta: any = {};

    // configuration for editor view
    public config: any = {
        monaco: {
            wordWrap: false,
            roundedSelection: false,
            scrollBeyondLastLine: true,
            glyphMargin: false,
            folding: true,
            fontSize: 14,
            automaticLayout: true,
            minimap: { enabled: false }
        }
    };

    constructor(editor: Editor, name: string, path: any, viewref: any, config: any = {}) {
        if (!editor.manager.tabcached[path]) editor.manager.tabcached[path] = [];
        editor.manager.tabcached[path].push(this);
        this.editor = editor;
        this.name = name;
        this.path = path;
        this.viewref = viewref;
        for (let key in config) {
            if (key == 'monaco') {
                for (let mkey in config[key]) {
                    this.config[key][mkey] = config[key][mkey];
                }
            } else {
                this.config[key] = config[key];
            }
        }
    }

    public destroy() {
        if (!this.editor.manager.tabcached[this.path]) return;
        let location = this.editor.manager.tabcached[this.path].indexOf(this);
        if (location < 0) return;
        this.editor.manager.tabcached[this.path].splice(location, 1);

        if (this.editor.manager.tabcached[this.path].length == 0) {
            delete this.editor.manager.files[this.path];
        }
    }

    public event: any = {};

    public bind(key: string, fn: any) {
        this.event[key] = fn;
        return this;
    }

    public async update() {
        if (this.event.update) {
            await this.event.update(this);

            if (this.editor.manager.event.updated) {
                await this.editor.manager.event.updated(this);
            }
            return;
        }
    }

    public async data() {
        // if path is not null
        if (this.path)
            if (this.editor.manager.files[this.path])
                return this.editor.manager.files[this.path];

        if (this.cache)
            return this.cache;

        // if event data binded
        if (this.event.data) {
            let data = await this.event.data(this);
            if (this.path)
                this.editor.manager.files[this.path] = data;
            this.cache = data;
            return data;
        }

        // default return cache
        return this.cache;
    }

    public async move(to: string) {
        let from = this.path + '';
        if (from == to) return;

        let data = this.editor.manager.files[from];
        this.editor.manager.files[to] = data;
        delete this.editor.manager.files[from];

        this.path = to;
        if (this.editor.manager.tabcached[from]) {
            this.editor.manager.tabcached[to] = [];
            for (let i = 0; i < this.editor.manager.tabcached[from].length; i++) {
                this.editor.manager.tabcached[from][i].path = to;
                this.editor.manager.tabcached[to].push(this.editor.manager.tabcached[from][i]);
            }
        }
    }
}

export class Editor {
    public id: string;                // editor instance id
    public manager: Manager;         // wiz editor
    public path: string;              // unique identifier for data
    public title: string;             // title for display tab
    public subtitle: string;          // subtitle for display tab
    public current: number | null = 0;       // activated edit item
    public tabs: Array<EditorTab> = []; // tabs
    public unique: boolean = false;   // is unique tab
    public component_id: string;
    public meta: any = {};

    constructor(manager: Manager, component_id: string, path: any = null, title: string = '', subtitle: string = '', current: number = 0, unique: boolean = false) {
        this.id = "editor-" + new Date().getTime();
        this.component_id = component_id;
        this.manager = manager;
        this.path = path;
        this.title = title;
        this.subtitle = subtitle;
        this.current = current;
        this.unique = unique;
    }

    public event: any = { update: null, delete: null, clone: null };

    public bind(key: string, fn: any) {
        this.event[key] = fn;
        return this;
    }

    public async update() {
        let currentTab = this.tab();
        if (currentTab)
            await currentTab.update();
    }

    public async delete() {
        if (this.event.delete)
            await this.event.delete(...arguments);
    }

    public async clone() {
        if (this.event.clone)
            await this.event.clone(...arguments);
    }

    public create(params = {}) {
        let config: any = { name: null, path: null, viewref: null, config: {} };
        for (let key in params) config[key] = params[key];
        let tab = new EditorTab(this, config.name, config.path, config.viewref, config.config);
        this.tabs.push(tab);
        return tab;
    }

    public modify(values: any = {}) {
        let manager = this.manager;
        let finded = manager.find(this);
        for (let i = 0; i < finded.length; i++) {
            if (values.path) finded[i].path = values.path;
            if (values.title) finded[i].title = values.title;
            if (values.subtitle) finded[i].subtitle = values.subtitle;
            if (values.meta)
                for (let key in values.meta)
                    finded[i].meta[key] = values.meta[key];
        }
    }

    // tab events
    public tab(current: number | null = null) {
        if (current !== null)
            return this.tabs[current]
        if (this.current !== null)
            return this.tabs[this.current];
        return null;
    }

    public async select(current: number) {
        let manager = this.manager;
        this.current = null;
        await manager.service.render();
        this.current = current;
        await manager.service.render();
    }

    // editor events
    public async open(location: number = -1) {
        let manager = this.manager;

        if (this.unique) {
            // if manager is activated editors
            let selected: Editor | null = null;
            for (let i = 0; i < manager.editable.length; i++) {
                if (manager.editable[i].path == this.path && manager.editable[i].component_id == this.component_id) {
                    selected = manager.editable[i];
                    break;
                }
            }

            if (selected) {
                await selected.activate();
                return;
            }

            // if not in activated, find minified
            for (let i = 0; i < manager.minified.length; i++) {
                if (manager.minified[i].path == this.path && manager.minified[i].component_id == this.component_id) {
                    selected = manager.minified[i];
                    break;
                }
            }

            if (selected) {
                await selected.activate();
                return;
            }
        }

        if (location > -1) {
            manager.editable.splice(location, 0, this)
        } else {
            manager.editable.push(this);
        }

        await this.activate();
    }

    public async close() {
        let manager = this.manager;
        let location = manager.editable.indexOf(this);
        if (location >= 0) {
            manager.editable.splice(location, 1);
            if (manager.activated && this.id == manager.activated.id) {
                if (manager.editable[location]) {
                    await manager.editable[location].activate();
                } else if (manager.editable[location - 1]) {
                    await manager.editable[location - 1].activate();
                } else {
                    manager.activated = null;
                }
            }
        } else {
            location = manager.minified.indexOf(this);
            if (location >= 0) {
                manager.minified.splice(location, 1);
            }
        }

        for (let i = 0; i < this.tabs.length; i++)
            this.tabs[i].destroy();

        if (this.event.close)
            await this.event.close(...arguments);

        await manager.service.render();
    }

    public async activate() {
        let manager = this.manager;
        let location = manager.minified.indexOf(this);
        if (location > -1) {
            manager.minified.splice(location, 1);
            manager.editable.push(this);
        }
        manager.activated = this;
        await manager.service.render();
    }

    public async minify() {
        let manager = this.manager;
        let location = manager.editable.indexOf(this);
        if (location > -1) manager.editable.splice(location, 1);
        manager.minified.push(this);
        await manager.service.render();
    }
}

export class Manager {
    Tab = EditorTab;
    Editor = Editor;

    tabcached: any = {};
    files: any = {};
    minified: Array<Editor> = [];
    editable: Array<Editor> = [];
    activated: Editor | null = null;
    event: any = {};

    constructor(public service: Service) { }

    public bind(key: string, fn: any) {
        this.event[key] = fn;
        return this;
    }

    public create(param = {}) {
        let config = {
            component_id: '',
            path: null,
            title: '',
            subtitle: '',
            current: 0,
            unique: false
        };

        for (let key in param) config[key] = param[key];
        return new Editor(this, config.component_id, config.path, config.title, config.subtitle, config.current, config.unique);
    }

    public find(item: Editor) {
        let result: any = [];
        for (let i = 0; i < this.editable.length; i++) {
            let target = this.editable[i];
            if (item.component_id == target.component_id && item.path == target.path) {
                result.push(target);
            }
        }

        for (let i = 0; i < this.minified.length; i++) {
            let target = this.minified[i];
            if (item.component_id == target.component_id && item.path == target.path) {
                result.push(target);
            }
        }

        return result;
    }

    public async update() {
        let current_app = this.activated;
        if (!current_app) return;
        await current_app.update();
    }

    public indexOf(item: Editor) {
        return this.editable.indexOf(item);
    }
}

export default Manager;