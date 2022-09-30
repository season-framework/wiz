import season
import subprocess
from abc import *

ESBUILD_SCRIPT = """const fs = require('fs');
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

ENV_SCRIPT = """export const environment = {
  production: true
};"""


class Build(metaclass=ABCMeta):
    def __init__(self, workspace):
        self.workspace = workspace

    def cmd(self, cmd):
        workspace = self.workspace
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        logger = workspace.wiz.logger('[build]')
        if out is not None and len(out) > 0: workspace.wiz.logger('[build][log]')(out.decode('utf-8').strip())
        if err is not None and len(err) > 0: workspace.wiz.logger('[build][error]')(err.decode('utf-8').strip(), level=season.LOG_CRITICAL)

    @abstractmethod
    def event_init(self):
        pass

    @abstractmethod
    def event_build(self):
        pass

    def params(self):
        obj = season.util.std.stdClass()
        obj.season = season
        obj.workspace = self.workspace
        obj.wiz = obj.workspace.wiz
        obj.config = obj.wiz.server.config.build
        
        obj.fs = season.util.std.stdClass()
        obj.fs.workspace = obj.workspace.fs()
        obj.fs.build = obj.workspace.fs(obj.config.folder)
        obj.fs.src = obj.workspace.fs("src")
        obj.fs.dist = obj.workspace.fs("dist")

        obj.workspacefs = obj.fs.workspace
        obj.buildfs = obj.fs.build
        obj.srcfs = obj.fs.src
        obj.distfs = obj.fs.dist

        obj.path = obj.buildfs.abspath()
        obj.cmd = self.cmd
        obj.command = self.cmd
        obj.execute = self.cmd

        return obj

    def __getattr__(self, key):
        params = self.params()
        obj = params[key]
        if hasattr(obj, '__call__'):
            return obj
        def fn():
            return obj
        return fn

    def init(self):
        workspace = self.workspace
        wiz = workspace.wiz
        fn = self.event_init
        params = self.params()
        season.util.fn.call(fn, **params)

    def clean(self):
        workspace = self.workspace
        wiz = workspace.wiz
        buildfs = self.buildfs()
        if buildfs.exists():
            buildfs.delete()
        self.init()

    def __call__(self, filepath=None):
        workspace = self.workspace
        wiz = workspace.wiz
        srcfs = self.srcfs().abspath()
        if filepath is None:
            filepath = ""
        elif filepath.startswith(srcfs):
            filepath = filepath[len(srcfs):]
            if len(filepath) > 0 and filepath[0] == "/":
                filepath = filepath[1:]

        fn = self.event_build
        params = self.params()
        params.filepath = filepath if filepath is not None else ""
        season.util.fn.call(fn, **params)