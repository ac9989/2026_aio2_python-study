# PlayEAT API 명세서｜최종 OpenAPI 기준

> 최종 제공된 OpenAPI JSON을 기준으로 작성한 수동 Markdown API 명세서입니다. OpenAPI에 없는 응답 구조·오류 코드·권한 조건은 임의로 추가하지 않았습니다.

## 목차

1. 문서 개요  
2. 문서 작성 기준  
3. 공통 인증·응답 기준  
4. 요청·응답 Pydantic 모델  
5. Restaurants  
6. Recommendations  
7. Auth  
8. Users  
9. Conversations & Chat  
10. Admin  
11. Admin Log Analysis  
12. System  
13. 현재 문서화 상태

## 1. 문서 개요

| 항목 | 내용 |
| --- | --- |
| 서비스명 | PlayEAT |
| API 문서 버전 | `0.2.0` |
| OpenAPI 버전 | `3.1.0` |
| 인증 Scheme | `HTTPBearer` (`type: http`, `scheme: bearer`) |
| 문서 형식 | Markdown |

> OpenAPI에 `servers` 항목이 없으므로 Base URL은 임의로 지정하지 않습니다.

## 2. 문서 작성 기준

- Endpoint, Method, Parameter, Request Body, Response, Schema, Security는 최종 OpenAPI 값을 기준으로 합니다.
- OpenAPI에 없는 오류 응답은 임의로 추가하지 않습니다.
- Endpoint/Schema의 `description`은 문서에 반영합니다.
- 성공 Response Schema가 `{}`이면 `스키마 미정의`로 표시합니다.

## 3. 공통 인증·응답 기준

| 표시 | 의미 |
| --- | --- |
| `HTTPBearer` | Operation의 `security`에 HTTPBearer가 정의됨 |
| `Authorization Header` | Parameter에 `authorization` Header가 직접 정의됨 |
| `없음` | 위 인증 정보가 OpenAPI에 정의되지 않음 |

## 4. 요청·응답 Pydantic 모델

