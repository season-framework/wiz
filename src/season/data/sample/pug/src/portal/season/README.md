# Installation

- python dependencies

```sh
apt install pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl
pip install peewee pymysql bcrypt python3-saml
```

- npm dependencies
    - `@fortawesome/fontawesome-free`
    - `urlpattern-polyfill`
    - `moment`
    - `sortablejs`

# Release

### 1.2.4

- 언어 패칭 기능 추가 (service.lang)
- event trigger 기능 추가 (service.trigger)

### 1.2.3

- auth api 업데이트

### 1.2.2

- pagenation 페이지 크기 설정 기능 추가
- service.init 관련 오류 수정 (auth.init 관련)

### 1.2.1

- app 이름 영문으로 변경
- Statusbar 기능 추가
- Tab 기능 추가

### 1.2.0

- Tree Viewer 추가
- 드롭다운 메뉴 추가

# 프로젝트에 적용하기

## 프로젝트 설정

### sample 설치하기

- Sample 폴더에서 필요한 항목을 설치 
- Sample 구성
    - `page`: 로그인
    - `component`: Navbar
    - `layout`: Empty, Topnav

### angular/angular.build.options.json
- `angular/angular.build.options.json` 파일을 아래 내용으로 변경

```
{
    "assets": [],
    "styles": [
        "node_modules/@tabler/core/dist/css/tabler.min.css",
        "node_modules/toastr/build/toastr.min.css",
        "node_modules/@fortawesome/fontawesome-free/css/all.min.css",
        "src/styles.scss"
    ],
    "scripts": [
        "src/libs/portal/season/base/array.js",
        "src/libs/portal/season/base/date.js",
        "src/libs/portal/season/base/function.js",
        "src/libs/portal/season/base/number.js",
        "src/libs/portal/season/base/string.js"
    ]
}
```

### angular/app/app-routing.module.ts
- `angular/app/app-routing.module.ts` 파일에서 아래 내용 변경
- `INDEX_PAGE` 는 만드는 페이지의 메인 페이지 경로로 변경

```ts
const INDEX_PAGE = "main";

import { URLPattern } from "urlpattern-polyfill";
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

...
```

### angular/app/app.component.ts

- `angular/app/app.component.ts` 파일을 아래 내용으로 변경

```ts
import { Component, OnInit, ChangeDetectorRef, enableProdMode } from '@angular/core';
import { Router } from '@angular/router';
import { Service } from '@wiz/libs/portal/season/service';

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
    constructor(
        public service: Service,
        public router: Router,
        public ref: ChangeDetectorRef
    ) { }

    public async ngOnInit() {
        enableProdMode();
        await this.service.init(this);
    }
}
```

### styles/styles.scss

- CSS 적용

```scss
@import "portal/season/core"
```

## Config 지정

### config/season.py

- 설정 추가

```python
orm_base = "db"

default_url = "/main"
default_login = "/login"

# SAML 설정
use_saml = False
saml_error = "/saml/error"
saml_base_path = "config/auth/saml"
saml_entity = "season"

def saml_acs(userinfo):
    uinfodict = {'uid': 'id', 'name': 'username'}
    sessiondata = dict()
    for key in userinfo:
        try:
            v = userinfo[key][0]
            if key in uinfodict: 
                key = uinfodict[key]
            sessiondata[key] = v
        except:
            pass

    model = wiz.model("portal/season/orm").use("users")
    userinfo = model.get(id=sessiondata['id'])

    if userinfo is None:
        userinfo = dict()
        userinfo['id'] = sessiondata['id']
        userinfo['role'] = 'user'
        userinfo['username'] = sessiondata['username']
        userinfo['email'] = sessiondata['email']
        userinfo['created'] = datetime.datetime.now()
        userinfo['last_access'] = datetime.datetime.now()
        userinfo['disabled'] = 'N'
        userinfo['thumbnail'] = ''
        model.upsert(userinfo)
    else:
        userinfo['last_access'] = datetime.datetime.now()
        model.upsert(userinfo)

    sessiondata['role'] = userinfo['role']

    return sessiondata

# default_logout = "/auth/saml/logout"
```

### (optional) config/smtp/`<template>`.html

- SMTP 발송 템플릿 설정
- config/smtp 폴더를 생성한 후 html 파일 생성 (ex. default.html)
    - `{Key}` 를 통해 대입할 값을 설정 할 수 있음
        - `{title}`: 제목
        - `{message}`: 메일 내용

```html
<div style="width: 100%; min-height: 100%; background: #f5f7fb; padding-top: 48px; padding-bottom: 48px;">
    <div style="width: 80%; max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px;">
        <div style="background: #3843D0; padding: 18px 24px; border-radius: 8px; padding-bottom: 12px;">
            <img src="https://my.season.co.kr/resources/logo/logo-white.png" style="height: 36px;">
        </div>

        <div style="padding: 8px 24px; padding-bottom: 32px; padding-top: 8px;">
            <h2 style="font-size: 24px; color: #F9623E; margin-bottom: 12px;">{title}</h2>
            {message}
        </div>

        <div
            style="padding: 12px 24px; background: #2e2e2e; color: #ffffff; border-bottom-right-radius: 8px; border-bottom-left-radius: 8px; text-align: center;">
            (30128) 세종특별자치시 나성북1로 12 (메가타워, 602호) 주식회사 시즌
        </div>
    </div>
</div>
```

- smtp 모델을 통해 메일 발송

```python
smtp = wiz.model("portal/season/smtp").use()
smtp.send("test@test.com", template="default", title="Hello", message="This is message", **kwargs)
```
