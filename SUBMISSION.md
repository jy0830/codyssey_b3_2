# B3-2 과제 제출 요약

## 과제 목표

Git 변경 사항(`git status`, `git diff`)을 AI API로 전달하여 커밋 메시지와 PR 초안을 자동 생성하는 Python CLI 도구 개발.

## 완성된 결과물

### 1. ✅ AI API 연동 및 자동화 흐름

**파일**: [main.py](main.py)

- **git 변경사항 수집**
  - `git status --porcelain`: 변경된 파일 목록
  - `git diff --cached` + `git diff`: 전체 변경 내용
  - 변경사항 없을 시 안내 메시지 출력 후 종료

- **AI API 호출**
  - 환경변수 `AI_API_KEY`로 API Key 관리 (하드코딩 금지)
  - Anthropic SDK 사용 (`claude-opus-5-5` 기본 모델)
  - 명령당 1회 호출 (비용 최소화)
  - 에러 처리: 인증, 네트워크, API 오류 명시

- **CLI 옵션**
  ```
  --model            AI 모델 선택 (기본: claude-opus-5-5)
  --temperature      생성 다양성 (0~1, 선택)
  --max-tokens       응답 최대 토큰 (기본: 1024)
  --safe-mode        민감정보 마스킹 + diff 길이 제한
  ```

### 2. ✅ GitHub 리포지토리

- **로컬 Git 저장소** (c:\Users\USER\Desktop\cody_b3_2)
- **커밋 히스토리**
  - Initial commit: 핵심 구현 (main.py, requirements.txt, README.md, .gitignore)
  - Commit 2: 테스트 가이드 (TESTING.md)
- **GitHub 푸시**: 사용자가 GitHub CLI 또는 `git remote add` + `git push`로 완료 가능

### 3. ✅ 사용 가이드 (README.md)

- **설치 방법**: 가상환경 + pip install
- **환경변수 설정**: AI_API_KEY 설정 방법 (bash, PowerShell)
- **실행 예시**:
  ```bash
  python main.py commit
  python main.py pr
  python main.py commit --safe-mode
  ```
- **출력 예시**: 커밋 메시지, PR 초안 샘플 포함
- **주의사항**:
  - 민감정보: `--safe-mode`로 API Key/이메일 자동 마스킹
  - 비용/횟수: 명령당 1회 호출, 로그에 호출 횟수 기재
  - 생성된 문구는 초안이므로 검토 후 적용

---

## 주요 기능 체크리스트

### 1. Git 변경 사항 수집 ✅
- [x] git status 결과 수집 (변경된 파일 목록)
- [x] git diff 결과 수집 (변경 내용)
- [x] 변경사항 없을 경우 안내 메시지 출력 후 종료
- [x] Git 저장소 아닌 경우 오류 처리

### 2. AI API 연동 ✅
- [x] API Key는 환경변수(`AI_API_KEY`) 관리, 하드코딩 금지
- [x] API 호출 성공 시 커밋/PR 텍스트 터미널 출력
- [x] API 호출 실패 시 오류 원인 출력 (인증, 네트워크, API 오류)
- [x] CLI 옵션으로 모델, temperature, max_tokens 변경 가능
- [x] 옵션 기본값 설정

### 3. 커밋 메시지 자동 생성 ✅
- [x] commit 명령 실행 → 커밋 메시지 생성
- [x] 메시지는 변경 사항 요약 기반
- [x] 첫 줄 커밋 제목 필수 (feat:/fix: 등 접두어)
- [x] 본문에 변경된 파일/모듈 1~3개 언급
- [x] 본문에 핵심 변경사항 1~2개를 불릿으로 요약
- [x] 터미널 출력으로 사용자가 복사 가능

### 4. PR 제목/본문 자동 생성 ✅
- [x] pr 명령으로 PR 초안 생성
- [x] PR 본문 템플릿 구조 (Why/What/How to Test)
- [x] 각 섹션 최소 1개 이상의 불릿 포함
- [x] PR 제목 1줄 출력
- [x] PR 제목 + 본문 함께 터미널 출력

### 5. 출력 형식 검증 및 다듬기 ✅
- [x] 커밋 제목: 72자 초과 시 경고 및 절단
- [x] PR 제목: 80자 초과 시 경고 및 절단
- [x] PR 본문: Why/What/How to Test 헤더 필수성 검증 (부재 시 경고)
- [x] 구분선/헤더로 구획 표시

