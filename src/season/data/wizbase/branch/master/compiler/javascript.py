def compile(wiz, js, data):
    if 'render_id' not in data:
        return js

    app_id = data['app_id']
    app_namespace = data['app_namespace']
    render_id = data['render_id']
    namespace = data['namespace']

    o = "{"
    e = "}"
    kwargsstr = "{$ kwargs $}"
    dicstr = "{$ dicstr $}"
    branch = wiz.branch()
    isdev = wiz.is_dev()
    if isdev: isdev = 'true'
    else: isdev = 'false'

    js = f"""
    function __init_{render_id}() {o}
        var wiz = season_wiz.load('{app_id}', '{namespace}', '{app_namespace}');
        wiz.render_id = '{render_id}';
        wiz.is_dev = {isdev};
        wiz.branch = '{branch}';
        wiz.data = wiz.kwargs = wiz.options = JSON.parse(atob('{kwargsstr}'));
        wiz.dic = wiz.DIC = JSON.parse(atob('{dicstr}'));
        
        {js};

        try {o}
            app.controller('{render_id}', wiz_controller); 
        {e} catch (e) {o} 
            app.controller('{render_id}', function() {o} {e} ); 
        {e} 
    {e}; 
    __init_{render_id}();
    """

    return js