# API Reference

WIZ 프레임워크에서 사용 가능한 주요 API 레퍼런스입니다.

## wiz 객체

`wiz` 객체는 WIZ 프레임워크의 핵심 API를 제공합니다. Python 코드 (api.py, controller.py, model 등)에서 사용할 수 있습니다.

### 요청 (Request)

#### wiz.request.query()
GET 또는 POST 파라미터를 가져옵니다.

```python
# 모든 파라미터 가져오기
data = wiz.request.query()  # dict

# 특정 키 가져오기
name = wiz.request.query("name", "default")

# 예시
# GET /api/users?name=Alice&age=25
name = wiz.request.query("name")  # "Alice"
age = wiz.request.query("age")    # "25"
```

#### wiz.request.files()
업로드된 파일을 가져옵니다.

```python
files = wiz.request.files()

for filename in files:
    file = files[filename]
    # file.read() - 파일 내용 읽기
    # file.filename - 원본 파일명
    # file.save(path) - 파일 저장
```

#### wiz.request.match()
URL 패턴을 매칭하고 세그먼트를 추출합니다.

```python
# URL: /api/users/123/posts/456
segment = wiz.request.match("/api/<resource>/<int:id>/<sub>/<int:sub_id>")

resource = segment.resource  # "users"
id = segment.id              # 123
sub = segment.sub            # "posts"
sub_id = segment.sub_id      # 456

# 지원하는 타입:
# - <name>: 문자열 (기본)
# - <int:name>: 정수
# - <float:name>: 실수
# - <path:name>: 경로 (/ 포함)
```

#### wiz.request.request()
Flask request 객체에 직접 접근합니다.

```python
req = wiz.request.request()

method = req.method          # GET, POST, PUT, DELETE
url = req.url                # 전체 URL
base_url = req.base_url      # 베이스 URL
headers = req.headers        # 헤더
cookies = req.cookies        # 쿠키
remote_addr = req.remote_addr  # 클라이언트 IP
```

#### wiz.request.uri()
현재 요청 URI를 반환합니다.

```python
uri = wiz.request.uri()  # "/api/users/123"
```

### 응답 (Response)

#### wiz.response.status()
JSON 응답을 반환합니다.

```python
# 성공 응답
data = {"message": "Success", "user_id": 123}
wiz.response.status(200, data)

# 에러 응답
error = {"error": "User not found"}
wiz.response.status(404, error)

# 일반적인 HTTP 상태 코드:
# 200 - OK
# 201 - Created
# 204 - No Content
# 400 - Bad Request
# 401 - Unauthorized
# 403 - Forbidden
# 404 - Not Found
# 500 - Internal Server Error
```

#### wiz.response.download()
파일 다운로드 응답을 반환합니다.

```python
# 파일 다운로드
filepath = "/path/to/file.pdf"
wiz.response.download(filepath, as_attachment=True)

# 브라우저에서 표시
wiz.response.download(filepath, as_attachment=False)

# 파일명 지정
wiz.response.download(filepath, filename="custom_name.pdf")
```

#### wiz.response.redirect()
다른 URL로 리다이렉트합니다.

```python
# 절대 경로
wiz.response.redirect("/dashboard")

# 외부 URL
wiz.response.redirect("https://example.com")

# 쿼리 파라미터와 함께
uri = wiz.request.uri()
wiz.response.redirect(uri)
```

#### wiz.response.abort()
HTTP 에러를 발생시킵니다.

```python
# 404 에러
wiz.response.abort(404)

# 403 에러
wiz.response.abort(403)

# 500 에러
wiz.response.abort(500)
```

#### wiz.response.send()
WebSocket을 통해 메시지를 전송합니다.

```python
# socket.py에서 사용
def on_message(data):
    response = {"echo": data}
    wiz.response.send(response)
```

#### wiz.response.data.set()
응답 데이터에 변수를 설정합니다.

```python
# 템플릿에서 사용할 데이터 설정
wiz.response.data.set(username="Alice", role="admin")
```

#### wiz.response.lang()
언어를 설정합니다.

```python
# 언어 설정
wiz.response.lang("ko")

# 지원 언어: ko, en, ja, zh 등
```

