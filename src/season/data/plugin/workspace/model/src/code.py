class Model:
    ESBUILD = """const fs = require('fs');
    const pug = require('pug');

    if (process.argv.length > 2) {
        for (let i = 2 ; i < process.argv.length ; i++) {
            const target = process.argv[i];
            const targetpath = target + '.pug';
            const savepath = target + '.html';
            const compiledFunction = pug.compileFile(targetpath);
            fs.writeFileSync(savepath, compiledFunction(), "utf8")
        }
    } else {
        const NgcEsbuild = require('ngc-esbuild');
        new NgcEsbuild({
            minify: true,
            open: false,
            serve: false,
            watch: false
        }).resolve.then((result) => {
            process.exit(1);
        });
    }
    """

    ENV = """export const environment = {
    production: true
    };"""

    TSCONFIG = """{
    "compileOnSave": false,
    "compilerOptions": {
        "baseUrl": "./",
        "outDir": "./dist/out-tsc",
        "forceConsistentCasingInFileNames": true,
        "strict": true,
        "noImplicitOverride": true,
        "noPropertyAccessFromIndexSignature": true,
        "noImplicitReturns": true,
        "noFallthroughCasesInSwitch": true,
        "sourceMap": true,
        "declaration": false,
        "downlevelIteration": true,
        "experimentalDecorators": true,
        "moduleResolution": "node",
        "importHelpers": true,
        "target": "ES2022",
        "module": "ES2022",
        "useDefineForClassFields": false,
        "lib": [
        "ES2022",
        "dom"
        ]
    },
    "angularCompilerOptions": {
        "enableI18nLegacyMessageIdFormat": false,
        "strictInjectionParameters": true,
        "strictInputAccessModifiers": true,
        "strictTemplates": true
    }
    }
    """

    STYLES = '@import "styles/styles"'

    TAILWIND = """/** @type {import('tailwindcss').Config} */
module.exports = {
content: [
    "./src/**/*.{html,ts}",
],
theme: {
    extend: {},
},
plugins: [],
}"""