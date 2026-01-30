# wiz.response API

HTTP 응답을 생성하는 API입니다. `api.py`, `controller.py`, `socket.py` 등에서 사용할 수 있습니다.

## 클래스 정보

- **클래스**: `season.lib.core.struct.Response`
- **접근**: `wiz.response`
- **소스**: `/mnt/data/git/wiz/src/season/lib/core/struct/response.py`

---

## 메서드

### wiz.response.status()

JSON 형식의 표준 응답을 반환합니다.

#### 구문
```python
wiz.response.status(status_code, data=None, **kwargs)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `status_code` | int | ✅ | - | HTTP 상태 코드 |
| `data` | dict/any | ❌ | None | 응답 데이터 |
| `**kwargs` | - | ❌ | - | 추가 키워드 인자 (data가 없을 때) |

#### 응답 형식

```json
{
    "code": 200,
    "data": { ... }
}
```

#### HTTP 상태 코드

| 코드 | 설명 | 사용 시점 |
|------|------|----------|
| 200 | OK | 성공적인 요청 |
| 201 | Created | 리소스 생성 완료 |
| 204 | No Content | 성공 (응답 본문 없음) |
| 400 | Bad Request | 잘못된 요청 |
| 401 | Unauthorized | 인증 필요 |
| 403 | Forbidden | 권한 없음 |
| 404 | Not Found | 리소스 없음 |
| 500 | Internal Server Error | 서버 에러 |

#### 예제

```python
# 성공 응답
data = {"message": "Success", "user_id": 123}
wiz.response.status(200, data)
# Response: {"code": 200, "data": {"message": "Success", "user_id": 123}}

# 생성 완료
wiz.response.status(201, {"id": 456})
# Response: {"code": 201, "data": {"id": 456}}

# 에러 응답
wiz.response.status(404, {"error": "User not found"})
# Response: {"code": 404, "data": {"error": "User not found"}}

# kwargs 사용
wiz.response.status(200, message="OK", count=10)
# Response: {"code": 200, "data": {"message": "OK", "count": 10}}

# 상태 코드만
wiz.response.status(204)
# Response: {"code": 204}
```

---

### wiz.response.download()

파일 다운로드 응답을 생성합니다.

#### 구문
```python
wiz.response.download(filepath, as_attachment=True, filename=None)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `filepath` | str | ✅ | - | 다운로드할 파일의 절대 경로 |
| `as_attachment` | bool | ❌ | True | True: 다운로드, False: 브라우저에서 표시 |
| `filename` | str | ❌ | None | 다운로드 시 파일명 (None이면 원본 파일명) |

#### 예제

```python
# 파일 다운로드
filepath = "/path/to/file.pdf"
wiz.response.download(filepath)

# 브라우저에서 표시 (PDF, 이미지 등)
wiz.response.download(filepath, as_attachment=False)

# 커스텀 파일명으로 다운로드
wiz.response.download(filepath, filename="report_2026.pdf")

# 프로젝트 파일 다운로드
fs = wiz.project.fs("data", "exports")
filepath = fs.abspath("data.csv")
wiz.response.download(filepath)

# 파일이 없으면 404
filename = wiz.request.query("filename")
fs = wiz.project.fs("data", "files")

if not fs.exists(filename):
    wiz.response.status(404, {"error": "File not found"})
else:
    filepath = fs.abspath(filename)
    wiz.response.download(filepath)
```

---

### wiz.response.redirect()

다른 URL로 리다이렉트합니다.

#### 구문
```python
wiz.response.redirect(url)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `url` | str | ✅ | - | 리다이렉트할 URL |

#### 예제

```python
# 절대 경로로 리다이렉트
wiz.response.redirect("/dashboard")

# 외부 URL
wiz.response.redirect("https://example.com")

# 현재 URI로 리다이렉트 (새로고침)
wiz.response.redirect(wiz.request.uri())

# 로그인 후 리다이렉트
def login():
    data = wiz.request.query()
    # 로그인 처리...
    
    redirect_url = wiz.request.query("redirect", "/")
    wiz.response.redirect(redirect_url)

# 언어 변경 후 리다이렉트
def change_language():
    lang = wiz.request.query("lang")
    wiz.response.lang(lang)
    wiz.response.redirect(wiz.request.uri())
```

---

### wiz.response.abort()

HTTP 에러를 발생시킵니다.

#### 구문
```python
wiz.response.abort(code=500)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `code` | int | ❌ | 500 | HTTP 에러 코드 |

#### 예제

```python
# 404 에러
if not user_exists:
    wiz.response.abort(404)

# 403 에러 (권한 없음)
if not has_permission:
    wiz.response.abort(403)

# 401 에러 (인증 필요)
if not is_authenticated:
    wiz.response.abort(401)

# 500 에러 (서버 에러)
wiz.response.abort(500)
```

---

### wiz.response.send()

텍스트 응답을 전송합니다.

