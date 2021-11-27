def compile(wiz, html, data):
    if 'render_id' not in data:
        return html
    app_id = data['app_id']
    render_id = data['render_id']
    html = html.split(">")
    if len(html) > 1:
        html = html[0] + f" id='{render_id}' ng-controller='{render_id}'>" + ">".join(html[1:])
    else:
        html = f"<div id='{render_id}' ng-controller='{render_id}'>" + ">".join(html) + "</div>"
    return html