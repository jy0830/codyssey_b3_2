# AI 커밋/PR 자동 생성기

Git 변경 사항(`git status`, `git diff`)을 수집해 AI API로 전달하고,
**커밋 메시지**와 **Pull Request 제목/본문 초안**을 자동 생성하는 터미널 CLI 도구입니다.

> 생성된 문구는 최종 정답이 아니며, 사용자가 검토 후 적용합니다.

---

## 1. 요구 사항

- Python 3.10 이상
- Git이 설치되어 있고, **Git이 초기화된 프로젝트 루트**에서 실행
- Codyssey에서 발급받은 Claude 호환 API Key (`sk-cody-...`)

## 2. 설치

### 2-1. 가상환경 생성

```bash
# 가상환경 생성
python -m venv .venv
```

### 2-2. 의존성 설치

**Windows PowerShell:**
```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS / Linux:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

또는 직접 설치:
```bash
pip install -r requirements.txt
```

## 3. API Key 발급 및 환경변수 설정

### 3-1. API Key 준비

이 도구는 Codyssey 게이트웨이(`https://copa.codyssey.kr`)를 통해 Claude API를 호출합니다.
Codyssey에서 발급받은 가상 키(`sk-cody-...`)를 준비하세요.

### 3-2. 환경변수 설정

**실행 전에 반드시 환경변수를 설정해야 합니다.**

API Key는 **코드에 하드코딩하지 않고 환경변수로만** 관리합니다.

| 환경변수 | 설명 | 필수 |
|----------|------|------|
| `AI_API_KEY` | 발급받은 가상 키 (`sk-cody-...`) | 필수 |
| `AI_BASE_URL` | 게이트웨이 주소 | 선택 (기본값 `https://copa.codyssey.kr`) |

### Windows PowerShell
```powershell
$env:AI_API_KEY="YOUR_API_KEY"
```

### macOS / Linux (bash)
```bash
export AI_API_KEY="YOUR_API_KEY"
```

> 환경변수는 현재 터미널 창에서만 유지됩니다. 새 터미널을 열면 다시 설정하세요.

## 4. 사용법

프로젝트 루트에서 변경 사항을 만든 뒤, **환경변수 설정 후 실행**합니다.

### 커밋 메시지 생성

**Windows PowerShell:**
```powershell
$env:AI_API_KEY="YOUR_API_KEY"
.venv\Scripts\python.exe main.py commit
```

**macOS / Linux:**
```bash
export AI_API_KEY="YOUR_API_KEY"
python main.py commit
```

### PR 제목/본문 초안 생성

**Windows PowerShell:**
```powershell
$env:AI_API_KEY="YOUR_API_KEY"
.venv\Scripts\python.exe main.py pr
```

**macOS / Linux:**
```bash
export AI_API_KEY="YOUR_API_KEY"
python main.py pr
```

### CLI 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--model` | 사용할 AI 모델 | `claude-sonnet-4` |
| `--temperature` | 생성 다양성(0~1). 낮을수록 일관적 | `0.3` |
| `--max-tokens` | 응답 최대 토큰 수 | `1024` |
| `--safe-mode` | 민감정보 마스킹 + diff 길이 제한 후 전송 | 꺼짐 |

**사용 예시:**
```bash
python main.py commit --model claude-haiku-4 --max-tokens 800 --safe-mode
python main.py pr --temperature 0.7
```

**모델 예시 (Codyssey 게이트웨이 기준):**
- `claude-sonnet-4` (기본)
- `claude-haiku-4` (더 빠르고 가벼움)

> 사용할 수 있는 모델은 Codyssey 문서의 모델 테이블을 확인하세요. 없는 모델을 지정하면 404 오류와 함께 안내 메시지가 출력됩니다.

## 5. 출력 예시

### 커밋 메시지 생성 예시

```
[INFO] Git status 수집 완료: 3개 파일 변경 감지
[INFO] Git diff 수집 완료: 128줄
[INFO] AI API 요청 중... (호출 횟수: 1회)
[DONE] 커밋 메시지 생성 완료
------------------------------------------------------------
--- Commit Message ---
feat: Git 변경 사항 기반 커밋 메시지 자동 생성 기능 추가

- git status/diff 결과를 수집해 AI 입력 컨텍스트로 전달
- 커밋 메시지 템플릿(feat/fix 등) 생성 규칙 적용
- API Key 미설정 시 안내 메시지 및 예외 처리 개선
------------------------------------------------------------
```