### 6. 리포지토리 및 문서화 ✅
- [x] GitHub 로컬 저장소 생성 및 커밋
- [x] README.md 포함:
  - [x] 설치 및 실행 방법
  - [x] 환경변수(API Key) 설정 방법
  - [x] 커밋/PR 생성 명령 사용 예시
  - [x] 출력 예시 (커밋 메시지 / PR 본문)
  - [x] 민감정보 처리 안내 (safe-mode)
  - [x] 비용/요청 횟수 제한 안내

---

## 과제 학습 목표 달성도

### 1. AI API를 REST API 방식으로 연동 ✅
- 요청 구성: 프롬프트 + 모델 + 옵션 파라미터
- 응답 처리: content 블록에서 텍스트 추출
- 예외 대응: AuthenticationError, APIConnectionError, RateLimitError, APIStatusError 모두 처리

### 2. 파라미터가 결과 품질에 미치는 영향 이해 ✅
- `temperature`: 생성 다양성 제어 (0~1)
- `max_tokens`: 응답 길이 상한선
- 모델 선택: 능력 vs 비용 트레이드오프
- 프롬프트 설계: 양식 지정 + 한국어 명시 → 출력 품질 향상

### 3. Git 명령 결과를 프로그램 입력으로 연결 ✅
- `git status --porcelain`: 파일 목록 파싱
- `git diff`: 변경 내용 수집 및 프롬프트에 포함
- 프로세스 호출 + 텍스트 처리로 자동화

### 4. Commit/PR 양식 + 프롬프트 설계 ✅
- Commit 프롬프트: feat:/fix: 접두어, 제목(50자), 본문(불릿) 명시
- PR 프롬프트: Why/What/How to Test 헤더 필수, 한국어 명시
- 결과: AI가 요구사항에 맞는 형식의 초안 생성

### 5. 생성된 텍스트 검증 및 다듬기 ✅
- 길이 검증: 커밋 제목 72자, PR 제목 80자
- 형식 검증: PR 헤더 필수성 체크
- 후처리: 초과 길이 절단 + 경고 메시지

---

## 디렉토리 구조

```
cody_b3_2/
├── main.py                  # 메인 CLI 도구 (410줄)
├── requirements.txt         # Python 의존성 (anthropic)
├── README.md               # 사용 가이드 (민감정보/비용 포함)
├── TESTING.md              # 테스트 가이드
├── .gitignore              # Python/환경 파일 제외
├── .git/                   # Git 저장소 (2개 커밋)
└── 예제 파일들             # example_feature.py, test_safe_mode.py (테스트용)
```

---

## 실행 흐름 (사용자 관점)

```bash
# 1. 준비
export AI_API_KEY="sk-ant-YOUR_KEY"

# 2. 개발 작업
echo "new feature" > feature.py
git add feature.py

# 3. 커밋 메시지 자동 생성
python main.py commit
# 출력: [INFO] ... 
#       [DONE] 커밋 메시지 생성 완료
#       --- Commit Message ---
#       feat: Add new feature module
#       ...

# 4. PR 초안 생성 (브랜치 푸시 후)
git push origin feature/xxx
python main.py pr
# 출력: ... PR Title ... PR Body ...

# 5. 사용자가 복사해서 GitHub에서 PR 생성
```

---

## 과제 요구사항 충족 정리

| 요구사항 | 구현 | 위치 |
|---------|------|------|
| Git 변경사항 수집 | ✅ | main.py:collect_git_changes() |
| AI API 연동 | ✅ | main.py:call_ai() + build_client() |
| 환경변수 관리 | ✅ | main.py:build_client() (AI_API_KEY) |
| 커밋 메시지 생성 | ✅ | main.py:cmd_commit() |
| PR 제목/본문 생성 | ✅ | main.py:cmd_pr() |
| 형식 검증 | ✅ | main.py:validate_commit/pr() |
| CLI 옵션 | ✅ | main.py:build_parser() |
| safe-mode (민감정보) | ✅ | main.py:apply_safe_mode() |
| 에러 처리 | ✅ | main.py:main() 예외 처리 |
| README 문서 | ✅ | README.md |
| GitHub 저장소 | ✅ | .git + 2개 커밋 |

---

## 다음 단계 (사용자 작업)

1. **API Key 준비**: Anthropic 콘솔에서 API Key 발급
2. **GitHub 푸시**:
   ```bash
   cd c:\Users\USER\Desktop\cody_b3_2
   git remote add origin https://github.com/YOUR_USERNAME/cody-b3-2.git
   git branch -M main
   git push -u origin main
   ```
3. **실제 사용**: README.md 참조하여 `python main.py commit/pr` 실행

---

**작성 완료**: 2026-11-27 (Claude Opus 4.8)
