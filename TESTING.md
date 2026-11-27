# 테스트 가이드

이 문서는 도구의 주요 기능을 수동으로 테스트하는 방법을 설명합니다.

## 1. 필수 사전 준비

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. API Key 설정
export AI_API_KEY="sk-ant-YOUR_ACTUAL_KEY"
# 또는 (Windows PowerShell)
$env:AI_API_KEY="sk-ant-YOUR_ACTUAL_KEY"
```

## 2. 테스트 케이스

### 2.1 변경사항 없을 때 (무작동 테스트)

```bash
# 깨끗한 git 상태에서
git status --porcelain
# (출력 없음)

python main.py commit
# 출력: [INFO] 변경 사항이 없습니다. 생성하지 않고 종료합니다.
```

### 2.2 커밋 메시지 생성

```bash
# 파일 생성/수정 후
echo "print('hello')" > test.py
git add test.py

# 커밋 메시지 생성
python main.py commit

# 출력 형식:
# [INFO] Git status 수집 완료: 1개 파일 변경 감지
# [INFO] Git diff 수집 완료: 2줄
# [INFO] AI API 요청 중... (호출 횟수: 1회)
# [DONE] 커밋 메시지 생성 완료
# ----
# --- Commit Message ---
# feat: Add hello world test module
# ...
```

### 2.3 PR 초안 생성

```bash
git checkout -b feature/test
# (변경사항 추가)
python main.py pr

# 출력 형식:
# [INFO] 현재 브랜치: feature/test
# [INFO] AI API 요청 중... (호출 횟수: 1회)
# [DONE] PR 초안 생성 완료
# ----
# --- PR Title ---
# feat: Add test module
# 
# --- PR Body ---
# ## Why
# ...
```

### 2.4 safe-mode 테스트

```bash
# 민감정보가 포함된 파일 추가
cat > config.py << 'EOF'
API_KEY = "sk-proj-123456"
EMAIL = "admin@example.com"
EOF
git add config.py

# --safe-mode 플래그로 실행
python main.py commit --safe-mode

# 출력에서 'safe-mode 활성화' 메시지 확인:
# [INFO] safe-mode 활성화: 민감정보 마스킹 + 최대 200줄 전송
```

### 2.5 옵션 테스트

```bash
# 모델 변경
python main.py commit --model claude-sonnet-5-5

# temperature 지정 (지원 모델에서만)
python main.py commit --temperature 0.3

# max-tokens 지정
python main.py commit --max-tokens 512

# 조합
python main.py pr --model claude-haiku-5-5 --max-tokens 800 --safe-mode
```

### 2.6 에러 처리 테스트

```bash
# API Key 미설정
unset AI_API_KEY
python main.py commit
# 출력: [ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.

# 잘못된 API Key
export AI_API_KEY="invalid-key"
python main.py commit  # (변경사항 필요)
# 출력: [ERROR] AI API 인증에 실패했습니다.

# 네트워크 오류 시뮬레이션
# (일반적으로는 발생하지 않음 - 실제 네트워크 오류 시 처리됨)
```

## 3. 검증 체크리스트

- [ ] 도구가 Git 저장소에서만 실행됨
- [ ] 변경사항 없을 때 안내 메시지 출력 후 종료
- [ ] `git status --porcelain` / `git diff`로 올바른 변경사항 수집
- [ ] API Key 환경변수 미설정 시 명확한 오류 메시지
- [ ] `commit` / `pr` 명령이 각각 AI API를 1회만 호출
- [ ] 커밋 제목 길이 ≤72자 (초과 시 경고)
- [ ] PR 제목 길이 ≤80자 (초과 시 경고)
- [ ] PR 본문에 Why/What/How to Test 헤더 필수 (부재 시 경고)
- [ ] `--safe-mode` 활성화 시 민감정보 마스킹 (API Key, 이메일)
- [ ] `--safe-mode` 활성화 시 diff 최대 200줄로 제한
- [ ] 모든 error/info/done 메시지가 정확하게 출력됨

## 4. 실제 사용 시나리오

```bash
# 1. 로컬 개발 중 변경사항 작성
# (여러 파일 수정)

# 2. 커밋 메시지 생성
python main.py commit

# 3. 출력된 메시지를 복사해서 실제 커밋에 적용
git commit -m "$(python main.py commit | grep -A 5 'Commit Message' | tail -n +2)"

# 4. 브랜치를 푸시 후 GitHub에서 PR 생성
git push origin feature/xxx

# 5. (선택) PR 초안 생성해 참고
python main.py pr
```

## 5. 성능 / 비용 체크

- 도구 1회 실행 ≈ AI API 1회 호출
- 프롬프트 토큰: 보통 500~2000개 (git diff 크기에 따라)
- 출력 토큰: 기본 max-tokens=1024 (지정 시 변경 가능)
- 예상 비용: 1회 ~$0.01 (claude-opus-5-5 기준)
