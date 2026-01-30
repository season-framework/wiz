# Filesystem API

파일 및 디렉토리를 관리하는 API입니다.

## 개요

- **클래스**: `season.util.Filesystem`
- **접근**: `wiz.fs()`, `wiz.project.fs()`, `season.util.fs()`
- **사용 위치**: `api.py`, `controller.py`, `model/*.py`

---

## 파일시스템 생성

### wiz.fs()

현재 컴포넌트의 파일시스템을 반환합니다.

```python
fs = wiz.fs()
```

### wiz.project.fs()

프로젝트 내 파일시스템을 반환합니다.

```python
fs = wiz.project.fs("data", "uploads")
```

### season.util.fs()

임의 경로의 파일시스템을 반환합니다.

```python
import season
fs = season.util.fs("/path/to/directory")
```

---

## 파일 읽기/쓰기

### read()

파일을 읽습니다.

#### 구문
```python
fs.read(filename, default=None)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `filename` | str | ✅ | - | 파일명 |
| `default` | any | ❌ | None | 파일이 없을 때 반환할 값 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `str` or `any` | 파일 내용 또는 기본값 |

#### 예제

```python
# 텍스트 파일 읽기
content = fs.read("file.txt")

# 파일이 없으면 기본값
content = fs.read("file.txt", "")

# None 처리
content = fs.read("file.txt", None)
if content is None:
    print("File not found")
```

---

### write()

파일에 씁니다.

#### 구문
```python
fs.write(filename, data, mode="w")
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `filename` | str | ✅ | - | 파일명 |
| `data` | str/bytes | ✅ | - | 저장할 데이터 |
| `mode` | str | ❌ | "w" | 쓰기 모드 ("w": 텍스트, "wb": 바이너리) |

#### 예제

```python
# 텍스트 쓰기
fs.write("file.txt", "Hello World")

# 바이너리 쓰기 (파일 업로드)
file = wiz.request.file("avatar")
fs.write("avatar.png", file.read(), mode="wb")

# 덮어쓰기
fs.write("log.txt", "New log entry")
```

---

## JSON 처리

### read.json()

JSON 파일을 읽습니다.

#### 구문
```python
fs.read.json(filename, default={})
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `filename` | str | ✅ | - | 파일명 |
| `default` | any | ❌ | {} | 파일이 없거나 JSON 파싱 실패 시 반환할 값 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `dict`/`list` or `any` | JSON 데이터 또는 기본값 |

#### 예제

```python
# JSON 읽기
config = fs.read.json("config.json")
print(config)  # {"key": "value"}

# 기본값 지정
config = fs.read.json("config.json", {"theme": "light"})

# 리스트 JSON
users = fs.read.json("users.json", [])
```

---

### write.json()

JSON 파일에 씁니다.

#### 구문
```python
fs.write.json(filename, data)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `filename` | str | ✅ | - | 파일명 |
| `data` | dict/list | ✅ | - | JSON으로 저장할 데이터 |

#### 예제

```python
# 딕셔너리 저장
config = {"theme": "dark", "language": "ko"}
fs.write.json("config.json", config)

# 리스트 저장
users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
fs.write.json("users.json", users)
```

---

## 파일/디렉토리 확인

### exists()

파일 또는 디렉토리 존재 여부를 확인합니다.

#### 구문
```python
fs.exists(path)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `path` | str | ✅ | - | 경로 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `bool` | 존재하면 True, 아니면 False |

#### 예제

```python
if fs.exists("config.json"):
    config = fs.read.json("config.json")

if not fs.exists("uploads"):
    fs.makedirs("uploads")
```

---

### isdir()

디렉토리인지 확인합니다.

#### 구문
```python
fs.isdir(path)
```

#### 반환값

| 타입 | 설명 |
|------|------|
| `bool` | 디렉토리면 True, 아니면 False |

#### 예제

```python
if fs.isdir("uploads"):
    print("uploads is a directory")
```

---

## 파일 목록

### files()

파일 목록을 반환합니다.

#### 구문
```python
fs.files(path="")
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `path` | str | ❌ | "" | 하위 경로 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `list` | 파일명 리스트 (디렉토리 제외) |

#### 예제

```python
# 현재 디렉토리의 파일
files = fs.files()
print(files)  # ["file1.txt", "file2.json"]

# 하위 디렉토리의 파일
files = fs.files("uploads")

# 모든 파일 처리
for filename in fs.files():
    content = fs.read(filename)
    print(f"{filename}: {len(content)} bytes")
```

---

### ls()

파일과 디렉토리 목록을 반환합니다.

#### 구문
```python
fs.ls(path="")
```

#### 반환값

| 타입 | 설명 |
|------|------|
| `list` | 파일명 및 디렉토리명 리스트 |

#### 예제

```python
items = fs.ls()
print(items)  # ["file.txt", "subdir", "data.json"]
```

---

## 디렉토리 관리

### makedirs()

디렉토리를 생성합니다 (중간 디렉토리 포함).