#### wiz.response.PIL()
PIL 이미지를 응답으로 반환합니다.

```python
from PIL import Image

img = Image.open("image.png")
wiz.response.PIL(img, type="PNG")

# 지원 타입: PNG, JPEG, GIF, BMP
```

### 파일시스템 (Filesystem)

#### wiz.fs()
현재 컴포넌트의 파일시스템 객체를 반환합니다.

```python
fs = wiz.fs()

# 파일 읽기
content = fs.read("file.txt")

# 파일 쓰기
fs.write("file.txt", "Hello World")

# 파일 존재 확인
exists = fs.exists("file.txt")  # True/False

# 파일 삭제
fs.delete("file.txt")

# JSON 읽기
data = fs.read.json("data.json", default={})

# JSON 쓰기 (자동으로 JSON 인코딩)
fs.write.json("data.json", {"key": "value"})

# 디렉토리 생성
fs.makedirs("subdir")

# 디렉토리 확인
is_dir = fs.isdir("subdir")

# 파일 목록
files = fs.files()           # 현재 디렉토리의 파일 목록
files = fs.files("subdir")   # 특정 디렉토리의 파일 목록

# 절대 경로
abspath = fs.abspath("file.txt")
```

#### wiz.project.fs()
프로젝트 내의 파일시스템 객체를 반환합니다.

```python
# project/main/data 디렉토리 접근
fs = wiz.project.fs("data")

# project/main/uploads/images 디렉토리 접근
fs = wiz.project.fs("uploads", "images")

# 사용법은 wiz.fs()와 동일
fs.write("user.json", data)
```

#### wiz.project.path()
프로젝트 경로를 반환합니다.

```python
# 프로젝트 루트 경로
path = wiz.project.path()  # "/path/to/project/main"

# 특정 하위 경로
path = wiz.project.path("src", "app")  # "/path/to/project/main/src/app"
```

### 모델 (Model)

#### wiz.model()
모델을 로드합니다.

```python
# 프로젝트 모델
model = wiz.model("user")
instance = model.use()

# 포털 모델
model = wiz.model("portal/season/session")
instance = model.use()

# 플러그인 모델
model = wiz.ide.plugin.model("builder")
instance = model.use()
```

### 세션 (Session)

#### wiz.session.set()
세션 값을 설정합니다.

```python
wiz.session.set("user_id", 123)
wiz.session.set("username", "Alice")
```

#### wiz.session.get()
세션 값을 가져옵니다.

```python
user_id = wiz.session.get("user_id", None)
username = wiz.session.get("username", "Guest")

# 모든 세션 데이터
session_data = wiz.session.get()
```

#### wiz.session.delete()
세션 값을 삭제합니다.

```python
wiz.session.delete("user_id")
```

#### wiz.session.clear()
모든 세션을 삭제합니다.

```python
wiz.session.clear()
```

### 프로젝트 (Project)

#### wiz.project()
현재 프로젝트 이름을 반환합니다.

```python
project_name = wiz.project()  # "main"
```

#### wiz.project.checkout()
프로젝트를 체크아웃합니다.

```python
wiz.project.checkout("main")
```

#### wiz.path()
현재 경로를 반환합니다.

```python
path = wiz.path()  # WIZ 루트 경로
```

---

## Service API (TypeScript)

Angular 컴포넌트에서 사용하는 Service API입니다.

### 초기화

```typescript
import { Service } from '@wiz/libs/portal/season/service';

export class Component {
    constructor(public service: Service) { }

    async ngOnInit() {
        await this.service.init();
        await this.service.render();
    }
}
```

### API 호출

#### service.api.call()
백엔드 API를 호출합니다.

```typescript
// GET 요청
let res = await this.service.api.call("functionName");
console.log(res.data);

// POST 요청 (데이터 전송)
let data = { name: "Alice", age: 25 };
let res = await this.service.api.call("functionName", data);

// 파일 업로드
let formData = new FormData();
formData.append("file", fileObject);
let res = await this.service.api.call("upload", formData);

// 응답 구조:
// {
//   code: 200,      // HTTP 상태 코드
//   data: {...}     // 응답 데이터
// }
```

