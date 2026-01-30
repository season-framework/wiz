# wiz.session API

세션 관리 API입니다. 사용자별 데이터를 서버 측에 저장하고 관리합니다.

## 개요

- **접근**: `wiz.session`
- **사용 위치**: `api.py`, `controller.py`, `socket.py`, `model/*.py`
- **백엔드**: Flask 세션 기반

---

## 메서드

### wiz.session.set()

세션에 값을 설정합니다.

#### 구문
```python
wiz.session.set(key, value)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `key` | str | ✅ | - | 세션 키 |
| `value` | any | ✅ | - | 저장할 값 (JSON 직렬화 가능한 타입) |

#### 예제

```python
# 간단한 값
wiz.session.set("user_id", 123)
wiz.session.set("username", "Alice")
wiz.session.set("is_admin", True)

# 딕셔너리
wiz.session.set("user", {
    "id": 123,
    "name": "Alice",
    "email": "alice@example.com"
})

# 리스트
wiz.session.set("cart", [1, 2, 3, 4, 5])
```

---

### wiz.session.get()

세션에서 값을 가져옵니다.

#### 구문
```python
wiz.session.get(key, default=None)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `key` | str | ✅ | - | 세션 키 |
| `default` | any | ❌ | None | 키가 없을 때 반환할 기본값 |

#### 반환값

| 타입 | 설명 |
|------|------|
| `any` | 세션 값 또는 기본값 |

#### 예제

```python
# 값 가져오기
user_id = wiz.session.get("user_id")
print(user_id)  # 123 또는 None

# 기본값 지정
username = wiz.session.get("username", "Guest")
print(username)  # "Alice" 또는 "Guest"

# 딕셔너리
user = wiz.session.get("user", {})

# 리스트
cart = wiz.session.get("cart", [])
```

---

### wiz.session.delete()

세션에서 특정 키를 삭제합니다.

#### 구문
```python
wiz.session.delete(key)
```

#### 파라미터

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `key` | str | ✅ | - | 삭제할 세션 키 |

#### 예제

```python
# 특정 키 삭제
wiz.session.delete("user_id")
wiz.session.delete("cart")
```

---

### wiz.session.clear()

모든 세션을 삭제합니다.

#### 구문
```python
wiz.session.clear()
```

#### 파라미터

없음

#### 예제

```python
# 로그아웃 시
def logout():
    wiz.session.clear()
    wiz.response.redirect("/login")
```

---

## 사용 예제

### 로그인/로그아웃

```python
# api.py

def login():
    """로그인"""
    data = wiz.request.query()
    email = data.get("email")
    password = data.get("password")
    
    # 사용자 인증
    user_model = wiz.model("user").use()
    user = user_model.authenticate(email, password)
    
    if user:
        # 세션 설정
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
    """로그아웃"""
    wiz.session.clear()
    wiz.response.status(200, {"message": "Logged out"})

def check_session():
    """세션 확인"""
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

### 장바구니

```python
# api.py

def add_to_cart():
    """장바구니에 추가"""
    product_id = wiz.request.query("product_id")
    
    # 현재 장바구니 가져오기
    cart = wiz.session.get("cart", [])
    
    # 제품 추가
    if product_id not in cart:
        cart.append(product_id)
        wiz.session.set("cart", cart)
    
    wiz.response.status(200, {
        "cart": cart,
        "count": len(cart)
    })

def remove_from_cart():
    """장바구니에서 제거"""
    product_id = wiz.request.query("product_id")
    
    cart = wiz.session.get("cart", [])
    
    if product_id in cart:
        cart.remove(product_id)
        wiz.session.set("cart", cart)
    
    wiz.response.status(200, {"cart": cart})

def get_cart():
    """장바구니 조회"""
    cart = wiz.session.get("cart", [])
    
    # 제품 정보 가져오기
    product_model = wiz.model("product").use()
    products = []
    
    for product_id in cart:
        product = product_model.get(product_id)
        if product:
            products.append(product)
    
    wiz.response.status(200, products)

def clear_cart():
    """장바구니 비우기"""
    wiz.session.delete("cart")
    wiz.response.status(200, {"message": "Cart cleared"})
```

---

### 다단계 폼

```python
# api.py

def save_step1():
    """1단계 저장"""
    data = wiz.request.query()
    
    # 세션에 1단계 데이터 저장
    wiz.session.set("registration_step1", {
        "name": data.get("name"),
        "email": data.get("email")
    })
    
    wiz.response.status(200, {"message": "Step 1 saved"})

