import { Directive } from '@angular/core';
import { ElementRef } from '@angular/core';

@Directive({
    selector: '[appHighlight]'
})
export class HighlightDirective {

    constructor(private el: ElementRef) {
        this.el.nativeElement.style.backgroundColor = 'yellow';
    }

}
