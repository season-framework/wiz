# Service API (TypeScript)

Angular 컴포넌트에서 사용하는 Service 클래스 API입니다.

## 클래스 정보

- **클래스**: `Service`
- **임포트**: `import { Service } from '@wiz/libs/portal/season/service';`
- **사용 위치**: Angular 컴포넌트 (view.ts)

---

## 초기화

### Constructor

Service 객체를 생성자에서 주입받습니다.

#### 구문
```typescript
constructor(public service: Service) { }
```

#### 예제

```typescript
import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    async ngOnInit() {
        await this.service.init();
        await this.service.render();
    }
}
```

---

### service.init()

Service를 초기화합니다. `ngOnInit`에서 가장 먼저 호출해야 합니다.

#### 구문
```typescript
await this.service.init()
```

#### 파라미터

없음

#### 반환값

| 타입 | 설명 |
|------|------|
| `Promise<void>` | 초기화 완료를 나타내는 Promise |

#### 예제

```typescript
async ngOnInit() {
    await this.service.init();
    // 초기화 이후 작업
    await this.loadData();
    await this.service.render();
}
```

---

### service.render()

컴포넌트를 다시 렌더링합니다.

#### 구문
```typescript
await this.service.render()
```

#### 파라미터

없음

#### 반환값

| 타입 | 설명 |
|------|------|
| `Promise<void>` | 렌더링 완료를 나타내는 Promise |

#### 예제

```typescript
// 데이터 변경 후 렌더링
async updateData() {
    this.data = newData;
    await this.service.render();
}

// 리스트 추가 후 렌더링
async addItem() {
    this.items.push(newItem);
    await this.service.render();
}
```

---

## API 통신

### service.api.call()

백엔드 API 함수를 호출합니다.

#### 구문
```typescript
service.api.call(functionName, data?)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `functionName` | string | ✅ | - | 호출할 API 함수 이름 (api.py의 함수명) |
| `data` | object/FormData | ❌ | undefined | 전송할 데이터 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `Promise<ApiResponse>` | API 응답 객체 |

#### 응답 형식

```typescript
interface ApiResponse {
    code: number;    // HTTP 상태 코드
    data: any;       // 응답 데이터
}
```

#### 예제

```typescript
// GET 요청 (데이터 없음)
async loadUsers() {
    let res = await this.service.api.call("get_users");
    if (res.code === 200) {
        this.users = res.data;
        await this.service.render();
    }
}

// POST 요청 (데이터 전송)
async createUser() {
    let data = {
        name: "Alice",
        email: "alice@example.com"
    };
    
    let res = await this.service.api.call("create_user", data);
    if (res.code === 201) {
        await this.service.alert.success("사용자 생성 완료");
        await this.loadUsers();
    }
}

// 파일 업로드
async uploadFile(event: any) {
    let files = event.target.files;
    let formData = new FormData();
    
    for (let i = 0; i < files.length; i++) {
        formData.append("file" + i, files[i]);
    }
    
    let res = await this.service.api.call("upload", formData);
    if (res.code === 200) {
        await this.service.alert.success(res.data.message);
    }
}

// 에러 처리
async saveData() {
    try {
        let res = await this.service.api.call("save", this.formData);
        if (res.code === 200) {
            await this.service.alert.success("저장 완료");
        } else {
            await this.service.alert.error(res.data.error);
        }
    } catch (e) {
        await this.service.alert.error("네트워크 에러");
    }
}
```

---

## WebSocket 통신

### service.socket.emit()

WebSocket 이벤트를 서버로 전송합니다.

#### 구문
```typescript
service.socket.emit(eventName, data?)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `eventName` | string | ✅ | - | 이벤트 이름 (socket.py의 함수명) |
| `data` | object | ❌ | undefined | 전송할 데이터 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `Promise<any>` | 서버 응답 |

#### 예제

```typescript
// 메시지 전송
async sendMessage() {
    let data = {
        username: this.username,
        message: this.message
    };
    
    await this.service.socket.emit("chat_message", data);
    this.message = "";
    await this.service.render();
}

// 타이핑 상태 전송
async onTyping() {
    await this.service.socket.emit("typing", {
        username: this.username,
        typing: true
    });
}
```

---

### service.socket.on()

