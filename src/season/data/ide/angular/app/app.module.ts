import { AppComponent } from './app.component';

import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, COMPOSITION_BUFFER_MODE } from '@angular/forms';
import { NuMonacoEditorModule } from '@ng-util/monaco-editor';
import { KeyboardShortcutsModule } from 'ng-keyboard-shortcuts';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { SortablejsModule } from '@wiz/libs/ngx-sortablejs';
import { NgxLoadingModule, ngxLoadingAnimationTypes } from "@wiz/libs/ngx-loading";

@NgModule({
    declarations: [
        '@wiz.declarations'
    ],
    imports: [
        BrowserModule,
        FormsModule,
        NuMonacoEditorModule.forRoot({ baseUrl: 'lib' }),
        NgxLoadingModule.forRoot({
            animationType: ngxLoadingAnimationTypes.cubeGrid,
            backdropBackgroundColour: "rgba(0,0,0,0.1)",
            primaryColour: "#3843D0",
            secondaryColour: "#3843D0",
            tertiaryColour: "#3843D0",
        }),
        SortablejsModule,
        KeyboardShortcutsModule.forRoot(),
        NgbModule,
        '@wiz.imports'
    ],
    providers: [
        {
            provide: COMPOSITION_BUFFER_MODE,
            useValue: false
        }
    ],
    bootstrap: [AppComponent]
})
export class AppModule { }