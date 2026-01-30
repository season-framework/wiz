# wiz.project API

프로젝트 관리 및 파일시스템 접근 API입니다.

## 클래스 정보

- **클래스**: `season.lib.core.struct.Project`
- **접근**: `wiz.project`
- **소스**: `/mnt/data/git/wiz/src/season/lib/core/struct/project.py`

---

## 메서드

### wiz.project()

현재 프로젝트 이름을 반환하거나 프로젝트를 체크아웃합니다.

#### 구문
```python
# 현재 프로젝트 조회
project_name = wiz.project()

# 프로젝트 체크아웃
wiz.project(project)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `project` | str | ❌ | None | 체크아웃할 프로젝트 이름. None이면 현재 프로젝트 반환 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `str` | 프로젝트 이름 (예: "main") |

#### 예제

```python
# 현재 프로젝트 확인
current = wiz.project()
print(current)  # "main"

# 프로젝트 체크아웃
wiz.project("admin")
print(wiz.project())  # "admin"

# 프로젝트별 처리
project = wiz.project()
if project == "main":
    # 메인 프로젝트 로직
    pass
elif project == "admin":
    # 관리자 프로젝트 로직
    pass
```

---

### wiz.project.checkout()

프로젝트를 체크아웃합니다.

#### 구문
```python
wiz.project.checkout(project)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `project` | str | ✅ | - | 체크아웃할 프로젝트 이름 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `str` | 체크아웃된 프로젝트 이름 |

#### 동작

- 프로젝트가 존재하면 쿠키에 저장하고 현재 프로젝트로 설정
- 프로젝트가 없으면 현재 프로젝트 유지

#### 예제

```python
# 프로젝트 체크아웃
wiz.project.checkout("main")

# 존재하지 않는 프로젝트는 무시됨
wiz.project.checkout("nonexistent")  # 현재 프로젝트 유지

# CLI 명령어에서 사용
def build(*args):
    project = args[0]
    wiz.project.checkout(project)
    builder = wiz.ide.plugin.model("builder")
    builder.build()
```

---

### wiz.project.exists()

프로젝트 존재 여부를 확인합니다.

#### 구문
```python
wiz.project.exists(project)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `project` | str | ✅ | - | 확인할 프로젝트 이름 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `bool` | 프로젝트가 존재하면 True, 아니면 False |

#### 예제

```python
# 프로젝트 존재 확인
if wiz.project.exists("admin"):
    print("Admin project exists")

# 프로젝트 생성 전 확인
project_name = "new_project"
if not wiz.project.exists(project_name):
    # 프로젝트 생성 로직
    pass
else:
    wiz.response.status(400, {"error": "Project already exists"})
```

---

### wiz.project.list()

모든 프로젝트 목록을 반환합니다.

#### 구문
```python
wiz.project.list()
```

#### 파라미터

없음

#### 반환값

| 타입 | 설명 |
|------|------|
| `list` | 프로젝트 이름 리스트 |

#### 예제

```python
# 프로젝트 목록 조회
projects = wiz.project.list()
print(projects)  # ["main", "admin", "api"]

# API 응답
def get_projects():
    projects = wiz.project.list()
    wiz.response.status(200, projects)
```

---

### wiz.project.path()

프로젝트 내 경로를 반환합니다.

#### 구문
```python
wiz.project.path(*args)
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
# 프로젝트 루트 경로
root = wiz.project.path()
print(root)  # "/path/to/project/main"

# 하위 경로
data_path = wiz.project.path("data")
print(data_path)  # "/path/to/project/main/data"

# 깊은 경로
uploads_path = wiz.project.path("data", "uploads", "images")
print(uploads_path)  # "/path/to/project/main/data/uploads/images"
```

---

### wiz.project.fs()

프로젝트 내 파일시스템 객체를 반환합니다.

#### 구문
```python
wiz.project.fs(*args)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `*args` | str | ❌ | - | 경로 세그먼트 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `Filesystem` | 파일시스템 객체 |

#### 파일시스템 메서드

| 메서드 | 설명 |
|--------|------|
| `read(filename)` | 파일 읽기 |
| `write(filename, data, mode="w")` | 파일 쓰기 |
| `read.json(filename, default={})` | JSON 읽기 |
| `write.json(filename, data)` | JSON 쓰기 |
| `exists(filename)` | 파일/디렉토리 존재 확인 |
| `isdir(path)` | 디렉토리 확인 |
| `delete(path)` | 파일/디렉토리 삭제 |
| `makedirs(path)` | 디렉토리 생성 |
| `files(path="")` | 파일 목록 |
| `ls(path="")` | 파일/디렉토리 목록 |
| `size(filename)` | 파일 크기 |
| `abspath(filename)` | 절대 경로 |
| `copy(src, dst)` | 복사 |
| `move(src, dst)` | 이동 |

#### 예제

```python
# 데이터 디렉토리 파일시스템
fs = wiz.project.fs("data")

# 파일 읽기
content = fs.read("file.txt")

# 파일 쓰기
fs.write("file.txt", "Hello World")

# JSON 읽기/쓰기
data = fs.read.json("config.json", default={})
fs.write.json("config.json", {"key": "value"})

# 파일 존재 확인
if fs.exists("users.db"):
    # 데이터베이스 사용
    pass

# 디렉토리 생성
fs.makedirs("uploads/images")

# 파일 목록
files = fs.files()
for filename in files:
    print(filename)

# 절대 경로 얻기
filepath = fs.abspath("file.txt")
print(filepath)  # "/path/to/project/main/data/file.txt"

# 파일 업로드 저장
fs_uploads = wiz.project.fs("data", "uploads")
files = wiz.request.files()
for file in files:
    fs_uploads.write(file.filename, file.read(), mode="wb")

# CSV 내보내기
fs_exports = wiz.project.fs("data", "exports")
csv_data = "name,email\nAlice,alice@example.com"
fs_exports.write("users.csv", csv_data)
filepath = fs_exports.abspath("users.csv")
wiz.response.download(filepath)
```