def save_step2():
    """2단계 저장"""
    data = wiz.request.query()
    
    # 세션에 2단계 데이터 저장
    wiz.session.set("registration_step2", {
        "phone": data.get("phone"),
        "address": data.get("address")
    })
    
    wiz.response.status(200, {"message": "Step 2 saved"})

def complete_registration():
    """등록 완료"""
    # 모든 단계 데이터 가져오기
    step1 = wiz.session.get("registration_step1", {})
    step2 = wiz.session.get("registration_step2", {})
    
    # 데이터 병합
    user_data = {**step1, **step2}
    
    # 사용자 생성
    user_model = wiz.model("user").use()
    user_id = user_model.create(user_data)
    
    # 세션 정리
    wiz.session.delete("registration_step1")
    wiz.session.delete("registration_step2")
    
    # 로그인 세션 설정
    wiz.session.set("user_id", user_id)
    
    wiz.response.status(201, {"id": user_id})
```

---

### 사용자 환경 설정

```python
# api.py

def update_preferences():
    """환경 설정 업데이트"""
    data = wiz.request.query()
    
    # 현재 설정 가져오기
    prefs = wiz.session.get("preferences", {})
    
    # 업데이트
    prefs.update({
        "theme": data.get("theme", "light"),
        "language": data.get("language", "ko"),
        "notifications": data.get("notifications", True)
    })
    
    # 저장
    wiz.session.set("preferences", prefs)
    
    wiz.response.status(200, prefs)

def get_preferences():
    """환경 설정 조회"""
    prefs = wiz.session.get("preferences", {
        "theme": "light",
        "language": "ko",
        "notifications": True
    })
    
    wiz.response.status(200, prefs)
```

---

### 컨트롤러 인증

```python
# controller/base.py

class Controller:
    def __init__(self):
        # 세션에서 사용자 ID 확인
        user_id = wiz.session.get("user_id")
        
        # 보호된 페이지 목록
        protected_pages = ["/dashboard", "/admin", "/profile"]
        current_uri = wiz.request.uri()
        
        # 인증 필요 확인
        requires_auth = any(current_uri.startswith(page) for page in protected_pages)
        
        if requires_auth and not user_id:
            # 로그인 페이지로 리다이렉트
            wiz.session.set("redirect_after_login", current_uri)
            wiz.response.redirect("/login")
        
        # 관리자 페이지 확인
        if current_uri.startswith("/admin"):
            is_admin = wiz.session.get("is_admin", False)
            if not is_admin:
                wiz.response.abort(403)
        
        # 사용자 정보 로드
        if user_id:
            user_model = wiz.model("user").use()
            user = user_model.get(user_id)
            wiz.response.data.set(current_user=user)
```

---

### 임시 메시지 (Flash Message)

```python
# api.py

def set_flash_message(message, type="info"):
    """Flash 메시지 설정"""
    wiz.session.set("flash_message", {
        "message": message,
        "type": type  # info, success, warning, error
    })

def get_flash_message():
    """Flash 메시지 가져오기 (한 번만)"""
    flash = wiz.session.get("flash_message")
    if flash:
        wiz.session.delete("flash_message")
    return flash

# 사용 예시
def create_user():
    data = wiz.request.query()
    user_model = wiz.model("user").use()
    user_id = user_model.create(data)
    
    # Flash 메시지 설정
    set_flash_message("사용자가 생성되었습니다", "success")
    
    wiz.response.redirect("/users")
```

---

## 보안 고려사항

### 1. 민감한 정보 저장 피하기

```python
# ❌ 나쁜 예
wiz.session.set("password", password)  # 비밀번호 저장 금지

# ✅ 좋은 예
wiz.session.set("user_id", user_id)
```

### 2. 세션 타임아웃

```python
# config/boot.py
import datetime

# 세션 타임아웃 설정 (예: 30분)
app.permanent_session_lifetime = datetime.timedelta(minutes=30)
```

### 3. 세션 재생성 (로그인 시)

```python
def login():
    # 로그인 성공 후 세션 재생성
    old_session = dict(wiz.session.get())
    wiz.session.clear()
    
    # 새 세션에 사용자 정보 설정
    wiz.session.set("user_id", user_id)
```

---

## 참고

- [wiz.request API](wiz-request.md)
- [wiz.response API](wiz-response.md)
- [wiz 객체 API](wiz-object.md)
- [전체 API 목록](README.md)
