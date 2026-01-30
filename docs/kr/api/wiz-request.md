# wiz.request API

HTTP 요청을 처리하는 API입니다. `api.py`, `controller.py`, `socket.py` 등에서 사용할 수 있습니다.

## 클래스 정보

- **클래스**: `season.lib.core.struct.Request`
- **접근**: `wiz.request`
- **소스**: `/mnt/data/git/wiz/src/season/lib/core/struct/request.py`

---

## 메서드

### wiz.request.query()

GET/POST 파라미터를 가져옵니다.

#### 구문
```python
wiz.request.query(key=None, default=None)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `key` | str | ❌ | None | 가져올 파라미터 키. None인 경우 모든 파라미터 반환 |
| `default` | any | ❌ | None | 키가 없을 때 반환할 기본값. True인 경우 400 에러 발생 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `dict` | key가 None인 경우, 모든 파라미터를 딕셔너리로 반환 |
| `any` | key가 지정된 경우, 해당 값 반환 (없으면 default 반환) |

#### 예제

```python
# 모든 파라미터 가져오기
data = wiz.request.query()
# {'name': 'Alice', 'age': '25', 'email': 'alice@example.com'}

# 특정 파라미터 가져오기
name = wiz.request.query("name")  # "Alice"
age = wiz.request.query("age")    # "25"

# 기본값 지정
city = wiz.request.query("city", "Seoul")  # "Seoul" (city 파라미터가 없는 경우)

# 필수 파라미터 (없으면 400 에러)
email = wiz.request.query("email", True)
```

---

### wiz.request.files()

업로드된 파일 목록을 가져옵니다.

#### 구문
```python
wiz.request.files(namespace='file')
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `namespace` | str | ❌ | 'file' | 파일 input의 name 속성 ([] 자동 추가) |

#### 반환값

| 타입 | 설명 |
|------|------|
| `list` | FileStorage 객체 리스트 |

#### 예제

```python
# 파일 업로드 처리
files = wiz.request.files()

for file in files:
    filename = file.filename
    content = file.read()
    
    # 파일 저장
    fs = wiz.project.fs("data", "uploads")
    fs.write(filename, content, mode="wb")

# HTML form 예시:
# <input type="file" name="file[]" multiple>
```

---

### wiz.request.file()

단일 파일을 가져옵니다.

#### 구문
```python
wiz.request.file(namespace='file')
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `namespace` | str | ❌ | 'file' | 파일 input의 name 속성 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `FileStorage` or `None` | 업로드된 파일 객체 또는 None |

#### 예제

```python
# 단일 파일 업로드
file = wiz.request.file('avatar')

if file:
    filename = file.filename
    fs = wiz.project.fs("data", "avatars")
    fs.write(filename, file.read(), mode="wb")

# HTML form 예시:
# <input type="file" name="avatar">
```

---

### wiz.request.match()

URL 패턴을 매칭하고 세그먼트를 추출합니다.

#### 구문
```python
wiz.request.match(pattern)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `pattern` | str | ✅ | - | URL 패턴 (Werkzeug 라우팅 규칙) |

#### 지원하는 패턴 타입

| 패턴 | 설명 | 예제 |
|------|------|------|
| `<name>` | 문자열 (기본) | `/users/<username>` |
| `<int:name>` | 정수 | `/posts/<int:id>` |
| `<float:name>` | 실수 | `/price/<float:amount>` |
| `<path:name>` | 경로 (/ 포함) | `/files/<path:filepath>` |

#### 반환값

| 타입 | 설명 |
|------|------|
| `stdClass` or `None` | 매칭된 세그먼트 객체 또는 None |

#### 예제

```python
# URL: /api/users/123/posts/456

# 기본 매칭
segment = wiz.request.match("/api/<resource>/<int:id>/<sub>/<int:sub_id>")
print(segment.resource)  # "users"
print(segment.id)        # 123
print(segment.sub)       # "posts"
print(segment.sub_id)    # 456

# 경로 매칭
# URL: /files/images/profile/avatar.png
segment = wiz.request.match("/files/<path:filepath>")
print(segment.filepath)  # "images/profile/avatar.png"

# 조건부 처리
segment = wiz.request.match("/brand/<action>/<path:path>")
action = segment.action

if action == "logo":
    # 로고 처리
    pass
elif action == "icon":
    # 아이콘 처리
    pass
```

---

### wiz.request.uri()

현재 요청의 URI를 반환합니다.

#### 구문
```python
wiz.request.uri()
```

#### 파라미터

없음

#### 반환값

| 타입 | 설명 |
|------|------|
| `str` | 베이스 URL을 제외한 요청 URI |

#### 예제

```python
# 요청 URL: http://localhost:3000/api/users/123
uri = wiz.request.uri()
print(uri)  # "/api/users/123"

# 리다이렉트에 활용
wiz.response.redirect(wiz.request.uri())
```

---

### wiz.request.method()

HTTP 메서드를 반환합니다.

#### 구문
```python
wiz.request.method()
```

#### 파라미터

없음

#### 반환값

| 타입 | 설명 |
|------|------|
| `str` | HTTP 메서드 (GET, POST, PUT, DELETE 등) |

#### 예제

```python
method = wiz.request.method()

if method == "GET":
    # GET 요청 처리
    pass
elif method == "POST":
    # POST 요청 처리
    pass
elif method == "PUT":
    # PUT 요청 처리
    pass
elif method == "DELETE":
    # DELETE 요청 처리
    pass
```

---

### wiz.request.headers()

HTTP 헤더 값을 가져옵니다.

