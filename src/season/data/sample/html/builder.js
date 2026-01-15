ult;
    }

    static dependencies(code) {
	            const result = {};
	            const pattern = /@dependencies\(([^\)]*)\)/gs;
	            const matches = code.matchAll(pattern);
	            
	            for (const match of matches) {
			                let data = match[1].replace(/'/g, '').replace(/"/g, '').replace(/,/g, '').replace(/ /g, '');
						            const keyValuePattern = /(.*):(.*)/;
						            const kvMatches = data.match(keyValuePattern);
						            if (kvMatches) {
								                    result[kvMatches[1]] = kvMatches[2];
								                }
						        }
	            return result;
	        }

    static ngComponentDesc(code) {
	            const res = { inputs: [], outputs: [] };
	            
	            // @Input() 추출
	    //         const inputPattern = /@Input\(\)([^=\:\n\;]*)/g;
	    //                 let match;
	    //                      const fs = require('fs');
const path = require('path');
const { spawn, execSync } = require('child_process');
const chokidar = require('chokidar');

// Annotator 클래스 (Python annotator.py 포팅)
class AnnotatorDefinition {
    static directives(code) {
        const result = {};
        const pattern = /@directives\(([^\)]*)\)/gs;
        const matches = code.matchAll(pattern);
        
        for (const match of matches) {
            let data = match[1].replace(/'/g, '').replace(/"/g, '').replace(/,/g, '').replace(/ /g, '');
            const keyValuePattern = /(.*):(.*)/;
            const kvMatches = data.match(keyValuePattern);
            if (kvMatches) {
                result[kvMatches[1]] = kvMatches[2];
            }
        }
        return res   while ((match = inputPattern.exec(code)) !== null) {
            res.inputs.push(match[1].replace(/ /g, ''));
        }
        
        // @Output() 추출
        const outputPattern = /@Output\(\)([^=\:\n\;]*)/g;
        while ((match = outputPattern.exec(code)) !== null) {
            res.outputs.push(match[1].replace(/ /g, ''));
        }
        
        return res;
    }
}

class AnnotatorInjection {
    static app(code) {
        const patterns = [
            /"@wiz\/app\/(.*)"/g,
            /'@wiz\/app\/(.*)'/g
        ];
        
        for (const pattern of patterns) {
            code = code.replace(pattern, (match, val) => {
                if (val.split('/').length > 1) {
                    val = val.replace('/directive', '/app.directive');
                    return `"src/app/${val}"`;
                }
                return `"src/app/${val}/${val}.component"`;
            });
        }
        return code;
    }

    static libs(code) {
        const patterns = [
            /"@wiz\/libs\/(.*)"/g,
            /'@wiz\/libs\/(.*)'/g
        ];
        
        for (const pattern of patterns) {
            code = code.replace(pattern, (match, val) => {
                return `"src/libs/${val}"`;
            });
        }
        return code;
    }

    static namespace(code, appId) {
        if (!appId) return code;
        
        code = code.replace(/@wiz\.namespace\((.*)\)/g, appId);
        code = code.replace(/@wiz\.namespace/g, appId);
        return code;
    }

    static cwd(code, appId) {
        if (!appId) return code;
        
        const patterns = [
            /"@wiz\/cwd\/(.*)"/g,
            /'@wiz\/cwd\/(.*)'/g
        ];
        
        for (const pattern of patterns) {
            code = code.replace(pattern, (match, val) => {
                val = val.replace('directive', 'app.directive');
                return `"src/app/${appId}/${val}"`;
            });
        }
        return code;
    }

    static baseuri(code, baseuri) {
        if (!baseuri) return code;
        
        code = code.replace(/@wiz\.baseuri\((.*)\)/g, (match, val) => {
            if (val.length > 0) {
                if (val[0] === '/') {
                    val = val.substring(1);
                }
                return baseuri + '/' + val;
            }
            return baseuri;
        });
        code = code.replace(/@wiz\.baseuri/g, baseuri);
        return code;
    }

    static dependencies(code) {
        return code.replace(/@dependencies\(([^\)]*)\)/gs, '');
    }

    static directives(code) {
        return code.replace(/@directives\(([^\)]*)\)/gs, '');
    }

    static declarations(code, declarations) {
        if (!declarations) return code;
        
        const patterns = [
            /"@wiz\.declarations\((.*)\)"/g,
            /'@wiz\.declarations\((.*)\)'/g
        ];
        
        for (const pattern of patterns) {
            code = code.replace(pattern, declarations);
        }
        code = code.replace(/'@wiz\.declarations'/g, declarations);
        code = code.replace(/"@wiz\.declarations"/g, declarations);
        return code;
    }

    static imports(code, imports) {
        const patterns = [
            /"@wiz\.imports\((.*)\)"/g,
            /'@wiz\.imports\((.*)\)'/g
        ];
        
        for (const pattern of patterns) {
            code = code.replace(pattern, imports);
        }
        code = code.replace(/'@wiz\.imports'/g, imports);
        code = code.replace(/"@wiz\.imports"/g, imports);
        return code;
    }

    static route(code) {
        // JSON 문자열 내에서 "component": "app_id" 형태를 component: AppIdComponent 형태로 변환
        // JSON 형식: "component": "layout.navbar" -> component: LayoutNavbarComponent
        // 정규식: "component" 뒤에 공백, 콜론, 공백, 따옴표, 값, 따옴표를 찾아서 변환
        code = code.replace(/"component"\s*:\s*"([^"]+)"/g, (match, val) => {
            return `component: ${Namespace.componentName(val)}Component`;
        });
        return code;
    }
}

// Namespace 클래스 (Python namespace.py 포팅)
class Namespace {
    static componentName(namespace) {
        const parts = namespace.split('.');
        return parts.map(part => 
            part.charAt(0).toUpperCase() + part.slice(1)
        ).join('');
    }

