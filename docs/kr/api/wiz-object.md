# wiz 객체 API

WIZ 프레임워크의 핵심 객체로, Python 코드에서 사용 가능한 모든 API의 진입점입니다.

## 클래스 정보

- **클래스**: `season.lib.core.Wiz`
- **접근**: `wiz` (전역 객체)
- **소스**: `/mnt/data/git/wiz/src/season/lib/core/wiz.py`
- **사용 위치**: `api.py`, `controller.py`, `socket.py`, `model/*.py`, `route/*/controller.py`

---

## 하위 API 객체

### wiz.request

HTTP 요청을 처리하는 API입니다.

| 메서드 | 설명 | 문서 |
|--------|------|------|
| `wiz.request.query()` | GET/POST 파라미터 가져오기 | [상세](wiz-request.md#wizrequestquery) |
| `wiz.request.files()` | 업로드된 파일 목록 | [상세](wiz-request.md#wizrequestfiles) |
| `wiz.request.file()` | 단일 파일 가져오기 | [상세](wiz-request.md#wizrequestfile) |
| `wiz.request.match()` | URL 패턴 매칭 | [상세](wiz-request.md#wizrequestmatch) |
| `wiz.request.uri()` | 현재 요청 URI | [상세](wiz-request.md#wizrequesturi) |
| `wiz.request.method()` | HTTP 메서드 | [상세](wiz-request.md#wizrequestmethod) |
| `wiz.request.headers()` | HTTP 헤더 | [상세](wiz-request.md#wizrequestheaders) |
| `wiz.request.cookies()` | 쿠키 값 | [상세](wiz-request.md#wizrequestcookies) |
| `wiz.request.ip()` | 클라이언트 IP | [상세](wiz-request.md#wizrequestip) |

📖 **전체 문서**: [wiz.request API](wiz-request.md)

---

### wiz.response

HTTP 응답을 생성하는 API입니다.

| 메서드 | 설명 | 문서 |
|--------|------|------|
| `wiz.response.status()` | JSON 응답 | [상세](wiz-response.md#wizresponsestatus) |
| `wiz.response.download()` | 파일 다운로드 | [상세](wiz-response.md#wizresponsedownload) |
| `wiz.response.redirect()` | URL 리다이렉트 | [상세](wiz-response.md#wizresponseredirect) |
| `wiz.response.abort()` | HTTP 에러 발생 | [상세](wiz-response.md#wizresponseabort) |
| `wiz.response.send()` | 텍스트 응답 | [상세](wiz-response.md#wizresponsesend) |
| `wiz.response.json()` | JSON 응답 | [상세](wiz-response.md#wizresponsejson) |
| `wiz.response.PIL()` | 이미지 응답 | [상세](wiz-response.md#wizresponsepil) |
| `wiz.response.stream()` | 스트리밍 | [상세](wiz-response.md#wizresponsestream) |

📖 **전체 문서**: [wiz.response API](wiz-response.md)

---

### wiz.project

프로젝트 관리 및 파일시스템 접근 API입니다.

| 메서드 | 설명 | 문서 |
|--------|------|------|
| `wiz.project()` | 현재 프로젝트 이름 | [상세](wiz-project.md#wizproject) |
| `wiz.project.checkout()` | 프로젝트 체크아웃 | [상세](wiz-project.md#wizprojectcheckout) |
| `wiz.project.exists()` | 프로젝트 존재 확인 | [상세](wiz-project.md#wizprojectexists) |
| `wiz.project.list()` | 프로젝트 목록 | [상세](wiz-project.md#wizprojectlist) |
| `wiz.project.path()` | 프로젝트 경로 | [상세](wiz-project.md#wizprojectpath) |
| `wiz.project.fs()` | 파일시스템 객체 | [상세](wiz-project.md#wizprojectfs) |
| `wiz.project.dev()` | 개발 모드 | [상세](wiz-project.md#wizprojectdev) |

📖 **전체 문서**: [wiz.project API](wiz-project.md)

---

### wiz.session

세션 관리 API입니다.

| 메서드 | 설명 |
|--------|------|
| `wiz.session.set(key, value)` | 세션 값 설정 |
| `wiz.session.get(key, default)` | 세션 값 가져오기 |
| `wiz.session.delete(key)` | 세션 값 삭제 |
| `wiz.session.clear()` | 모든 세션 삭제 |

📖 **전체 문서**: [wiz.session API](wiz-session.md)

---

## 메서드

### wiz.fs()

현재 위치의 파일시스템 객체를 반환합니다.

#### 구문
```python
wiz.fs(*args)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `*args` | str | ❌ | - | 경로 세그먼트 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `Filesystem` | 파일시스템 객체 |

#### 예제

```python
# 현재 컴포넌트 디렉토리
fs = wiz.fs()
content = fs.read("data.json")

# 하위 디렉토리
fs = wiz.fs("config")
config = fs.read.json("settings.json")
```

---

### wiz.path()

WIZ 루트 경로를 반환합니다.

#### 구문
```python
wiz.path(*args)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `*args` | str | ❌ | - | 경로 세그먼트 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `str` | 절대 경로 |

#### 예제

```python
# WIZ 루트 경로
root = wiz.path()
print(root)  # "/path/to/wiz"

# config 경로
config_path = wiz.path("config")
print(config_path)  # "/path/to/wiz/config"
```

---

### wiz.model()

모델을 로드합니다.

#### 구문
```python
wiz.model(namespace)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `namespace` | str | ✅ | - | 모델 네임스페이스 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `class` | 모델 클래스 |

#### 예제

```python
# 프로젝트 모델
UserModel = wiz.model("user")
user_instance = UserModel(wiz)

# use() 헬퍼 사용
user_model = wiz.model("user").use()
users = user_model.get_all()

# 포털 모델
session_model = wiz.model("portal/season/session").use()
sessiondata = session_model.get()
```

---

### wiz.controller()

컨트롤러를 로드합니다.

#### 구문
```python
wiz.controller(namespace)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `namespace` | str | ✅ | - | 컨트롤러 네임스페이스 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `class` | 컨트롤러 클래스 |

#### 예제

```python
# 베이스 컨트롤러 로드
BaseController = wiz.controller("base")
base = BaseController()
```

---

### wiz.logger()

로거 객체를 생성합니다.

#### 구문
```python
wiz.logger(*tags)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `*tags` | str | ❌ | - | 로그 태그 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `Logger` | 로거 객체 |

#### 로거 메서드

| 메서드 | 설명 |
|--------|------|
| `debug(message)` | 디버그 로그 |
| `info(message)` | 정보 로그 |
| `warning(message)` | 경고 로그 |
| `error(message)` | 에러 로그 |
| `critical(message)` | 치명적 에러 로그 |

#### 예제

```python
# 로거 생성
logger = wiz.logger("myapp", "api")

# 로그 출력
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")

# 시간 포함 로그 (자동)
# [125ms] [myapp] [api] Info message
```

---

### wiz.src()

프로젝트의 bundle/src 경로 파일시스템을 반환합니다.

#### 구문
```python
wiz.src(*args)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `*args` | str | ❌ | - | 경로 세그먼트 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `Filesystem` | 파일시스템 객체 |

#### 예제

```python
# src 파일시스템
fs = wiz.src()

# app 디렉토리
fs = wiz.src("app")

# 모델 디렉토리
fs = wiz.src("model")
```

---

## 전체 사용 예제

### API 핸들러

```python
# app/page.users/api.py

def get_users():
    """사용자 목록 조회"""
    # 로거
    logger = wiz.logger("users", "api")
    logger.info("Get users request")
    
    # 모델 로드
    user_model = wiz.model("user").use()
    users = user_model.get_all()
    
    # 응답
    wiz.response.status(200, users)

def create_user():
    """사용자 생성"""
    # 요청 데이터
    data = wiz.request.query()
    
    # 유효성 검사
    if not data.get("email"):
        wiz.response.status(400, {"error": "Email required"})
        return
    
    # 모델 사용
    user_model = wiz.model("user").use()
    user_id = user_model.create(data)
    
    # 세션 설정
    wiz.session.set("last_created_user", user_id)
    
    # 응답
    wiz.response.status(201, {"id": user_id})

def upload_avatar():
    """아바타 업로드"""
    # 파일 가져오기
    file = wiz.request.file("avatar")
    
    if not file:
        wiz.response.status(400, {"error": "No file"})
        return
    
    # 파일 저장
    fs = wiz.project.fs("data", "avatars")
    filename = file.filename
    fs.write(filename, file.read(), mode="wb")
    
    # 응답
    wiz.response.status(200, {
        "filename": filename,
        "path": fs.abspath(filename)
    })
```

### 컨트롤러

```python
# controller/base.py

class Controller:
    def __init__(self):
        # 현재 프로젝트
        project = wiz.project()
        
        # 세션 모델
        session_model = wiz.model("portal/season/session").use()
        sessiondata = session_model.get()
        
        # 템플릿에 데이터 전달
        wiz.response.data.set(
            project=project,
            session=sessiondata
        )
        
        # 인증 확인
        user_id = wiz.session.get("user_id")
        if not user_id:
            # 보호된 페이지 확인
            uri = wiz.request.uri()
            protected = ["/dashboard", "/admin"]
            
            if any(uri.startswith(p) for p in protected):
                wiz.response.redirect("/login")
```

### 라우트

```python
# route/api/controller.py

# URL 매칭
segment = wiz.request.match("/api/<resource>/<path:path>")
resource = segment.resource
path = segment.path

# HTTP 메서드
method = wiz.request.method()

# 로거
logger = wiz.logger("api", resource)
logger.info(f"{method} /{resource}/{path}")

# 모델
db = wiz.model("database").use()

if resource == "users":
    if method == "GET":
        users = db.query("SELECT * FROM users")
        wiz.response.status(200, users)
    elif method == "POST":
        data = wiz.request.query()
        user_id = db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            [data.get("name"), data.get("email")]
        )
        wiz.response.status(201, {"id": user_id})

wiz.response.abort(404)
```

---

## 참고

- [wiz.request API](wiz-request.md)
- [wiz.response API](wiz-response.md)
- [wiz.project API](wiz-project.md)
- [wiz.session API](wiz-session.md)
- [Service API (TypeScript)](service-api.md)
- [전체 API 목록](README.md)
