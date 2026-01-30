# WIZ Framework Examples Collection

Learn the various features of the WIZ framework through practical examples.

## Table of Contents

1. [Basic Page Creation](#1-basic-page-creation)
2. [API Communication](#2-api-communication)
3. [File Upload/Download](#3-file-uploaddownload)
4. [WebSocket Real-time Communication](#4-websocket-real-time-communication)
5. [Database Integration](#5-database-integration)
6. [Session Management](#6-session-management)
7. [RESTful API](#7-restful-api)
8. [Image Processing](#8-image-processing)
9. [CSV/Excel File Processing](#9-csvexcel-file-processing)
10. [Authentication System](#10-authentication-system)

---

## 1. Basic Page Creation

### Directory Structure
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

## 2. API Communication

### Backend (api.py)
```python
def get_data():
    """Handle GET request"""
    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ],
        "total": 2
    }
    wiz.response.status(200, data)

def save_data():
    """Handle POST request"""
    # Get request data
    data = wiz.request.query()
    name = data.get("name", "")
    email = data.get("email", "")
    
    # Validation
    if not name or not email:
        wiz.response.status(400, {
            "error": "Name and email are required"
        })
        return
    
    # Save data (example)
    user_id = 123  # Actually save to DB
    
    wiz.response.status(200, {
        "id": user_id,
        "name": name,
        "email": email
    })
```

### Frontend (view.ts)
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
            await this.service.alert.error("Failed to load data");
        }
    }

    async saveData() {
        try {
            let res = await this.service.api.call("save_data", this.newUser);
            if (res.code === 200) {
                await this.service.alert.success("Saved successfully");
                await this.loadData();
                this.newUser = { name: "", email: "" };
                await this.service.render();
            }
        } catch (e) {
            await this.service.alert.error("Failed to save");
        }
    }
}
```

### Template (view.pug)
```pug
.api-example
    .form-group
        input.form-control(
            [(ngModel)]="newUser.name",
            placeholder="Name"
        )
        input.form-control(
            [(ngModel)]="newUser.email",
            placeholder="Email"
        )
        button.btn.btn-primary((click)="saveData()") Save
    
    .user-list
        .user-item(*ngFor="let user of users")
            | {{ user.name }} ({{ user.email }})
```

---

## 3. File Upload/Download

### Backend (api.py)
```python
def upload():
    """File upload"""
    files = wiz.request.files()
    
    if len(files) == 0:
        wiz.response.status(400, {"error": "No file uploaded"})
        return
    
    uploaded_files = []
    fs = wiz.project.fs("data", "uploads")
    
    for key in files:
        file = files[key]
        filename = file.filename
        
        # Save file
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
    """File download"""
    filename = wiz.request.query("filename")
    
    fs = wiz.project.fs("data", "uploads")
    
    if not fs.exists(filename):
        wiz.response.status(404, {"error": "File not found"})
        return
    
    filepath = fs.abspath(filename)
    wiz.response.download(filepath, as_attachment=True)

def list_files():
    """File list"""
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

### Frontend (view.ts)
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
            await this.service.alert.error("Upload failed");
        } finally {
            this.service.loading.hide();
        }
    }

    async downloadFile(filename: string) {
        window.open(`/api/page.files/download?filename=${filename}`, '_blank');
    }
}
```

### Template (view.pug)
```pug
.file-manager
    .upload-section
        h3 File Upload
        input(
            type="file",
            multiple,
            (change)="onFileSelect($event)"
        )
    
    .file-list
        h3 File List
        table.table
            thead
                tr
                    th Filename
                    th Size
                    th Actions
            tbody
                tr(*ngFor="let file of files")
                    td {{ file.name }}
                    td {{ file.size }} bytes
                    td
                        button.btn.btn-sm.btn-primary(
                            (click)="downloadFile(file.name)"
                        ) Download
```

---

## 4. WebSocket Real-time Communication

### Backend (socket.py)
```python
import time

def connect():
    """Client connection"""
    print("Client connected")
    wiz.response.send({
        "type": "welcome",
        "message": "Connected to server"
    })

def disconnect():
    """Client disconnection"""
    print("Client disconnected")

def chat_message(data):
    """Receive chat message"""
    username = data.get("username", "Anonymous")
    message = data.get("message", "")
    timestamp = time.time()
    
    # Broadcast to all clients
    wiz.response.send({
        "type": "chat",
        "username": username,
        "message": message,
        "timestamp": timestamp
    })

def typing(data):
    """Typing status"""
    username = data.get("username", "Anonymous")
    is_typing = data.get("typing", False)
    
    wiz.response.send({
        "type": "typing",
        "username": username,
        "typing": is_typing
    })
```

### Frontend (view.ts)
```typescript
export class Component implements OnInit {
    constructor(public service: Service) { }

    public messages: any[] = [];
    public username: string = "User";
    public message: string = "";
    public typingUsers: string[] = [];

    async ngOnInit() {
        await this.service.init();
        
        // Socket event listeners
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

### Template (view.pug)
```pug
.chat-container
    .chat-header
        h3 Real-time Chat
        input.form-control(
            [(ngModel)]="username",
            placeholder="Username"
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
            placeholder="Enter message..."
        )
        button.btn.btn-primary((click)="sendMessage()") Send
```

---

## 5. Database Integration

### Model (model/database.py)
```python
import sqlite3
import season

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.db_path = wiz.project.path("data", "database.db")
        self.init_db()
    
    def init_db(self):
        """Initialize database"""
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
        """Execute SQL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id
    
    def query(self, query, params=()):
        """SELECT query"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    def query_one(self, query, params=()):
        """Query single result"""
        results = self.query(query, params)
        return results[0] if results else None
```

### API (api.py)
```python
def get_users():
    """User list"""
    db = wiz.model("database").use()
    users = db.query("SELECT * FROM users ORDER BY created_at DESC")
    wiz.response.status(200, users)

def get_user():
    """User details"""
    user_id = wiz.request.query("id")
    db = wiz.model("database").use()
    user = db.query_one("SELECT * FROM users WHERE id = ?", [user_id])
    
    if user:
        wiz.response.status(200, user)
    else:
        wiz.response.status(404, {"error": "User not found"})

def create_user():
    """Create user"""
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
    """Update user"""
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
    """Delete user"""
    user_id = wiz.request.query("id")
    db = wiz.model("database").use()
    
    db.execute("DELETE FROM users WHERE id = ?", [user_id])
    wiz.response.status(200, {"result": "success"})
```

---

## 6. Session Management

### Login (api.py)
```python
import bcrypt

def login():
    """Login"""
    data = wiz.request.query()
    email = data.get("email")
    password = data.get("password")
    
    # Query user
    db = wiz.model("database").use()
    user = db.query_one("SELECT * FROM users WHERE email = ?", [email])
    
    if not user:
        wiz.response.status(401, {"error": "Invalid credentials"})
        return
    
    # Verify password (actually compare hash)
    # if not bcrypt.checkpw(password.encode(), user['password'].encode()):
    #     wiz.response.status(401, {"error": "Invalid credentials"})
    #     return
    
    # Set session
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
    """Logout"""
    wiz.session.clear()
    wiz.response.status(200, {"message": "Logout successful"})

def check_session():
    """Check session"""
    user_id = wiz.session.get("user_id")
    
    if user_id:
        db = wiz.model("database").use()
        user = db.query_one("SELECT id, email FROM users WHERE id = ?", [user_id])
        wiz.response.status(200, {"logged_in": True, "user": user})
    else:
        wiz.response.status(200, {"logged_in": False})
```

### Controller Authentication (controller/base.py)
```python
import season

class Controller:
    def __init__(self):
        # Check session
        user_id = wiz.session.get("user_id")
        
        # Pages requiring login
        protected_pages = ["/dashboard", "/profile", "/settings"]
        current_uri = wiz.request.uri()
        
        if any(current_uri.startswith(page) for page in protected_pages):
            if not user_id:
                # Redirect to login page
                wiz.response.redirect("/login")
        
        # Pass user info to template
        if user_id:
            db = wiz.model("database").use()
            user = db.query_one("SELECT * FROM users WHERE id = ?", [user_id])
            wiz.response.data.set(current_user=user)
```

---

## 7. RESTful API

### Route (route/api/controller.py)
```python
import season

# URL matching
segment = wiz.request.match("/api/<resource>/<path:path>")
resource = segment.resource
path = segment.path

# HTTP method
method = wiz.request.request().method

# Database model
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

## 8. Image Processing

### API (api.py)
```python
from PIL import Image
from io import BytesIO
import base64

def resize_image():
    """Resize image"""
    files = wiz.request.files()
    width = int(wiz.request.query("width", 800))
    height = int(wiz.request.query("height", 600))
    
    if len(files) == 0:
        wiz.response.status(400, {"error": "No image uploaded"})
        return
    
    file = list(files.values())[0]
    img = Image.open(file)
    
    # Resize
    img = img.resize((width, height), Image.LANCZOS)
    
    # Save
    fs = wiz.project.fs("data", "images")
    output_path = fs.abspath("resized.png")
    img.save(output_path)
    
    wiz.response.status(200, {
        "message": "Image resized",
        "size": [width, height]
    })

def thumbnail():
    """Generate thumbnail"""
    filename = wiz.request.query("filename")
    size = int(wiz.request.query("size", 150))
    
    fs = wiz.project.fs("data", "images")
    
    if not fs.exists(filename):
        wiz.response.abort(404)
    
    img = Image.open(fs.abspath(filename))
    img.thumbnail((size, size), Image.LANCZOS)
    
    # Send PIL image as response
    wiz.response.PIL(img, type="PNG")

def convert_format():
    """Convert image format"""
    files = wiz.request.files()
    output_format = wiz.request.query("format", "PNG")  # PNG, JPEG, GIF
    
    file = list(files.values())[0]
    img = Image.open(file)
    
    # Convert to RGB (JPEG doesn't support RGBA)
    if output_format == "JPEG" and img.mode == "RGBA":
        img = img.convert("RGB")
    
    buffer = BytesIO()
    img.save(buffer, format=output_format)
    buffer.seek(0)
    
    wiz.response.PIL(Image.open(buffer), type=output_format)
```

---

## 9. CSV/Excel File Processing

### API (api.py)
```python
import csv
import json
from io import StringIO

def import_csv():
    """Import CSV file"""
    files = wiz.request.files()
    
    if len(files) == 0:
        wiz.response.status(400, {"error": "No file uploaded"})
        return
    
    file = list(files.values())[0]
    content = file.read().decode('utf-8')
    
    # Parse CSV
    csv_reader = csv.DictReader(StringIO(content))
    data = list(csv_reader)
    
    # Save to database
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
    """Export CSV file"""
    db = wiz.model("database").use()
    users = db.query("SELECT * FROM users")
    
    # Generate CSV
    output = StringIO()
    if len(users) > 0:
        fieldnames = users[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)
    
    # Save to file
    fs = wiz.project.fs("data", "exports")
    csv_content = output.getvalue()
    fs.write("users.csv", csv_content)
    
    # Download
    filepath = fs.abspath("users.csv")
    wiz.response.download(filepath, as_attachment=True)
```

---

## 10. Authentication System

### Model (model/auth.py)
```python
import bcrypt
import uuid

class Model:
    def __init__(self, wiz):
        self.wiz = wiz
        self.db = wiz.model("database").use()
    
    def register(self, email, password, name):
        """Register"""
        # Hash password
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        # Create user
        try:
            user_id = self.db.execute(
                "INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
                [email, hashed.decode(), name]
            )
            return user_id
        except:
            return None
    
    def login(self, email, password):
        """Login"""
        user = self.db.query_one(
            "SELECT * FROM users WHERE email = ?",
            [email]
        )
        
        if not user:
            return None
        
        # Verify password
        if bcrypt.checkpw(password.encode(), user['password'].encode()):
            return user
        
        return None
    
    def create_token(self, user_id):
        """Create authentication token"""
        token = str(uuid.uuid4())
        
        self.db.execute(
            "INSERT INTO tokens (user_id, token) VALUES (?, ?)",
            [user_id, token]
        )
        
        return token
    
    def verify_token(self, token):
        """Verify token"""
        result = self.db.query_one(
            "SELECT user_id FROM tokens WHERE token = ?",
            [token]
        )
        
        return result['user_id'] if result else None
```

These examples can help you utilize various features of the WIZ framework.
