import { Input } from '@angular/core';

export class Component {
    @Input() title: string = "Card Title";
    @Input() text: string = "Content";

    constructor() {
    }
}