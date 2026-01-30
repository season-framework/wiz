# WIZ Framework Architecture

## 개요

WIZ는 Python Flask 기반의 풀스택 웹 개발 프레임워크로, Angular를 쉽게 사용할 수 있도록 설계되었습니다. 백엔드와 프론트엔드를 통합하여 관리하며, 플러그인 기반 아키텍처를 통해 확장 가능한 IDE 환경을 제공합니다.

## 핵심 구성 요소

### 1. 프레임워크 구조 (season 패키지)

```
season/
├── __init__.py          # 패키지 초기화 및 주요 API 노출
├── cmd.py               # CLI 명령어 엔트리포인트
├── version.py           # 버전 정보
├── command/             # CLI 명령어 구현
│   ├── bundle.py        # 번들링 관련 명령어
│   ├── create.py        # 프로젝트 생성
│   ├── daemon.py        # 서버 실행 및 데몬 관리
│   ├── ide.py           # IDE 관련 명령어
│   └── service.py       # 시스템 서비스 관리
├── lib/                 # 핵심 라이브러리
│   ├── server.py        # 서버 클래스 (Flask + SocketIO)
│   ├── core.py          # Wiz 핵심 기능
│   ├── binding/         # HTTP 및 소켓 바인딩
│   ├── static/          # 정적 리소스 관리
│   └── ...
├── util/                # 유틸리티 함수
│   ├── cache.py
│   ├── compiler.py
│   ├── filesystem.py
│   ├── logger.py
│   └── string.py
└── data/                # 템플릿 데이터
    ├── ide/             # IDE 소스코드
    ├── plugin/          # 플러그인 템플릿
    ├── sample/          # 샘플 프로젝트
    └── websrc/          # 웹 소스 템플릿
```

### 2. 서버 아키텍처

#### Server 클래스 (`season.lib.server.Server`)

WIZ 프레임워크의 핵심 서버 클래스로, 다음과 같은 기능을 제공합니다:

```python
class Server:
    def __init__(self, path=None):
        self.boottime = time.time()
        self.package = season.lib.static.Package()
        self.path = season.lib.static.Path(path)
        self.config = season.lib.static.Config(server=self)
        self.cache = season.util.Cache()
        
        # Flask 및 SocketIO 애플리케이션 초기화
        self.app.flask = Flask(...)
        self.app.socketio = SocketIO(...)
        
        # HTTP 및 소켓 바인딩
        season.lib.binding.http(self)
        season.lib.binding.socket(self)
```

**주요 기능:**
- **Flask 통합**: 웹 서버 기본 기능
- **SocketIO 통합**: 실시간 양방향 통신
- **설정 관리**: `config.boot` 기반 구성
- **캐싱 시스템**: 성능 최적화
- **Wiz API**: `wiz()` 메서드를 통한 확장 API 제공

#### 프로젝트 구조

생성된 WIZ 프로젝트는 다음과 같은 구조를 가집니다:

```
myapp/
├── config/              # 설정 파일
│   ├── boot.py          # 서버 부팅 설정
│   ├── ide.py           # IDE 설정
│   ├── service.py       # 서비스 설정
│   └── plugin.json      # 플러그인 설정
├── public/              # 공개 디렉토리
│   ├── app.py           # 애플리케이션 엔트리포인트
│   └── app.wsgi         # WSGI 설정
├── project/             # 프로젝트 디렉토리
│   └── main/            # 메인 프로젝트
│       ├── config/      # 프로젝트 설정
│       ├── src/         # 소스 코드
│       │   ├── app/     # Angular 앱 컴포넌트
│       │   ├── controller/ # 백엔드 컨트롤러
│       │   ├── model/   # 데이터 모델
│       │   ├── route/   # API 라우트
│       │   ├── portal/  # 포털 (재사용 가능한 모듈)
│       │   ├── angular/ # Angular 설정
│       │   └── assets/  # 정적 자산
│       ├── build/       # 빌드 결과물
│       └── bundle/      # 번들 파일
├── ide/                 # WIZ IDE 소스
├── plugin/              # 플러그인
│   ├── core/
│   ├── workspace/
│   ├── git/
│   └── utility/
└── wiz.pid              # 데몬 프로세스 ID
```

### 3. 프로젝트 내부 구조 (src/)

#### 3.1 App (Angular 컴포넌트)

`src/app/` 디렉토리는 Angular 기반의 프론트엔드 컴포넌트를 포함합니다.

