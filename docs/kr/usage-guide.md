# WIZ Framework 사용 가이드

## 목차
1. [설치](#설치)
2. [프로젝트 생성](#프로젝트-생성)
3. [프로젝트 구조](#프로젝트-구조)
4. [서버 실행](#서버-실행)
5. [페이지 생성](#페이지-생성)
6. [컴포넌트 개발](#컴포넌트-개발)
7. [API 개발](#api-개발)
8. [라우트 추가](#라우트-추가)
9. [모델 작성](#모델-작성)
10. [포털 사용](#포털-사용)
11. [빌드 및 배포](#빌드-및-배포)

---

## 설치

### 1. 시스템 요구사항

- Python 3.8 이상
- Node.js 및 npm
- Angular CLI

### 2. Node.js 및 npm 설치

```bash
# Node.js 및 npm 설치
apt install nodejs npm

# n 패키지를 통한 최신 버전 설치
npm i -g n
n stable

# 이전 버전 제거
apt purge nodejs npm
```

### 3. WIZ 프레임워크 설치

```bash
# 설치
pip install season

# 업그레이드
pip install season --upgrade
```

### 4. 설치 확인

```bash
wiz --version
```

---

## 프로젝트 생성

### 1. 새 프로젝트 생성

```bash
# 작업 디렉토리로 이동
cd <workspace>

# 프로젝트 생성
wiz create myapp

# 프로젝트 디렉토리로 이동
cd myapp
```

### 2. 생성된 프로젝트 구조

```
myapp/
├── config/              # 설정 파일
│   ├── boot.py          # 서버 부팅 설정
│   ├── ide.py           # IDE 설정
│   ├── service.py       # 서비스 설정
│   └── plugin.json      # 플러그인 설정
├── public/              # 공개 디렉토리
│   ├── app.py           # 애플리케이션 엔트리포인트
│   └── app.wsgi         # WSGI 설정
├── project/             # 프로젝트 디렉토리 (비어있음)
├── ide/                 # WIZ IDE 소스
├── plugin/              # 플러그인
│   ├── core/
│   ├── workspace/
│   ├── git/
│   └── utility/
└── wiz.pid              # 데몬 프로세스 ID (실행 시 생성)
```

---

## 프로젝트 구조

WIZ에서 실제 애플리케이션은 `project/` 디렉토리 하위에 생성됩니다. 기본적으로 `main` 프로젝트를 생성하는 것을 권장합니다.

### 프로젝트 내부 구조 (project/main/)

```
project/main/
├── config/              # 프로젝트 설정 (선택사항)
├── src/                 # 소스 코드
│   ├── app/             # Angular 앱 컴포넌트
│   │   ├── layout.empty/    # 레이아웃 컴포넌트
│   │   │   ├── view.pug
│   │   │   ├── view.ts
│   │   │   ├── view.scss
│   │   │   └── app.json
│   │   └── page.main/       # 페이지 컴포넌트
│   │       ├── view.pug     # Pug 템플릿
│   │       ├── view.ts      # TypeScript 로직
│   │       ├── view.scss    # 스타일시트
│   │       ├── app.json     # 앱 메타데이터
│   │       ├── api.py       # 백엔드 API (선택사항)
│   │       └── socket.py    # 소켓 핸들러 (선택사항)
│   ├── controller/      # 백엔드 컨트롤러
│   │   └── base.py      # 기본 컨트롤러
│   ├── model/           # 데이터 모델
│   ├── route/           # API 라우트
│   │   ├── brand/
│   │   │   ├── app.json
│   │   │   └── controller.py
│   │   └── setting/
│   ├── portal/          # 포털 (재사용 가능한 모듈)
│   │   ├── season/
│   │   │   ├── portal.json
│   │   │   ├── app/
│   │   │   ├── controller/
│   │   │   ├── model/
│   │   │   └── route/
│   │   └── ...
│   ├── angular/         # Angular 설정
│   └── assets/          # 정적 자산
├── build/               # 빌드 결과물 (자동 생성)
├── bundle/              # 번들 파일 (자동 생성)
├── package.json         # npm 패키지 설정
└── node_modules/        # npm 의존성
```

---

## 서버 실행

### 1. 개발 모드로 실행

```bash
# 기본 실행 (포트 3000)
wiz run

# 포트 지정
wiz run --port=3000

# 호스트 및 포트 지정
wiz run --port=3000 --host=0.0.0.0

# 로그 파일 지정
wiz run --port=3000 --log=wiz.log
```

### 2. 데몬 모드로 실행

```bash
# 데몬 시작
wiz server start

# 데몬 중지
wiz server stop

# 데몬 재시작
wiz server restart

# 로그 파일 지정
wiz server start --log=wiz.log
```

### 3. 시스템 서비스로 등록 (Linux)

```bash
# 서비스 등록
wiz service regist myapp

# 서비스 시작
wiz service start myapp

# 서비스 중지
wiz service stop myapp

# 서비스 상태 확인
wiz service status myapp
```

### 4. IDE 접속

서버 실행 후 브라우저에서 다음 URL로 접속:

```
http://127.0.0.1:3000/wiz
```

---

## 페이지 생성

### 1. WIZ IDE를 통한 생성

1. 브라우저에서 `http://127.0.0.1:3000/wiz` 접속
2. 좌측 파일 탐색기에서 `project/main/src/app` 디렉토리 우클릭
3. "New Page" 선택
4. 페이지 이름 입력 (예: `page.dashboard`)

### 2. 수동으로 생성

#### 2.1 디렉토리 생성

```bash
cd project/main/src/app
mkdir page.dashboard
```

#### 2.2 필수 파일 생성

**app.json** - 페이지 메타데이터
```json
{
    "title": "Dashboard",
    "mode": "page",
    "namespace": "main",
    "category": "general",
    "id": "page.dashboard",
    "ng.build": {
        "id": "page.dashboard",
        "name": "PageDashboardComponent",
        "path": "./page.dashboard/page.dashboard.component"
    },
    "viewuri": "/dashboard/**",
    "layout": "layout.empty",
    "preview": "/dashboard",
    "ng": {
        "selector": "wiz-page-dashboard",
        "inputs": [],
        "outputs": []
    },
    "template": "wiz-page-dashboard()",
    "controller": ""
}
```

**view.ts** - TypeScript 로직
```typescript
import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public async ngOnInit() {
        await this.service.init();
        await this.service.render();
    }

    public async load() {
        // 데이터 로드 로직
    }
}
```

**view.pug** - Pug 템플릿
```pug
.container
    h1 Dashboard
    p Welcome to the dashboard!
```

**view.scss** - 스타일시트
```scss
.container {
    padding: 20px;
    
    h1 {
        color: #333;
    }
}
```

#### 2.3 API 핸들러 (선택사항)

**api.py** - 백엔드 API
```python
# GET 요청 처리
def load():
    data = {"message": "Hello from API"}
    wiz.response.status(200, data)

# POST 요청 처리
def save():
    data = wiz.request.query()
    # 데이터 처리 로직
    wiz.response.status(200, {"result": "success"})
```

**socket.py** - WebSocket 핸들러
```python
def connect():
    """클라이언트 연결 시"""
    print("Client connected")

def disconnect():
    """클라이언트 연결 해제 시"""
    print("Client disconnected")

def on_message(data):
    """메시지 수신 시"""
    wiz.response.send({"echo": data})
```

### 4. WebSocket (socket.py) 상세 가이드

#### 4.1 Socket Controller 개요

`socket.py`는 WIZ 프레임워크에서 실시간 양방향 통신을 위한 WebSocket 핸들러입니다. Flask-SocketIO 기반으로 구현되어 있으며, 각 앱 컴포넌트마다 독립적인 WebSocket 네임스페이스를 가집니다.

**네임스페이스 구조:**
```
/wiz/app/{project}/{app_id}
```

예: `/wiz/app/main/page.dashboard`

#### 4.2 Socket Controller 클래스 구조

Socket Controller는 `Controller` 클래스를 정의하여 구현합니다.

```python
class Controller:
    def __init__(self, server):
        """
        Socket Controller 초기화
        
        Parameters:
            server: WIZ 서버 인스턴스
        """
        self.server = server

    def connect(self):
        """클라이언트 연결 시 호출"""
        pass

    def disconnect(self, flask, io):
        """클라이언트 연결 해제 시 호출"""
        sid = flask.request.sid  # 클라이언트 세션 ID
        pass

    def join(self, data, io):
        """룸 참가 이벤트"""
        io.join(data)  # data를 룸 이름으로 사용하여 참가

    def leave(self, data, io):
        """룸 퇴장 이벤트"""
        io.leave(data)  # data를 룸 이름으로 사용하여 퇴장

    def custom_event(self, data, io):
        """사용자 정의 이벤트"""
        # data: 클라이언트에서 전송한 데이터
        # io: SocketHandler 인스턴스
        io.emit("response", {"message": "received"})
```

#### 4.3 사용 가능한 파라미터

Controller 메서드에서는 다음 파라미터들을 사용할 수 있습니다:

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `server` | Server | WIZ 서버 인스턴스 |
| `wiz` | Wiz | WIZ 코어 객체 (model, project, session 등 접근) |
| `socketio` | SocketIO | Flask-SocketIO 인스턴스 |
| `flask_socketio` | module | flask_socketio 모듈 |
| `flask` | module | Flask 모듈 (request.sid 등 접근) |
| `io` | SocketHandler | 소켓 핸들러 (emit, join, leave 등) |
| `data` | any | 클라이언트에서 전송한 데이터 |

#### 4.4 SocketHandler (io) API

`io` 파라미터로 제공되는 SocketHandler 클래스의 메서드:

```python
# 메시지 전송
io.emit(event, data, to=None, room=None, broadcast=False)
# - event: 이벤트 이름
# - data: 전송할 데이터
# - to: 특정 클라이언트 SID
# - room: 특정 룸
# - broadcast: 전체 브로드캐스트

# 일반 메시지 전송
io.send(message, to=None, room=None)

# 룸 참가
io.join(room, sid=None)
io.join_room(room, sid=None)  # 별칭

# 룸 퇴장
io.leave(room, sid=None)
io.leave_room(room, sid=None)  # 별칭

# 상태 메시지 전송
io.status(channel='message', to=None, type='status', **msg)

# 룸 내 클라이언트 목록 조회
clients = io.clients(room)  # [(sid, eio_sid), ...]

# 모든 룸 목록 조회
rooms = io.rooms()
```

#### 4.5 실전 예제

**채팅 서버 구현:**

```python
class Controller:
    def __init__(self, server):
        self.server = server

    def connect(self):
        print("New client connected")

    def disconnect(self, flask, io):
        sid = flask.request.sid
        print(f"Client {sid} disconnected")

    def join(self, data, io, flask, wiz):
        """채팅방 참가"""
        # 세션 검증
        wiz.session = wiz.model("portal/season/session")
        session = wiz.session.use()
        user = session.get()
        
        if not user:
            return  # 인증되지 않은 사용자
        
        room = data.get('room', 'default')
        io.join(room)
        
        # 참가 알림
        io.emit("user_joined", {
            "user": user.get('username'),
            "room": room
        }, room=room)

    def leave(self, data, io, flask, wiz):
        """채팅방 퇴장"""
        room = data.get('room', 'default')
        io.leave(room)
        io.emit("user_left", {"room": room}, room=room)

    def message(self, data, io, wiz):
        """메시지 전송"""
        wiz.session = wiz.model("portal/season/session")
        session = wiz.session.use()
        user = session.get()
        
        room = data.get('room', 'default')
        message = data.get('message', '')
        
        io.emit("new_message", {
            "user": user.get('username', 'Anonymous'),
            "message": message,
            "timestamp": wiz.project.timestamp()
        }, room=room)
```

**실시간 로그 브로드캐스트:**

```python
class Controller:
    def __init__(self, server):
        self.server = server

    def wplog(self, data, io, wiz):
        """워크플로우 로그를 특정 클라이언트에게 전송"""
        project = wiz.project()
        socketNamespace = f"/wiz/app/{project}/page.main"

        for log in data:
            event = log['event']
            to = log['id']  # 대상 클라이언트 SID
            io.emit(event, log, to=to, namespace=socketNamespace)

    def broadcast_log(self, data, io):
        """모든 클라이언트에게 로그 전송"""
        io.emit("log", data)  # 현재 네임스페이스의 모든 클라이언트
```

**인증이 필요한 Socket Controller:**

```python
class Controller:
    def __init__(self, server):
        self.server = server

    def _check_auth(self, wiz):
        """인증 검증 헬퍼"""
        wiz.session = wiz.model("portal/season/session")
        struct = wiz.model("portal/dizest/struct")
        config = struct.config
        try:
            config.acl()
            return True
        except:
            return False

    def join(self, data, io, wiz):
        if not self._check_auth(wiz):
            return  # 인증 실패 시 무시
        io.join(data)

    def leave(self, data, io, wiz):
        if not self._check_auth(wiz):
            return
        io.leave(data)

    def secure_action(self, data, io, wiz):
        if not self._check_auth(wiz):
            io.emit("error", {"message": "Unauthorized"})
            return
        
        # 인증된 작업 수행
        io.emit("success", {"data": "secure data"})
```

#### 4.6 프론트엔드에서 WebSocket 사용

**view.ts에서 Socket.IO 사용:**

```typescript
import { OnInit, OnDestroy } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit, OnDestroy {
    constructor(public service: Service) { }

    public socket: any;

    public async ngOnInit() {
        await this.service.init();
        
        // Socket.IO 연결
        this.socket = this.service.socket.create();
        
        // 이벤트 리스너 등록
        this.socket.on("new_message", (data) => {
            console.log("Received:", data);
        });
        
        this.socket.on("user_joined", (data) => {
            console.log(`${data.user} joined ${data.room}`);
        });
        
        // 룸 참가
        this.socket.emit("join", { room: "general" });
    }

    public sendMessage(message: string) {
        this.socket.emit("message", {
            room: "general",
            message: message
        });
    }

    public ngOnDestroy() {
        // 컴포넌트 파괴 시 연결 해제
        if (this.socket) {
            this.socket.emit("leave", { room: "general" });
            this.socket.disconnect();
        }
    }
}
```

#### 4.7 Socket Controller 실행 과정

WIZ 프레임워크에서 Socket Controller는 다음과 같은 과정으로 실행됩니다:

1. **서버 시작 시**: `season.lib.binding.socket.Socket` 클래스가 초기화됨
2. **socket.py 파일 탐색**: 각 프로젝트의 `bundle/src/app/` 하위에서 `socket.py` 파일 검색
3. **Controller 클래스 로드**: `season.util.compiler`를 사용하여 동적으로 클래스 로드
4. **이벤트 바인딩**: Controller 클래스의 모든 메서드를 Socket.IO 이벤트로 등록
5. **네임스페이스 할당**: `/wiz/app/{project}/{app_id}` 형태의 네임스페이스 자동 생성

**내부 동작 흐름:**

```
클라이언트 이벤트 발생
    ↓
Socket.IO 이벤트 핸들러 호출
    ↓
wrapper 함수에서 파라미터 준비 (wiz, io, flask, data 등)
    ↓
season.util.compiler를 통해 Controller 메서드 호출
    ↓
메서드 시그니처에 따라 필요한 파라미터만 주입
    ↓
메서드 실행 및 응답
```

#### 4.8 주의사항

1. **메서드 이름 규칙**: `__`로 시작하고 끝나는 메서드는 이벤트로 등록되지 않음
2. **파라미터 주입**: 메서드 시그니처에 정의된 파라미터만 주입됨 (필요한 것만 선언)
3. **예외 처리**: 예외 발생 시 서버 로그에 기록됨
4. **빌드 필요**: socket.py 변경 후 반드시 빌드 필요 (bundle 폴더에 복사됨)
5. **네임스페이스 격리**: 각 앱의 Socket은 독립된 네임스페이스를 가짐

### 3. 페이지 접속

빌드 후 다음 URL로 접속:
```
http://127.0.0.1:3000/dashboard
```

---

## 컴포넌트 개발

### 1. 레이아웃 컴포넌트 생성

레이아웃은 페이지를 감싸는 공통 구조입니다.

**app.json**
```json
{
    "mode": "layout",
    "id": "layout.default",
    "ng.build": {
        "id": "layout.default",
        "name": "LayoutDefaultComponent",
        "path": "./layout.default/layout.default.component"
    }
}
```

**view.pug**
```pug
.layout
    header
        h1 My Application
        nav
            a(href="/") Home
            a(href="/dashboard") Dashboard
    
    main
        router-outlet
    
    footer
        p © 2026 My Application
```

### 2. 위젯 컴포넌트 생성

재사용 가능한 UI 컴포넌트입니다.

**app.json**
```json
{
    "mode": "widget",
    "id": "widget.button",
    "ng": {
        "selector": "wiz-widget-button",
        "inputs": ["label", "color"],
        "outputs": ["onClick"]
    }
}
```

**view.ts**
```typescript
import { Input, Output, EventEmitter } from '@angular/core';

export class Component {
    @Input() label: string = "Click me";
    @Input() color: string = "primary";
    @Output() onClick = new EventEmitter();

    public handleClick() {
        this.onClick.emit();
    }
}
```

**view.pug**
```pug
button.btn([class]="'btn-' + color", (click)="handleClick()")
    | {{ label }}
```

### 3. 컴포넌트 사용

다른 컴포넌트에서 위젯 사용:

```pug
wiz-widget-button(
    [label]="'Submit'",
    [color]="'success'",
    (onClick)="onSubmit()"
)
```

---

## API 개발

### 1. 컴포넌트 내 API (api.py)

각 페이지/위젯 디렉토리에 `api.py`를 생성하여 해당 컴포넌트 전용 API를 만들 수 있습니다.

**project/main/src/app/page.dashboard/api.py**
```python
# GET /api/page.dashboard/users
def users():
    users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    wiz.response.status(200, users)

# POST /api/page.dashboard/user
def user():
    data = wiz.request.query()
    name = data.get("name", "")
    
    # 데이터베이스 저장 로직
    user_id = 123
    
    wiz.response.status(200, {
        "id": user_id,
        "name": name
    })

# 파일 업로드
def upload():
    files = wiz.request.files()
    for filename in files:
        file = files[filename]
        # 파일 저장 로직
        fs = wiz.project.fs("data", "uploads")
        fs.write(filename, file.read())
    
    wiz.response.status(200, {"result": "success"})

# 파일 다운로드
def download():
    fs = wiz.project.fs("data", "uploads")
    filepath = fs.abspath("sample.pdf")
    wiz.response.download(filepath, as_attachment=True)
```

### 2. 프론트엔드에서 API 호출

**view.ts**
```typescript
export class Component {
    constructor(public service: Service) { }

    public async loadUsers() {
        // GET 요청
        let res = await this.service.api.call("users");
        console.log(res.data); // [{id: 1, name: "Alice"}, ...]
    }

    public async createUser() {
        // POST 요청
        let data = { name: "Charlie" };
        let res = await this.service.api.call("user", data);
        console.log(res.data); // {id: 123, name: "Charlie"}
    }

    public async uploadFile(event) {
        let files = event.target.files;
        let formData = new FormData();
        formData.append("file", files[0]);
        
        let res = await this.service.api.call("upload", formData);
        console.log(res.data);
    }
}
```

### 3. wiz 객체 API

**api.py**에서 사용 가능한 주요 `wiz` API:

```python
# 요청 데이터
data = wiz.request.query()           # GET/POST 파라미터
data = wiz.request.query("key", default)  # 특정 키 가져오기
files = wiz.request.files()          # 업로드된 파일
segment = wiz.request.match("/users/<id>")  # URL 패턴 매칭

# 응답
wiz.response.status(200, data)       # JSON 응답
wiz.response.download(path)          # 파일 다운로드
wiz.response.redirect(url)           # 리다이렉트
wiz.response.abort(404)              # HTTP 에러

# 파일시스템
fs = wiz.project.fs("data")          # 프로젝트 파일시스템
fs = wiz.fs()                        # 현재 컴포넌트 파일시스템
data = fs.read("file.txt")           # 파일 읽기
fs.write("file.txt", data)           # 파일 쓰기
fs.read.json("data.json")            # JSON 읽기

# 모델
model = wiz.model("portal/season/session")
instance = model.use()

# 세션
wiz.session.set("key", "value")
value = wiz.session.get("key")
```

---

## 라우트 추가

라우트는 독립적인 API 엔드포인트를 제공합니다.

### 1. 라우트 생성

**project/main/src/route/api/app.json**
```json
{
    "id": "api",
    "uri": "/api"
}
```

**project/main/src/route/api/controller.py**
```python
import season
import json

# URL 세그먼트 가져오기
segment = wiz.request.match("/api/<action>/<path:path>")
action = segment.action
path = segment.path

if action == "users":
    # /api/users/... 처리
    users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    wiz.response.status(200, users)

elif action == "posts":
    # /api/posts/... 처리
    posts = [
        {"id": 1, "title": "Hello World"},
        {"id": 2, "title": "WIZ Framework"}
    ]
    wiz.response.status(200, posts)

# 404 에러
wiz.response.abort(404)
```

### 2. 라우트 접근

```
GET http://127.0.0.1:3000/api/users
GET http://127.0.0.1:3000/api/posts
```

### 3. 고급 라우팅

**RESTful API 예시:**

```python
segment = wiz.request.match("/api/<resource>/<int:id>")
resource = segment.resource
resource_id = segment.id

method = wiz.request.request().method

if resource == "users":
    if method == "GET":
        # 사용자 조회
        user = get_user_by_id(resource_id)
        wiz.response.status(200, user)
    
    elif method == "POST":
        # 사용자 생성
        data = wiz.request.query()
        user_id = create_user(data)
        wiz.response.status(201, {"id": user_id})
    
    elif method == "PUT":
        # 사용자 수정
        data = wiz.request.query()
        update_user(resource_id, data)
        wiz.response.status(200, {"result": "success"})
    
    elif method == "DELETE":
        # 사용자 삭제
        delete_user(resource_id)
        wiz.response.status(204)
```

---

## 모델 작성

모델은 비즈니스 로직과 데이터 접근을 캡슐화합니다.

### 1. 모델 파일 생성

**project/main/src/model/user.py**
```python
import season

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.db = self.wiz.model("portal/season/db").use()
    
    def get_users(self):
        """모든 사용자 조회"""
        query = "SELECT * FROM users"
        return self.db.query(query)
    
    def get_user(self, user_id):
        """특정 사용자 조회"""
        query = "SELECT * FROM users WHERE id = ?"
        return self.db.queryOne(query, [user_id])
    
    def create_user(self, name, email):
        """사용자 생성"""
        query = "INSERT INTO users (name, email) VALUES (?, ?)"
        return self.db.execute(query, [name, email])
    
    def update_user(self, user_id, data):
        """사용자 수정"""
        query = "UPDATE users SET name = ?, email = ? WHERE id = ?"
        return self.db.execute(query, [data['name'], data['email'], user_id])
    
    def delete_user(self, user_id):
        """사용자 삭제"""
        query = "DELETE FROM users WHERE id = ?"
        return self.db.execute(query, [user_id])
```

### 2. 모델 사용

**api.py 또는 controller.py에서:**

```python
# 모델 로드
user_model = wiz.model("user").use()

# 사용자 조회
users = user_model.get_users()
wiz.response.status(200, users)

# 사용자 생성
user_id = user_model.create_user("Alice", "alice@example.com")
wiz.response.status(201, {"id": user_id})
```

### 3. 파일시스템 기반 모델

데이터베이스 대신 파일로 데이터를 관리하는 모델:

**project/main/src/model/storage.py**
```python
import season
import json

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.fs = wiz.project.fs("data", "storage")
    
    def save(self, key, data):
        """데이터 저장"""
        filename = f"{key}.json"
        json_data = json.dumps(data, default=season.util.string.json_default)
        self.fs.write(filename, json_data)
    
    def load(self, key):
        """데이터 로드"""
        filename = f"{key}.json"
        if not self.fs.exists(filename):
            return None
        return self.fs.read.json(filename)
    
    def delete(self, key):
        """데이터 삭제"""
        filename = f"{key}.json"
        self.fs.delete(filename)
    
    def list(self):
        """모든 키 조회"""
        files = self.fs.files()
        return [f.replace(".json", "") for f in files]
```

---

## 포털 사용

포털은 재사용 가능한 모듈 패키지입니다.

### 1. 포털 구조

```
src/portal/myportal/
├── portal.json          # 포털 메타데이터
├── app/                 # Angular 컴포넌트
│   └── widget.button/
├── controller/          # 컨트롤러
│   └── base.py
├── model/               # 모델
│   └── user.py
├── route/               # 라우트
│   └── api/
└── libs/                # 공유 라이브러리
    └── service.ts
```

### 2. portal.json 설정

**src/portal/myportal/portal.json**
```json
{
    "package": "myportal",
    "title": "My Portal",
    "version": "1.0.0",
    "use_app": true,
    "use_widget": true,
    "use_route": true,
    "use_libs": true,
    "use_controller": true,
    "use_model": true,
    "use_styles": true,
    "use_assets": true
}
```

### 3. 포털 사용

**모델 사용:**
```python
# portal/myportal/model/user.py 로드
user_model = wiz.model("portal/myportal/user").use()
```

**컴포넌트 사용:**
```pug
// portal/myportal/app/widget.button 사용
wiz-myportal-widget-button([label]="'Click'")
```

**라이브러리 사용 (TypeScript):**
```typescript
import { Service } from '@wiz/libs/portal/myportal/service';

constructor(public myService: Service) { }
```

### 4. 포털 공유

포털은 독립적인 패키지로 다른 프로젝트에서 재사용할 수 있습니다.

1. `src/portal/myportal` 디렉토리를 복사
2. 다른 프로젝트의 `src/portal/`에 붙여넣기
3. 빌드하면 자동으로 인식됨

---

## 빌드 및 배포

### 1. 프로젝트 빌드

```bash
# IDE에서 빌드 (권장)
# http://127.0.0.1:3000/wiz 접속 후 빌드 버튼 클릭

# CLI에서 빌드
wiz command workspace build main
```

빌드 결과:
- `project/main/build/` - 빌드된 파일
- `project/main/bundle/` - 최종 번들

### 2. 번들 모드로 실행

번들 모드는 빌드된 코드를 사용하여 성능이 향상됩니다.

```bash
wiz run --bundle=true
```

### 3. 프로덕션 배포

#### WSGI 서버 (Gunicorn)

```bash
# Gunicorn 설치
pip install gunicorn

# 실행
cd /path/to/myapp/public
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

#### Nginx 리버스 프록시

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:3000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Docker 배포

**Dockerfile**
```dockerfile
FROM python:3.10

# Node.js 설치
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# WIZ 설치
RUN pip install season

# 프로젝트 복사
COPY . /app
WORKDIR /app

# 포트 노출
EXPOSE 3000

# 서버 실행
CMD ["wiz", "run", "--port=3000", "--host=0.0.0.0"]
```

**빌드 및 실행:**
```bash
docker build -t myapp .
docker run -p 3000:3000 myapp
```

### 4. IDE 업그레이드

```bash
# WIZ 패키지 업그레이드
pip install season --upgrade

# IDE 업그레이드
wiz ide upgrade
```

### 5. 환경 변수 설정

**config/boot.py에서:**
```python
import os

# 환경에 따른 설정
ENV = os.getenv("WIZ_ENV", "development")

if ENV == "production":
    run['debug'] = False
    run['use_reloader'] = False
    secret_key = os.getenv("SECRET_KEY", "production-secret-key")
else:
    run['debug'] = True
    run['use_reloader'] = True
    secret_key = "development-secret-key"
```

---

## 추가 팁

### 1. 디버깅

**Python 로깅:**
```python
import season

logger = season.util.Logger("myapp", level=season.LOG_DEBUG)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

**JavaScript 콘솔:**
```typescript
console.log("Debug message");
console.error("Error message");
```

### 2. 핫 리로드

개발 모드에서는 파일 변경 시 자동으로 재빌드됩니다.

```bash
wiz run --port=3000
```

### 3. 멀티 프로젝트

하나의 WIZ 인스턴스에서 여러 프로젝트를 관리할 수 있습니다.

```
project/
├── main/        # 메인 애플리케이션
├── admin/       # 관리자 페이지
└── api/         # API 전용
```

각 프로젝트는 독립적으로 빌드되며, URL 네임스페이스로 구분됩니다.

### 4. 플러그인 개발

커스텀 플러그인을 개발하여 WIZ를 확장할 수 있습니다.

```
plugin/
└── myplugin/
    ├── plugin.json
    ├── command.py
    ├── filter.py
    ├── app/
    └── model/
```

---

## 참고 자료

- [아키텍처 문서](architecture.md)
- [GitHub 저장소](https://github.com/season-framework/wiz)
- 공식 웹사이트 (준비 중)

---

## 문제 해결

### Q: 빌드가 실패합니다.
A: Node.js와 Angular CLI가 올바르게 설치되었는지 확인하세요.

### Q: 포트가 이미 사용 중입니다.
A: 다른 포트를 지정하거나 해당 포트를 사용하는 프로세스를 종료하세요.

### Q: IDE에 접속할 수 없습니다.
A: 방화벽 설정을 확인하고, 서버가 정상적으로 실행 중인지 확인하세요.

### Q: 페이지가 404 에러를 반환합니다.
A: `app.json`의 `viewuri` 설정이 올바른지 확인하고, 빌드를 다시 수행하세요.