---

### wiz.project.dev()

개발 모드 상태를 확인하거나 설정합니다.

#### 구문
```python
# 개발 모드 확인
is_dev = wiz.project.dev()

# 개발 모드 설정
wiz.project.dev(True)  # 개발 모드 활성화
wiz.project.dev(False)  # 개발 모드 비활성화
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `devmode` | bool | ❌ | None | 개발 모드 설정. None이면 현재 상태 반환 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `bool` | 개발 모드 여부 |

#### 예제

```python
# 개발 모드 확인
if wiz.project.dev():
    # 개발 모드에서만 실행
    print("Development mode")

# 개발 모드 활성화
wiz.project.dev(True)

# 개발/프로덕션 분기
if wiz.project.dev():
    # 개발 환경 설정
    debug = True
    log_level = "DEBUG"
else:
    # 프로덕션 환경 설정
    debug = False
    log_level = "ERROR"
```

---

## 전체 예제

### 프로젝트별 데이터 관리

```python
# model/storage.py

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.fs = wiz.project.fs("data", "storage")
    
    def save(self, key, data):
        """데이터 저장"""
        filename = f"{key}.json"
        self.fs.write.json(filename, data)
    
    def load(self, key):
        """데이터 로드"""
        filename = f"{key}.json"
        if not self.fs.exists(filename):
            return None
        return self.fs.read.json(filename)
    
    def delete(self, key):
        """데이터 삭제"""
        filename = f"{key}.json"
        if self.fs.exists(filename):
            self.fs.delete(filename)
    
    def list(self):
        """모든 키 조회"""
        files = self.fs.files()
        return [f.replace(".json", "") for f in files if f.endswith(".json")]
```

### 파일 업로드 (프로젝트별)

```python
# app/page.upload/api.py

def upload():
    """파일 업로드"""
    # 현재 프로젝트의 uploads 디렉토리
    fs = wiz.project.fs("data", "uploads")
    
    files = wiz.request.files()
    uploaded = []
    
    for file in files:
        filename = file.filename
        
        # 파일 저장
        fs.write(filename, file.read(), mode="wb")
        
        uploaded.append({
            "project": wiz.project(),
            "name": filename,
            "size": fs.size(filename),
            "path": fs.abspath(filename)
        })
    
    wiz.response.status(200, {
        "files": uploaded,
        "count": len(uploaded)
    })

def list_files():
    """파일 목록"""
    fs = wiz.project.fs("data", "uploads")
    
    files = []
    for filename in fs.files():
        files.append({
            "name": filename,
            "size": fs.size(filename)
        })
    
    wiz.response.status(200, files)

def download():
    """파일 다운로드"""
    filename = wiz.request.query("filename")
    fs = wiz.project.fs("data", "uploads")
    
    if not fs.exists(filename):
        wiz.response.status(404, {"error": "File not found"})
    else:
        filepath = fs.abspath(filename)
        wiz.response.download(filepath)
```

### 멀티 프로젝트 관리

```python
# app/page.projects/api.py

def get_projects():
    """프로젝트 목록"""
    projects = wiz.project.list()
    current = wiz.project()
    
    result = []
    for project in projects:
        result.append({
            "name": project,
            "current": project == current
        })
    
    wiz.response.status(200, result)

def switch_project():
    """프로젝트 전환"""
    project = wiz.request.query("project")
    
    if not wiz.project.exists(project):
        wiz.response.status(404, {"error": "Project not found"})
        return
    
    wiz.project.checkout(project)
    wiz.response.status(200, {
        "message": "Project switched",
        "project": wiz.project()
    })

def create_project():
    """프로젝트 생성"""
    project = wiz.request.query("name")
    
    if wiz.project.exists(project):
        wiz.response.status(400, {"error": "Project already exists"})
        return
    
    # 프로젝트 디렉토리 생성
    import os
    project_path = os.path.join(wiz.server.path.project, project)
    os.makedirs(project_path)
    
    # 기본 구조 생성
    os.makedirs(os.path.join(project_path, "src"))
    os.makedirs(os.path.join(project_path, "data"))
    
    wiz.response.status(201, {
        "message": "Project created",
        "project": project
    })
```

### 환경별 설정

```python
# config/boot.py

def bootstrap(app, config):
    """부트스트랩 함수"""
    import os
    
    # 환경 변수
    ENV = os.getenv("ENV", "development")
    
    if ENV == "production":
        # 프로덕션 설정
        config.boot.run['debug'] = False
        config.boot.log_level = season.LOG_ERROR
    else:
        # 개발 설정
        config.boot.run['debug'] = True
        config.boot.log_level = season.LOG_DEBUG

# 프로젝트별 설정
project = wiz.project()

if project == "main":
    # 메인 프로젝트 설정
    run['port'] = 3000
elif project == "admin":
    # 관리자 프로젝트 설정
    run['port'] = 3001
```

---

## 참고

- [wiz.fs() API](wiz-filesystem.md)
- [wiz.request API](wiz-request.md)
- [전체 API 목록](README.md)
