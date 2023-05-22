import season
import re

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

Model = Definition()