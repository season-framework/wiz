def compile(wiz, js, data):
    if 'render_id' not in data:
        return js

    plugin_id = data['plugin_id']
    app_id = data['app_id']
    render_id = data['render_id']

    o = "{"
    e = "}"
    kwargsstr = "{$ kwargs $}"
    dicstr = "{$ dicstr $}"

    js = f"""
    function __init_{render_id}() {o}
        let wiz = season_wiz.load('{plugin_id}', '{app_id}', '{render_id}');
        wiz.data = wiz.kwargs = wiz.options = JSON.parse(atob('{kwargsstr}'));
        wiz.dic = wiz.DIC = JSON.parse(atob('{dicstr}'));
        
        {js};

        try {o}
            app.controller('{render_id}', wiz_controller); 
        {e} catch (e) {o} 
            app.controller('{render_id}', ()=> {o} {e} ); 
        {e} 
    {e}; 
    __init_{render_id}();
    """

    return js