### 소켓 통신

#### service.socket.emit()
소켓 이벤트를 발송합니다.

```typescript
// 이벤트 발송
await this.service.socket.emit("eventName", { data: "value" });

// 응답 받기
let res = await this.service.socket.emit("eventName", { data: "value" });
console.log(res);
```

#### service.socket.on()
소켓 이벤트를 구독합니다.

```typescript
// 이벤트 구독
this.service.socket.on("eventName", (data) => {
    console.log("Received:", data);
});

// 구독 해제
this.service.socket.off("eventName");
```

### 라우팅

#### service.href()
URL로 이동합니다.

```typescript
// 페이지 이동
this.service.href("/dashboard");

// 외부 URL
this.service.href("https://example.com");

// 새 탭에서 열기
this.service.href("/dashboard", true);
```

### 알림

#### service.alert()
알림 메시지를 표시합니다.

```typescript
// 정보 알림
await this.service.alert.show("정보 메시지");

// 성공 알림
await this.service.alert.success("성공했습니다!");

// 에러 알림
await this.service.alert.error("에러가 발생했습니다.");

// 확인 대화상자
let confirmed = await this.service.alert.confirm("삭제하시겠습니까?");
if (confirmed) {
    // 삭제 로직
}
```

### 로딩

#### service.loading()
로딩 인디케이터를 제어합니다.

```typescript
// 로딩 시작
this.service.loading.show();

// 로딩 종료
this.service.loading.hide();

// 비동기 작업 중 자동 로딩
async loadData() {
    this.service.loading.show();
    try {
        let res = await this.service.api.call("load");
        // 데이터 처리
    } finally {
        this.service.loading.hide();
    }
}
```

### 렌더링

#### service.render()
컴포넌트를 다시 렌더링합니다.

```typescript
// 수동 렌더링
await this.service.render();

// 데이터 변경 후 렌더링
this.data = newData;
await this.service.render();
```

---

## 유틸리티 (season.util)

Python에서 사용 가능한 유틸리티 함수들입니다.

### Logger

```python
import season

logger = season.util.Logger("myapp", level=season.LOG_DEBUG)

logger.debug("디버그 메시지")
logger.info("정보 메시지")
logger.warning("경고 메시지")
logger.error("에러 메시지")
logger.critical("치명적 에러")

# 로그 레벨:
# season.LOG_DEBUG = 0
# season.LOG_INFO = 1
# season.LOG_WARNING = 2
# season.LOG_DEV = 3
# season.LOG_ERROR = 4
# season.LOG_CRITICAL = 5
```

### Cache

```python
import season

cache = season.util.Cache()

# 캐시 설정
cache.set("key", "value", timeout=3600)  # 1시간

# 캐시 가져오기
value = cache.get("key", default=None)

# 캐시 삭제
cache.delete("key")

# 캐시 초기화
cache.clear()

# 캐시 존재 확인
exists = cache.has("key")
```

### String

```python
import season
import json

# JSON 기본 인코더
data = {"date": datetime.now()}
json_str = json.dumps(data, default=season.util.string.json_default)
```

### Filesystem

```python
import season

fs = season.util.fs("/path/to/directory")

# 파일 읽기/쓰기
content = fs.read("file.txt")
fs.write("file.txt", "content")

# 파일 복사
fs.copy("source.txt", "destination.txt")

# 디렉토리 복사
fs.copy("/source/dir", "/dest/dir")

# 파일 이동
fs.move("old.txt", "new.txt")

# 파일 존재 확인
exists = fs.exists("file.txt")

# 디렉토리 생성
fs.makedirs("path/to/dir")

# 파일/디렉토리 삭제
fs.delete("file.txt")
fs.delete("directory")  # 디렉토리 전체 삭제
```

---

## 설정 (Config)

### boot.py

