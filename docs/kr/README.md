# WIZ Framework 문서

WIZ 프레임워크에 대한 상세 문서입니다.

## 📚 문서 목차

### 1. [사용 가이드](usage-guide.md)
WIZ 프레임워크를 시작하기 위한 완전한 가이드입니다.

- **설치**: Python, Node.js, WIZ 프레임워크 설치 방법
- **프로젝트 생성**: 새 프로젝트 생성 및 초기 구조 이해
- **서버 실행**: 개발/프로덕션 모드로 서버 실행
- **페이지 생성**: 새 페이지 및 컴포넌트 생성 방법
- **API 개발**: 백엔드 API 작성 및 사용
- **라우트 추가**: 독립적인 API 엔드포인트 생성
- **모델 작성**: 데이터 모델 및 비즈니스 로직 구현
- **포털 사용**: 재사용 가능한 모듈 패키지 활용
- **빌드 및 배포**: 프로덕션 환경 배포 방법

### 2. [명령어 가이드](command.md)
WIZ CLI 명령어에 대한 완전한 레퍼런스입니다.

- **기본 명령어**: create, run, build, server, bundle, kill
- **IDE 관리**: ide install, remove, upgrade, build, clean
- **서비스 관리**: service regist, start, stop, restart, status, list
- **프로젝트 관리**: project build, create, delete, list, export
- **앱 관리**: project app create, delete, list
- **컨트롤러 관리**: project controller create, delete, list
- **라우트 관리**: project route create, delete, list
- **패키지 관리**: project package create, delete, list
- **NPM 관리**: project npm install, uninstall, list

### 3. [아키텍처](architecture.md)
WIZ 프레임워크의 내부 구조와 설계 원칙을 설명합니다.

- **개요**: WIZ 프레임워크 소개
- **핵심 구성 요소**: season 패키지 구조
- **서버 아키텍처**: Server 클래스 및 프로젝트 구조
- **프로젝트 내부 구조**: app, controller, model, route, portal
- **설정 시스템**: boot.py 및 설정 관리
- **플러그인 시스템**: 확장 가능한 플러그인 구조
- **IDE 통합**: 웹 기반 IDE 환경
- **빌드 시스템**: Angular 빌드 프로세스
- **통신 아키텍처**: HTTP 및 WebSocket 통신
- **데이터 플로우**: 요청-응답 흐름
- **확장성 및 보안**: 스케일링 및 보안 고려사항

### 4. [API 레퍼런스](api/README.md)
WIZ 프레임워크의 전체 API 상세 문서입니다.

#### 백엔드 API (Python)
- **[wiz.request](api/wiz-request.md)** - HTTP 요청 처리
- **[wiz.response](api/wiz-response.md)** - HTTP 응답 생성
- **[wiz.project](api/wiz-project.md)** - 프로젝트 관리 및 파일시스템
- **[wiz.session](api/wiz-session.md)** - 세션 관리
- **[wiz.model()](api/wiz-model.md)** - 모델 로드
- **[wiz.fs()](api/wiz-filesystem.md)** - 파일시스템 접근

#### 프론트엔드 API (TypeScript)
- **[Service API](api/service-api.md)** - Angular 컴포넌트 서비스

### 5. [예제 모음](examples.md)
실전 예제를 통한 학습 가이드입니다.

- 기본 페이지 생성
- API 통신
- 파일 업로드/다운로드
- WebSocket 실시간 통신
- 데이터베이스 연동
- 세션 관리
- RESTful API
- 이미지 처리
- CSV/Excel 파일 처리
- 인증 시스템

## 🚀 빠른 시작

### 설치

```bash
# WIZ 프레임워크 설치
pip install season
```

### 프로젝트 생성

```bash
# 새 프로젝트 생성
wiz create myapp
cd myapp
```

### 서버 실행

```bash
# 개발 서버 시작
wiz run --port=3000

# 브라우저에서 접속
# http://127.0.0.1:3000/wiz
```

## 💡 주요 특징

### 1. 풀스택 프레임워크
- **백엔드**: Python Flask 기반
- **프론트엔드**: Angular 기반
- **실시간 통신**: SocketIO 지원

### 2. 웹 기반 IDE
- 브라우저에서 직접 개발
- 파일 탐색기, 코드 에디터, 터미널 제공
- 실시간 미리보기

### 3. 모듈화된 구조
- **App**: Angular 컴포넌트 (페이지, 레이아웃, 위젯)
- **Controller**: 백엔드 로직
- **Model**: 데이터 모델
- **Route**: API 엔드포인트
- **Portal**: 재사용 가능한 모듈

### 4. 플러그인 시스템
- 확장 가능한 아키텍처
- 커스텀 CLI 명령어
- IDE 기능 확장

## 📁 프로젝트 구조

```
myapp/
├── config/              # 설정 파일
│   └── boot.py          # 서버 부팅 설정
├── public/              # 공개 디렉토리
│   └── app.py           # 엔트리포인트
├── project/             # 프로젝트
│   └── main/            # 메인 프로젝트
│       └── src/         # 소스 코드
│           ├── app/     # Angular 컴포넌트
│           ├── controller/  # 컨트롤러
│           ├── model/   # 모델
│           ├── route/   # API 라우트
│           └── portal/  # 포털
├── ide/                 # WIZ IDE
└── plugin/              # 플러그인
```

## 🔧 개발 워크플로우

### 1. 페이지 생성

```bash
# IDE에서 또는 수동으로 생성
project/main/src/app/page.mypage/
├── view.pug     # 템플릿
├── view.ts      # 로직
├── view.scss    # 스타일
├── app.json     # 메타데이터
├── api.py       # 백엔드 API
└── socket.py    # WebSocket 핸들러
```

### 2. API 작성

**api.py**
```python
def load():
    data = {"message": "Hello"}
    wiz.response.status(200, data)
```

**view.ts**
```typescript
async loadData() {
    let res = await this.service.api.call("load");
    console.log(res.data);
}
```

### 3. 빌드 및 테스트

```bash
# 빌드
wiz command workspace build main

# 서버 실행
wiz run --port=3000

# 접속
http://127.0.0.1:3000/mypage
```

## 📖 학습 경로

1. **초보자**: [사용 가이드](usage-guide.md)의 설치부터 페이지 생성까지 따라하기
2. **중급자**: API 개발, 모델 작성, 라우트 추가 학습
3. **고급자**: [아키텍처](architecture.md) 문서로 내부 구조 이해, 플러그인 개발

## 🔗 관련 링크

- **GitHub**: https://github.com/season-framework/wiz
- **PyPI**: https://pypi.org/project/season/
- **라이선스**: MIT License

## 🤝 기여하기

WIZ 프레임워크는 오픈소스 프로젝트입니다. 기여를 환영합니다!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 라이선스

MIT License - 자유롭게 사용, 수정, 배포할 수 있습니다.

## 📞 지원

- **이슈 리포팅**: [GitHub Issues](https://github.com/season-framework/wiz/issues)
- **이메일**: proin@season.co.kr

---

**Copyright 2021 SEASON CO. LTD.**
