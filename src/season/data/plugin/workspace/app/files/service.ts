import { CollectionViewer, SelectionChange, DataSource } from '@angular/cdk/collections';
import { BehaviorSubject, merge, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

/** Flat node with expandable and level information */
export class FileNode {
    constructor(
        public name: string,
        public path: string,
        public type: string = 'file',
        public parent: FileNode | null = null,
        public level: number = -1,
    ) {
        this.rename = name + '';
    }

    public rename: string = "";
    public isLoading: boolean = false;
    public editable: boolean = false;
    public extended: boolean = false;
}

export class FileDataSource implements DataSource<FileNode> {
    public dataChange = new BehaviorSubject<FileNode[]>([]);

    get data(): FileNode[] {
        return this.dataChange.value;
    }

    set data(value: FileNode[]) {
        this.component.treeControl.dataNodes = value;
        this.dataChange.next(value);
    }

    constructor(private component: any) { }

    connect(collectionViewer: CollectionViewer): Observable<FileNode[]> {
        this.component.treeControl.expansionModel.changed.subscribe(change => {
            if ((change as SelectionChange<FileNode>).added || (change as SelectionChange<FileNode>).removed) {
                this.handleTreeControl(change as SelectionChange<FileNode>);
            }
        });
        return merge(collectionViewer.viewChange, this.dataChange).pipe(map(() => this.data));
    }

    disconnect(collectionViewer: CollectionViewer): void { }

    async handleTreeControl(change: SelectionChange<FileNode>) {
        if (change.added) {
            change.added.forEach(async (node) => {
                await this.toggle(node, true)
            });
        }

        if (change.removed) {
            change.removed.slice().reverse().forEach(async (node) => {
                await this.toggle(node, false);
            });
        }
    }

    async prepend(node: FileNode, to: FileNode | null) {
        let index = 0;
        if (to) {
            index = this.data.indexOf(to);
            if (index < 0)
                return;
            index = index + 1;
            node.level = to.level + 1;
        }
        this.data.splice(index, 0, node);
        this.dataChange.next(this.data);
    }

    async delete(node: FileNode) {
        let index = this.data.indexOf(node);
        if (index < 0)
            return;
        this.toggle(node, false);
        this.data.splice(index, 1);
        this.dataChange.next(this.data);
    }

    async toggle(node: FileNode, expand: boolean) {
        const index = this.data.indexOf(node);
        if (index < 0) {
            this.dataChange.next(this.data);
            return;
        }

        if (expand) {
            node.isLoading = true;
            let count = 0;
            for (
                let i = index + 1;
                i < this.data.length && this.data[i].level > node.level;
                i++, count++
            ) { }
            this.data.splice(index + 1, count);

            const nodes = await this.component.list(node);
            this.data.splice(index + 1, 0, ...nodes);
            node.isLoading = false;
            node.extended = true;
        } else {
            let count = 0;
            for (
                let i = index + 1;
                i < this.data.length && this.data[i].level > node.level;
                i++, count++
            ) { }
            this.data.splice(index + 1, count);
            node.extended = false;
        }

        this.dataChange.next(this.data);
        await this.component.service.render();
    }
}
