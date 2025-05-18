# seoyeongje_Quiz API Server

## 서버구동
1. apiserver 디렉토리로 이동
```sh
cd apiserver
```

2. 의존성세팅
```sh
poetry install
```

3. sqlalchemy orm을 기반으로 PostgreSQL에 데이터베이스 생성 및 테이블 초기화
```sh
poetry run python tools/create_tables.py
```

4. api서버 실행
```sh
poetry run apiserver
```

## API Documentation: FastAPI 요약
Version: 0.1.0

### 🔑 인증 (Auth)
- **POST** `/auth/token`: 로그인 (OAuth2 Password Grant 방식)

### 👥 사용자 (Users)
- **GET** `/users`: 사용자 목록 조회 (pagination 지원)

- **POST** `/users`: 사용자 등록

### 🧠 퀴즈 (Quizzes)
#### 1. 생성 및 목록
- **POST** `/quizzes/`: 퀴즈 생성 (질문/선택지 포함 가능, 질문은 최소2개여야하며 선택지는 최소1개의 정답을 포함해야 함)

- **GET** `/quizzes/`: 퀴즈 목록 조회 (pagination 지원)

#### 2. 개별 퀴즈 관리
- **PATCH** `/quizzes/{quiz_id}`: 퀴즈 수정 (관리자용)

- **DELETE** `/quizzes/{quiz_id}`: 퀴즈 삭제 (관리자용)

#### 3. 퀴즈 상세 조회
- **GET** `/quizzes/{quiz_id}/forstaff`: 퀴즈 상세 조회 (관리자용, `Question`에 대해 pagination 지원)

- **GET** `/quizzes/{quiz_id}/foruser`: 퀴즈 상세 조회 (사용자용, `Question`에 대해 pagination 지원, 응시된 퀴즈에 대해서만 상세조회 가능)

#### 4. 퀴즈 응시 및 제출
- **POST** `/quizzes/{quiz_id}/attempt`: 퀴즈 응시 시작 (attempt ID 반환)

- **POST** `/quizzes/{quiz_id}/answer`: 퀴즈 응답 저장 (질문에 대한 선택지 정보를 입력받아 임시저장)

- **POST** `/quizzes/{quiz_id}/submit`: 퀴즈 제출 및 점수 확인 (한번 제출된 퀴즈는 다시 제출 불가)

### 📦 주요 스키마 (Schemas)
#### ✅ Quiz 관련
`QuizCreate`, `QuizUpdate`, `QuizConfig`

`QuizCreateResponse`, `QuizGetListResponse`, `QuizGetDetailForUserResponse`, `QuizGetDetailForStaffResponse`

`QuizQuestion`, `QuizQuestionChoice`, `QuestionCreate`, `ChoiceCreate`

#### ✅ 응답 관련
`QuizAnswerCreate`, `QuizAnswerCreateResponse`, `QuizAttemptResponse`, `QuizSubmitResponse`

### ⚙️ 인증 방식
전 API 대부분이 `OAuth2PasswordBearer` 보안 스킴을 사용하며, `Authorization: Bearer <token>` 헤더 필요.

## 참고
- API문서는 http://127.0.0.1:8000/docs 에서 확인 가능합니다.
- 데이터베이스 접속정보는 apiserver/db/database.py에 하드코딩되어있습니다.

이 외의 별도의 세팅은 필요하지 않습니다.

감사합니다.