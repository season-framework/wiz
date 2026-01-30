# wiz.session API

API for session management. Stores and manages user-specific data on the server side.

## Overview

- **Access**: `wiz.session`
- **Usage Location**: `api.py`, `controller.py`, `socket.py`, `model/*.py`
- **Backend**: Flask session-based

---

## Methods

### wiz.session.set()

Sets a value in the session.

#### Syntax
```python
wiz.session.set(key, value)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `key` | str | ✅ | - | Session key |
| `value` | any | ✅ | - | Value to store (JSON-serializable type) |

#### Examples

```python
# Simple values
wiz.session.set("user_id", 123)
wiz.session.set("username", "Alice")
wiz.session.set("is_admin", True)

# Dictionary
wiz.session.set("user", {
    "id": 123,
    "name": "Alice",
    "email": "alice@example.com"
})

# List
wiz.session.set("cart", [1, 2, 3, 4, 5])
```

---

### wiz.session.get()

Gets a value from the session.

#### Syntax
```python
wiz.session.get(key, default=None)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `key` | str | ✅ | - | Session key |
| `default` | any | ❌ | None | Default value when key doesn't exist |

#### Return Value

| Type | Description |
|------|-------------|
| `any` | Session value or default value |

#### Examples

```python
# Get value
user_id = wiz.session.get("user_id")
print(user_id)  # 123 or None

# Set default value
username = wiz.session.get("username", "Guest")
print(username)  # "Alice" or "Guest"

# Dictionary
user = wiz.session.get("user", {})

# List
cart = wiz.session.get("cart", [])
```

---

### wiz.session.delete()

Deletes a specific key from the session.

#### Syntax
```python
wiz.session.delete(key)
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `key` | str | ✅ | - | Session key to delete |

#### Examples

```python
# Delete specific key
wiz.session.delete("user_id")
wiz.session.delete("cart")
```

---

### wiz.session.clear()

Deletes all sessions.

#### Syntax
```python
wiz.session.clear()
```

#### Parameters

None

#### Examples

```python
# On logout
def logout():
    wiz.session.clear()
    wiz.response.redirect("/login")
```

---

## Usage Examples

### Login/Logout

```python
# api.py

def login():
    """Login"""
    data = wiz.request.query()
    email = data.get("email")
    password = data.get("password")
    
    # User authentication
    user_model = wiz.model("user").use()
    user = user_model.authenticate(email, password)
    
    if user:
        # Set session
        wiz.session.set("user_id", user['id'])
        wiz.session.set("user_email", user['email'])
        wiz.session.set("is_admin", user.get('is_admin', False))
        
        wiz.response.status(200, {
            "message": "Login successful",
            "user": user
        })
    else:
        wiz.response.status(401, {"error": "Invalid credentials"})

def logout():
    """Logout"""
    wiz.session.clear()
    wiz.response.status(200, {"message": "Logged out"})

def check_session():
    """Check session"""
    user_id = wiz.session.get("user_id")
    
    if user_id:
        user_model = wiz.model("user").use()
        user = user_model.get(user_id)
        
        wiz.response.status(200, {
            "logged_in": True,
            "user": user
        })
    else:
        wiz.response.status(200, {"logged_in": False})
```

---

### Shopping Cart

```python
# api.py

def add_to_cart():
    """Add to cart"""
    product_id = wiz.request.query("product_id")
    
    # Get current cart
    cart = wiz.session.get("cart", [])
    
    # Add product
    if product_id not in cart:
        cart.append(product_id)
        wiz.session.set("cart", cart)
    
    wiz.response.status(200, {
        "cart": cart,
        "count": len(cart)
    })

def remove_from_cart():
    """Remove from cart"""
    product_id = wiz.request.query("product_id")
    
    cart = wiz.session.get("cart", [])
    
    if product_id in cart:
        cart.remove(product_id)
        wiz.session.set("cart", cart)
    
    wiz.response.status(200, {"cart": cart})

def get_cart():
    """Get cart"""
    cart = wiz.session.get("cart", [])
    
    # Get product information
    product_model = wiz.model("product").use()
    products = []
    
    for product_id in cart:
        product = product_model.get(product_id)
        if product:
            products.append(product)
    
    wiz.response.status(200, products)

def clear_cart():
    """Clear cart"""
    wiz.session.delete("cart")
    wiz.response.status(200, {"message": "Cart cleared"})