| 모델 | 설명 | 필드 | 타입 | 필수 | 제약 |
| --- | --- | --- | --- | :---: | --- |
| `ChatRequest` | POST /conversations/{id}/chat 사용자 메시지. | `content` | `string` | O | - |
| `ChatRequest` |  | `restaurant_category` | `string | null` | X | - |
| `ChatRequest` |  | `menu_type` | `string | null` | X | - |
| `ChatRequest` |  | `price_level` | `string | null` | X | - |
| `ChatRequest` |  | `tone` | `string | null` | X | - |
| `ChatRequest` |  | `length` | `string | null` | X | - |
| `CleaningRunRequest` | 로그 정제 실행 요청. | `period_start` | `date-time` | O | - |
| `CleaningRunRequest` |  | `period_end` | `date-time` | O | - |
| `CleaningRunRequest` |  | `criteria_version` | `string | null` | X | - |
| `EvaluationRunRequest` | 요약 품질평가 실행 요청. | `summary_id` | `uuid` | O | - |
| `EvaluationRunRequest` |  | `case_id` | `uuid | null` | X | - |
| `EvaluationRunRequest` |  | `experiment_id` | `uuid | null` | X | - |
| `EvaluationRunRequest` |  | `run_type` | `string` | X | baseline / before / after, 기본 `baseline` |
| `ExperimentCreateRequest` | 개선 실험 생성 요청. | `name` | `string` | O | 최소 1자, 최대 100자 |
| `ExperimentCreateRequest` |  | `hypothesis` | `string` | O | 최소 1자 |
| `ExperimentCreateRequest` |  | `change_description` | `string` | O | 최소 1자 |
| `ExperimentCreateRequest` |  | `before_version` | `string` | O | 최소 1자, 최대 50자 |
| `ExperimentCreateRequest` |  | `after_version` | `string` | O | 최소 1자, 최대 50자 |
| `FeedbackCreateRequest` | POST /recommendations/{id}/feedback 요청. | `feedback_value` | `string` | O | 1 / 2 / 3 |
| `FeedbackRequest` | 대화 메시지에 대한 좋아요/싫어요. | `message_id` | `uuid` | O | - |
| `FeedbackRequest` |  | `value` | `string | null` | X | - |
| `HTTPValidationError` | - | `detail` | `array[ValidationError]` | X | - |
| `LogFilters` | 로그 조회·요약에 쓰는 필터. | `endpoint` | `string | null` | X | - |
| `LogFilters` |  | `http_method` | `string | null` | X | - |
| `LogFilters` |  | `status_code` | `integer | null` | X | - |
| `LogFilters` |  | `error_only` | `boolean` | X | 기본 `false` |
| `LogSummaryRequest` | LLM 로그 요약 요청. | `period_start` | `date-time` | O | - |
| `LogSummaryRequest` |  | `period_end` | `date-time` | O | - |
| `LogSummaryRequest` |  | `cleaning_run_id` | `uuid` | O | - |
| `LogSummaryRequest` |  | `filters` | `LogFilters` | X | - |
| `LoginRequest` | 로그인 요청. MVP는 이메일+비밀번호만 받는다. | `email` | `email` | O | - |
| `LoginRequest` |  | `password` | `string` | O | - |
| `MessageCreate` | 대화에 메시지를 저장할 때 받는 값. | `role` | `string` | O | user / assistant / system |
| `MessageCreate` |  | `content` | `string` | O | 최소 1자 |
| `MessageOut` | 저장된 메시지 조회 응답. | `id` | `uuid` | O | - |
| `MessageOut` |  | `conversation_id` | `uuid` | O | - |
| `MessageOut` |  | `role` | `string` | O | - |
| `MessageOut` |  | `content` | `string` | O | - |
| `MessageOut` |  | `created_at` | `date-time` | O | - |
| `MyConversationCreate` | POST /conversations 요청.<br><br>user_id는 받지 않는다. 토큰에서 꺼낸 값만 신뢰한다.<br>받으면 남의 명의로 대화를 만들 수 있다. | `title` | `string | null` | X | - |
| `NicknameUpdateRequest` | PATCH /users/me 닉네임 수정 요청. | `nickname` | `string` | O | 최소 1자, 최대 45자 |
| `PasswordChangeRequest` | 비밀번호 변경 요청. 확인 값은 화면에서만 검사한다. | `current_password` | `string` | O | 최소 8자, 최대 128자 |
| `PasswordChangeRequest` |  | `new_password` | `string` | O | 최소 8자, 최대 128자 |
| `RegenerateRequest` | 같은 대화에서 답변만 다시 생성할 때 쓰는 요청.<br><br>ChatRequest를 재사용하면 안 된다. 거기에는 content가 필수라서<br>질문을 다시 보내지 않는 이 요청은 422로 거부당한다. | `tone` | `string | null` | X | - |
| `RegenerateRequest` |  | `length` | `string | null` | X | - |
| `ResponseMeta` | 성공 응답에 함께 담을 요청 번호와 시각. | `request_id` | `uuid` | O | - |
| `ResponseMeta` |  | `timestamp` | `date-time` | O | - |
| `SignUpRequest` | POST /auth/signups 요청. 이메일 회원 생성. | `email` | `email` | O | - |
| `SignUpRequest` |  | `password` | `string` | O | 최소 8자, 최대 128자 |
| `SignUpRequest` |  | `nickname` | `string` | O | 최소 1자, 최대 45자 |
| `SignUpRequest` |  | `terms_agreed` | `boolean` | O | `true` |
| `SignUpRequest` |  | `privacy_agreed` | `boolean` | O | `true` |
| `SignUpResponse` | 회원가입 완료 후 돌려줄 회원 정보. | `user_id` | `uuid` | O | - |
| `SignUpResponse` |  | `email` | `email` | O | - |
| `SignUpResponse` |  | `nickname` | `string` | O | - |
| `SignUpResponse` |  | `created_at` | `date-time` | O | - |
| `SuccessResponse_SignUpResponse_` | - | `data` | `SignUpResponse` | O | - |
| `SuccessResponse_SignUpResponse_` |  | `meta` | `ResponseMeta` | O | - |
| `ValidationError` | - | `loc` | `array[string | integer]` | O | - |
| `ValidationError` |  | `msg` | `string` | O | - |
| `ValidationError` |  | `type` | `string` | O | - |
| `ValidationError` |  | `input` | `-` | X | - |
| `ValidationError` |  | `ctx` | `object` | X | - |

## 5. Restaurants

