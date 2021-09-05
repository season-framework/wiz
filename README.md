# SEASON WIZ (Widget Interface Zone)

- SEASON WIZ depends on `season-flask`

## Installation

```bash
sf module import wiz --uri https://github.com/season-framework/season-flask-wiz
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
```

### websrc/modules/theme/view/layout-wiz.pug

- setup base theme layout for wiz

```pug
mixin layout()
    doctype 5
    include theme/component

    html(ng-app="app")
        head
            +header
            
        body.antialiased
            div.page(ng-controller="content" ng-cloak)
                +content

            +builder
```

## Usage

### websrc/app/filter/indexfilter.py

- add code to indexfilter

```python
framework.wiz = framework.model("wiz", module="wiz")
framework.response.data.set(wiz=framework.wiz)
```

### in Templates

- load view using `namespace`
    - wiz.view("namespace")

```pug
mixin content()
    .container.mt-4
        .row.row-deck.row-cards
            .col-md-4
                {$ wiz.view("widget-commute") $}

            .col-md-4
                {$ wiz.view("widget-monthly-worktime") $}

            .col-md-4
                {$ wiz.view("widget-vacation") $}
    
include theme/layout
+layout
```