WebSocket 이벤트를 구독합니다.

#### 구문
```typescript
service.socket.on(eventName, callback)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `eventName` | string | ✅ | - | 이벤트 이름 |
| `callback` | function | ✅ | - | 이벤트 핸들러 함수 |

#### 예제

```typescript
async ngOnInit() {
    await this.service.init();
    
    // 메시지 수신 구독
    this.service.socket.on("message", (data) => {
        this.messages.push(data);
        this.service.render();
    });
    
    // 연결 상태 구독
    this.service.socket.on("connect", () => {
        console.log("Connected to server");
    });
    
    this.service.socket.on("disconnect", () => {
        console.log("Disconnected from server");
    });
    
    await this.service.render();
}
```

---

### service.socket.off()

WebSocket 이벤트 구독을 해제합니다.

#### 구문
```typescript
service.socket.off(eventName)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `eventName` | string | ✅ | - | 이벤트 이름 |

#### 예제

```typescript
ngOnDestroy() {
    // 컴포넌트 파괴 시 구독 해제
    this.service.socket.off("message");
    this.service.socket.off("connect");
}
```

---

## 알림 및 대화상자

### service.alert.show()

정보 알림을 표시합니다.

#### 구문
```typescript
service.alert.show(message, options?)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `message` | string | ✅ | - | 표시할 메시지 |
| `options` | object | ❌ | {} | 알림 옵션 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `Promise<void>` | 알림 닫기를 기다리는 Promise |

#### 예제

```typescript
await this.service.alert.show("정보 메시지");
```

---

### service.alert.success()

성공 알림을 표시합니다.

#### 구문
```typescript
service.alert.success(message)
```

#### 예제

```typescript
await this.service.alert.success("저장 완료!");
await this.service.alert.success("파일 업로드 성공");
```

---

### service.alert.error()

에러 알림을 표시합니다.

#### 구문
```typescript
service.alert.error(message)
```

#### 예제

```typescript
await this.service.alert.error("저장 실패");
await this.service.alert.error("네트워크 에러가 발생했습니다");
```

---

### service.alert.warning()

경고 알림을 표시합니다.

#### 구문
```typescript
service.alert.warning(message)
```

#### 예제

```typescript
await this.service.alert.warning("변경 사항이 저장되지 않았습니다");
```

---

### service.alert.confirm()

확인 대화상자를 표시합니다.

#### 구문
```typescript
service.alert.confirm(message)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `message` | string | ✅ | - | 확인 메시지 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `Promise<boolean>` | 확인: true, 취소: false |

#### 예제

```typescript
async deleteUser(userId: number) {
    let confirmed = await this.service.alert.confirm("정말 삭제하시겠습니까?");
    
    if (confirmed) {
        let res = await this.service.api.call("delete_user", { id: userId });
        if (res.code === 200) {
            await this.service.alert.success("삭제 완료");
            await this.loadUsers();
        }
    }
}

// 복잡한 확인 로직
async saveChanges() {
    if (this.hasChanges) {
        let confirmed = await this.service.alert.confirm(
            "변경 사항이 있습니다. 저장하시겠습니까?"
        );
        
        if (confirmed) {
            await this.save();
        }
    }
}
```

---

## 로딩 인디케이터

### service.loading.show()

로딩 인디케이터를 표시합니다.

#### 구문
```typescript
service.loading.show()
```

#### 예제

```typescript
this.service.loading.show();
```

---

### service.loading.hide()

로딩 인디케이터를 숨깁니다.

#### 구문
```typescript
service.loading.hide()
```

#### 예제

```typescript
this.service.loading.hide();
```

---

### 로딩 사용 패턴

```typescript
async loadData() {
    this.service.loading.show();
    
    try {
        let res = await this.service.api.call("get_data");
        this.data = res.data;
        await this.service.render();
    } catch (e) {
        await this.service.alert.error("로드 실패");
    } finally {
        this.service.loading.hide();
    }
}

// 여러 API 호출
async loadAll() {
    this.service.loading.show();
    
    try {
        let [users, posts, comments] = await Promise.all([
            this.service.api.call("get_users"),
            this.service.api.call("get_posts"),
            this.service.api.call("get_comments")
        ]);
        
        this.users = users.data;
        this.posts = posts.data;
        this.comments = comments.data;
        
        await this.service.render();
    } finally {
        this.service.loading.hide();
    }
}
```