| 기능 | Method | API | 요청 위치 | 요청 항목 | 타입 | 필수 | 제약 | Response | 인증 | 예외처리 |
| --- | :---: | --- | :---: | --- | --- | :---: | --- | --- | --- | --- |
| List Restaurant Categories | GET | `/api/v1/restaurant-categories` | - | 없음 | - | - | - | `200` · 스키마 미정의 | 없음 | - |
| List Restaurants | GET | `/api/v1/restaurants` | Query | `page` | integer | X | 최소 1, 기본 `1` | `200` · 스키마 미정의 | 없음 | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Query | `page_size` | integer | X | 최소 1, 최대 100, 기본 `20` |  |  |  |
| Search Restaurants | GET | `/api/v1/restaurants/search` | Query | `category` | string | null | X | - | `200` · 스키마 미정의 | 없음 | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Query | `menu_types` | array[string] | null | X | - |  |  |  |
| ↳ |  |  | Query | `price_level` | string | null | X | - |  |  |  |
| Get Restaurant | GET | `/api/v1/restaurants/{restaurant_id}` | Path | `restaurant_id` | uuid | O | - | `200` · 스키마 미정의 | 없음 | `422` · Validation Error · HTTPValidationError |
| List Tag Categories | GET | `/api/v1/tag-categories` | - | 없음 | - | - | - | `200` · 스키마 미정의 | 없음 | - |
| List Restaurant Tags By Category | GET | `/api/v1/restaurant-tags/{category_id}` | Path | `category_id` | uuid | O | - | `200` · 스키마 미정의 | 없음 | `422` · Validation Error · HTTPValidationError |
| List Restaurant Tags | GET | `/api/v1/restaurant-tags` | - | 없음 | - | - | - | `200` · 스키마 미정의 | 없음 | - |

**기타 설명**

- `GET /api/v1/restaurant-categories`: 음식 카테고리 목록을 반환한다.
- `GET /api/v1/restaurants`: 식당 목록을 페이지 단위로 반환한다.
- `GET /api/v1/restaurants/search`: 사용자가 선택한 조건과 가장 많이 일치하는 식당을 조회한다.  모든 조건을 만족할 필요는 없다. 음식문화권과 태그가 일치할 때마다 1점을 부여하고 점수가 높은 식당부터 반환한다.
- `GET /api/v1/restaurants/{restaurant_id}`: 식당 한 곳의 상세·메뉴·태그를 반환한다.
- `GET /api/v1/tag-categories`: 가격대·메뉴 특성 등 태그 분류 목록을 반환한다.
- `GET /api/v1/restaurant-tags/{category_id}`: 선택한 분류에 속한 태그를 반환한다.
- `GET /api/v1/restaurant-tags`: 전체 식당 태그를 반환한다.

## 6. Recommendations

| 기능 | Method | API | 요청 위치 | 요청 항목 | 타입 | 필수 | 제약 | Response | 인증 | 예외처리 |
| --- | :---: | --- | :---: | --- | --- | :---: | --- | --- | --- | --- |
| Create Recommendation Feedback | POST | `/api/v1/recommendations/{recommendation_id}/feedback` | Path | `recommendation_id` | uuid | O | - | `200` · 스키마 미정의 | HTTPBearer | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Body | `FeedbackCreateRequest` | Pydantic Model | O | - |  |  |  |

**기타 설명**

- `POST /api/v1/recommendations/{recommendation_id}/feedback`: 추천 평가를 저장하거나, 이미 있으면 값을 바꾼다.

## 7. Auth

| 기능 | Method | API | 요청 위치 | 요청 항목 | 타입 | 필수 | 제약 | Response | 인증 | 예외처리 |
| --- | :---: | --- | :---: | --- | --- | :---: | --- | --- | --- | --- |
| Create User | POST | `/api/v1/auth/signups` | Body | `SignUpRequest` | Pydantic Model | O | - | `201` · SuccessResponse_SignUpResponse_ | 없음 | `422` · Validation Error · HTTPValidationError |
| Login | POST | `/api/v1/auth/login` | Body | `LoginRequest` | Pydantic Model | O | - | `200` · 스키마 미정의 | 없음 | `422` · Validation Error · HTTPValidationError |
| Change Password | PATCH | `/api/v1/auth/password` | Body | `PasswordChangeRequest` | Pydantic Model | O | - | `200` · 스키마 미정의 | HTTPBearer | `422` · Validation Error · HTTPValidationError |