    static selector(namespace) {
        return 'wiz-' + namespace.split('.').join('-');
    }
}

// Builder 클래스 (Python builder.py 포팅)
class Builder {
    constructor(projectRoot = process.cwd()) {
        this.projectRoot = projectRoot;
        this.buildDir = path.join(projectRoot, 'build');
        this.srcDir = path.join(projectRoot, 'src');
        this.bundleDir = path.join(projectRoot, 'bundle');
        this.isBuilding = false;
        this.buildQueue = [];
        this.watcher = null;
        this.angularProcess = null;
        this.debounceTimer = null;
        this.pendingChanges = [];
        
        // 설정 읽기
        this.baseuri = process.env.BASEURI || '/wiz';
        this.template = this.getTemplate();
        this.port = 3000;
    }

    setPort(port) {
      this.port = port;
    }

    getTemplate() {
        // config/build.json에서 template 읽기
        const configPath = path.join(this.projectRoot, 'config', 'build.json');
        if (fs.existsSync(configPath)) {
            try {
                const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
                if (config.template && ['pug', 'html'].includes(config.template)) {
                    return config.template;
                }
            } catch (e) {
                // ignore
            }
        }
        return process.env.TEMPLATE || 'html';
    }

    // 파일 시스템 헬퍼
    ensureDir(dir) {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    }

    copyFile(src, dest) {
        this.ensureDir(path.dirname(dest));
        fs.copyFileSync(src, dest);
    }

    copyDir(src, dest) {
        if (!fs.existsSync(src)) return;
        this.ensureDir(dest);
        const files = fs.readdirSync(src);
        for (const file of files) {
            const srcPath = path.join(src, file);
            const destPath = path.join(dest, file);
            const stat = fs.statSync(srcPath);
            if (stat.isDirectory()) {
                this.copyDir(srcPath, destPath);
            } else {
                this.copyFile(srcPath, destPath);
            }
        }
    }

    deleteDir(dir) {
        if (fs.existsSync(dir)) {
            fs.rmSync(dir, { recursive: true, force: true });
        }
    }

    readFile(file) {
        if (!fs.existsSync(file)) return '';
        return fs.readFileSync(file, 'utf8');
    }

    writeFile(file, content) {
        this.ensureDir(path.dirname(file));
        fs.writeFileSync(file, content, 'utf8');
    }

    fileExists(file) {
        return fs.existsSync(file);
    }

    isDir(file) {
        if (!fs.existsSync(file)) return false;
        return fs.statSync(file).isDirectory();
    }

    listDir(dir) {
        if (!fs.existsSync(dir)) return [];
        return fs.readdirSync(dir);
    }

    readJson(file, defaultValue = {}) {
        if (!fs.existsSync(file)) return defaultValue;
        try {
            return JSON.parse(fs.readFileSync(file, 'utf8'));
        } catch (e) {
            return defaultValue;
        }
    }

    writeJson(file, obj) {
        this.writeFile(file, JSON.stringify(obj, null, 4));
    }

    abspath(...args) {
        return path.join(this.projectRoot, ...args);
    }

    // 파일 검색
    search(targetFile, result = [], extension = null) {
        if (this.isDir(targetFile)) {
            const files = this.listDir(targetFile);
            for (const f of files) {
                this.search(path.join(targetFile, f), result, extension);
            }
            return result;
        }

        if (extension === null) {
            result.push(targetFile);
            return result;
        }

        const ext = path.extname(targetFile);
        if (ext === extension) {
            result.push(targetFile.replace(ext, ''));
            return result;
        }

        return result;
    }

    // TypeScript annotation 추가
    typescript(code, appId = null, baseuri = null, declarations = null, imports = null, prefix = null) {
        if (prefix) {
            code = prefix + '\n\n' + code;
        }
        code = AnnotatorInjection.declarations(code, declarations);
        code = AnnotatorInjection.imports(code, imports);
        code = AnnotatorInjection.app(code);
        code = AnnotatorInjection.libs(code);
        code = AnnotatorInjection.namespace(code, appId);
        code = AnnotatorInjection.cwd(code, appId);
        code = AnnotatorInjection.baseuri(code, baseuri);
        code = AnnotatorInjection.dependencies(code);
        code = AnnotatorInjection.directives(code);
        return code;
    }

    // Pug annotation 추가
    pug(code, appId = null, baseuri = null) {
        code = AnnotatorInjection.cwd(code, appId);
        code = AnnotatorInjection.baseuri(code, baseuri);
        return code;
    }

