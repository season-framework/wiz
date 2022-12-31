import { AfterViewInit, Input, ViewChild, ViewContainerRef, ComponentFactoryResolver, Type } from '@angular/core';
import { Service } from '@wiz/service/service';

export class Component implements AfterViewInit {
    @ViewChild('container', { read: ViewContainerRef }) container: ViewContainerRef;
    @Input() editor;

    constructor(
        public service: Service,
        private componentFactoryResolver: ComponentFactoryResolver
    ) { }

    public async ngAfterViewInit() {
        let componentClass = this.editor.tab().viewref;
        if (!componentClass) return;
        const componentFactory = this.componentFactoryResolver.resolveComponentFactory(componentClass);
        const component = this.container.createComponent(componentFactory);
        component.instance.editor = this.editor;
        await this.service.render();
    }
}