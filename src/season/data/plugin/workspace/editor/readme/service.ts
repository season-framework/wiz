export const defaultComponent = `import \{ OnInit, OnDestroy, Input, Output, EventEmitter \} from "@angular/core";
import \{ Service \} from '@wiz/libs/portal/season/service';

export class Component implements OnInit, OnDestroy \{
    // \@Input() title = "";
    // \@Output() event = new EventEmitter();

    constructor(
        public service: Service,
    ) \{ \}

    async ngOnInit() \{
        await this.service.init();
        await this.service.auth.allow(true);
    \}

    async ngOnDestroy() \{\}

    private someEvent() \{
        console.log("this is child to parent event");
        this.event.emit(\{ key: "value" \});
    \}
\}`;