### PR 초안 생성 예시

```
[INFO] 현재 브랜치: feature/commit-pr-generator
[INFO] Git status 수집 완료: 3개 파일 변경 감지
[INFO] Git diff 수집 완료: 128줄
[INFO] AI API 요청 중... (호출 횟수: 1회)
[DONE] PR 초안 생성 완료
------------------------------------------------------------
--- PR Title ---
feat: 커밋/PR 자동 생성 기능 추가

--- PR Body ---
## Why
- 팀 협업 시 커밋 메시지와 PR 설명 작성에 시간이 소요되어 자동 생성 도구가 필요했습니다.
- Git 변경 사항을 기반으로 일관된 형식의 요약 텍스트를 생성해 리뷰 효율을 높이고자 했습니다.

## What
- git status/diff 수집 및 AI 입력 컨텍스트 전달 로직 추가
- 커밋 메시지 자동 생성 기능(python main.py commit) 구현
- PR 제목/본문 자동 생성 기능(python main.py pr) 구현

## How to Test
- 환경변수 설정: export AI_API_KEY="YOUR_KEY"
- 커밋 메시지 생성: python main.py commit
- PR 초안 생성: python main.py pr
- 결과로 출력된 PR 본문이 Why/What/How to Test 구조와 길이 규칙을 만족하는지 확인
------------------------------------------------------------
```

### 환경변수 미설정 오류 예시

```
[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.
  예) (PowerShell) $env:AI_API_KEY="YOUR_KEY"
  예) (bash)       export AI_API_KEY="YOUR_KEY"
```

### 변경 사항이 없는 경우 예시

```
[INFO] 변경 사항이 없습니다. 생성하지 않고 종료합니다.
```

## 6. 동작 방식

1. Git 저장소 확인 후 `git status`, `git diff`로 변경 사항을 수집합니다.
2. 변경 사항이 없으면 안내 메시지를 출력하고 종료합니다.
3. (옵션) `--safe-mode`에서 민감정보를 마스킹하고 diff 길이를 제한합니다.
4. 커밋/PR 양식을 포함한 프롬프트를 구성해 **AI API를 1회 호출**합니다.
5. 길이·형식 규칙(커밋 제목 ≤72자, PR 제목 ≤80자, PR 섹션 헤더 필수)을 검증·후처리합니다.
6. 구분선/헤더로 구획이 나뉘어 터미널에 출력됩니다. (사용자가 복사해 적용)

## 7. 보안 주의사항

### 민감정보 보호

**문제:** git diff에 API Key, 개인정보, 비밀번호 등 민감정보가 포함될 수 있습니다.

**해결 방법:**

1. **`--safe-mode` 옵션 사용 (권장)**
   ```bash
   python main.py commit --safe-mode
   python main.py pr --safe-mode
   ```
   - API Key 형태(sk-..., AKIA...) 등 패턴 자동 마스킹
   - diff를 최대 200줄로 제한하여 전송
   - 민감정보가 포함될 가능성이 있는 저장소에서 필수 권장

2. **민감 파일 사전 제외**
   - `.gitignore`에 민감 정보 파일 추가
   - `git add`하기 전에 diff 검토

### 비용 및 요청 횟수 제한

- `commit`/`pr` 각 명령은 AI API를 **1회만 호출**하여 비용을 제어합니다.
- 로그에 호출 횟수를 명시하므로 모니터링이 용이합니다.
- 과도한 사용을 방지하기 위해 1회 호출 시 max_tokens를 1024로 제한합니다.

## 8. 주의사항

- 생성된 커밋/PR 문구는 초안입니다. **반드시 검토 후 적용하세요.**
- 이 도구는 초안 **텍스트 출력**까지만 수행합니다. `git commit`, `git push`, GitHub PR 생성 등은 사용자가 수동으로 수행해야 합니다.
- API Key는 절대 코드에 하드코딩하지 마세요. 환경변수로만 관리하세요.
- 발급받은 가상 키는 Codyssey 이용 규정에 맞게 사용하고, 다른 사람과 공유하지 마세요.
