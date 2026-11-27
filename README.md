# AI 커밋/PR 자동 생성기

Git 변경 사항(`git status`, `git diff`)을 수집해 AI API로 전달하고,
**커밋 메시지**와 **Pull Request 제목/본문 초안**을 자동 생성하는 터미널 CLI 도구입니다.

> 생성된 문구는 최종 정답이 아니며, 사용자가 검토 후 적용합니다.

---

## 1. 요구 사항

- Python 3.10 이상
- Git이 설치되어 있고, **Git이 초기화된 프로젝트 루트**에서 실행
- AI API Key (Anthropic API Key)

## 2. 설치

### 2-1. 가상환경 생성

```bash
# 가상환경 생성
python -m venv .venv
```

### 2-2. 가상환경 활성화

#### Windows PowerShell (권장)
```powershell
# 방법 1: 직접 pip 실행 (스크립트 보안 정책 우회)
.venv\Scripts\python.exe -m pip install -r requirements.txt

# 방법 2: 가상환경 활성화 스크립트 사용
#         (보안 정책 오류 발생 시 "방법 1"을 사용하세요)
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**⚠️ Windows 보안 정책 오류가 발생하는 경우:**
- `Activate.ps1` 스크립트 실행이 차단되는 경우, **방법 1을 사용**하세요.
- 혹은 `cmd.exe` (명령 프롬프트)에서는 아래 명령을 사용하세요:
  ```cmd
  .venv\Scripts\activate.bat
  pip install -r requirements.txt
  ```

#### macOS / Linux
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2-3. 의존성 설치

```bash
# 위 2-2 단계에서 가상환경 활성화 후 실행하면 됩니다.
# (또는 방법 1을 사용하면 Activate.ps1 없이도 설치됩니다)
pip install -r requirements.txt
```

## 3. 환경변수(API Key) 설정

API Key는 **코드에 하드코딩하지 않고 환경변수로만** 관리합니다.

```bash
# macOS / Linux (bash)
export AI_API_KEY="YOUR_KEY"

# Windows PowerShell
$env:AI_API_KEY="YOUR_KEY"
```

> `ANTHROPIC_API_KEY` 환경변수도 대체 키로 인식합니다.

## 4. 사용법

프로젝트 루트에서 변경 사항을 만든 뒤 실행합니다.

```bash
# 커밋 메시지 생성
python main.py commit

# PR 제목/본문 초안 생성
python main.py pr
```

### CLI 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--model` | 사용할 AI 모델 | `claude-opus-5-5` |
| `--temperature` | 생성 다양성(0~1). 지원 모델에서만 적용 | 미지정 |
| `--max-tokens` | 응답 최대 토큰 수 | `1024` |
| `--safe-mode` | 민감정보 마스킹 + diff 길이 제한 후 전송 | 꺼짐 |

```bash
python main.py commit --model claude-opus-5-5 --max-tokens 800 --safe-mode
python main.py pr --temperature 0.4
```

## 5. 출력 예시

### 커밋 메시지

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

### PR 초안

```
[INFO] 현재 브랜치: feature/commit-pr-generator
[INFO] AI API 요청 중... (호출 횟수: 1회)
[DONE] PR 초안 생성 완료
------------------------------------------------------------
--- PR Title ---
feat: 커밋/PR 자동 생성 기능 추가

--- PR Body ---
## Why
- 커밋 메시지와 PR 설명 작성에 드는 시간을 줄이기 위해 자동화 도구가 필요했습니다.

## What
- git status/diff 수집 및 AI 입력 컨텍스트 전달 로직 추가
- commit / pr 명령 구현

## How to Test
- export AI_API_KEY="YOUR_KEY"
- python main.py commit / python main.py pr 실행 후 출력 확인
------------------------------------------------------------
```

## 6. 동작 방식

1. `git status`, `git diff`로 변경 사항을 수집합니다.
2. 변경 사항이 없으면 안내 후 종료합니다.
3. (옵션) `--safe-mode`에서 민감정보를 마스킹하고 diff 길이를 제한합니다.
4. 커밋/PR 양식을 포함한 프롬프트를 구성해 **AI API를 1회 호출**합니다.
5. 길이·형식 규칙(커밋 제목 ≤72자, PR 제목 ≤80자, PR 섹션 헤더 필수)을 검증·후처리합니다.
6. 구분선/헤더로 구획을 나눠 터미널에 출력합니다. (사용자가 복사해 적용)

## 7. 가상환경 활성화 문제 해결

### Windows에서 "Activate.ps1을 실행할 수 없다"는 오류

PowerShell 보안 정책이 스크립트 실행을 차단할 수 있습니다.

**해결 방법:**

1. **pip를 직접 호출 (권장 - 스크립트 우회)**
   ```powershell
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
   이 방법은 가상환경을 활성화할 필요 없이 직접 패키지를 설치합니다.

2. **cmd.exe (명령 프롬프트) 사용**
   ```cmd
   .venv\Scripts\activate.bat
   pip install -r requirements.txt
   ```

3. **PowerShell 실행 정책 임시 변경 (고급)**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   .venv\Scripts\Activate.ps1
   ```
   현재 세션에서만 정책이 적용됩니다.

### 가상환경 활성화 확인
정상적으로 활성화되면 프롬프트가 다음과 같이 변합니다:
```
(.venv) PS C:\Users\USER\Desktop\cody_b3_2>
```

## 8. 주의사항 (운영 관점)

- **민감정보**: `--safe-mode`를 사용하면 API Key/이메일 등 패턴을 마스킹하고,
  diff를 최대 10개 파일·200줄로 제한해 전송합니다. 민감정보가 포함될 수 있는
  저장소에서는 `--safe-mode` 사용을 권장합니다.
- **비용/요청 제한**: 과도한 비용을 막기 위해 `commit`/`pr` 명령은 각각
  **AI API를 1회만 호출**하며, 로그에 호출 횟수를 출력합니다.
- 생성된 커밋/PR 문구는 초안입니다. 반드시 검토 후 적용하세요.
- 이 도구는 초안 **텍스트 출력**까지만 수행하며, `git push`나 원격 PR 생성은 하지 않습니다.
