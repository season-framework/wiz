## WIZ Terminal App
### How to Add

- install from github

```
wiz plugin add https://github.com/season-framework/wiz-plugin-xterm
```

- add configuration `System Setting - IDE Menu`

```
{
    "app": [
        ...

        {
            "name": "Terminal",
            "id": "xterm.app.term",
            "icon": "fa-solid fa-terminal",
            "width": 721
        },

        ...
    ]
}
```