**기타 설명**

- `POST /api/v1/auth/signups`: 이메일 회원을 만들고 profiles·user_consents를 함께 저장한다.
- `POST /api/v1/auth/login`: 이메일 로그인. 관리자(profile_type=0)와 일반 사용자를 구분한다.
- `PATCH /api/v1/auth/password`: 현재 비밀번호를 확인한 뒤 Auth 비밀번호를 바꾸고 세션을 종료한다.

## 8. Users

| 기능 | Method | API | 요청 위치 | 요청 항목 | 타입 | 필수 | 제약 | Response | 인증 | 예외처리 |
| --- | :---: | --- | :---: | --- | --- | :---: | --- | --- | --- | --- |
| Get My Profile | GET | `/api/v1/users/me` | - | 없음 | - | - | - | `200` · 스키마 미정의 | HTTPBearer | - |
| Update My Profile | PATCH | `/api/v1/users/me` | Body | `NicknameUpdateRequest` | Pydantic Model | O | - | `200` · 스키마 미정의 | HTTPBearer | `422` · Validation Error · HTTPValidationError |
| Get My Tags | GET | `/api/v1/users/me/tags` | - | 없음 | - | - | - | `200` · 스키마 미정의 | HTTPBearer | - |
| Get My Likes | GET | `/api/v1/users/me/likes` | - | 없음 | - | - | - | `200` · 스키마 미정의 | HTTPBearer | - |
| Get My Categories | GET | `/api/v1/users/me/categories` | - | 없음 | - | - | - | `200` · 스키마 미정의 | HTTPBearer | - |

**기타 설명**

- `GET /api/v1/users/me`: 로그인한 사용자의 이메일과 닉네임을 반환한다.
- `PATCH /api/v1/users/me`: 닉네임을 수정한다. 다른 사용자와 중복이면 409.
- `GET /api/v1/users/me/tags`: 저장된 추천 조건에 포함된 태그 사용 횟수 상위 5개를 반환한다.
- `GET /api/v1/users/me/likes`: feedback_value=3 평가를 최신순으로 서로 다른 식당 3개를 반환한다.
- `GET /api/v1/users/me/categories`: 긍정 평가 식당을 음식 카테고리별로 나눈 비율을 반환한다.

## 9. Conversations & Chat

| 기능 | Method | API | 요청 위치 | 요청 항목 | 타입 | 필수 | 제약 | Response | 인증 | 예외처리 |
| --- | :---: | --- | :---: | --- | --- | :---: | --- | --- | --- | --- |
| Create Conversation | POST | `/api/v1/conversations/` | Body | `MyConversationCreate` | Pydantic Model | O | - | `201` · 스키마 미정의 | HTTPBearer | `422` · Validation Error · HTTPValidationError |
| Create Conversation | POST | `/api/v1/conversations` | Body | `MyConversationCreate` | Pydantic Model | O | - | `201` · 스키마 미정의 | HTTPBearer | `422` · Validation Error · HTTPValidationError |
| Post Message | POST | `/api/v1/conversations/{conversation_id}/messages` | Path | `conversation_id` | uuid | O | - | `200` · MessageOut | HTTPBearer | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Body | `MessageCreate` | Pydantic Model | O | - |  |  |  |
| Get Messages | GET | `/api/v1/conversations/{conversation_id}/messages` | Path | `conversation_id` | uuid | O | - | `200` · array[MessageOut] | HTTPBearer | `422` · Validation Error · HTTPValidationError |
| Save Feedback | POST | `/api/v1/conversations/{conversation_id}/feedback` | Path | `conversation_id` | uuid | O | - | `200` · 스키마 미정의 | HTTPBearer | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Body | `FeedbackRequest` | Pydantic Model | O | - |  |  |  |
| Read Feedback | GET | `/api/v1/conversations/{conversation_id}/feedback` | Path | `conversation_id` | uuid | O | - | `200` · 스키마 미정의 | HTTPBearer | `422` · Validation Error · HTTPValidationError |
| Usage Logs | GET | `/api/v1/conversations/{conversation_id}/usage-logs` | Path | `conversation_id` | uuid | O | - | `200` · 스키마 미정의 | HTTPBearer | `422` · Validation Error · HTTPValidationError |
| Reset Context | POST | `/api/v1/conversations/{conversation_id}/reset-context` | Path | `conversation_id` | uuid | O | - | `200` · MessageOut | HTTPBearer | `422` · Validation Error · HTTPValidationError |
| Regenerate | POST | `/api/v1/conversations/{conversation_id}/regenerate` | Path | `conversation_id` | uuid | O | - | `200` · 스키마 미정의 | HTTPBearer | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Body | `RegenerateRequest` | Pydantic Model | O | - |  |  |  |
| Chat | POST | `/api/v1/conversations/{conversation_id}/chat` | Path | `conversation_id` | uuid | O | - | `200` · 스키마 미정의 | HTTPBearer | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Body | `ChatRequest` | Pydantic Model | O | - |  |  |  |
| Chat Options | GET | `/api/v1/chat/options` | - | 없음 | - | - | - | `200` · 스키마 미정의 | 없음 | - |