    // 재구성: src를 build로 복사 (증분 빌드 지원)
    reconstruct(changedFiles = null) {
        // console.log('[Builder] Reconstructing...');

        // config 디렉토리 확인
        this.ensureDir(this.abspath('config'));

        // wizbuild.js 작성
        const wizbuildContent = this.getDefaultWizbuild();
        this.writeFile(this.abspath('build', 'wizbuild.js'), wizbuildContent);

        // tsconfig.json 작성
        const tsconfigContent = this.getDefaultTsconfig();
        this.writeFile(this.abspath('build', 'tsconfig.json'), tsconfigContent);

        // tailwind.config.js
        const tailwindSrc = this.abspath('src', 'angular', 'tailwind.config.js');
        if (this.fileExists(tailwindSrc)) {
            this.copyFile(tailwindSrc, this.abspath('build', 'tailwind.config.js'));
        } else if (!this.fileExists(this.abspath('build', 'tailwind.config.js'))) {
            this.writeFile(this.abspath('build', 'tailwind.config.js'), this.getDefaultTailwind());
        }

        // environments
        this.ensureDir(this.abspath('build', 'src', 'environments'));
        const envSrc = this.abspath('src', 'angular', 'environment.ts');
        if (this.fileExists(envSrc)) {
            this.copyFile(envSrc, this.abspath('build', 'src', 'environments', 'environment.ts'));
        } else {
            this.writeFile(this.abspath('build', 'src', 'environments', 'environment.ts'),
                'export const environment = { production: false };');
        }

        // styles.scss
        this.writeFile(this.abspath('build', 'src', 'styles.scss'), '@import "styles/styles"');

        const buildSrcDir = this.abspath('build', 'src');
        const angularSrc = this.abspath('src', 'angular');

        if (changedFiles && changedFiles.length > 0) {
            // 증분 빌드: 변경된 파일만 처리
            for (const changedFile of changedFiles) {
                this.copyChangedFile(changedFile, buildSrcDir, angularSrc);
            }
        } else {
            // 전체 빌드: build/src 디렉토리 정리 후 전체 복사
            ['app', 'assets', 'controller', 'libs', 'model', 'route', 'styles'].forEach(dir => {
                this.deleteDir(path.join(buildSrcDir, dir));
            });

            // src 복사
            if (this.fileExists(path.join(angularSrc, 'main.ts'))) {
                this.copyFile(path.join(angularSrc, 'main.ts'), path.join(buildSrcDir, 'main.ts'));
            }
            if (this.fileExists(path.join(angularSrc, 'wiz.ts'))) {
                this.copyFile(path.join(angularSrc, 'wiz.ts'), path.join(buildSrcDir, 'wiz.ts'));
            }

            // index 파일 복사
            if (this.template === 'pug' && this.fileExists(path.join(angularSrc, 'index.pug'))) {
                this.copyFile(path.join(angularSrc, 'index.pug'), path.join(buildSrcDir, 'index.pug'));
            } else if (this.fileExists(path.join(angularSrc, 'index.html'))) {
                this.copyFile(path.join(angularSrc, 'index.html'), path.join(buildSrcDir, 'index.html'));
            }

            // 디렉토리 복사
            if (this.fileExists(path.join(angularSrc, 'app'))) {
                this.copyDir(path.join(angularSrc, 'app'), path.join(buildSrcDir, 'app'));
            }
            if (this.fileExists(path.join(this.srcDir, 'app'))) {
                this.copyDir(path.join(this.srcDir, 'app'), path.join(buildSrcDir, 'app'));
            }
            if (this.fileExists(path.join(this.srcDir, 'assets'))) {
                this.copyDir(path.join(this.srcDir, 'assets'), path.join(buildSrcDir, 'assets'));
            }
            if (this.fileExists(path.join(this.srcDir, 'controller'))) {
                this.copyDir(path.join(this.srcDir, 'controller'), path.join(buildSrcDir, 'controller'));
            }
            if (this.fileExists(path.join(this.srcDir, 'model'))) {
                this.copyDir(path.join(this.srcDir, 'model'), path.join(buildSrcDir, 'model'));
            }
            if (this.fileExists(path.join(this.srcDir, 'route'))) {
                this.copyDir(path.join(this.srcDir, 'route'), path.join(buildSrcDir, 'route'));
            }
            if (this.fileExists(path.join(angularSrc, 'libs'))) {
                this.copyDir(path.join(angularSrc, 'libs'), path.join(buildSrcDir, 'libs'));
            }
            if (this.fileExists(path.join(angularSrc, 'styles'))) {
                this.copyDir(path.join(angularSrc, 'styles'), path.join(buildSrcDir, 'styles'));
            }

            // portal 빌드
            this.buildPortal();
        }
    }

    // 변경된 파일만 복사
    copyChangedFile(changedFile, buildSrcDir, angularSrc) {
        const srcPath = path.resolve(changedFile);
        const projectRoot = path.resolve(this.projectRoot);
        
        // src 디렉토리 내의 파일인지 확인
        if (!srcPath.startsWith(projectRoot)) {
            return;
        }

        const relativePath = path.relative(projectRoot, srcPath);
        let buildPath = null;
        
        // src/angular 또는 src/ 디렉토리 내의 파일인지 확인
        if (relativePath.startsWith('src/angular/')) {
            buildPath = path.join(buildSrcDir, relativePath.substring('src/angular/'.length));
        } else if (relativePath.startsWith('src/')) {
            buildPath = path.join(buildSrcDir, relativePath.substring('src/'.length));
        } else if (relativePath.startsWith('config/')) {
            // config 파일은 그대로 복사
            buildPath = path.join(this.buildDir, relativePath);
        }
        
        if (buildPath && this.fileExists(srcPath)) {
            this.ensureDir(path.dirname(buildPath));
            this.copyFile(srcPath, buildPath);
            
            // SCSS/CSS 파일의 경우, ngc-esbuild가 감지할 수 있도록 처리
            if (srcPath.endsWith('.scss') || srcPath.endsWith('.css')) {
                // 파일을 다시 쓰기하여 타임스탬프 업데이트 (ngc-esbuild가 감지하도록)
                const content = this.readFile(buildPath);
                this.writeFile(buildPath, content);
                
                // 관련 컴포넌트 TypeScript 파일 찾기
                const dir = path.dirname(buildPath);
                
                // view.ts 파일 찾기 (view.ts가 component.ts로 변환되므로)
                const viewTs = path.join(dir, 'view.ts');
                if (this.fileExists(viewTs)) {
                    // 약간의 지연 후 터치 (파일 시스템 이벤트가 확실히 발생하도록)
                    setTimeout(() => {
                        const tsContent = this.readFile(viewTs);
                        this.writeFile(viewTs, tsContent);
                    }, 300);
                }
                
                // component.ts 파일들 찾기
                const files = this.listDir(dir);
                for (const file of files) {
                    if (file.endsWith('.component.ts')) {
                        const componentTs = path.join(dir, file);
                        setTimeout(() => {
                            const tsContent = this.readFile(componentTs);
                            this.writeFile(componentTs, tsContent);
                        }, 300);
                    }
                }
            }
        }
    }