#### 구문
```python
wiz.request.headers(key, default=None)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `key` | str | ✅ | - | 헤더 이름 |
| `default` | any | ❌ | None | 헤더가 없을 때 반환할 기본값 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `str` or `any` | 헤더 값 또는 기본값 |

#### 예제

```python
# User-Agent 가져오기
user_agent = wiz.request.headers("User-Agent")
print(user_agent)  # "Mozilla/5.0 ..."

# Authorization 헤더
auth = wiz.request.headers("Authorization", "")
if auth.startswith("Bearer "):
    token = auth[7:]  # "Bearer " 제거

# Content-Type
content_type = wiz.request.headers("Content-Type", "application/json")
```

---

### wiz.request.cookies()

쿠키 값을 가져옵니다.

#### 구문
```python
wiz.request.cookies(key, default=None)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `key` | str | ✅ | - | 쿠키 이름 |
| `default` | any | ❌ | None | 쿠키가 없을 때 반환할 기본값 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `str` or `any` | 쿠키 값 또는 기본값 |

#### 예제

```python
# 세션 ID 가져오기
session_id = wiz.request.cookies("session_id")

# 언어 설정
lang = wiz.request.cookies("language", "ko")

# 프로젝트 선택
project = wiz.request.cookies("season-wiz-project", "main")
```

---

### wiz.request.ip()

클라이언트 IP 주소를 가져옵니다.

#### 구문
```python
wiz.request.ip()
```

#### 파라미터

없음

#### 반환값

| 타입 | 설명 |
|------|------|
| `str` | 클라이언트 IP 주소 |

#### 예제

```python
ip = wiz.request.ip()
print(ip)  # "192.168.1.100"

# 로깅
logger = wiz.logger("access")
logger.info(f"Request from {ip}")

# IP 기반 접근 제어
allowed_ips = ["127.0.0.1", "192.168.1.0/24"]
if ip not in allowed_ips:
    wiz.response.abort(403)
```

---

### wiz.request.language()

요청 언어를 가져옵니다.

#### 구문
```python
wiz.request.language()
```

#### 파라미터

없음

#### 반환값

| 타입 | 설명 |
|------|------|
| `str` | 언어 코드 (대문자, 예: "KO", "EN", "DEFAULT") |

#### 예제

```python
lang = wiz.request.language()
print(lang)  # "KO"

# 언어별 처리
if lang == "KO":
    message = "안녕하세요"
elif lang == "EN":
    message = "Hello"
else:
    message = "Hello"

wiz.response.status(200, {"message": message})
```

---

### wiz.request.request()

Flask request 객체에 직접 접근합니다.

#### 구문
```python
wiz.request.request()
```

#### 파라미터

없음

#### 반환값

| 타입 | 설명 |
|------|------|
| `flask.Request` | Flask request 객체 |

#### 예제

```python
req = wiz.request.request()

# 전체 URL
print(req.url)  # "http://localhost:3000/api/users?page=1"

# 베이스 URL
print(req.base_url)  # "http://localhost:3000/api/users"

# 메서드
print(req.method)  # "GET"

# 헤더 전체
headers = dict(req.headers)

# 폼 데이터
form_data = dict(req.form)

# JSON 데이터
json_data = req.get_json()

# 원격 주소
print(req.remote_addr)  # "127.0.0.1"
```

---

## 전체 예제

### RESTful API 엔드포인트

```python
# route/api/controller.py

# URL 매칭
segment = wiz.request.match("/api/<resource>/<path:path>")
resource = segment.resource
path = segment.path

# HTTP 메서드
method = wiz.request.method()

# 데이터베이스
db = wiz.model("database").use()

if resource == "users":
    if method == "GET":
        if path:
            # GET /api/users/123
            user_id = path
            user = db.get_user(user_id)
            wiz.response.status(200, user)
        else:
            # GET /api/users
            users = db.get_users()
            wiz.response.status(200, users)
    
    elif method == "POST":
        # POST /api/users
        data = wiz.request.query()
        user_id = db.create_user(data)
        wiz.response.status(201, {"id": user_id})
    
    elif method == "PUT":
        # PUT /api/users/123
        user_id = path
        data = wiz.request.query()
        db.update_user(user_id, data)
        wiz.response.status(200, {"result": "success"})
    
    elif method == "DELETE":
        # DELETE /api/users/123
        user_id = path
        db.delete_user(user_id)
        wiz.response.status(204)

wiz.response.abort(404)
```

### 파일 업로드 처리

```python
# app/page.upload/api.py

def upload():
    """파일 업로드"""
    files = wiz.request.files()
    
    if len(files) == 0:
        wiz.response.status(400, {"error": "No files uploaded"})
        return
    
    fs = wiz.project.fs("data", "uploads")
    uploaded = []
    
    for file in files:
        filename = file.filename
        fs.write(filename, file.read(), mode="wb")
        uploaded.append({
            "name": filename,
            "size": fs.size(filename)
        })
    
    wiz.response.status(200, {
        "files": uploaded,
        "count": len(uploaded)
    })
```

### 인증 처리

```python
# controller/base.py

class Controller:
    def __init__(self):
        # 토큰 인증
        auth = wiz.request.headers("Authorization", "")
        
        if auth.startswith("Bearer "):
            token = auth[7:]
            auth_model = wiz.model("auth").use()
            user_id = auth_model.verify_token(token)
            
            if user_id:
                wiz.session.set("user_id", user_id)
            else:
                wiz.response.status(401, {"error": "Invalid token"})
        
        # IP 기반 제한
        ip = wiz.request.ip()
        if ip in blacklist:
            wiz.response.abort(403)
```

---

## 참고

- [wiz.response API](wiz-response.md)
- [wiz.session API](wiz-session.md)
- [전체 API 목록](README.md)
