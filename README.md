# SEASON WIZ (Widget Interface Zone)

- SEASON WIZ depends on `season-flask`

## Installation

```bash
sf module import wiz --uri https://github.com/season-framework/season-flask-wiz
pip install libsass dukpy
```

## Configuration

### MySQL Table Scheme

```sql
CREATE TABLE `widget` (
  `id` varchar(32) NOT NULL,
  `title` varchar(128) NOT NULL DEFAULT '',
  `namespace` varchar(32) DEFAULT NULL,
  `category` varchar(20) DEFAULT NULL,
  `content` text,
  `user_id` varchar(20) NOT NULL,
  `html` longtext,
  `js` longtext,
  `css` longtext,
  `api` longtext,
  `created` datetime NOT NULL,
  `updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `kwargs` longtext,
  `theme` varchar(32) DEFAULT NULL,
  `viewuri` text DEFAULT NULL,
  `route` varchar(192) DEFAULT NULL,
  `properties` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `namespace` (`namespace`),
  KEY `title` (`title`),
  KEY `category` (`category`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4;
```

### websrc/app/config/config.py

- add variable start/end string config: `{$` / `$}`

```python
import season
config = season.stdClass()

# ...

config.jinja_variable_start_string = "{$"
config.jinja_variable_end_string = "$}"
```

### websrc/app/config/database.py

- Add Database Connection Info for WIZ

```python
from season import stdClass
config = stdClass()

# ...

config.wiz = stdClass()
config.wiz.host = '127.0.0.1'
config.wiz.user = 'db_user'
config.wiz.password = 'db_password'
config.wiz.database = 'db_name'
config.wiz.charset = 'utf8'
```

### websrc/app/config/wiz.py

```python
from season import stdClass
config = stdClass()

def acl(framework):
    if 'role' not in framework.session:
        framework.response.abort(401)
    if framework.session['role'] not in ['admin']:
        framework.response.abort(401)

def uid(framework):
    return framework.session['id']

config.acl = acl
config.uid = uid
config.home = "/"
config.table = 'widget'
config.category = ["widget", "page"]
config.wizsrc = '/<wiz-src-path>/wiz-src'
config.topmenus = [{ 'title': 'HOME', 'url': '/' }, { 'title': 'sample', 'url': 'sample' }]

def themeobj(module, view):
    obj = stdClass()
    obj.module = module
    obj.view = view
    return obj

config.theme = stdClass()
config.theme.default = themeobj("<modulename>", "<viewname>.pug")
config.theme.default = themeobj("theme", "layout-wiz.pug")

config.pug = stdClass()
config.pug.variable_start_string = "{$"
config.pug.variable_end_string = "$}"
```

### custom theme

- setup base theme layout for wiz (eg. websrc/modules/theme/view/layout-wiz.pug)

```pug
doctype 5
include wiz/theme/component

html(ng-app="app")
    head
        +header
        
    body.antialiased
        script(src='/resources/wiz/theme/libs/tabler/dist/libs/bootstrap/dist/js/bootstrap.bundle.min.js')
        script(src='/resources/wiz/theme/libs/tabler/dist/libs/peity/jquery.peity.min.js')
        script(src='/resources/wiz/theme/libs/tabler/dist/js/tabler.min.js')

        .page(ng-controller="content" ng-cloak)
            .preview
                {$ view $}

            style.
                html,
                body {
                    overflow: auto;
                }

                body {
                    padding: 32px;
                }

                .page {
                    background: transparent;
                }

        +builder
```

## Usage

### websrc/app/filter/indexfilter.py

- add code to indexfilter

```python
framework.wiz = framework.model("wiz", module="wiz")
framework.response.data.set(wiz=framework.wiz)
framework.wiz.route(framework)
```

### in Templates

- load view using `namespace`
    - wiz.view("namespace")

```pug
mixin content()
    .container.mt-4
        .row.row-deck.row-cards
            .col-md-4
                {$ wiz.render("widget-commute") $}

            .col-md-4
                {$ wiz.render("widget-monthly-worktime") $}

            .col-md-4
                {$ wiz.render("widget-vacation") $}
    
include theme/layout
+layout
```