**기타 설명**

- `POST /api/v1/conversations/`: 로그인한 사용자 명의로 새 대화를 만든다.
- `POST /api/v1/conversations`: 로그인한 사용자 명의로 새 대화를 만든다.
- `POST /api/v1/conversations/{conversation_id}/messages`: 내 대화에만 메시지를 추가한다.
- `GET /api/v1/conversations/{conversation_id}/messages`: 내 대화의 메시지 목록을 반환한다.
- `POST /api/v1/conversations/{conversation_id}/feedback`: AI 추천 답변에 대한 피드백을 저장한다.
- `GET /api/v1/conversations/{conversation_id}/feedback`: 현재 대화방의 피드백 상태를 반환한다.
- `GET /api/v1/conversations/{conversation_id}/usage-logs`: 대화에서 Gemini를 호출한 사용량 로그를 반환한다.
- `POST /api/v1/conversations/{conversation_id}/reset-context`: 이전 음식 추천 맥락을 초기화한다.  DB의 기존 메시지를 삭제하지 않고 이 지점 이후의 메시지만 Gemini에게 전달한다.
- `POST /api/v1/conversations/{conversation_id}/regenerate`: 마지막 AI 추천 답변을 삭제하고 같은 조건으로 다음 식당을 고른다.
- `POST /api/v1/conversations/{conversation_id}/chat`: 사용자 질문을 저장하고 DB 식당 한 곳을 추천한다.
- `GET /api/v1/chat/options`: 음식점 추천 화면에서 사용할 선택지를 반환한다.  restaurant_categories     한식 / 중식 / 일식 / 양식 / 기타  menu_types     매운거 / 든든한거 / 국물여부  price_levels     인당가격_하 / 인당가격_중 / 인당가격_상

## 10. Admin

| 기능 | Method | API | 요청 위치 | 요청 항목 | 타입 | 필수 | 제약 | Response | 인증 | 예외처리 |
| --- | :---: | --- | :---: | --- | --- | :---: | --- | --- | --- | --- |
| Delete Admin Restaurant | DELETE | `/api/v1/admin/restaurants/{restaurant_id}` | Path | `restaurant_id` | uuid | O | - | `200` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Header | `authorization` | string | null | X | - |  |  |  |
| List Admin Feedback | GET | `/api/v1/admin/feedback` | Query | `page` | integer | X | 최소 1, 기본 `1` | `200` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Query | `page_size` | integer | X | 최소 1, 최대 100, 기본 `20` |  |  |  |
| ↳ |  |  | Header | `authorization` | string | null | X | - |  |  |  |
| List Search Stats | GET | `/api/v1/admin/search-stats` | Header | `authorization` | string | null | X | - | `200` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |

**기타 설명**

- `DELETE /api/v1/admin/restaurants/{restaurant_id}`: 관리자가 식당을 비활성화한다. 행은 삭제하지 않는다.
- `GET /api/v1/admin/feedback`: 관리자 추천 평가 목록과 값별 건수를 반환한다.
- `GET /api/v1/admin/search-stats`: 관리자 검색정보 차트용 집계를 반환한다.

## 11. Admin Log Analysis

