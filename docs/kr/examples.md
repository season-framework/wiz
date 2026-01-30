# WIZ Framework 예제 모음

실제 사용 예제를 통해 WIZ 프레임워크의 다양한 기능을 학습할 수 있습니다.

## 목차

1. [기본 페이지 생성](#1-기본-페이지-생성)
2. [API 통신](#2-api-통신)
3. [파일 업로드/다운로드](#3-파일-업로드다운로드)
4. [WebSocket 실시간 통신](#4-websocket-실시간-통신)
5. [데이터베이스 연동](#5-데이터베이스-연동)
6. [세션 관리](#6-세션-관리)
7. [RESTful API](#7-restful-api)
8. [이미지 처리](#8-이미지-처리)
9. [CSV/Excel 파일 처리](#9-csvexcel-파일-처리)
10. [인증 시스템](#10-인증-시스템)

---

## 1. 기본 페이지 생성

### 디렉토리 구조
```
src/app/page.hello/
├── app.json
├── view.pug
├── view.ts
└── view.scss
```

### app.json
```json
{
    "title": "Hello Page",
    "mode": "page",
    "namespace": "main",
    "id": "page.hello",
    "viewuri": "/hello",
    "layout": "layout.empty",
    "ng": {
        "selector": "wiz-page-hello"
    }
}
```

### view.ts
```typescript
import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public message: string = "Hello, WIZ!";

    async ngOnInit() {
        await this.service.init();
        await this.service.render();
    }
}
```

### view.pug
```pug
.container
    h1 {{ message }}
    p Welcome to WIZ Framework
```

### view.scss
```scss
.container {
    padding: 20px;
    text-align: center;
    
    h1 {
        color: #007bff;
        font-size: 2.5rem;
    }
}
```

---

## 2. API 통신

### 백엔드 (api.py)
```python
def get_data():
    """GET 요청 처리"""
    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ],
        "total": 2
    }
    wiz.response.status(200, data)

def save_data():
    """POST 요청 처리"""
    # 요청 데이터 가져오기
    data = wiz.request.query()
    name = data.get("name", "")
    email = data.get("email", "")
    
    # 유효성 검사
    if not name or not email:
        wiz.response.status(400, {
            "error": "Name and email are required"
        })
        return
    
    # 데이터 저장 (예시)
    user_id = 123  # 실제로는 DB에 저장
    
    wiz.response.status(200, {
        "id": user_id,
        "name": name,
        "email": email
    })
```

### 프론트엔드 (view.ts)
```typescript
export class Component implements OnInit {
    constructor(public service: Service) { }

    public users: any[] = [];
    public newUser = { name: "", email: "" };

    async ngOnInit() {
        await this.service.init();
        await this.loadData();
        await this.service.render();
    }

    async loadData() {
        try {
            let res = await this.service.api.call("get_data");
            if (res.code === 200) {
                this.users = res.data.users;
            }
        } catch (e) {
            await this.service.alert.error("데이터 로드 실패");
        }
    }

    async saveData() {
        try {
            let res = await this.service.api.call("save_data", this.newUser);
            if (res.code === 200) {
                await this.service.alert.success("저장 완료");
                await this.loadData();
                this.newUser = { name: "", email: "" };
                await this.service.render();
            }
        } catch (e) {
            await this.service.alert.error("저장 실패");
        }
    }
}
```

### 템플릿 (view.pug)
```pug
.api-example
    .form-group
        input.form-control(
            [(ngModel)]="newUser.name",
            placeholder="이름"
        )
        input.form-control(
            [(ngModel)]="newUser.email",
            placeholder="이메일"
        )
        button.btn.btn-primary((click)="saveData()") 저장
    
    .user-list
        .user-item(*ngFor="let user of users")
            | {{ user.name }} ({{ user.email }})
```

---

## 3. 파일 업로드/다운로드

### 백엔드 (api.py)
```python
def upload():
    """파일 업로드"""
    files = wiz.request.files()
    
    if len(files) == 0:
        wiz.response.status(400, {"error": "No file uploaded"})
        return
    
    uploaded_files = []
    fs = wiz.project.fs("data", "uploads")
    
    for key in files:
        file = files[key]
        filename = file.filename
        
        # 파일 저장
        fs.write(filename, file.read(), mode="wb")
        uploaded_files.append({
            "name": filename,
            "size": fs.size(filename)
        })
    
    wiz.response.status(200, {
        "files": uploaded_files,
        "message": f"{len(uploaded_files)} file(s) uploaded"
    })

def download():
    """파일 다운로드"""
    filename = wiz.request.query("filename")
    
    fs = wiz.project.fs("data", "uploads")
    
    if not fs.exists(filename):
        wiz.response.status(404, {"error": "File not found"})
        return
    
    filepath = fs.abspath(filename)
    wiz.response.download(filepath, as_attachment=True)

def list_files():
    """파일 목록"""
    fs = wiz.project.fs("data", "uploads")
    files = fs.files()
    
    file_list = []
    for filename in files:
        file_list.append({
            "name": filename,
            "size": fs.size(filename)
        })
    
    wiz.response.status(200, file_list)
```

### 프론트엔드 (view.ts)
```typescript
export class Component implements OnInit {
    constructor(public service: Service) { }

    public files: any[] = [];

    async ngOnInit() {
        await this.service.init();
        await this.loadFiles();
        await this.service.render();
    }

    async loadFiles() {
        let res = await this.service.api.call("list_files");
        this.files = res.data;
    }

    async onFileSelect(event: any) {
        let files = event.target.files;
        if (files.length === 0) return;

        this.service.loading.show();
        
        let formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append("file" + i, files[i]);
        }

        try {
            let res = await this.service.api.call("upload", formData);
            await this.service.alert.success(res.data.message);
            await this.loadFiles();
            await this.service.render();
        } catch (e) {
            await this.service.alert.error("업로드 실패");
        } finally {
            this.service.loading.hide();
        }
    }

    async downloadFile(filename: string) {
        window.open(`/api/page.files/download?filename=${filename}`, '_blank');
    }
}
```

### 템플릿 (view.pug)
```pug
.file-manager
    .upload-section
        h3 파일 업로드
        input(
            type="file",
            multiple,
            (change)="onFileSelect($event)"
        )
    
    .file-list
        h3 파일 목록
        table.table
            thead
                tr
                    th 파일명
                    th 크기
                    th 작업
            tbody
                tr(*ngFor="let file of files")
                    td {{ file.name }}
                    td {{ file.size }} bytes
                    td
                        button.btn.btn-sm.btn-primary(
                            (click)="downloadFile(file.name)"
                        ) 다운로드
```

---

## 4. WebSocket 실시간 통신

### 백엔드 (socket.py)
```python
import time

def connect():
    """클라이언트 연결"""
    print("Client connected")
    wiz.response.send({
        "type": "welcome",
        "message": "Connected to server"
    })

def disconnect():
    """클라이언트 연결 해제"""
    print("Client disconnected")

def chat_message(data):
    """채팅 메시지 수신"""
    username = data.get("username", "Anonymous")
    message = data.get("message", "")
    timestamp = time.time()
    
    # 모든 클라이언트에게 브로드캐스트
    wiz.response.send({
        "type": "chat",
        "username": username,
        "message": message,
        "timestamp": timestamp
    })

def typing(data):
    """타이핑 상태"""
    username = data.get("username", "Anonymous")
    is_typing = data.get("typing", False)
    
    wiz.response.send({
        "type": "typing",
        "username": username,
        "typing": is_typing
    })
```

### 프론트엔드 (view.ts)
```typescript
export class Component implements OnInit {
    constructor(public service: Service) { }

    public messages: any[] = [];
    public username: string = "User";
    public message: string = "";
    public typingUsers: string[] = [];

    async ngOnInit() {
        await this.service.init();
        
        // 소켓 이벤트 리스너
        this.service.socket.on("connect", () => {
            console.log("Connected to server");
        });

        this.service.socket.on("message", (data) => {
            if (data.type === "welcome") {
                console.log(data.message);
            } else if (data.type === "chat") {
                this.messages.push(data);
                this.service.render();
            } else if (data.type === "typing") {
                this.updateTypingStatus(data);
            }
        });

        await this.service.render();
    }

    async sendMessage() {
        if (!this.message.trim()) return;

        await this.service.socket.emit("chat_message", {
            username: this.username,
            message: this.message
        });

        this.message = "";
        await this.service.render();
    }

    async onTyping() {
        await this.service.socket.emit("typing", {
            username: this.username,
            typing: true
        });
    }

    updateTypingStatus(data: any) {
        if (data.username === this.username) return;

        if (data.typing) {
            if (!this.typingUsers.includes(data.username)) {
                this.typingUsers.push(data.username);
            }
        } else {
            this.typingUsers = this.typingUsers.filter(u => u !== data.username);
        }
        this.service.render();
    }
}
```

### 템플릿 (view.pug)
```pug
.chat-container
    .chat-header
        h3 실시간 채팅
        input.form-control(
            [(ngModel)]="username",
            placeholder="사용자명"
        )
    
    .chat-messages
        .message(*ngFor="let msg of messages")
            strong {{ msg.username }}:
            span {{ msg.message }}
    
    .typing-indicator(*ngIf="typingUsers.length > 0")
        | {{ typingUsers.join(', ') }} typing...
    
    .chat-input
        input.form-control(
            [(ngModel)]="message",
            (keyup)="onTyping()",
            (keyup.enter)="sendMessage()",
            placeholder="메시지 입력..."
        )
        button.btn.btn-primary((click)="sendMessage()") 전송
```

---

## 5. 데이터베이스 연동

### 모델 (model/database.py)
```python
import sqlite3
import season

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.db_path = wiz.project.path("data", "database.db")
        self.init_db()
    
    def init_db(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute(self, query, params=()):
        """SQL 실행"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id
    
    def query(self, query, params=()):
        """SELECT 쿼리"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def query_one(self, query, params=()):
        """단일 결과 조회"""
        results = self.query(query, params)
        return results[0] if results else None
```

### API (api.py)
```python
def get_users():
    """사용자 목록"""
    db = wiz.model("database").use()
    users = db.query("SELECT * FROM users ORDER BY created_at DESC")
    wiz.response.status(200, users)

def get_user():
    """사용자 상세"""
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
    
    db = wiz.model("database").use()
    
    try:
        user_id = db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            [name, email]
        )
        wiz.response.status(201, {"id": user_id})
    except Exception as e:
        wiz.response.status(400, {"error": str(e)})

def update_user():
    """사용자 수정"""
    data = wiz.request.query()
    user_id = data.get("id")
    name = data.get("name")
    email = data.get("email")
    
    db = wiz.model("database").use()
    
    try:
        db.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            [name, email, user_id]
        )
        wiz.response.status(200, {"result": "success"})
    except Exception as e:
        wiz.response.status(400, {"error": str(e)})

def delete_user():
    """사용자 삭제"""
    user_id = wiz.request.query("id")
    db = wiz.model("database").use()
    
    db.execute("DELETE FROM users WHERE id = ?", [user_id])
    wiz.response.status(200, {"result": "success"})
```

---

## 6. 세션 관리

### 로그인 (api.py)
```python
import bcrypt

def login():
    """로그인"""
    data = wiz.request.query()
    email = data.get("email")
    password = data.get("password")
    
    # 사용자 조회
    db = wiz.model("database").use()
    user = db.query_one("SELECT * FROM users WHERE email = ?", [email])
    
    if not user:
        wiz.response.status(401, {"error": "Invalid credentials"})
        return
    
    # 비밀번호 확인 (실제로는 해시 비교)
    # if not bcrypt.checkpw(password.encode(), user['password'].encode()):
    #     wiz.response.status(401, {"error": "Invalid credentials"})
    #     return
    
    # 세션 설정
    wiz.session.set("user_id", user['id'])
    wiz.session.set("user_email", user['email'])
    
    wiz.response.status(200, {
        "message": "Login successful",
        "user": {
            "id": user['id'],
            "email": user['email']
        }
    })

def logout():
    """로그아웃"""
    wiz.session.clear()
    wiz.response.status(200, {"message": "Logout successful"})

def check_session():
    """세션 확인"""
    user_id = wiz.session.get("user_id")
    
    if user_id:
        db = wiz.model("database").use()
        user = db.query_one("SELECT id, email FROM users WHERE id = ?", [user_id])
        wiz.response.status(200, {"logged_in": True, "user": user})
    else:
        wiz.response.status(200, {"logged_in": False})
```

### 컨트롤러 인증 (controller/base.py)
```python
import season

class Controller:
    def __init__(self):
        # 세션 확인
        user_id = wiz.session.get("user_id")
        
        # 로그인 필요한 페이지
        protected_pages = ["/dashboard", "/profile", "/settings"]
        current_uri = wiz.request.uri()
        
        if any(current_uri.startswith(page) for page in protected_pages):
            if not user_id:
                # 로그인 페이지로 리다이렉트
                wiz.response.redirect("/login")
        
        # 사용자 정보를 템플릿에 전달
        if user_id:
            db = wiz.model("database").use()
            user = db.query_one("SELECT * FROM users WHERE id = ?", [user_id])
            wiz.response.data.set(current_user=user)
```

---

## 7. RESTful API

### 라우트 (route/api/controller.py)
```python
import season

# URL 매칭
segment = wiz.request.match("/api/<resource>/<path:path>")
resource = segment.resource
path = segment.path

# HTTP 메서드
method = wiz.request.request().method

# 데이터베이스 모델
db = wiz.model("database").use()

if resource == "users":
    if method == "GET":
        if path:
            # GET /api/users/123
            user_id = path
            user = db.query_one("SELECT * FROM users WHERE id = ?", [user_id])
            if user:
                wiz.response.status(200, user)
            else:
                wiz.response.status(404, {"error": "User not found"})
        else:
            # GET /api/users
            users = db.query("SELECT * FROM users")
            wiz.response.status(200, users)
    
    elif method == "POST":
        # POST /api/users
        data = wiz.request.query()
        user_id = db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            [data.get("name"), data.get("email")]
        )
        wiz.response.status(201, {"id": user_id})
    
    elif method == "PUT":
        # PUT /api/users/123
        user_id = path
        data = wiz.request.query()
        db.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            [data.get("name"), data.get("email"), user_id]
        )
        wiz.response.status(200, {"result": "success"})
    
    elif method == "DELETE":
        # DELETE /api/users/123
        user_id = path
        db.execute("DELETE FROM users WHERE id = ?", [user_id])
        wiz.response.status(204)

wiz.response.abort(404)
```

---

## 8. 이미지 처리

### API (api.py)
```python
from PIL import Image
from io import BytesIO
import base64

def resize_image():
    """이미지 리사이즈"""
    files = wiz.request.files()
    width = int(wiz.request.query("width", 800))
    height = int(wiz.request.query("height", 600))
    
    if len(files) == 0:
        wiz.response.status(400, {"error": "No image uploaded"})
        return
    
    file = list(files.values())[0]
    img = Image.open(file)
    
    # 리사이즈
    img = img.resize((width, height), Image.LANCZOS)
    
    # 저장
    fs = wiz.project.fs("data", "images")
    output_path = fs.abspath("resized.png")
    img.save(output_path)
    
    wiz.response.status(200, {
        "message": "Image resized",
        "size": [width, height]
    })

def thumbnail():
    """썸네일 생성"""
    filename = wiz.request.query("filename")
    size = int(wiz.request.query("size", 150))
    
    fs = wiz.project.fs("data", "images")
    
    if not fs.exists(filename):
        wiz.response.abort(404)
    
    img = Image.open(fs.abspath(filename))
    img.thumbnail((size, size), Image.LANCZOS)
    
    # PIL 이미지를 응답으로 전송
    wiz.response.PIL(img, type="PNG")

def convert_format():
    """이미지 포맷 변환"""
    files = wiz.request.files()
    output_format = wiz.request.query("format", "PNG")  # PNG, JPEG, GIF
    
    file = list(files.values())[0]
    img = Image.open(file)
    
    # RGB 변환 (JPEG는 RGBA 지원 안함)
    if output_format == "JPEG" and img.mode == "RGBA":
        img = img.convert("RGB")
    
    buffer = BytesIO()
    img.save(buffer, format=output_format)
    buffer.seek(0)
    
    wiz.response.PIL(Image.open(buffer), type=output_format)
```

---

## 9. CSV/Excel 파일 처리

### API (api.py)
```python
import csv
import json
from io import StringIO

def import_csv():
    """CSV 파일 임포트"""
    files = wiz.request.files()
    
    if len(files) == 0:
        wiz.response.status(400, {"error": "No file uploaded"})
        return
    
    file = list(files.values())[0]
    content = file.read().decode('utf-8')
    
    # CSV 파싱
    csv_reader = csv.DictReader(StringIO(content))
    data = list(csv_reader)
    
    # 데이터베이스에 저장
    db = wiz.model("database").use()
    count = 0
    
    for row in data:
        db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            [row.get("name"), row.get("email")]
        )
        count += 1
    
    wiz.response.status(200, {
        "message": f"{count} records imported",
        "data": data
    })

def export_csv():
    """CSV 파일 익스포트"""
    db = wiz.model("database").use()
    users = db.query("SELECT * FROM users")
    
    # CSV 생성
    output = StringIO()
    if len(users) > 0:
        fieldnames = users[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)
    
    # 파일로 저장
    fs = wiz.project.fs("data", "exports")
    csv_content = output.getvalue()
    fs.write("users.csv", csv_content)
    
    # 다운로드
    filepath = fs.abspath("users.csv")
    wiz.response.download(filepath, as_attachment=True)
```

---

## 10. 인증 시스템

### 모델 (model/auth.py)
```python
import bcrypt
import uuid

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.db = wiz.model("database").use()
    
    def register(self, email, password, name):
        """회원가입"""
        # 비밀번호 해시
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        # 사용자 생성
        try:
            user_id = self.db.execute(
                "INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
                [email, hashed.decode(), name]
            )
            return user_id
        except:
            return None
    
    def login(self, email, password):
        """로그인"""
        user = self.db.query_one(
            "SELECT * FROM users WHERE email = ?",
            [email]
        )
        
        if not user:
            return None
        
        # 비밀번호 확인
        if bcrypt.checkpw(password.encode(), user['password'].encode()):
            return user
        
        return None
    
    def create_token(self, user_id):
        """인증 토큰 생성"""
        token = str(uuid.uuid4())
        
        self.db.execute(
            "INSERT INTO tokens (user_id, token) VALUES (?, ?)",
            [user_id, token]
        )
        
        return token
    
    def verify_token(self, token):
        """토큰 검증"""
        result = self.db.query_one(
            "SELECT user_id FROM tokens WHERE token = ?",
            [token]
        )
        
        return result['user_id'] if result else None
```

이러한 예제들을 참고하여 WIZ 프레임워크의 다양한 기능을 활용할 수 있습니다.