    buildPortal() {
        const portalDir = this.abspath('src', 'portal');
        if (!this.fileExists(portalDir)) return;

        const modules = this.listDir(portalDir);
        for (const module of modules) {
            const portalJsonPath = path.join(portalDir, module, 'portal.json');
            if (!this.fileExists(portalJsonPath)) continue;

            const info = this.readJson(portalJsonPath, {});
            const checker = (name) => {
                const key = `use_${name}`;
                return info[key] || false;
            };

            if (checker('app')) this.buildPortalApp(module, 'app');
            if (checker('widget')) this.buildPortalApp(module, 'widget');
            if (checker('route')) this.buildPortalApi(module);
            if (checker('controller')) this.buildPortalFiles(module, 'controller', 'controller');
            if (checker('model')) this.buildPortalFiles(module, 'model', 'model');
            if (checker('assets')) this.buildPortalFiles(module, 'assets', 'assets');
            if (checker('libs')) this.buildPortalFiles(module, 'libs', 'libs');
            if (checker('styles')) this.buildPortalFiles(module, 'styles', 'styles');
        }
    }

    buildPortalApp(module, mode = 'app') {
        const appsDir = this.abspath('src', 'portal', module, mode);
        if (!this.fileExists(appsDir)) return;

        const apps = this.listDir(appsDir);
        for (const app of apps) {
            const namespace = `portal.${module}.${app}`;
            const srcPath = path.join('src', 'portal', module, mode, app);
            const targetPath = path.join('build', 'src', 'app', namespace);
            
            this.copyDir(this.abspath(srcPath), this.abspath(targetPath));
            
            const appJsonPath = this.abspath(targetPath, 'app.json');
            const appJson = this.readJson(appJsonPath, {});
            appJson.id = namespace;
            appJson.mode = 'portal';
            appJson.path = this.abspath(srcPath, 'app.json');
            
            if (appJson.controller && appJson.controller.length > 0) {
                appJson.controller = `portal/${module}/${appJson.controller}`;
            }
            
            this.writeJson(appJsonPath, appJson);
        }
    }

    buildPortalApi(module) {
        const routeDir = this.abspath('src', 'portal', module, 'route');
        if (!this.fileExists(routeDir)) return;

        const apps = this.listDir(routeDir);
        for (const app of apps) {
            const namespace = `portal.${module}.${app}`;
            const srcPath = this.abspath('src', 'portal', module, 'route', app);
            const targetPath = this.abspath('build', 'src', 'route', namespace);
            
            this.copyDir(srcPath, targetPath);
            
            const appJsonPath = path.join(targetPath, 'app.json');
            const appJson = this.readJson(appJsonPath, {});
            appJson.id = namespace;
            
            if (appJson.controller && appJson.controller.length > 0) {
                appJson.controller = `portal/${module}/${appJson.controller}`;
            }
            
            this.writeJson(appJsonPath, appJson);
        }
    }

    buildPortalFiles(module, target, src) {
        const srcDir = this.abspath('src', 'portal', module, target);
        if (!this.fileExists(srcDir)) return;

        const destDir = this.abspath('build', 'src', src, 'portal', module);
        this.ensureDir(destDir);

        const files = this.listDir(srcDir);
        for (const f of files) {
            const srcPath = this.abspath('src', 'portal', module, target, f);
            const destPath = path.join(destDir, f);
            if (this.isDir(srcPath)) {
                this.copyDir(srcPath, destPath);
            } else {
                this.copyFile(srcPath, destPath);
            }
        }
    }

