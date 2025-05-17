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

# API Documentation: FastAPI 요약약
Version: 0.1.0

/users
GET - Get Users
Responses:

    200: Successful Response

POST - Post Users
Request Body Content Types: application/json

Responses:

    200: Successful Response

    422: Validation Error

description:

    유저 정보를 조회하는 api입니다.

/auth/token
POST - Login
Request Body Content Types: application/x-www-form-urlencoded

Responses:

    200: Successful Response

    422: Validation Error

description:

    jwt기반 로그인 api입니다. http://127.0.0.1:8000/docs에서 우측상단 Authorize버튼으로 자동 요청되는 엔드포인트입니다.

/quizzes/
POST - Create Quiz
Request Body Content Types: application/json

Responses:

    200: Successful Response

    422: Validation Error

description:

    퀴즈 생성 api입니다. 

GET - List Quizzes
Parameters:

    skip (integer, in: query) - Optional

    limit (integer, in: query) - Optional

Responses:

    200: Successful Response

    422: Validation Error

description:

    퀴즈 조회 api입니다. skip과 limit로 페이징이 가능하며 관리자에게만 QuizConfig값이 보입니다.

/quizzes/{quiz_id}
PATCH - Update Quiz
Parameters:

quiz_id (string, in: path) - Required

Request Body Content Types: application/json

Responses:

    200: Successful Response

    422: Validation Error

description:

    퀴즈 수정 api입니다. 관리자만 사용 할 수 있으며 주로 QuizConfig값을 수정하는데 사용됩니다.

DELETE - Delete Quiz
Parameters:

    quiz_id (string, in: path) - Required

Responses:

    204: Successful Response

    422: Validation Error

description:

    퀴즈 삭제 api입니다. 관리자만 사용 할 수 있으며 Quiz의 id값을 참조하는 모든 테이블의 컬럼을 영구적으로 삭제합니다

GET - Get Quiz Questions
Parameters:

    quiz_id (string, in: path) - Required

    page (integer, in: query) - Optional

    per_page (integer, in: query) - Optional

Responses:

    200: Successful Response

    422: Validation Error

description:

    퀴즈 상세 조회 api입니다. 유저가 응시한 Quiz에 대해서만만 요청 할 수 있습니다. Quiz내의 Question을 페이징합니다.

/quizzes/{quiz_id}/attempt
POST - Attempt Quiz
Parameters:

    quiz_id (string, in: path) - Required

Responses:

    200: Successful Response

    422: Validation Error

description:

    퀴즈 응시 api입니다. 응시 후 QuizAttempt테이블이 생성되며 응시한 Question과 Choice들이 JSON타입의 컬럼으로 임베디드 됩니다. 이때 QuizConfig의 설정에 따라 어떤 문제들이 총 몇개로 저장될지와 랜덤배치여부를 결정합니다. 이후 퀴즈 상세 조회 api를 요청 할 수 있습니다.

/quizzes/{quiz_id}/answer
POST - Save Quiz Answers
Parameters:

    quiz_id (string, in: path) - Required

Request Body Content Types: application/json

Responses:

    200: Successful Response

    422: Validation Error

description:

    응시내용 임시저장 api입니다. 퀴즈 응시 후 퀴즈상세정보를 조회하고 이후 각 문제의 문항에서 정답을 선택한 후 요청되는 api입니다. 이를 통해 응시 중 새로고침이 되어도 출제된 문제의 구성이나 순서, 사용자가 체크한 답안이 그대로 남아있습니다. 해당 기능이 가능한 이유는 클라이언트 단에서 유저가 문항을 선택 할 때마다 이 api를 요청하면 되기 때문입니다.

/quizzes/{quiz_id}/submit
POST - Submit Quiz Attempt
Parameters:

    quiz_id (string, in: path) - Required

Responses:

    200: Successful Response

    422: Validation Error

description:

    퀴즈 체점 api입니다. 선택된 문항이 정답인지 체크하여 각 문항당 1점씩 점수를 계산합니다.

## 참고
데이터베이스 접속정보는 apiserver/db/database.py에 하드코딩되어있습니다.
이 외의 별도의 세팅은 필요하지 않습니다.

감사합니다.