#### 구문
```python
fs.makedirs(path)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `path` | str | ✅ | - | 디렉토리 경로 |

#### 예제

```python
# 디렉토리 생성
fs.makedirs("uploads/images")
fs.makedirs("data/cache/temp")

# 존재 확인 후 생성
if not fs.exists("logs"):
    fs.makedirs("logs")
```

---

## 파일/디렉토리 삭제

### delete()

파일 또는 디렉토리를 삭제합니다.

#### 구문
```python
fs.delete(path)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `path` | str | ✅ | - | 삭제할 경로 |

#### 예제

```python
# 파일 삭제
fs.delete("temp.txt")

# 디렉토리 삭제 (하위 항목 포함)
fs.delete("temp_folder")

# 존재 확인 후 삭제
if fs.exists("old_data.json"):
    fs.delete("old_data.json")
```

---

## 파일 복사/이동

### copy()

파일 또는 디렉토리를 복사합니다.

#### 구문
```python
fs.copy(src, dst)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `src` | str | ✅ | - | 원본 경로 |
| `dst` | str | ✅ | - | 대상 경로 |

#### 예제

```python
# 파일 복사
fs.copy("file.txt", "file_backup.txt")

# 디렉토리 복사
fs.copy("source_dir", "backup_dir")
```

---

### move()

파일 또는 디렉토리를 이동합니다.

#### 구문
```python
fs.move(src, dst)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `src` | str | ✅ | - | 원본 경로 |
| `dst` | str | ✅ | - | 대상 경로 |

#### 예제

```python
# 파일 이동
fs.move("old.txt", "new.txt")

# 디렉토리 이동
fs.move("old_folder", "new_folder")
```

---

## 파일 정보

### size()

파일 크기를 반환합니다.

#### 구문
```python
fs.size(filename)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `filename` | str | ✅ | - | 파일명 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `int` | 파일 크기 (바이트) |

#### 예제

```python
size = fs.size("file.txt")
print(f"{size} bytes")

# 파일 목록과 크기
for filename in fs.files():
    size = fs.size(filename)
    print(f"{filename}: {size} bytes")
```

---

### abspath()

절대 경로를 반환합니다.

#### 구문
```python
fs.abspath(path="")
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `path` | str | ❌ | "" | 상대 경로 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `str` | 절대 경로 |

#### 예제

```python
# 현재 디렉토리 절대 경로
path = fs.abspath()
print(path)  # "/path/to/project/data"

# 파일 절대 경로
filepath = fs.abspath("file.txt")
print(filepath)  # "/path/to/project/data/file.txt"

# 다운로드에 사용
filepath = fs.abspath("report.pdf")
wiz.response.download(filepath)
```

---

## 전체 예제

### 파일 업로드 관리

```python
# app/page.upload/api.py

def upload():
    """파일 업로드"""
    fs = wiz.project.fs("data", "uploads")
    
    # uploads 디렉토리 생성
    if not fs.exists(""):
        fs.makedirs("")
    
    files = wiz.request.files()
    uploaded = []
    
    for file in files:
        filename = file.filename
        
        # 파일 저장
        fs.write(filename, file.read(), mode="wb")
        
        uploaded.append({
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
    
    if not fs.exists(""):
        wiz.response.status(200, [])
        return
    
    files = []
    for filename in fs.files():
        files.append({
            "name": filename,
            "size": fs.size(filename)
        })
    
    wiz.response.status(200, files)

def delete_file():
    """파일 삭제"""
    filename = wiz.request.query("filename")
    fs = wiz.project.fs("data", "uploads")
    
    if fs.exists(filename):
        fs.delete(filename)
        wiz.response.status(200, {"message": "Deleted"})
    else:
        wiz.response.status(404, {"error": "File not found"})
```

### 설정 파일 관리

```python
# model/config.py

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.fs = wiz.project.fs("config")
    
    def load(self, name="app"):
        """설정 로드"""
        filename = f"{name}.json"
        return self.fs.read.json(filename, {})
    
    def save(self, name, data):
        """설정 저장"""
        filename = f"{name}.json"
        self.fs.write.json(filename, data)
    
    def delete(self, name):
        """설정 삭제"""
        filename = f"{name}.json"
        if self.fs.exists(filename):
            self.fs.delete(filename)
```

### 로그 파일 관리

```python
# model/logger.py

import datetime

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.fs = wiz.project.fs("logs")
        
        # logs 디렉토리 생성
        if not self.fs.exists(""):
            self.fs.makedirs("")
    
    def log(self, level, message):
        """로그 작성"""
        today = datetime.date.today().strftime("%Y-%m-%d")
        filename = f"{today}.log"
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        # 기존 내용 읽기
        content = self.fs.read(filename, "")
        
        # 새 로그 추가
        content += log_entry
        
        # 저장
        self.fs.write(filename, content)
    
    def get_logs(self, date=None):
        """로그 조회"""
        if date is None:
            date = datetime.date.today().strftime("%Y-%m-%d")
        
        filename = f"{date}.log"
        return self.fs.read(filename, "")
```

---

## 참고

- [wiz.project API](wiz-project.md)
- [wiz 객체 API](wiz-object.md)
- [전체 API 목록](README.md)
