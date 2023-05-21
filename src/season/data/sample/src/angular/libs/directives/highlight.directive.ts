import { Directive, Input, ElementRef, HostListener } from '@angular/core';

@Directive({
    selector: '[appHighlight]'
})
export class HighlightDirective {

    constructor(private el: ElementRef) {
    }

    @Input() appHighlight: string = '';
    @Input() color: string = '';

    @HostListener('mouseenter') onMouseEnter() {
        this.highlight(this.appHighlight, this.color || 'black');
    }

    @HostListener('mouseleave') onMouseLeave() {
        this.highlight('', '');
    }

    private highlight(bgcolor: string, color: string) {
        this.el.nativeElement.style.backgroundColor = bgcolor;
        this.el.nativeElement.style.color = color;
    }
}