#### 구문
```python
wiz.response.send(message, content_type=None)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `message` | str | ✅ | - | 전송할 메시지 |
| `content_type` | str | ❌ | None | Content-Type 헤더 |

#### 예제

```python
# 일반 텍스트
wiz.response.send("Hello World")

# HTML
html = "<h1>Hello</h1><p>Welcome</p>"
wiz.response.send(html, content_type="text/html")

# XML
xml = '<?xml version="1.0"?><root><item>data</item></root>'
wiz.response.send(xml, content_type="application/xml")

# WebSocket에서도 사용 (socket.py)
def on_message(data):
    wiz.response.send({"echo": data})
```

---

### wiz.response.json()

JSON 응답을 전송합니다.

#### 구문
```python
wiz.response.json(obj)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `obj` | dict/any | ✅ | - | JSON으로 변환할 객체 |

#### 예제

```python
# 딕셔너리 전송
data = {"name": "Alice", "age": 25}
wiz.response.json(data)

# 리스트 전송
users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
wiz.response.json(users)

# datetime 객체 자동 변환
import datetime
data = {"timestamp": datetime.datetime.now()}
wiz.response.json(data)  # 자동으로 문자열로 변환됨
```

---

### wiz.response.PIL()

PIL 이미지를 응답으로 전송합니다.

#### 구문
```python
wiz.response.PIL(pil_image, type='JPEG', mimetype='image/jpeg', as_attachment=False, filename=None)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `pil_image` | PIL.Image | ✅ | - | PIL 이미지 객체 |
| `type` | str | ❌ | 'JPEG' | 이미지 포맷 (JPEG, PNG, GIF, BMP) |
| `mimetype` | str | ❌ | 'image/jpeg' | MIME 타입 |
| `as_attachment` | bool | ❌ | False | 다운로드 여부 |
| `filename` | str | ❌ | None | 파일명 |

#### 예제

```python
from PIL import Image
from io import BytesIO
import base64

# 이미지 파일 열기
img = Image.open("/path/to/image.png")
wiz.response.PIL(img, type="PNG", mimetype="image/png")

# 이미지 리사이즈
img = Image.open("/path/to/image.jpg")
img = img.resize((800, 600), Image.LANCZOS)
wiz.response.PIL(img, type="JPEG")

# 썸네일 생성
img = Image.open("/path/to/image.jpg")
img.thumbnail((150, 150), Image.LANCZOS)
wiz.response.PIL(img, type="JPEG")

# Base64 디코딩
def load_base64_image():
    data = wiz.request.query("image")
    img_data = data.split(",")[1]  # "data:image/png;base64," 제거
    buf = BytesIO(base64.b64decode(img_data))
    img = Image.open(buf)
    
    # 처리...
    img = img.convert('RGB')
    wiz.response.PIL(img, type="PNG")
```

---

### wiz.response.stream()

비디오/오디오 스트리밍 응답을 생성합니다.

#### 구문
```python
wiz.response.stream(filepath, rangeHeader=None, mimetype='video/mp4', content_type=None, direct_passthrough=True)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `filepath` | str | ✅ | - | 스트리밍할 파일 경로 |
| `rangeHeader` | str | ❌ | None | Range 헤더 값 |
| `mimetype` | str | ❌ | 'video/mp4' | MIME 타입 |
| `content_type` | str | ❌ | None | Content-Type (None이면 mimetype 사용) |
| `direct_passthrough` | bool | ❌ | True | 직접 전송 여부 |

#### 예제

```python
# 비디오 스트리밍
filepath = "/path/to/video.mp4"
range_header = wiz.request.headers("Range")
wiz.response.stream(filepath, rangeHeader=range_header)

# 오디오 스트리밍
filepath = "/path/to/audio.mp3"
range_header = wiz.request.headers("Range")
wiz.response.stream(filepath, rangeHeader=range_header, mimetype="audio/mpeg")
```

---

### wiz.response.lang() / wiz.response.language()

응답 언어를 설정합니다.

#### 구문
```python
wiz.response.lang(lang)
wiz.response.language(lang)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `lang` | str | ✅ | - | 언어 코드 (2자리) |

#### 예제

```python
# 언어 설정
wiz.response.lang("ko")  # 한국어
wiz.response.lang("en")  # 영어
wiz.response.lang("ja")  # 일본어

# 언어 변경 후 리다이렉트
def change_language():
    lang = wiz.request.query("lang", "ko")
    wiz.response.lang(lang)
    wiz.response.redirect(wiz.request.uri())
```

---

## 응답 헬퍼 객체

### wiz.response.data

응답 데이터를 관리하는 객체입니다.

#### 메서드

##### wiz.response.data.set()

템플릿에서 사용할 데이터를 설정합니다.

```python
wiz.response.data.set(key1=value1, key2=value2, ...)
```

**파라미터**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `**kwargs` | - | ✅ | 키워드 인자 형태의 데이터 |

**예제**

```python
# 컨트롤러에서 템플릿 변수 설정
wiz.response.data.set(username="Alice", role="admin")