| 기능 | Method | API | 요청 위치 | 요청 항목 | 타입 | 필수 | 제약 | Response | 인증 | 예외처리 |
| --- | :---: | --- | :---: | --- | --- | :---: | --- | --- | --- | --- |
| List Api Logs | GET | `/api/v1/admin/api-logs` | Query | `period_start` | date-time | null | X | - | `200` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Query | `period_end` | date-time | null | X | - |  |  |  |
| ↳ |  |  | Query | `endpoint` | string | null | X | - |  |  |  |
| ↳ |  |  | Query | `http_method` | string | null | X | - |  |  |  |
| ↳ |  |  | Query | `status_code` | integer | null | X | - |  |  |  |
| ↳ |  |  | Query | `status_class` | string | null | X | - |  |  |  |
| ↳ |  |  | Query | `error_only` | boolean | X | 기본 `false` |  |  |  |
| ↳ |  |  | Query | `cleaning_run_id` | uuid | null | X | - |  |  |  |
| ↳ |  |  | Query | `page` | integer | X | 최소 1, 기본 `1` |  |  |  |
| ↳ |  |  | Query | `page_size` | integer | X | 최소 1, 최대 100, 기본 `20` |  |  |  |
| ↳ |  |  | Header | `authorization` | string | null | X | - |  |  |  |
| Get Api Log | GET | `/api/v1/admin/api-logs/{api_log_id}` | Path | `api_log_id` | uuid | O | - | `200` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Header | `authorization` | string | null | X | - |  |  |  |
| Create Admin Cleaning Run | POST | `/api/v1/admin/log-cleaning-runs` | Header | `authorization` | string | null | X | - | `201` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Body | `CleaningRunRequest` | Pydantic Model | O | - |  |  |  |
| Get Admin Cleaning Run | GET | `/api/v1/admin/log-cleaning-runs/{run_id}` | Path | `run_id` | uuid | O | - | `200` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Header | `authorization` | string | null | X | - |  |  |  |
| Get Usage Statistics | GET | `/api/v1/admin/api-statistics/usage` | Query | `period_start` | date-time | null | X | - | `200` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Query | `period_end` | date-time | null | X | - |  |  |  |
| ↳ |  |  | Query | `endpoint` | string | null | X | - |  |  |  |
| ↳ |  |  | Query | `http_method` | string | null | X | - |  |  |  |
| ↳ |  |  | Query | `status_code` | integer | null | X | - |  |  |  |
| ↳ |  |  | Query | `status_class` | string | null | X | - |  |  |  |
| ↳ |  |  | Query | `error_only` | boolean | X | 기본 `false` |  |  |  |
| ↳ |  |  | Query | `cleaning_run_id` | uuid | null | X | - |  |  |  |
| ↳ |  |  | Header | `authorization` | string | null | X | - |  |  |  |
| Get Latency Statistics | GET | `/api/v1/admin/api-statistics/latency` | Query | `period_start` | date-time | null | X | - | `200` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Query | `period_end` | date-time | null | X | - |  |  |  |
| ↳ |  |  | Query | `endpoint` | string | null | X | - |  |  |  |
| ↳ |  |  | Query | `http_method` | string | null | X | - |  |  |  |
| ↳ |  |  | Query | `status_code` | integer | null | X | - |  |  |  |
| ↳ |  |  | Query | `status_class` | string | null | X | - |  |  |  |
| ↳ |  |  | Query | `error_only` | boolean | X | 기본 `false` |  |  |  |
| ↳ |  |  | Query | `cleaning_run_id` | uuid | null | X | - |  |  |  |
| ↳ |  |  | Header | `authorization` | string | null | X | - |  |  |  |
| Get Error Statistics | GET | `/api/v1/admin/api-statistics/errors` | Query | `period_start` | date-time | null | X | - | `200` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Query | `period_end` | date-time | null | X | - |  |  |  |
| ↳ |  |  | Query | `endpoint` | string | null | X | - |  |  |  |
| ↳ |  |  | Query | `http_method` | string | null | X | - |  |  |  |
| ↳ |  |  | Query | `status_code` | integer | null | X | - |  |  |  |
| ↳ |  |  | Query | `status_class` | string | null | X | - |  |  |  |
| ↳ |  |  | Query | `error_only` | boolean | X | 기본 `false` |  |  |  |
| ↳ |  |  | Query | `cleaning_run_id` | uuid | null | X | - |  |  |  |
| ↳ |  |  | Header | `authorization` | string | null | X | - |  |  |  |
| Create Admin Log Summary | POST | `/api/v1/admin/log-summaries` | Header | `authorization` | string | null | X | - | `201` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Body | `LogSummaryRequest` | Pydantic Model | O | - |  |  |  |
| Get Admin Log Summary | GET | `/api/v1/admin/log-summaries/{summary_id}` | Path | `summary_id` | uuid | O | - | `200` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Header | `authorization` | string | null | X | - |  |  |  |
| Create Admin Evaluation Run | POST | `/api/v1/admin/summary-evaluation-runs` | Header | `authorization` | string | null | X | - | `201` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Body | `EvaluationRunRequest` | Pydantic Model | O | - |  |  |  |
| Get Admin Evaluation Run | GET | `/api/v1/admin/summary-evaluation-runs/{run_id}` | Path | `run_id` | uuid | O | - | `200` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Header | `authorization` | string | null | X | - |  |  |  |
| Create Admin Improvement Experiment | POST | `/api/v1/admin/improvement-experiments` | Header | `authorization` | string | null | X | - | `201` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Body | `ExperimentCreateRequest` | Pydantic Model | O | - |  |  |  |
| Get Admin Improvement Experiment | GET | `/api/v1/admin/improvement-experiments/{experiment_id}` | Path | `experiment_id` | uuid | O | - | `200` · 스키마 미정의 | Authorization Header | `422` · Validation Error · HTTPValidationError |
| ↳ |  |  | Header | `authorization` | string | null | X | - |  |  |  |

