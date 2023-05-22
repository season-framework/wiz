import season
import re

class Injection:
    def app(self, fileinfo):
        def convert(match_obj):
            val = match_obj.group(1)
            if len(val.split("/")) > 1:
                val = val.replace("/directive", "/app.directive")
                return f'"src/app/{val}"'
            return f'"src/app/{val}/{val}.component"'
        patterns = [r'"@wiz\/app\/(.*)"', r"'@wiz\/app\/(.*)'"]
        for pattern in patterns:
            fileinfo.code = re.sub(pattern, convert, fileinfo.code)
        return fileinfo

    def libs(self, fileinfo):
        def convert(match_obj):
            val = match_obj.group(1)
            return f'"src/libs/{val}"'
        patterns = [r'"@wiz\/libs\/(.*)"', r"'@wiz\/libs\/(.*)'"]
        for pattern in patterns:
            fileinfo.code = re.sub(pattern, convert, fileinfo.code)
        return fileinfo

    def namespace(self, fileinfo):
        if fileinfo.app_id is None: return fileinfo
        def convert(match_obj):
            return fileinfo.app_id
        pattern = r'@wiz.namespace\((.*)\)'
        fileinfo.code = re.sub(pattern, convert, fileinfo.code)
        fileinfo.code = fileinfo.code.replace("@wiz.namespace", fileinfo.app_id)
        return fileinfo

    def cwd(self, fileinfo):
        if fileinfo.app_id is None: return fileinfo
        def convert(match_obj):
            val = match_obj.group(1)
            val = val.replace("directive", "app.directive")
            return f'"src/app/{fileinfo.app_id}/{val}"'
        patterns = [r'"@wiz\/cwd\/(.*)"', r"'@wiz\/cwd\/(.*)'"]
        for pattern in patterns:
            fileinfo.code = re.sub(pattern, convert, fileinfo.code)
        return fileinfo

    def baseuri(self, fileinfo):
        if fileinfo.baseuri is None: return fileinfo
        def convert(match_obj):
            val = match_obj.group(1)
            if len(val) > 0:
                if val[0] == "/":
                    val = val[1:]
                return fileinfo.baseuri + "/" + val
            return fileinfo.baseuri
        pattern = r'@wiz.baseuri\((.*)\)'
        fileinfo.code = re.sub(pattern, convert, fileinfo.code)
        fileinfo.code = fileinfo.code.replace("@wiz.baseuri", fileinfo.baseuri)
        return fileinfo

    def dependencies(self, fileinfo):
        def convert(match_obj):
            val1 = match_obj.group(1)
            return ""
        pattern = re.compile('@dependencies\(([^\)]*)\)', re.DOTALL)
        fileinfo.code = re.sub(pattern, convert, fileinfo.code)
        return fileinfo
    
    def directives(self, fileinfo):
        def convert(match_obj):
            val1 = match_obj.group(1)
            return ""
        pattern = re.compile('@directives\(([^\)]*)\)', re.DOTALL)
        fileinfo.code = re.sub(pattern, convert, fileinfo.code)
        return fileinfo

    def declarations(self, fileinfo):
        if fileinfo.declarations is None: return fileinfo
        def convert(match_obj):
            return fileinfo.declarations
        patterns = [r'"@wiz.declarations\((.*)\)"', r"'@wiz.declarations\((.*)\)'"]
        for pattern in patterns:
            fileinfo.code = re.sub(pattern, convert, fileinfo.code)
        fileinfo.code = fileinfo.code.replace("'@wiz.declarations'", fileinfo.declarations)
        fileinfo.code = fileinfo.code.replace('"@wiz.declarations"', fileinfo.declarations)
        return fileinfo

    def imports(self, fileinfo):
        if fileinfo.imports is None: return fileinfo
        def convert(match_obj):
            return fileinfo.imports
        patterns = [r'"@wiz.imports\((.*)\)"', r"'@wiz.imports\((.*)\)'"]
        for pattern in patterns:
            fileinfo.code = re.sub(pattern, convert, fileinfo.code)
        fileinfo.code = fileinfo.code.replace("'@wiz.imports'", fileinfo.imports)
        fileinfo.code = fileinfo.code.replace('"@wiz.imports"', fileinfo.imports)
        return fileinfo

Model = Injection()