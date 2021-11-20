import season
import pypugjs

def compile(wiz, code, data):
    pugconfig = season.stdClass()
    pugconfig.variable_start_string = '{$'
    pugconfig.variable_end_string = '$}'

    pug = pypugjs.Parser(code)
    pug = pug.parse()
    html = pypugjs.ext.jinja.Compiler(pug, **pugconfig).compile()
    return html