```

---

### Multi-step Form

```python
# api.py

def save_step1():
    """Save step 1"""
    data = wiz.request.query()
    
    # Save step 1 data in session
    wiz.session.set("registration_step1", {
        "name": data.get("name"),
        "email": data.get("email")
    })
    
    wiz.response.status(200, {"message": "Step 1 saved"})

def save_step2():
    """Save step 2"""
    data = wiz.request.query()
    
    # Save step 2 data in session
    wiz.session.set("registration_step2", {
        "phone": data.get("phone"),
        "address": data.get("address")
    })
    
    wiz.response.status(200, {"message": "Step 2 saved"})

def complete_registration():
    """Complete registration"""
    # Get all step data
    step1 = wiz.session.get("registration_step1", {})
    step2 = wiz.session.get("registration_step2", {})
    
    # Merge data
    user_data = {**step1, **step2}
    
    # Create user
    user_model = wiz.model("user").use()
    user_id = user_model.create(user_data)
    
    # Clean up session
    wiz.session.delete("registration_step1")
    wiz.session.delete("registration_step2")
    
    # Set login session
    wiz.session.set("user_id", user_id)
    
    wiz.response.status(201, {"id": user_id})
```

---

### User Preferences

```python
# api.py

def update_preferences():
    """Update preferences"""
    data = wiz.request.query()
    
    # Get current preferences
    prefs = wiz.session.get("preferences", {})
    
    # Update
    prefs.update({
        "theme": data.get("theme", "light"),
        "language": data.get("language", "ko"),
        "notifications": data.get("notifications", True)
    })
    
    # Save
    wiz.session.set("preferences", prefs)
    
    wiz.response.status(200, prefs)

def get_preferences():
    """Get preferences"""
    prefs = wiz.session.get("preferences", {
        "theme": "light",
        "language": "ko",
        "notifications": True
    })
    
    wiz.response.status(200, prefs)
```

---

### Controller Authentication

```python
# controller/base.py

class Controller:
    def __init__(self):
        # Check user ID from session
        user_id = wiz.session.get("user_id")
        
        # List of protected pages
        protected_pages = ["/dashboard", "/admin", "/profile"]
        current_uri = wiz.request.uri()
        
        # Check if authentication required
        requires_auth = any(current_uri.startswith(page) for page in protected_pages)
        
        if requires_auth and not user_id:
            # Redirect to login page
            wiz.session.set("redirect_after_login", current_uri)
            wiz.response.redirect("/login")
        
        # Check admin page
        if current_uri.startswith("/admin"):
            is_admin = wiz.session.get("is_admin", False)
            if not is_admin:
                wiz.response.abort(403)
        
        # Load user information
        if user_id:
            user_model = wiz.model("user").use()
            user = user_model.get(user_id)
            wiz.response.data.set(current_user=user)
```

---

### Flash Messages

```python
# api.py

def set_flash_message(message, type="info"):
    """Set flash message"""
    wiz.session.set("flash_message", {
        "message": message,
        "type": type  # info, success, warning, error
    })

def get_flash_message():
    """Get flash message (once only)"""
    flash = wiz.session.get("flash_message")
    if flash:
        wiz.session.delete("flash_message")
    return flash

# Usage example
def create_user():
    data = wiz.request.query()
    user_model = wiz.model("user").use()
    user_id = user_model.create(data)
    
    # Set flash message
    set_flash_message("User created successfully", "success")
    
    wiz.response.redirect("/users")
```

---

## Security Considerations

### 1. Avoid Storing Sensitive Information

```python
# ❌ Bad example
wiz.session.set("password", password)  # Never store passwords

# ✅ Good example
wiz.session.set("user_id", user_id)
```

### 2. Session Timeout

```python
# config/boot.py
import datetime

# Set session timeout (e.g., 30 minutes)
app.permanent_session_lifetime = datetime.timedelta(minutes=30)
```

### 3. Session Regeneration (on login)

```python
def login():
    # Regenerate session after successful login
    old_session = dict(wiz.session.get())
    wiz.session.clear()
    
    # Set user information in new session
    wiz.session.set("user_id", user_id)
```

---

## References

- [wiz.request API](wiz-request.md)
- [wiz.response API](wiz-response.md)
- [wiz Object API](wiz-object.md)
- [Full API List](README.md)