---

## 라우팅

### service.href()

URL로 이동합니다.

#### 구문
```typescript
service.href(url, newTab?)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `url` | string | ✅ | - | 이동할 URL |
| `newTab` | boolean | ❌ | false | 새 탭에서 열기 여부 |

#### 예제

```typescript
// 페이지 이동
goToDashboard() {
    this.service.href("/dashboard");
}

// 외부 URL
openExternal() {
    this.service.href("https://example.com");
}

// 새 탭에서 열기
openInNewTab() {
    this.service.href("/report", true);
}

// 동적 URL
viewUser(userId: number) {
    this.service.href(`/users/${userId}`);
}
```

---

## 전체 예제

### CRUD 애플리케이션

```typescript
import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public users: any[] = [];
    public selectedUser: any = null;
    public formData = { name: "", email: "" };

    async ngOnInit() {
        await this.service.init();
        await this.loadUsers();
        await this.service.render();
    }

    // 조회 (Read)
    async loadUsers() {
        this.service.loading.show();
        
        try {
            let res = await this.service.api.call("get_users");
            if (res.code === 200) {
                this.users = res.data;
                await this.service.render();
            }
        } catch (e) {
            await this.service.alert.error("데이터 로드 실패");
        } finally {
            this.service.loading.hide();
        }
    }

    // 생성 (Create)
    async createUser() {
        if (!this.formData.name || !this.formData.email) {
            await this.service.alert.warning("모든 필드를 입력해주세요");
            return;
        }

        this.service.loading.show();
        
        try {
            let res = await this.service.api.call("create_user", this.formData);
            if (res.code === 201) {
                await this.service.alert.success("사용자 생성 완료");
                this.formData = { name: "", email: "" };
                await this.loadUsers();
            } else {
                await this.service.alert.error(res.data.error);
            }
        } catch (e) {
            await this.service.alert.error("생성 실패");
        } finally {
            this.service.loading.hide();
        }
    }

    // 수정 (Update)
    async updateUser() {
        if (!this.selectedUser) return;

        this.service.loading.show();
        
        try {
            let res = await this.service.api.call("update_user", this.selectedUser);
            if (res.code === 200) {
                await this.service.alert.success("수정 완료");
                this.selectedUser = null;
                await this.loadUsers();
            }
        } catch (e) {
            await this.service.alert.error("수정 실패");
        } finally {
            this.service.loading.hide();
        }
    }

    // 삭제 (Delete)
    async deleteUser(userId: number) {
        let confirmed = await this.service.alert.confirm("정말 삭제하시겠습니까?");
        if (!confirmed) return;

        this.service.loading.show();
        
        try {
            let res = await this.service.api.call("delete_user", { id: userId });
            if (res.code === 200) {
                await this.service.alert.success("삭제 완료");
                await this.loadUsers();
            }
        } catch (e) {
            await this.service.alert.error("삭제 실패");
        } finally {
            this.service.loading.hide();
        }
    }

    // 선택
    selectUser(user: any) {
        this.selectedUser = { ...user };
        this.service.render();
    }
}
```

### 실시간 채팅

```typescript
import { OnInit, OnDestroy } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit, OnDestroy {
    constructor(public service: Service) { }

    public messages: any[] = [];
    public username: string = "User";
    public message: string = "";

    async ngOnInit() {
        await this.service.init();
        
        // 소켓 이벤트 구독
        this.service.socket.on("connect", () => {
            console.log("Connected");
        });

        this.service.socket.on("message", (data) => {
            if (data.type === "chat") {
                this.messages.push(data);
                this.service.render();
                this.scrollToBottom();
            }
        });

        await this.service.render();
    }

    ngOnDestroy() {
        // 구독 해제
        this.service.socket.off("message");
        this.service.socket.off("connect");
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

    scrollToBottom() {
        // 채팅 스크롤을 맨 아래로
        setTimeout(() => {
            let chatBox = document.querySelector('.chat-messages');
            if (chatBox) {
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        }, 100);
    }
}
```

---

## 참고

- [wiz.request API](wiz-request.md)
- [wiz.response API](wiz-response.md)
- [전체 API 목록](README.md)
