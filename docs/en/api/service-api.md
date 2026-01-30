# Service API (TypeScript)

Service class API used in Angular components.

## Class Information

- **Class**: `Service`
- **Import**: `import { Service } from '@wiz/libs/portal/season/service';`
- **Usage Location**: Angular components (view.ts)

---

## Initialization

### Constructor

Inject the Service object in the constructor.

#### Syntax
```typescript
constructor(public service: Service) { }
```

#### Examples

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

Initializes the Service. Must be called first in `ngOnInit`.

#### Syntax
```typescript
await this.service.init()
```

#### Parameters

None

#### Return Value

| Type | Description |
|------|-------------|
| `Promise<void>` | Promise indicating initialization completion |

#### Examples

```typescript
async ngOnInit() {
    await this.service.init();
    // Work after initialization
    await this.loadData();
    await this.service.render();
}
```

---

### service.render()

Re-renders the component.

#### Syntax
```typescript
await this.service.render()
```

#### Parameters

None

#### Return Value

| Type | Description |
|------|-------------|
| `Promise<void>` | Promise indicating rendering completion |

#### Examples

```typescript
// Render after data change
async updateData() {
    this.data = newData;
    await this.service.render();
}

// Render after list addition
async addItem() {
    this.items.push(newItem);
    await this.service.render();
}
```

---

## API Communication

### service.api.call()

Calls a backend API function.

#### Syntax
```typescript
service.api.call(functionName, data?)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `functionName` | string | ✅ | - | API function name to call (function name in api.py) |
| `data` | object/FormData | ❌ | undefined | Data to send |

#### Return Value

| Type | Description |
|------|-------------|
| `Promise<ApiResponse>` | API response object |

#### Response Format

```typescript
interface ApiResponse {
    code: number;    // HTTP status code
    data: any;       // Response data
}
```

#### Examples

```typescript
// GET request (no data)
async loadUsers() {
    let res = await this.service.api.call("get_users");
    if (res.code === 200) {
        this.users = res.data;
        await this.service.render();
    }
}

// POST request (send data)
async createUser() {
    let data = {
        name: "Alice",
        email: "alice@example.com"
    };
    
    let res = await this.service.api.call("create_user", data);
    if (res.code === 201) {
        await this.service.alert.success("User created");
        await this.loadUsers();
    }
}

// File upload
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

// Error handling
async saveData() {
    try {
        let res = await this.service.api.call("save", this.formData);
        if (res.code === 200) {
            await this.service.alert.success("Saved");
        } else {
            await this.service.alert.error(res.data.error);
        }
    } catch (e) {
        await this.service.alert.error("Network error");
    }
}
```

---

## WebSocket Communication

### service.socket.emit()

Sends a WebSocket event to the server.

#### Syntax
```typescript
service.socket.emit(eventName, data?)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `eventName` | string | ✅ | - | Event name (function name in socket.py) |
| `data` | object | ❌ | undefined | Data to send |

#### Return Value

| Type | Description |
|------|-------------|
| `Promise<any>` | Server response |

#### Examples

```typescript
// Send message
async sendMessage() {
    let data = {
        username: this.username,
        message: this.message
    };
    
    await this.service.socket.emit("chat_message", data);
    this.message = "";
    await this.service.render();
}

// Send typing status
async onTyping() {
    await this.service.socket.emit("typing", {
        username: this.username,
        typing: true
    });
}
```

---

### service.socket.on()

Subscribes to a WebSocket event.