# 여러 변수 설정
wiz.response.data.set(
    title="Dashboard",
    user={"id": 1, "name": "Alice"},
    items=[1, 2, 3, 4, 5]
)
```

##### wiz.response.data.get()

설정된 데이터를 가져옵니다.

```python
wiz.response.data.get(key=None)
```

**파라미터**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `key` | str | ❌ | None | 가져올 키. None이면 전체 데이터 반환 |

**예제**

```python
# 전체 데이터
data = wiz.response.data.get()

# 특정 키
username = wiz.response.data.get("username")
```

##### wiz.response.data.set_json()

JSON 형태로 데이터를 설정합니다.

```python
wiz.response.data.set_json(key=value, ...)
```

**예제**

```python
import datetime

# datetime 객체를 JSON 문자열로 자동 변환
wiz.response.data.set_json(
    timestamp=datetime.datetime.now(),
    user={"id": 1, "name": "Alice"}
)
```

---

### wiz.response.headers

응답 헤더를 관리하는 객체입니다.

#### 메서드

##### wiz.response.headers.set()

응답 헤더를 설정합니다.

```python
wiz.response.headers.set(key1=value1, key2=value2, ...)
```

**예제**

```python
# 커스텀 헤더 설정
wiz.response.headers.set(**{
    'X-Custom-Header': 'value',
    'Cache-Control': 'no-cache'
})

# Content-Type 설정
wiz.response.headers.set(**{'Content-Type': 'text/html'})

# CORS 헤더
wiz.response.headers.set(**{
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE'
})
```

##### wiz.response.headers.get()

설정된 헤더를 가져옵니다.

```python
wiz.response.headers.get(name=None)
```

---

### wiz.response.cookies

응답 쿠키를 관리하는 객체입니다.

#### 메서드

##### wiz.response.cookies.set()

쿠키를 설정합니다.

```python
wiz.response.cookies.set(key1=value1, key2=value2, ...)
```

**예제**

```python
# 쿠키 설정
wiz.response.cookies.set(**{
    'session_id': 'abc123',
    'user_pref': 'dark_mode'
})

# 언어 쿠키
wiz.response.cookies.set(**{'framework-language': 'KO'})

# 프로젝트 쿠키
wiz.response.cookies.set(**{'season-wiz-project': 'main'})
```

---

## 전체 예제

### RESTful API 응답

```python
# app/page.users/api.py

def get_users():
    """사용자 목록 조회"""
    db = wiz.model("database").use()
    users = db.query("SELECT * FROM users")
    wiz.response.status(200, users)

def get_user():
    """사용자 상세 조회"""
    user_id = wiz.request.query("id")
    db = wiz.model("database").use()
    user = db.query_one("SELECT * FROM users WHERE id = ?", [user_id])
    
    if user:
        wiz.response.status(200, user)
    else:
        wiz.response.status(404, {"error": "User not found"})

def create_user():
    """사용자 생성"""
    data = wiz.request.query()
    name = data.get("name")
    email = data.get("email")
    
    # 유효성 검사
    if not name or not email:
        wiz.response.status(400, {"error": "Name and email required"})
        return
    
    db = wiz.model("database").use()
    user_id = db.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        [name, email]
    )
    
    wiz.response.status(201, {"id": user_id})

def delete_user():
    """사용자 삭제"""
    user_id = wiz.request.query("id")
    db = wiz.model("database").use()
    
    db.execute("DELETE FROM users WHERE id = ?", [user_id])
    wiz.response.status(204)
```

### 파일 다운로드

```python
# route/download/controller.py

segment = wiz.request.match("/download/<file_type>/<filename>")
file_type = segment.file_type
filename = segment.filename

fs = wiz.project.fs("data", file_type)

if not fs.exists(filename):
    wiz.response.status(404, {"error": "File not found"})
else:
    filepath = fs.abspath(filename)
    wiz.response.download(filepath)
```

### 이미지 처리

```python
# app/page.image/api.py

from PIL import Image

def thumbnail():
    """썸네일 생성"""
    filename = wiz.request.query("filename")
    size = int(wiz.request.query("size", 150))
    
    fs = wiz.project.fs("data", "images")
    
    if not fs.exists(filename):
        wiz.response.abort(404)
    
    img = Image.open(fs.abspath(filename))
    img.thumbnail((size, size), Image.LANCZOS)
    
    wiz.response.PIL(img, type="PNG", mimetype="image/png")

def resize():
    """이미지 리사이즈"""
    files = wiz.request.files()
    width = int(wiz.request.query("width", 800))
    height = int(wiz.request.query("height", 600))
    
    if len(files) == 0:
        wiz.response.status(400, {"error": "No image uploaded"})
        return
    
    file = files[0]
    img = Image.open(file)
    img = img.resize((width, height), Image.LANCZOS)
    
    fs = wiz.project.fs("data", "resized")
    output = fs.abspath("resized.png")
    img.save(output)
    
    wiz.response.status(200, {"message": "Image resized", "size": [width, height]})
```

---

## 참고

- [wiz.request API](wiz-request.md)
- [wiz.session API](wiz-session.md)
- [전체 API 목록](README.md)
