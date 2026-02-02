# WIZ 명령어 가이드

WIZ 프레임워크는 프로젝트 생성, 개발, 빌드, 배포를 위한 다양한 CLI 명령어를 제공합니다.

## 목차

- [기본 명령어](#기본-명령어)
  - [wiz create](#wiz-create)
  - [wiz run](#wiz-run)
  - [wiz build](#wiz-build)
  - [wiz server](#wiz-server)
  - [wiz bundle](#wiz-bundle)
  - [wiz kill](#wiz-kill)
- [IDE 관리](#ide-관리)
  - [wiz ide](#wiz-ide)
- [서비스 관리](#서비스-관리)
  - [wiz service](#wiz-service)
- [프로젝트 관리](#프로젝트-관리)
  - [wiz project](#wiz-project)
  - [wiz project app](#wiz-project-app)
  - [wiz project controller](#wiz-project-controller)
  - [wiz project route](#wiz-project-route)
  - [wiz project package](#wiz-project-package)
  - [wiz project npm](#wiz-project-npm)

---

## 기본 명령어

### wiz create

새로운 WIZ 워크스페이스를 생성합니다.

```bash
wiz create <projectname>
```

**예시:**

```bash
# 'myapp' 워크스페이스 생성
wiz create myapp
```

**생성되는 구조:**
- `config/` - 설정 파일
- `public/` - 웹 서버 파일
- `ide/` - WIZ IDE
- `plugin/` - 플러그인
- `project/` - 프로젝트 폴더

---

### wiz run

개발 서버를 실행합니다.

```bash
wiz run [옵션]
```

**옵션:**

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--host` | 바인딩할 호스트 주소 | `0.0.0.0` |
| `--port` | 서버 포트 | `3000` |
| `--bundle` | 번들 모드로 실행 | `false` |
| `--log` | 로그 파일 경로 | - |

**예시:**

```bash
# 기본 실행 (0.0.0.0:3000)
wiz run

# 커스텀 포트로 실행
wiz run --port=8080

# 특정 호스트에서 실행
wiz run --host=127.0.0.1

# 번들 모드로 실행
wiz run --bundle

# 로그 파일 지정
wiz run --log=server.log
```

---

### wiz server

서버를 데몬(백그라운드)으로 관리합니다.

```bash
wiz server <action> [옵션]
```

**액션:**

| 액션 | 설명 |
|------|------|
| `start` | 데몬으로 서버 시작 |
| `stop` | 데몬 서버 중지 |
| `restart` | 데몬 서버 재시작 |

**옵션:**

| 옵션 | 설명 |
|------|------|
| `--log` | 로그 파일 경로 |
| `--force` | 강제 시작 (오래된 PID 제거) |

**예시:**

```bash
# 데몬 시작
wiz server start

# 로그 파일과 함께 시작
wiz server start --log=/var/log/wiz.log

# 강제 시작 (오래된 PID 제거)
wiz server start --force

# 데몬 중지
wiz server stop

# 데몬 재시작
wiz server restart
```

---

### wiz bundle

배포용 번들을 생성합니다.

```bash
wiz bundle [옵션]
```

**옵션:**

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--project` | 프로젝트 이름 | `main` |

**예시:**

```bash
# 기본 프로젝트 번들
wiz bundle

# 특정 프로젝트 번들
wiz bundle --project=dev
```

**생성되는 번들 구조:**
```
bundle/
├── project/main/bundle/
├── config/
├── public/
└── plugin/
```

---

### wiz kill

모든 WIZ 프로세스를 종료합니다.

```bash
wiz kill
```

---

## IDE 관리

### wiz ide

WIZ IDE를 관리합니다.

```bash
wiz ide <action>
```

**액션:**

| 액션 | 설명 |
|------|------|
| `install` | WIZ IDE 설치 |
| `remove` | WIZ IDE 제거 |
| `upgrade` | WIZ IDE 업그레이드 |
| `build` | WIZ IDE 빌드 |
| `clean` | WIZ IDE 캐시 정리 |

**예시:**

```bash
# IDE 설치
wiz ide install

# IDE 제거
wiz ide remove

# IDE 업그레이드
wiz ide upgrade

# IDE 빌드
wiz ide build

# IDE 캐시 정리
wiz ide clean
```

---

## 서비스 관리

### wiz service

Linux systemd 서비스로 WIZ를 관리합니다. (Linux 전용)

```bash
wiz service <action> [name] [옵션]
```

**액션:**

| 액션 | 설명 |
|------|------|
| `regist` | 서비스 등록 |
| `unregist` | 서비스 등록 해제 |
| `start` | 서비스 시작 |
| `stop` | 서비스 중지 |
| `restart` | 서비스 재시작 |
| `status` | 서비스 상태 확인 |
| `list` | 등록된 서비스 목록 |

**예시:**

```bash
# 서비스 등록
wiz service regist myapp

# 특정 포트로 서비스 등록
wiz service regist myapp 8080

# 번들 모드로 서비스 등록
wiz service regist myapp 8080 bundle

# 서비스 시작
wiz service start myapp

# 모든 서비스 시작
wiz service start

# 서비스 중지
wiz service stop myapp

# 서비스 재시작
wiz service restart myapp

# 서비스 상태 확인
wiz service status myapp

# 서비스 목록 조회
wiz service list

# 서비스 등록 해제
wiz service unregist myapp
```

**서비스 파일 경로:**
- 실행 파일: `/usr/local/bin/wiz.<name>`
- 서비스 파일: `/etc/systemd/system/wiz.<name>.service`
- 로그 파일: `/var/log/wiz/<name>`

---

## 프로젝트 관리

### wiz project

프로젝트를 관리합니다.

```bash
wiz project <subcommand> [action] [옵션]
```

#### 프로젝트 기본 명령어

| 명령어 | 설명 |
|--------|------|
| `build` | 프로젝트 빌드 |
| `create` | 프로젝트 생성 |
| `delete` | 프로젝트 삭제 |
| `list` | 프로젝트 목록 |
| `clean` | 프로젝트 캐시 정리 |
| `export` | 프로젝트 내보내기 (.wizproject) |

**예시:**

```bash
# 프로젝트 빌드
wiz project build --project=main

# 클린 빌드
wiz project build --project=main --clean

# 새 프로젝트 생성
wiz project create --project=dev

# Git에서 프로젝트 생성
wiz project create --project=dev --uri=https://github.com/user/repo.git

# .wizproject 파일에서 프로젝트 생성
wiz project create --project=dev --path=/path/to/backup.wizproject

# 프로젝트 삭제
wiz project delete --project=dev

# 프로젝트 목록
wiz project list

# 프로젝트 캐시 정리
wiz project clean --project=main

# 프로젝트 내보내기
wiz project export --project=main --output=backup.wizproject
```

---

### wiz project app

앱(App)을 관리합니다.

```bash
wiz project app <action> [옵션]
```

**액션:**

| 액션 | 설명 |
|------|------|
| `list` | 앱 목록 조회 |
| `create` | 앱 생성 |
| `delete` | 앱 삭제 |

**옵션:**

| 옵션 | 설명 |
|------|------|
| `--namespace` | 앱 네임스페이스 (예: main.dashboard) |
| `--project` | 프로젝트 이름 (기본: main) |
| `--package` | 포탈 패키지 이름 |

**예시:**

```bash
# 앱 목록 조회
wiz project app list

# 패키지 내 앱 목록
wiz project app list --package=myportal

# 앱 생성
wiz project app create --namespace=main.dashboard

# 패키지 내 앱 생성
wiz project app create --namespace=main.dashboard --package=myportal

# 앱 삭제
wiz project app delete --namespace=main.dashboard
```

**생성되는 파일:**
```
app/<namespace>/
├── app.json      # 앱 설정
├── view.ts       # 컴포넌트 로직
└── view.html     # 템플릿
```

---

### wiz project controller

컨트롤러를 관리합니다.

```bash
wiz project controller <action> [옵션]
```

**액션:**

| 액션 | 설명 |
|------|------|
| `list` | 컨트롤러 목록 조회 |
| `create` | 컨트롤러 생성 |
| `delete` | 컨트롤러 삭제 |

**옵션:**

| 옵션 | 설명 |
|------|------|
| `--namespace` | 컨트롤러 이름 |
| `--project` | 프로젝트 이름 (기본: main) |
| `--package` | 포탈 패키지 이름 |

**예시:**

```bash
# 컨트롤러 목록
wiz project controller list

# 컨트롤러 생성
wiz project controller create --namespace=api

# 패키지 내 컨트롤러 생성
wiz project controller create --namespace=api --package=myportal

# 컨트롤러 삭제
wiz project controller delete --namespace=api
```

---

### wiz project route

라우트를 관리합니다.

```bash
wiz project route <action> [옵션]
```

**액션:**

| 액션 | 설명 |
|------|------|
| `list` | 라우트 목록 조회 |
| `create` | 라우트 생성 |
| `delete` | 라우트 삭제 |

**옵션:**

| 옵션 | 설명 |
|------|------|
| `--namespace` | 라우트 이름 |
| `--project` | 프로젝트 이름 (기본: main) |
| `--package` | 포탈 패키지 이름 |
| `--path` | 라우트 경로 |
| `--methods` | HTTP 메서드 (기본: GET,POST) |

**예시:**

```bash
# 라우트 목록
wiz project route list

# 라우트 생성
wiz project route create --namespace=api

# 경로 지정하여 라우트 생성
wiz project route create --namespace=api --path=/api/v1

# 라우트 삭제
wiz project route delete --namespace=api
```

**생성되는 파일:**
```
route/<namespace>/
├── app.json      # 라우트 설정
└── route.py      # 라우트 핸들러
```

---

### wiz project package

포탈 패키지를 관리합니다.

```bash
wiz project package <action> [옵션]
```

**액션:**

| 액션 | 설명 |
|------|------|
| `list` | 패키지 목록 조회 |
| `create` | 패키지 생성 |
| `delete` | 패키지 삭제 |

**옵션:**

| 옵션 | 설명 |
|------|------|
| `--namespace` | 패키지 이름 |
| `--project` | 프로젝트 이름 (기본: main) |

**예시:**

```bash
# 패키지 목록
wiz project package list

# 패키지 생성
wiz project package create --namespace=myportal

# 패키지 삭제
wiz project package delete --namespace=myportal
```

**생성되는 구조:**
```
portal/<namespace>/
├── portal.json    # 패키지 설정
├── README.md      # 패키지 문서
├── app/           # 앱 폴더
├── controller/    # 컨트롤러 폴더
└── route/         # 라우트 폴더
```

---

### wiz project npm

NPM 패키지를 관리합니다. (프로젝트 build 폴더 기준)

```bash
wiz project npm <action> [옵션]
```

**액션:**

| 액션 | 설명 |
|------|------|
| `list` | 패키지 목록 조회 |
| `install` | 패키지 설치 |
| `uninstall` | 패키지 제거 |

**옵션:**

| 옵션 | 설명 |
|------|------|
| `--package` | 패키지 이름 |
| `--version` | 패키지 버전 |
| `--dev` | 개발 의존성으로 설치 |
| `--project` | 프로젝트 이름 (기본: main) |

**예시:**

```bash
# 패키지 목록 조회
wiz project npm list

# 모든 의존성 설치
wiz project npm install

# 특정 패키지 설치
wiz project npm install --package=@angular/core

# 버전 지정하여 설치
wiz project npm install --package=@angular/core --version=^18.2.5

# 개발 의존성으로 설치
wiz project npm install --package=typescript --dev

# 패키지 제거
wiz project npm uninstall --package=@angular/core
```

> **참고:** NPM 명령어는 `project/<name>/build` 폴더에서 실행되며, 작업 후 `package.json`이 `src/angular/package.json`으로 동기화됩니다.

---

## 공통 옵션

### --version

WIZ 버전을 확인합니다.

```bash
wiz --version
```

### --help

명령어 도움말을 확인합니다.

```bash
wiz --help
wiz <command> --help
```

---

## 워크플로우 예시

### 새 프로젝트 시작

```bash
# 1. 워크스페이스 생성
wiz create myapp

# 2. 워크스페이스로 이동
cd myapp

# 3. 개발 서버 실행
wiz run
```

### 프로젝트 개발

```bash
# 새 앱 생성
wiz project app create --namespace=main.dashboard

# 컨트롤러 생성
wiz project controller create --namespace=api

# 라우트 생성
wiz project route create --namespace=api --path=/api

# 프로젝트 빌드
wiz project build
```

### 배포 준비

```bash
# 프로젝트 번들 생성
wiz bundle --project=main

# 또는 프로젝트 내보내기
wiz project export --project=main --output=backup.wizproject
```

### 프로덕션 서버 (Linux)

```bash
# 서비스 등록
wiz service regist myapp 80

# 서비스 시작
wiz service start myapp

# 서비스 상태 확인
wiz service status myapp
```