```python
# 부트스트랩 함수 - 서버 시작 시 실행
def bootstrap(app, config):
    # 초기화 로직
    pass

# Flask 설정
import_name = "myapp"
secret_key = "your-secret-key"

flask = dict()
flask['template_folder'] = 'templates'
flask['static_folder'] = 'static'

# SocketIO 설정
socketio = dict()
socketio['async_mode'] = 'threading'  # threading, eventlet, gevent
socketio['cors_allowed_origins'] = '*'
socketio['async_handlers'] = True
socketio['always_connect'] = False
socketio['manage_session'] = True

# 서버 실행 설정
run = dict()
run['allow_unsafe_werkzeug'] = True
run['host'] = "0.0.0.0"
run['port'] = 3000
run['debug'] = False
run['use_reloader'] = False

# 로그 레벨
import season
log_level = season.LOG_INFO
```

---

## 예제

### 전체 예제: 사용자 관리 API

**model/user.py**
```python
import season

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.fs = wiz.project.fs("data", "users")
    
    def list(self):
        users = []
        for filename in self.fs.files():
            user = self.fs.read.json(filename)
            users.append(user)
        return users
    
    def get(self, user_id):
        filename = f"{user_id}.json"
        if not self.fs.exists(filename):
            return None
        return self.fs.read.json(filename)
    
    def create(self, data):
        import uuid
        user_id = str(uuid.uuid4())
        data['id'] = user_id
        self.fs.write.json(f"{user_id}.json", data)
        return user_id
    
    def update(self, user_id, data):
        filename = f"{user_id}.json"
        if not self.fs.exists(filename):
            return False
        data['id'] = user_id
        self.fs.write.json(filename, data)
        return True
    
    def delete(self, user_id):
        filename = f"{user_id}.json"
        if not self.fs.exists(filename):
            return False
        self.fs.delete(filename)
        return True
```

**app/page.users/api.py**
```python
# 사용자 목록 조회
def list():
    user_model = wiz.model("user").use()
    users = user_model.list()
    wiz.response.status(200, users)

# 사용자 상세 조회
def get():
    user_id = wiz.request.query("id")
    user_model = wiz.model("user").use()
    user = user_model.get(user_id)
    
    if user is None:
        wiz.response.status(404, {"error": "User not found"})
    else:
        wiz.response.status(200, user)

# 사용자 생성
def create():
    data = wiz.request.query()
    user_model = wiz.model("user").use()
    user_id = user_model.create(data)
    wiz.response.status(201, {"id": user_id})

# 사용자 수정
def update():
    user_id = wiz.request.query("id")
    data = wiz.request.query()
    user_model = wiz.model("user").use()
    
    if user_model.update(user_id, data):
        wiz.response.status(200, {"result": "success"})
    else:
        wiz.response.status(404, {"error": "User not found"})

# 사용자 삭제
def delete():
    user_id = wiz.request.query("id")
    user_model = wiz.model("user").use()
    
    if user_model.delete(user_id):
        wiz.response.status(200, {"result": "success"})
    else:
        wiz.response.status(404, {"error": "User not found"})
```

**app/page.users/view.ts**
```typescript
import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public users: any[] = [];
    public selectedUser: any = null;

    async ngOnInit() {
        await this.service.init();
        await this.loadUsers();
        await this.service.render();
    }

    async loadUsers() {
        let res = await this.service.api.call("list");
        this.users = res.data;
    }

    async createUser() {
        let data = {
            name: "New User",
            email: "user@example.com"
        };
        
        await this.service.api.call("create", data);
        await this.loadUsers();
        await this.service.render();
    }

    async updateUser(user) {
        await this.service.api.call("update", user);
        await this.loadUsers();
        await this.service.render();
    }

    async deleteUser(userId) {
        let confirmed = await this.service.alert.confirm("삭제하시겠습니까?");
        if (confirmed) {
            await this.service.api.call("delete", { id: userId });
            await this.loadUsers();
            await this.service.render();
        }
    }
}
```

**app/page.users/view.pug**
```pug
.users-page
    .header
        h1 사용자 관리
        button.btn.btn-primary((click)="createUser()") 새 사용자

    .users-list
        .user-item(*ngFor="let user of users")
            .user-info
                h3 {{ user.name }}
                p {{ user.email }}
            .user-actions
                button.btn.btn-sm.btn-info((click)="updateUser(user)") 수정
                button.btn.btn-sm.btn-danger((click)="deleteUser(user.id)") 삭제
```
