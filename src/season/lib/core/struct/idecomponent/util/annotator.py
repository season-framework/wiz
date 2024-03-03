import re
from .namespace import Namespace

class Definition:
    def directives(self, code):
        result = dict()
        pattern = re.compile('@directives\(([^\)]*)\)', re.DOTALL)
        res = pattern.findall(code)
        for data in res:
            data = data.replace("'", '').replace('"', '').replace(',', '').replace(' ', '')
            pattern = re.compile('(.*):(.*)')
            finded = pattern.findall(data)
            for item in finded:
                result[item[0]] = item[1]
        return result

    def dependencies(self, code):
        result = dict()
        pattern = re.compile('@dependencies\(([^\)]*)\)', re.DOTALL)
        res = pattern.findall(code)
        for data in res:
            data = data.replace("'", '').replace('"', '').replace(',', '').replace(' ', '')
            pattern = re.compile('(.*):(.*)')
            finded = pattern.findall(data)
            for item in finded:
                result[item[0]] = item[1]
        return result

    def directives(self, code):
        result = dict()
        pattern = re.compile('@directives\(([^\)]*)\)', re.DOTALL)
        res = pattern.findall(code)
        for data in res:
            data = data.replace("'", '').replace('"', '').replace(',', '').replace(' ', '')
            pattern = re.compile('(.*):(.*)')
            finded = pattern.findall(data)
            for item in finded:
                result[item[0]] = item[1]
        return result

    def ngComponentDesc(self, code):
        res = dict(inputs=[], outputs=[])
        def convert(match_obj):
            val = match_obj.group(1).replace(" ", "")
            res['inputs'].append(val)
            return val
        pattern = re.compile('@Input\(\)([^=\:\n\;]*)')
        re.sub(pattern, convert, code)
        
        def convert(match_obj):
            val = match_obj.group(1).replace(" ", "")
            res['outputs'].append(val)
            return val
        pattern = re.compile('@Output\(\)([^=\:\n\;]*)')
        re.sub(pattern, convert, code)
        
        return res

class Injection:
    def title(self, code, title):
        if title is None: return code
        pattern = r'@wiz.title\((.*)\)'
        def convert(match_obj):
            return title
        code = re.sub(pattern, convert, code)
        code = code.replace("@wiz.title", title)
        return code
       
    def app(self, code):
        def convert(match_obj):
            val = match_obj.group(1)
            if len(val.split("/")) > 1:
                val = val.replace("/directive", "/app.directive")
                return f'"src/app/{val}"'
            return f'"src/app/{val}/{val}.component"'
        patterns = [r'"@wiz\/app\/(.*)"', r"'@wiz\/app\/(.*)'"]
        for pattern in patterns:
            code = re.sub(pattern, convert, code)
        return code
    
    def service(self, code):
        def convert(match_obj):
            val = match_obj.group(1)
            return f'"src/service/{val}"'
        pattern = r'"@wiz\/service\/(.*)"'
        code = re.sub(pattern, convert, code)
        pattern = r"'@wiz\/service\/(.*)'"
        code = re.sub(pattern, convert, code)
        return code

    def libs(self, code):
        def convert(match_obj):
            val = match_obj.group(1)
            return f'"src/libs/{val}"'
        patterns = [r'"@wiz\/libs\/(.*)"', r"'@wiz\/libs\/(.*)'"]
        for pattern in patterns:
            code = re.sub(pattern, convert, code)
        return code

    def namespace(self, code, app_id):
        if app_id is None: return code
        def convert(match_obj):
            return app_id
        pattern = r'@wiz.namespace\((.*)\)'
        code = re.sub(pattern, convert, code)
        code = code.replace("@wiz.namespace", app_id)
        return code

    def cwd(self, code, app_id):
        if app_id is None: return code
        def convert(match_obj):
            val = match_obj.group(1)
            val = val.replace("directive", "app.directive")
            return f'"src/app/{app_id}/{val}"'
        patterns = [r'"@wiz\/cwd\/(.*)"', r"'@wiz\/cwd\/(.*)'"]
        for pattern in patterns:
            code = re.sub(pattern, convert, code)
        return code

    def baseuri(self, code, baseuri):
        if baseuri is None: return code
        def convert(match_obj):
            val = match_obj.group(1)
            if len(val) > 0:
                if val[0] == "/":
                    val = val[1:]
                return baseuri + "/" + val
            return baseuri
        pattern = r'@wiz.baseuri\((.*)\)'
        code = re.sub(pattern, convert, code)
        code = code.replace("@wiz.baseuri", baseuri)
        return code

    def dependencies(self, code):
        def convert(match_obj):
            val1 = match_obj.group(1)
            return ""
        pattern = re.compile('@dependencies\(([^\)]*)\)', re.DOTALL)
        code = re.sub(pattern, convert, code)
        return code
    
    def directives(self, code):
        def convert(match_obj):
            val1 = match_obj.group(1)
            return ""
        pattern = re.compile('@directives\(([^\)]*)\)', re.DOTALL)
        code = re.sub(pattern, convert, code)
        return code

    def declarations(self, code, declarations):
        if declarations is None: return code
        def convert(match_obj):
            return declarations
        patterns = [r'"@wiz.declarations\((.*)\)"', r"'@wiz.declarations\((.*)\)'"]
        for pattern in patterns:
            code = re.sub(pattern, convert, code)
        code = code.replace("'@wiz.declarations'", declarations)
        code = code.replace('"@wiz.declarations"', declarations)
        return code

    def imports(self, code, imports):
        if imports is None: return code
        def convert(match_obj):
            return imports
        patterns = [r'"@wiz.imports\((.*)\)"', r"'@wiz.imports\((.*)\)'"]
        for pattern in patterns:
            code = re.sub(pattern, convert, code)
        code = code.replace("'@wiz.imports'", imports)
        code = code.replace('"@wiz.imports"', imports)
        return code
    
    def route(self, code):
        def convert(match_obj):
            val = match_obj.group(1)
            return 'component: ' + Namespace.componentName(val) + "Component"
        pattern = r"component.*:.*'(.*)'"
        code = re.sub(pattern, convert, code)
        pattern = r'component.*:.*"(.*)"'
        code = re.sub(pattern, convert, code)
        code = code.replace("'component", "component")
        code = code.replace('"component', "component")
        return code

class _Annotator:
    def __init__(self):
        self.definition = Definition()
        self.injection = Injection()

Annotator = _Annotator()