#### Syntax
```typescript
service.socket.on(eventName, callback)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `eventName` | string | ✅ | - | Event name |
| `callback` | function | ✅ | - | Event handler function |

#### Examples

```typescript
async ngOnInit() {
    await this.service.init();
    
    // Subscribe to message reception
    this.service.socket.on("message", (data) => {
        this.messages.push(data);
        this.service.render();
    });
    
    // Subscribe to connection status
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

Unsubscribes from a WebSocket event.

#### Syntax
```typescript
service.socket.off(eventName)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `eventName` | string | ✅ | - | Event name |

#### Examples

```typescript
ngOnDestroy() {
    // Unsubscribe on component destruction
    this.service.socket.off("message");
    this.service.socket.off("connect");
}
```

---

## Alerts and Dialogs

### service.alert.show()

Displays an information alert.

#### Syntax
```typescript
service.alert.show(message, options?)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `message` | string | ✅ | - | Message to display |
| `options` | object | ❌ | {} | Alert options |

#### Return Value

| Type | Description |
|------|-------------|
| `Promise<void>` | Promise waiting for alert to close |

#### Examples

```typescript
await this.service.alert.show("Information message");
```

---

### service.alert.success()

Displays a success alert.

#### Syntax
```typescript
service.alert.success(message)
```

#### Examples

```typescript
await this.service.alert.success("Saved successfully!");
await this.service.alert.success("File upload successful");
```

---

### service.alert.error()

Displays an error alert.

#### Syntax
```typescript
service.alert.error(message)
```

#### Examples

```typescript
await this.service.alert.error("Save failed");
await this.service.alert.error("A network error occurred");
```

---

### service.alert.warning()

Displays a warning alert.

#### Syntax
```typescript
service.alert.warning(message)
```

#### Examples

```typescript
await this.service.alert.warning("Changes have not been saved");
```

---

### service.alert.confirm()

Displays a confirmation dialog.

#### Syntax
```typescript
service.alert.confirm(message)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `message` | string | ✅ | - | Confirmation message |

#### Return Value

| Type | Description |
|------|-------------|
| `Promise<boolean>` | Confirm: true, Cancel: false |

#### Examples

```typescript
async deleteUser(userId: number) {
    let confirmed = await this.service.alert.confirm("Are you sure you want to delete?");
    
    if (confirmed) {
        let res = await this.service.api.call("delete_user", { id: userId });
        if (res.code === 200) {
            await this.service.alert.success("Deleted");
            await this.loadUsers();
        }
    }
}

// Complex confirmation logic
async saveChanges() {
    if (this.hasChanges) {
        let confirmed = await this.service.alert.confirm(
            "There are unsaved changes. Do you want to save?"
        );
        
        if (confirmed) {
            await this.save();
        }
    }
}
```

---

## Loading Indicator

### service.loading.show()

Displays a loading indicator.

#### Syntax
```typescript
service.loading.show()
```

#### Examples

```typescript
this.service.loading.show();
```

---

### service.loading.hide()

Hides the loading indicator.

#### Syntax
```typescript
service.loading.hide()
```

#### Examples

```typescript
this.service.loading.hide();
```

---

### Loading Usage Pattern

```typescript
async loadData() {
    this.service.loading.show();
    
    try {
        let res = await this.service.api.call("get_data");
        this.data = res.data;
        await this.service.render();
    } catch (e) {
        await this.service.alert.error("Load failed");
    } finally {
        this.service.loading.hide();
    }
}

// Multiple API calls
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

## Routing

### service.href()

Navigates to a URL.

#### Syntax
```typescript
service.href(url, newTab?)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | ✅ | - | URL to navigate to |
| `newTab` | boolean | ❌ | false | Whether to open in new tab |

#### Examples

```typescript
// Page navigation
goToDashboard() {
    this.service.href("/dashboard");
}

// External URL
openExternal() {
    this.service.href("https://example.com");
}

// Open in new tab
openInNewTab() {
    this.service.href("/report", true);
}

// Dynamic URL
viewUser(userId: number) {
    this.service.href(`/users/${userId}`);
}
```

---

## Complete Examples

### CRUD Application

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

    // Read
    async loadUsers() {
        this.service.loading.show();
        
        try {
            let res = await this.service.api.call("get_users");
            if (res.code === 200) {
                this.users = res.data;
                await this.service.render();
            }
        } catch (e) {
            await this.service.alert.error("Data load failed");
        } finally {
            this.service.loading.hide();
        }
    }

    // Create
    async createUser() {
        if (!this.formData.name || !this.formData.email) {
            await this.service.alert.warning("Please fill in all fields");
            return;
        }

        this.service.loading.show();
        
        try {
            let res = await this.service.api.call("create_user", this.formData);
            if (res.code === 201) {
                await this.service.alert.success("User created");
                this.formData = { name: "", email: "" };
                await this.loadUsers();
            } else {
                await this.service.alert.error(res.data.error);
            }
        } catch (e) {
            await this.service.alert.error("Creation failed");
        } finally {
            this.service.loading.hide();
        }
    }

    // Update
    async updateUser() {
        if (!this.selectedUser) return;

        this.service.loading.show();
        
        try {
            let res = await this.service.api.call("update_user", this.selectedUser);
            if (res.code === 200) {
                await this.service.alert.success("Updated");
                this.selectedUser = null;
                await this.loadUsers();
            }
        } catch (e) {
            await this.service.alert.error("Update failed");
        } finally {
            this.service.loading.hide();
        }
    }

    // Delete
    async deleteUser(userId: number) {
        let confirmed = await this.service.alert.confirm("Are you sure you want to delete?");
        if (!confirmed) return;

        this.service.loading.show();
        
        try {
            let res = await this.service.api.call("delete_user", { id: userId });
            if (res.code === 200) {
                await this.service.alert.success("Deleted");
                await this.loadUsers();
            }
        } catch (e) {
            await this.service.alert.error("Deletion failed");
        } finally {
            this.service.loading.hide();
        }
    }

    // Select
    selectUser(user: any) {
        this.selectedUser = { ...user };
        this.service.render();
    }
}
```

### Real-time Chat

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
        
        // Subscribe to socket events
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
        // Unsubscribe
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
        // Scroll chat to bottom
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

## References

- [wiz.request API](wiz-request.md)
- [wiz.response API](wiz-response.md)
- [Full API List](README.md)