**기타 설명**

- `GET /api/v1/admin/api-logs`: 원본 API 로그 목록을 기간·필터로 조회한다. 본문은 반환하지 않는다.
- `GET /api/v1/admin/api-logs/{api_log_id}`: 원본 로그 한 건과 정제 포함 여부를 반환한다.
- `POST /api/v1/admin/log-cleaning-runs`: 지정 기간의 원본 로그를 정제한다. 원본은 덮어쓰지 않는다.
- `GET /api/v1/admin/log-cleaning-runs/{run_id}`: 정제 실행 결과를 조회한다.
- `POST /api/v1/admin/log-summaries`: 정제된 로그를 LLM으로 요약하고 근거 로그를 남긴다.
- `GET /api/v1/admin/log-summaries/{summary_id}`: 저장된 로그 요약과 근거를 조회한다.
- `POST /api/v1/admin/summary-evaluation-runs`: 요약 품질평가를 실행한다. 사실성·완전성 점수를 저장한다.
- `GET /api/v1/admin/summary-evaluation-runs/{run_id}`: 품질평가 실행 결과를 조회한다.
- `POST /api/v1/admin/improvement-experiments`: 요약 개선 실험을 등록한다.
- `GET /api/v1/admin/improvement-experiments/{experiment_id}`: 개선 실험과 연결된 평가 실행을 조회한다.

## 12. System

| 기능 | Method | API | 요청 위치 | 요청 항목 | 타입 | 필수 | 제약 | Response | 인증 | 예외처리 |
| --- | :---: | --- | :---: | --- | --- | :---: | --- | --- | --- | --- |
| Health | GET | `/health` | - | 없음 | - | - | - | `200` · 스키마 미정의 | 없음 | - |

## 13. 현재 문서화 상태

| 점검 항목 | 상태 | 내용 |
| --- | :---: | --- |
| Endpoint 설명 | O | 다수 Operation에 한국어 `description`이 정의됨 |
| Request Model | O | POST/PATCH 요청 모델과 필수·선택·제약 확인 가능 |
| Nested Model | O | `LogSummaryRequest.filters → LogFilters` 존재 |
| Response Model | △ | 일부는 정의되어 있으나 다수 성공 응답은 `{}` |
| Schema 설명 | O | 주요 Pydantic Schema에 `description`이 정의됨 |
| 필드 Example | △ | 별도 example/examples는 확인되지 않음 |
| Validation Error | O | 다수 검증 대상 Operation에 `422 HTTPValidationError`가 정의됨 |

---

### 표 읽는 방법

- 한 API에 요청 항목이 여러 개 있으면 `↳` 행으로 이어집니다.
- `요청 위치`는 Path / Query / Header / Body를 구분합니다.
- Body는 Pydantic 모델명을 표시하며 세부 필드는 4번 모델 표에서 확인합니다.
- `Response`는 OpenAPI의 2xx 응답과 Schema를 표시합니다.
- `예외처리`는 OpenAPI에 명시된 비-2xx 응답만 표시합니다.