**구조 예시:**
```
src/app/
├── layout.empty/        # 레이아웃 컴포넌트
│   ├── view.pug
│   ├── view.ts
│   ├── view.scss
│   └── app.json
└── page.main/           # 페이지 컴포넌트
    ├── view.pug         # Pug 템플릿
    ├── view.ts          # TypeScript 로직
    ├── view.scss        # 스타일시트
    ├── app.json         # 앱 메타데이터
    ├── api.py           # 백엔드 API
    └── socket.py        # 소켓 핸들러
```

**app.json 예시:**
```json
{
    "title": "/workflow",
    "mode": "page",
    "namespace": "main",
    "category": "general",
    "id": "page.main",
    "viewuri": "/workflow/**",
    "layout": "layout.empty",
    "ng": {
        "selector": "wiz-page-main",
        "inputs": [],
        "outputs": []
    }
}
```

**컴포넌트 유형:**
- **Page**: 라우팅 가능한 페이지 컴포넌트
- **Layout**: 페이지를 감싸는 레이아웃
- **Widget**: 재사용 가능한 UI 컴포넌트

#### 3.2 Controller

`src/controller/` 디렉토리는 백엔드 로직의 기본 컨트롤러를 정의합니다.

**base.py 예시:**
```python
class Controller:
    def __init__(self):
        # 세션 초기화
        wiz.session = wiz.model("portal/season/session").use()
        sessiondata = wiz.session.get()
        wiz.response.data.set(session=sessiondata)
        
        # 다국어 처리
        lang = wiz.request.query("lang", None)
        if lang is not None:
            wiz.response.lang(lang)
            wiz.response.redirect(wiz.request.uri())
```

**역할:**
- 세션 관리
- 요청/응답 처리
- 공통 로직 구현
- 인증/인가

#### 3.3 Model

`src/model/` 디렉토리는 데이터 모델과 비즈니스 로직을 포함합니다.

**특징:**
- 데이터베이스 추상화
- 비즈니스 로직 캡슐화
- 재사용 가능한 코드 구조

#### 3.4 Route

`src/route/` 디렉토리는 API 엔드포인트를 정의합니다.

**구조:**
```
src/route/
├── brand/
│   ├── app.json
│   └── controller.py
└── setting/
    ├── app.json
    └── controller.py
```

**controller.py 예시:**
```python
segment = wiz.request.match("/brand/<action>/<path:path>")
action = segment.action

if action == "logo":
    # 로고 처리 로직
    fs = wiz.project.fs("bundle", "src", "assets", "brand")
    wiz.response.download(fs.abspath("logo.png"), as_attachment=False)

if action == "icon":
    # 아이콘 처리 로직
    wiz.response.download(fs.abspath("icon.ico"), as_attachment=False)

wiz.response.abort(404)
```

**특징:**
- RESTful API 설계
- URL 패턴 매칭
- 파일 다운로드 및 업로드
- JSON 응답 처리

#### 3.5 Portal

`src/portal/` 디렉토리는 재사용 가능한 모듈 패키지입니다.

**구조:**
```
src/portal/
├── season/              # 포털 패키지
│   ├── portal.json      # 메타데이터
│   ├── app/             # Angular 컴포넌트
│   ├── controller/      # 컨트롤러
│   ├── model/           # 모델
│   ├── route/           # 라우트
│   └── libs/            # 라이브러리
└── dizest/
    └── ...
```

**portal.json 예시:**
```json
{
    "package": "season",
    "title": "",
    "version": "2.0.0",
    "use_app": true,
    "use_widget": false,
    "use_route": true,
    "use_libs": true,
    "use_controller": true,
    "use_model": true
}
```

**특징:**
- 모듈화된 기능
- 프로젝트 간 재사용
- 독립적인 네임스페이스
- 선택적 기능 활성화

### 4. 설정 시스템

#### boot.py (서버 부팅 설정)

```python
# 부트스트랩 함수
def bootstrap(app, config):
    pass

# 시크릿 키
secret_key = "season-wiz-secret"

# SocketIO 설정
socketio = dict()
socketio['async_mode'] = 'threading'
socketio['cors_allowed_origins'] = '*'
socketio['async_handlers'] = True

# 서버 실행 설정
run = dict()
run['host'] = "0.0.0.0"
run['port'] = 3000
run['use_reloader'] = False
```

**설정 항목:**
- `bootstrap`: 서버 시작 시 실행되는 함수
- `secret_key`: Flask 세션 암호화 키
- `socketio`: SocketIO 서버 옵션
- `run`: 서버 실행 옵션 (host, port 등)

### 5. 플러그인 시스템

WIZ는 강력한 플러그인 아키텍처를 제공합니다.