    // 빌드: TypeScript와 Pug에 annotation 추가
    build(changedFiles = null) {
        // console.log('[Builder] Building...');

        const baseuri = this.baseuri;
        const template = this.template;

        // build apps
        const apps = [];
        const buildAppDir = this.abspath('build', 'src', 'app');
        
        if (this.fileExists(buildAppDir)) {
            const appDirs = this.listDir(buildAppDir);
            
            for (const appId of appDirs) {
                const appJsonPath = path.join(buildAppDir, appId, 'app.json');
                if (!this.fileExists(appJsonPath)) continue;

                const app = this.readJson(appJsonPath, {});
                const viewTsPath = path.join(buildAppDir, appId, 'view.ts');
                if (!this.fileExists(viewTsPath)) continue;

                const viewts = this.readFile(viewTsPath);

                // update app.json
                const componentName = Namespace.componentName(appId) + 'Component';

                app.id = appId;
                app.path = `./${appId}/${appId}.component`;
                app.name = componentName;

                const componentInfo = AnnotatorDefinition.ngComponentDesc(viewts);
                app['ng.build'] = {
                    id: appId,
                    name: componentName,
                    path: `./${appId}/${appId}.component`
                };
                const ngtemplate = app.ng = {
                    selector: Namespace.selector(appId),
                    ...componentInfo
                };
                const injector = [
                    ...ngtemplate.inputs.map(x => `[${x}]=""`),
                    ...ngtemplate.outputs.map(x => `(${x})=""`)
                ].join(', ');
                app.template = `${ngtemplate.selector}(${injector})`;

                this.writeJson(appJsonPath, app);

                app['view.ts'] = viewts;
                apps.push(app);
            }
        }

        // routing
        const appsRouting = {};
        for (const app of apps) {
            try {
                if (app.mode === 'page') {
                    const layout = app.layout || 'default';
                    if (!appsRouting[layout]) {
                        appsRouting[layout] = [];
                    }
                    if (app.viewuri && app.viewuri.length > 0) {
                        let routingUri = app.viewuri;
                        if (routingUri[0] === '/') {
                            routingUri = routingUri.substring(1);
                        }
                        appsRouting[layout].push({
                            path: routingUri,
                            component: app.id,
                            app_id: app.id
                        });
                    }
                }
            } catch (e) {
                // ignore
            }
        }

        let appRoutingAuto = [];
        for (const layout in appsRouting) {
            appRoutingAuto.push({
                component: layout,
                children: appsRouting[layout]
            });
        }

        // JSON을 문자열로 변환하고 route 변환 적용
        let appRoutingAutoStr = JSON.stringify(appRoutingAuto, null, 4);
        // Python route() 메서드와 동일한 로직
        // JSON 문자열에서 "component": "app_id" 형태를 component: AppIdComponent로 변환
        // 패턴: "component": "app_id" -> component: AppIdComponent
        appRoutingAutoStr = appRoutingAutoStr.replace(/"component"\s*:\s*"([^"]+)"/g, (match, val) => {
            return `component: ${Namespace.componentName(val)}Component`;
        });
        appRoutingAutoStr = appRoutingAutoStr.replace(/'component'\s*:\s*'([^']+)'/g, (match, val) => {
            return `component: ${Namespace.componentName(val)}Component`;
        });
        // 남은 따옴표 제거 (혹시 남아있는 경우)
        appRoutingAutoStr = appRoutingAutoStr.replace(/"component/g, 'component');
        appRoutingAutoStr = appRoutingAutoStr.replace(/'component/g, 'component');

        // prefix and imports
        let prefix = apps.map(x => ({ name: x.name, path: x.path }));
        let imports = [];
        let declarations = apps.map(x => x.name);

        for (const app of apps) {
            const appId = app.id;
            const code = app['view.ts'];
            const deps = AnnotatorDefinition.dependencies(code);

            for (const dep in deps) {
                const pkg = deps[dep];
                const tmp = { name: dep, path: pkg };
                if (!prefix.find(p => p.name === tmp.name && p.path === tmp.path)) {
                    prefix.push(tmp);
                }
                if (!imports.includes(dep)) {
                    imports.push(dep);
                }
            }

            const dirDeps = AnnotatorDefinition.directives(code);
            for (const dep in dirDeps) {
                const pkg = dirDeps[dep];
                const tmp = { name: dep, path: pkg };
                if (!prefix.find(p => p.name === tmp.name && p.path === tmp.path)) {
                    prefix.push(tmp);
                }
                if (!declarations.includes(dep)) {
                    declarations.push(dep);
                }
            }
        }

        const prefixStr = prefix.map(x => `import { ${x.name} } from '${x.path}';`).join('\n');
        const importsStr = imports.map(x => `        ${x}`).join(',\n');
        const declarationsStr = 'AppComponent,\n' + declarations.map(x => `        ${x}`).join(',\n');

        // build pug (pug 모드일 때만, 증분 빌드 지원)
        if (template === 'pug') {
            let pugTargets = [];
            if (changedFiles && changedFiles.length > 0) {
                // 변경된 파일만 처리
                for (const changedFile of changedFiles) {
                    const srcPath = path.resolve(changedFile);
                    const projectRoot = path.resolve(this.projectRoot);
                    if (!srcPath.startsWith(projectRoot)) continue;
                    
                    const relativePath = path.relative(projectRoot, srcPath);
                    if (relativePath.startsWith('src/') && relativePath.endsWith('.pug')) {
                        let buildPath = relativePath;
                        if (relativePath.startsWith('src/angular/')) {
                            buildPath = path.join('build', 'src', relativePath.substring('src/angular/'.length));
                        } else if (relativePath.startsWith('src/')) {
                            buildPath = path.join('build', 'src', relativePath.substring('src/'.length));
                        }
                        const fullBuildPath = this.abspath(buildPath);
                        if (this.fileExists(fullBuildPath)) {
                            pugTargets.push(fullBuildPath.replace(/\.pug$/, ''));
                        }
                    }
                }
            } else {
                // 전체 빌드: 모든 파일 처리
                pugTargets = this.search(this.abspath('build', 'src'), [], '.pug');
            }
            
            for (const target of pugTargets) {
                let code = this.readFile(target + '.pug');
                const filename = path.basename(target);
                if (filename === 'view') {
                    const appId = path.basename(path.dirname(target));
                    code = this.pug(code, appId, baseuri);
                } else {
                    code = this.pug(code, null, baseuri);
                }
                this.writeFile(target + '.pug', code);
            }
        }

        // build typescript (증분 빌드: 변경된 파일만 처리)
        let tsTargets = [];
        if (changedFiles && changedFiles.length > 0) {
            // 변경된 파일만 처리
            const processedDirs = new Set();
            for (const changedFile of changedFiles) {
                const srcPath = path.resolve(changedFile);
                const projectRoot = path.resolve(this.projectRoot);
                if (!srcPath.startsWith(projectRoot)) continue;
                
                const relativePath = path.relative(projectRoot, srcPath);
                
                // SCSS/CSS 파일이 변경되면 관련 TypeScript 파일도 처리
                if (relativePath.startsWith('src/') && (relativePath.endsWith('.scss') || relativePath.endsWith('.css'))) {
                    // SCSS 파일의 디렉토리에서 view.ts 또는 component.ts 찾기
                    const scssDir = path.dirname(relativePath);
                    let buildDir = scssDir;
                    if (scssDir.startsWith('src/angular/')) {
                        buildDir = path.join('build', 'src', scssDir.substring('src/angular/'.length));
                    } else if (scssDir.startsWith('src/')) {
                        buildDir = path.join('build', 'src', scssDir.substring('src/'.length));
                    }
                    const fullBuildDir = this.abspath(buildDir);
                    
                    // view.ts 찾기
                    const viewTs = path.join(fullBuildDir, 'view.ts');
                    if (this.fileExists(viewTs)) {
                        const dirKey = path.dirname(viewTs);
                        if (!processedDirs.has(dirKey)) {
                            tsTargets.push(viewTs.replace(/\.ts$/, ''));
                            processedDirs.add(dirKey);
                        }
                    }
                    
                    // component.ts 찾기
                    const basename = path.basename(relativePath, path.extname(relativePath));
                    const componentTs = path.join(fullBuildDir, basename + '.component.ts');
                    if (this.fileExists(componentTs)) {
                        const dirKey = path.dirname(componentTs);
                        if (!processedDirs.has(dirKey)) {
                            tsTargets.push(componentTs.replace(/\.ts$/, ''));
                            processedDirs.add(dirKey);
                        }
                    }
                } else if (relativePath.startsWith('src/') && relativePath.endsWith('.ts')) {
                    // TypeScript 파일 변경
                    let buildPath = relativePath;
                    if (relativePath.startsWith('src/angular/')) {
                        buildPath = path.join('build', 'src', relativePath.substring('src/angular/'.length));
                    } else if (relativePath.startsWith('src/')) {
                        buildPath = path.join('build', 'src', relativePath.substring('src/'.length));
                    }
                    const fullBuildPath = this.abspath(buildPath);
                    if (this.fileExists(fullBuildPath)) {
                        tsTargets.push(fullBuildPath.replace(/\.ts$/, ''));
                    }
                }
            }
        } else {
            // 전체 빌드: 모든 파일 처리
            tsTargets = this.search(this.abspath('build', 'src', 'app'), [], '.ts');
        }
        
        for (const target of tsTargets) {
            let code = this.readFile(target + '.ts');
            const filename = path.basename(target);
            const dirname = path.dirname(target);

            if (filename === 'view') {
                const appId = path.basename(dirname);

                // if view.ts
                const importString = "import { Component } from '@angular/core';\n";
                const componentName = Namespace.componentName(appId);
                const componentOpts = `{\n    selector: '${Namespace.selector(appId)}',\n    templateUrl: './view.html',\n    styleUrls: ['./view.scss']\n}`;

                code = `import Wiz from 'src/wiz';\nlet wiz = new Wiz('${baseuri}').app('${appId}');\n` + code;
                code = code.replace('export class Component', `@Component(${componentOpts})\n` + `export class ${componentName}Component`);
                code = `${importString}\n` + code.trim();
                code = code + `\n\nexport default ${componentName}Component;`;

                if (fs.existsSync(target + '.ts')) {
                    fs.unlinkSync(target + '.ts');
                }
                const newTarget = path.join(dirname, appId + '.component');

                code = this.typescript(code, appId, baseuri, declarationsStr, importsStr);
                this.writeFile(newTarget + '.ts', code);
            } else if (filename === 'app-routing.module') {
                code = code.replace('wiz.routes()', appRoutingAutoStr);
                code = this.typescript(code, null, baseuri, declarationsStr, importsStr, prefixStr);
                this.writeFile(target + '.ts', code);
            } else if (filename === 'app.component') {
                code = `import Wiz from 'src/wiz';\nlet wiz = new Wiz('${baseuri}');\n` + code;
                code = this.typescript(code, null, baseuri);
                this.writeFile(target + '.ts', code);
            } else if (filename === 'app.module') {
                code = this.typescript(code, null, baseuri, declarationsStr, importsStr, prefixStr);
                this.writeFile(target + '.ts', code);
            } else {
                code = this.typescript(code, null, baseuri);
                this.writeFile(target + '.ts', code);
            }
        }

        // build pug files (pug 모드일 때만)
        if (template === 'pug') {
            const pugTargets = this.search(this.abspath('build', 'src'), [], '.pug');
            if (pugTargets.length > 0) {
                const buildBasePath = this.abspath('build');
                const targetsStr = pugTargets.join(' ');
                try {
                    execSync(`cd ${buildBasePath} && node wizbuild.js ${targetsStr}`, { stdio: 'inherit' });
                } catch (e) {
                    console.error('[Builder] Pug compilation failed:', e.message);
                }
            }
        }

        // build angular json
        const angularJsonPath = this.abspath('src', 'angular', 'angular.json');
        let angularJson = this.readJson(angularJsonPath, {
            projects: {
                build: {
                    architect: {
                        build: {
                            options: {}
                        }
                    }
                }
            }
        });

        const angularBuildOptionsJsonPath = this.abspath('src', 'angular', 'angular.build.options.json');
        if (this.fileExists(angularBuildOptionsJsonPath)) {
            const angularBuildOptionsJson = this.readJson(angularBuildOptionsJsonPath, {});
            for (const key in angularBuildOptionsJson) {
                if (['outputPath', 'index', 'main', 'polyfills', 'tsConfig', 'inlineStyleLanguage'].includes(key)) continue;
                if (angularJson.projects && angularJson.projects.build && 
                    angularJson.projects.build.architect && angularJson.projects.build.architect.build &&
                    angularJson.projects.build.architect.build.options) {
                    angularJson.projects.build.architect.build.options[key] = angularBuildOptionsJson[key];
                }
            }
        }

        this.writeJson(this.abspath('build', 'angular.json'), angularJson);
        // this.writeJson(angularJsonPath, angularJson);

        // build tailwindcss
        const tailwindBin = this.abspath('build', 'node_modules', '.bin', 'tailwindcss');
        if (this.fileExists(tailwindBin)) {
            const buildBasePath = this.abspath('build');
            try {
                execSync(`cd ${buildBasePath} && node_modules/.bin/tailwindcss -o tailwind.min.css --minify`, { stdio: 'inherit' });
            } catch (e) {
                // ignore tailwind errors
            }
        }
    }

    // Angular 빌드
    angular(watch = false) {
        // console.log(`[Builder] Building Angular (watch: ${watch})...`);

        return new Promise((resolve, reject) => {
            if (watch && this.angularProcess) {
                this.angularProcess.kill();
            }

            const wizbuildPath = path.join(this.buildDir, 'wizbuild.js');
            const args = watch ? ['--watch'] : [];

            if (watch) {
                // watch 모드에서는 "changed:" 로그를 필터링하고 빌드 완료 이벤트 감지
                this.angularProcess = spawn('node', [wizbuildPath, ...args], {
                    cwd: this.buildDir,
                    stdio: ['inherit', 'pipe', 'pipe']
                });

                let stdoutBuffer = '';
                let stderrBuffer = '';

                // stdout 필터링 및 빌드 완료 감지
                this.angularProcess.stdout.on('data', (data) => {
                    stdoutBuffer += data.toString();
                    const lines = stdoutBuffer.split('\n');
                    stdoutBuffer = lines.pop() || ''; // 마지막 불완전한 라인 보관

                    for (const line of lines) {
                        if (line.trim() && !line.trim().startsWith('changed:')) {
                            process.stdout.write(line + '\n');
                        }
                        // EsBuild complete 감지 시 bundle 실행
                        if (line.includes('EsBuild complete')) {
                            setTimeout(() => {
                                try {
                                    this.bundle();
                                } catch (err) {
                                    console.error('[Builder] Bundle error:', err);
                                }
                            }, 100);
                        }
                    }
                });

                // stderr 필터링
                this.angularProcess.stderr.on('data', (data) => {
                    stderrBuffer += data.toString();
                    const lines = stderrBuffer.split('\n');
                    stderrBuffer = lines.pop() || '';

                    for (const line of lines) {
                        if (line.trim() && !line.trim().startsWith('changed:')) {
                            process.stderr.write(line + '\n');
                        }
                    }
                });

                resolve();
            } else {
                // 일반 빌드 모드에서는 모든 출력 표시
                this.angularProcess = spawn('node', [wizbuildPath, ...args], {
                    cwd: this.buildDir,
                    stdio: 'inherit'
                });

                this.angularProcess.on('close', (code) => {
                    if (code === 0 || code === 1) {
                        resolve();
                    } else {
                        reject(new Error(`Angular build failed with code ${code}`));
                    }
                });
            }
        });
    }

    // Bundle: build/dist/build를 bundle/www로 복사
    bundle() {
        // console.log('[Builder] Bundling...');

        // bundle 디렉토리 삭제 및 생성
        if (fs.existsSync(this.bundleDir)) {
            fs.rmSync(this.bundleDir, { recursive: true, force: true });
        }
        this.ensureDir(this.bundleDir);

        // 복사
        const distBuildDir = path.join(this.buildDir, 'dist', 'build');
        if (this.fileExists(distBuildDir)) {
            this.copyDir(distBuildDir, path.join(this.bundleDir, 'www'));
        }

        const buildSrcDir = path.join(this.buildDir, 'src');
        ['assets', 'controller', 'model', 'route'].forEach(dir => {
            const src = path.join(buildSrcDir, dir);
            if (this.fileExists(src)) {
                this.copyDir(src, path.join(this.bundleDir, 'src', dir));
            }
        });

        // config 복사
        if (this.fileExists(this.abspath('config'))) {
            this.copyDir(this.abspath('config'), path.join(this.bundleDir, 'config'));
        }

        // app 디렉토리의 .py, .json 파일 복사
        this.copyAppFiles();
    }

    copyAppFiles() {
        const buildAppDir = this.abspath('build', 'src', 'app');
        if (!this.fileExists(buildAppDir)) return;

        const walk = (dir, baseDir = '') => {
            const files = this.listDir(dir);
            for (const file of files) {
                const filePath = path.join(dir, file);
                const relPath = path.join(baseDir, file);
                const stat = fs.statSync(filePath);

                if (stat.isDirectory()) {
                    walk(filePath, relPath);
                } else {
                    const ext = path.extname(file);
                    if (['.py', '.json'].includes(ext)) {
                        const dest = path.join(this.bundleDir, 'src', 'app', relPath);
                        this.copyFile(filePath, dest);
                    }
                }
            }
        };

        walk(buildAppDir);
    }

    // 전체 빌드 프로세스
    async fullBuild(skipAngular = false, changedFiles = null) {
        if (this.isBuilding) {
            // console.log('[Builder] Build already in progress, queuing...');
            return new Promise((resolve) => {
                this.buildQueue.push(resolve);
            });
        }

        this.isBuilding = true;
        try {
            this.reconstruct(changedFiles);
            this.build(changedFiles);
            if (!skipAngular) {
                await this.angular(false);
                this.bundle();
            }
            // console.log('[Builder] Build completed successfully');
        } catch (error) {
            console.error('[Builder] Build failed:', error);
            throw error;
        } finally {
            this.isBuilding = false;
            if (this.buildQueue.length > 0) {
                const next = this.buildQueue.shift();
                next();
                await this.fullBuild(skipAngular, changedFiles);
            }
        }
    }

    // Watch 모드 시작
    async watch() {
        // console.log('[Builder] Starting watch mode...');

        // 초기 빌드
        await this.fullBuild();

        // Angular watch 모드 시작
        await this.angular(true);

        // 파일 감시 설정
        const watchPaths = [
            path.join(this.srcDir, '**/*'),
            path.join(this.projectRoot, 'config', '**/*')
        ];

        this.watcher = chokidar.watch(watchPaths, {
            ignored: /(^|[\/\\])\../,
            persistent: true,
            ignoreInitial: true
        });

        this.watcher
            .on('add', (filePath) => this.onFileChange(filePath))
            .on('change', (filePath) => this.onFileChange(filePath))
            .on('unlink', (filePath) => this.onFileChange(filePath))
            .on('error', (error) => console.error('[Builder] Watcher error:', error));

        // console.log('[Builder] Watching for changes...');
    }

    async onFileChange(filePath) {
        // console.log(`[Builder] File changed: ${filePath}`);

        if (filePath.includes('/build/') || filePath.includes('/node_modules/') ||
            filePath.includes('/bundle/') || filePath.includes('/.git/')) {
            return;
        }

        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        // 변경된 파일 목록 수집 (debounce 동안 여러 파일 변경 가능)
        if (!this.pendingChanges) {
            this.pendingChanges = [];
        }
        this.pendingChanges.push(filePath);

        this.debounceTimer = setTimeout(async () => {
            try {
                const changedFiles = [...this.pendingChanges];
                this.pendingChanges = [];
                
                // watch 모드에서는 ngc-esbuild가 자동으로 빌드하므로,
                // reconstruct와 build만 실행하고 angular는 건너뜀
                // 증분 빌드: 변경된 파일만 처리
                this.reconstruct(changedFiles);
                this.build(changedFiles);
                
                // SCSS 파일이 변경된 경우, ngc-esbuild가 감지하도록 관련 TypeScript 파일 터치
                const hasScssChange = changedFiles.some(f => f.endsWith('.scss') || f.endsWith('.css'));
                if (hasScssChange) {
                    // 관련 TypeScript 파일들을 찾아서 터치
                    for (const changedFile of changedFiles) {
                        if (changedFile.endsWith('.scss') || changedFile.endsWith('.css')) {
                            const srcPath = path.resolve(changedFile);
                            const projectRoot = path.resolve(this.projectRoot);
                            if (!srcPath.startsWith(projectRoot)) continue;
                            
                            const relativePath = path.relative(projectRoot, srcPath);
                            if (relativePath.startsWith('src/')) {
                                let buildPath = relativePath;
                                if (relativePath.startsWith('src/angular/')) {
                                    buildPath = path.join('build', 'src', relativePath.substring('src/angular/'.length));
                                } else if (relativePath.startsWith('src/')) {
                                    buildPath = path.join('build', 'src', relativePath.substring('src/'.length));
                                }
                                
                                const buildDir = path.dirname(this.abspath(buildPath));
                                
                                // view.ts 파일 찾아서 터치 (view.ts가 component.ts로 변환되므로)
                                const viewTs = path.join(buildDir, 'view.ts');
                                if (this.fileExists(viewTs)) {
                                    // view.ts를 다시 읽어서 쓰기 (타임스탬프 업데이트)
                                    // 지연 시간을 늘려서 파일 시스템 이벤트가 확실히 발생하도록
                                    setTimeout(() => {
                                        const content = this.readFile(viewTs);
                                        this.writeFile(viewTs, content);
                                    }, 300);
                                }
                                
                                // component.ts 파일들 찾아서 터치
                                const files = this.listDir(buildDir);
                                for (const file of files) {
                                    if (file.endsWith('.component.ts')) {
                                        const componentTs = path.join(buildDir, file);
                                        setTimeout(() => {
                                            const content = this.readFile(componentTs);
                                            this.writeFile(componentTs, content);
                                        }, 300);
                                    }
                                }
                            }
                        }
                    }
                }
                
                this.bundle();
                
                if (changedFiles.some(f => f.endsWith('.py'))) {
                    const wiz_url = `http://localhost:${this.port}${this.baseuri}/ide/api/core.app.ide/cache_clear`;
                    await fetch(wiz_url);
                    // let res = await fetch(wiz_url);
                    // res = await res.json();
                }
            } catch (error) {
                console.error('[Builder] Build error:', error);
            }
        }, 500);
    }

    // 정리
    stop() {
        if (this.watcher) {
            this.watcher.close();
        }
        if (this.angularProcess) {
            this.angularProcess.kill();
        }
    }

    // 기본 템플릿들
    getDefaultWizbuild() {
        return `const fs = require('fs');
const pug = require('pug');
const watchMode = process.argv.includes('--watch');

if (!watchMode && process.argv.length > 2) {
    for (let i = 2; i < process.argv.length; i++) {
        const target = process.argv[i];
        const targetpath = target + '.pug';
        const savepath = target + '.html';
        const compiledFunction = pug.compileFile(targetpath);
        fs.writeFileSync(savepath, compiledFunction(), "utf8")
    }
} else {
    const NgcEsbuild = require('ngc-esbuild');
    new NgcEsbuild({
        minify: !watchMode,
        open: false,
        serve: false,
        watch: watchMode,
    }).resolve.then((result) => {
        if (!watchMode) {
            process.exit(1);
        }
    });
}`;
    }

    getDefaultTsconfig() {
        return JSON.stringify({
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
                "lib": ["ES2022", "dom"]
            },
            "angularCompilerOptions": {
                "enableI18nLegacyMessageIdFormat": false,
                "strictInjectionParameters": true,
                "strictInputAccessModifiers": true,
                "strictTemplates": true
            }
        }, null, 2);
    }

    getDefaultTailwind() {
        return `/** @type {import('tailwindcss').Config} */
module.exports = {
content: [
    "./src/**/*.{html,ts}",
],
theme: {
    extend: {},
},
plugins: [],
}`;
    }
}

// CLI 인터페이스
if (require.main === module) {
    const args = process.argv.slice(2);
    const watchMode = args.includes('--watch') || args.includes('-w');
    const builder = new Builder();
    const portIndex = args.findIndex(arg => ['--port', '-p'].includes(arg));
    const port = portIndex !== -1 ? args[portIndex + 1] : 3000;
    builder.setPort(port);

    if (watchMode) {
        builder.watch().catch(error => {
            console.error('Error:', error);
            process.exit(1);
        });

        process.on('SIGINT', () => {
            // console.log('\n[Builder] Stopping...');
            builder.stop();
            process.exit(0);
        });
    } else {
        builder.fullBuild().catch(error => {
            console.error('Error:', error);
            process.exit(1);
        });
    }
}

module.exports = Builder;