**플러그인 구조:**
```
plugin/
├── core/                # 핵심 플러그인
├── workspace/           # 워크스페이스 관리
│   ├── app/
│   ├── command.py       # CLI 명령어
│   ├── filter.py
│   ├── model/
│   └── plugin.json
├── git/                 # Git 통합
├── utility/             # 유틸리티
└── xterm/               # 터미널
```

**command.py 예시:**
```python
def build(*args):
    if len(args) < 1:
        print("wiz command workspace build [projectName]")
        return
    
    project = args[0]
    wiz.project.checkout(project)
    builder = wiz.ide.plugin.model("builder")
    builder.build()
```

**플러그인 기능:**
- 커스텀 CLI 명령어
- IDE 확장
- 백엔드 API 추가
- 프론트엔드 위젯

### 6. IDE 통합

WIZ는 웹 기반 IDE를 내장하여 프로젝트를 브라우저에서 직접 개발할 수 있습니다.

**IDE 구조:**
```
ide/
├── package.json
├── angular/             # Angular 설정
│   ├── angular.build.options.json
│   ├── index.html
│   ├── main.ts
│   ├── wiz.ts
│   └── wizbuild.js
├── app/                 # IDE 앱 컴포넌트
│   ├── core.app.ide/
│   ├── core.editor.monaco/
│   ├── workspace.app.explore/
│   └── ...
└── assets/
```

**주요 기능:**
- 파일 탐색기
- 코드 에디터 (Monaco Editor)
- 터미널
- Git 통합
- 실시간 미리보기

### 7. 빌드 시스템

WIZ는 Angular 프로젝트를 자동으로 빌드합니다.

**빌드 프로세스:**
1. TypeScript 컴파일
2. Pug 템플릿 변환
3. SCSS 컴파일
4. Angular 번들링
5. 최적화 및 압축

**빌드 명령어:**
```bash
wiz command workspace build main
```

### 8. 통신 아키텍처

#### HTTP 통신
- RESTful API
- JSON 요청/응답
- 파일 업로드/다운로드

#### WebSocket 통신 (SocketIO)
- 실시간 양방향 통신
- 이벤트 기반 메시징
- 네임스페이스 지원

**소켓 핸들러 예시 (socket.py):**
```python
def connect():
    # 클라이언트 연결 시
    pass

def disconnect():
    # 클라이언트 연결 해제 시
    pass

def on_message(data):
    # 메시지 수신 시
    wiz.response.send({"result": "ok"})
```

## 데이터 플로우

### 1. HTTP 요청 플로우

```
Browser → Flask Router → Controller → Model → Response
                ↓
            Route (API)
                ↓
            App (API Handler)
```

### 2. 페이지 렌더링 플로우

```
URL Request → Route Matching → Layout Load → Page Component Load
                                                    ↓
                                            Angular Rendering
                                                    ↓
                                            API Calls (api.py)
```

### 3. 소켓 통신 플로우

```
Client Event → SocketIO Namespace → socket.py Handler → Response
                                           ↓
                                      Business Logic
```

## 확장성

### 1. 수평 확장
- 멀티 프로세스 지원
- 로드 밸런싱 가능

### 2. 수직 확장
- 플러그인을 통한 기능 추가
- 포털 시스템을 통한 모듈 재사용
- 커스텀 컴포넌트 개발

### 3. 통합
- WSGI 표준 지원
- 다양한 웹 서버와 호환 (Nginx, Apache 등)
- 컨테이너화 지원 (Docker)

## 보안

### 1. 세션 관리
- Flask 세션 기반
- Secret Key 암호화

### 2. CORS 설정
- SocketIO CORS 지원
- 도메인별 접근 제어

### 3. 인증/인가
- 커스텀 인증 시스템 구현 가능
- 세션 기반 권한 관리

## 성능 최적화

### 1. 캐싱
- 서버 레벨 캐시 (`season.util.Cache`)
- 정적 파일 캐싱

### 2. 번들링
- Angular AOT 컴파일
- 코드 스플리팅
- 압축 및 최소화

### 3. 비동기 처리
- SocketIO 비동기 핸들러
- 멀티스레딩 지원

## 결론

WIZ는 Flask와 Angular을 통합한 풀스택 프레임워크로, 다음과 같은 특징을 가집니다:

- **통합 개발 환경**: 백엔드와 프론트엔드를 하나의 프로젝트로 관리
- **플러그인 아키텍처**: 확장 가능하고 모듈화된 구조
- **웹 기반 IDE**: 브라우저에서 직접 개발 가능
- **실시간 통신**: SocketIO를 통한 양방향 통신
- **간편한 배포**: CLI를 통한 프로젝트 관리 및 서비스 등록

이러한 아키텍처를 통해 WIZ는 빠르고 효율적인 웹 애플리케이션 개발을 지원합니다.
