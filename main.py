#!/usr/bin/env python3
"""Git 변경 사항 기반 커밋 메시지 / PR 초안 자동 생성 CLI 도구.

사용 예:
    python main.py commit
    python main.py pr
    python main.py commit --model claude-opus-5-5 --max-tokens 1024 --safe-mode
"""

import argparse
import os
import re
import subprocess
import sys

try:
    import anthropic
except ImportError:
    print("[ERROR] anthropic 패키지가 설치되어 있지 않습니다. 'pip install -r requirements.txt' 를 실행하세요.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 설정값
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "claude-opus-5-5"
API_KEY_ENV = "AI_API_KEY"          # 과제 지정 환경변수
SAFE_MAX_FILES = 10                  # safe-mode: 최대 파일 수
SAFE_MAX_LINES = 200                 # safe-mode: 최대 diff 줄 수
LINE = "-" * 60


# ---------------------------------------------------------------------------
# 로그 헬퍼
# ---------------------------------------------------------------------------
def info(msg):
    print(f"[INFO] {msg}")


def done(msg):
    print(f"[DONE] {msg}")


def error(msg):
    print(f"[ERROR] {msg}")


# ---------------------------------------------------------------------------
# Git 변경 사항 수집
# ---------------------------------------------------------------------------
def run_git(args):
    """git 명령을 실행하고 표준출력을 반환한다. 실패 시 None."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        error("git 명령을 찾을 수 없습니다. Git이 설치되어 있는지 확인하세요.")
        sys.exit(1)

    if result.returncode != 0:
        return None
    return result.stdout


def collect_git_changes():
    """git status / git diff 결과를 수집한다."""
    # Git 저장소인지 확인
    if run_git(["rev-parse", "--is-inside-work-tree"]) is None:
        error("현재 디렉토리는 Git 저장소가 아닙니다. 프로젝트 루트에서 실행하세요.")
        sys.exit(1)

    status = run_git(["status", "--porcelain"]) or ""
    # 작업트리 + 스테이징된 변경을 모두 수집
    diff_unstaged = run_git(["diff"]) or ""
    diff_staged = run_git(["diff", "--staged"]) or ""
    diff = (diff_staged + "\n" + diff_unstaged).strip()

    changed_files = [line[3:] for line in status.splitlines() if line.strip()]
    return status.strip(), diff, changed_files


def current_branch():
    return (run_git(["rev-parse", "--abbrev-ref", "HEAD"]) or "unknown").strip()


# ---------------------------------------------------------------------------
# 보안 / 민감정보 처리 (safe-mode)
# ---------------------------------------------------------------------------
MASK_PATTERNS = [
    # API Key 형태 (sk-..., AKIA..., 긴 토큰 등)
    (re.compile(r"\b(sk-[A-Za-z0-9\-_]{10,})"), "[MASKED_API_KEY]"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "[MASKED_AWS_KEY]"),
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), "[MASKED_EMAIL]"),
    # key=... / token: ... 형태의 값
    (re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[^\s'\"]+"),
     r"\1=[MASKED]"),
]


def apply_safe_mode(diff, changed_files):
    """민감정보 마스킹 + diff 길이 제한."""
    # (A) 민감 패턴 마스킹
    for pattern, repl in MASK_PATTERNS:
        diff = pattern.sub(repl, diff)

    # (B) 파일 수 / 줄 수 제한
    lines = diff.splitlines()
    truncated = False
    if len(lines) > SAFE_MAX_LINES:
        lines = lines[:SAFE_MAX_LINES]
        truncated = True
    diff = "\n".join(lines)
    if truncated:
        diff += f"\n... (safe-mode: {SAFE_MAX_LINES}줄까지만 전송)"

    note = f"safe-mode 활성화: 민감정보 마스킹 + 최대 {SAFE_MAX_LINES}줄 전송"
    return diff, note


# ---------------------------------------------------------------------------
# 프롬프트 구성
# ---------------------------------------------------------------------------
COMMIT_PROMPT = """당신은 숙련된 소프트웨어 엔지니어입니다.
아래 Git 변경 사항을 바탕으로 한국어 커밋 메시지를 작성하세요.

[규칙]
- 첫 줄은 커밋 제목이며 50자 이내(최대 72자)로 작성합니다.
- 제목은 'feat:', 'fix:', 'refactor:', 'docs:', 'chore:' 중 적절한 접두어로 시작합니다.
- 제목 다음 빈 줄을 두고, 본문에 핵심 변경 사항을 '- ' 불릿으로 1~3개 요약합니다.
- 변경된 파일/모듈을 한 번 이상 언급합니다.
- 커밋 메시지 텍스트만 출력하고 다른 설명은 붙이지 마세요.

[변경된 파일 목록]
{files}

[변경 내용(diff)]
{diff}
"""

PR_PROMPT = """당신은 숙련된 소프트웨어 엔지니어입니다.
아래 Git 변경 사항을 바탕으로 한국어 Pull Request 제목과 본문을 작성하세요.

[출력 형식 — 반드시 그대로 지키세요]
첫 줄: PR 제목 (최대 80자, 'feat:'/'fix:' 등 접두어 포함)
둘째 줄: ###BODY###
셋째 줄부터: PR 본문(마크다운)

[PR 본문 규칙]
- 아래 세 섹션 헤더를 반드시 포함합니다: '## Why', '## What', '## How to Test'
- 각 섹션에는 '- ' 불릿을 최소 1개 이상 작성합니다.
- Why: 변경 배경/이유, What: 핵심 변경 사항, How to Test: 테스트 방법

[현재 브랜치]
{branch}

[변경된 파일 목록]
{files}

[변경 내용(diff)]
{diff}
"""


# ---------------------------------------------------------------------------
# AI API 호출
# ---------------------------------------------------------------------------
def call_ai(client, model, max_tokens, temperature, prompt):
    """AI API를 1회 호출하고 텍스트를 반환한다."""
    params = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    # temperature는 일부 모델에서 지원하지 않으므로 지정된 경우에만 전송
    if temperature is not None:
        params["temperature"] = temperature

    try:
        response = client.messages.create(**params)
    except anthropic.BadRequestError as e:
        # temperature 미지원 모델 대응: 제거 후 1회 재시도
        if temperature is not None and "temperature" in str(e).lower():
            info("이 모델은 temperature를 지원하지 않아 기본값으로 재요청합니다.")
            params.pop("temperature", None)
            response = client.messages.create(**params)
        else:
            raise
    return "".join(b.text for b in response.content if b.type == "text").strip()


# ---------------------------------------------------------------------------
# 출력 형식 검증 및 다듬기
# ---------------------------------------------------------------------------
def validate_commit(message):
    lines = message.splitlines()
    title = lines[0] if lines else ""
    if len(title) > 72:
        info(f"커밋 제목이 72자를 초과하여 잘라냅니다({len(title)}자).")
        title = title[:72]
        lines[0] = title
        message = "\n".join(lines)
    elif len(title) > 50:
        info(f"커밋 제목이 권장 길이(50자)를 초과했습니다({len(title)}자).")
    return message


def validate_pr(title, body):
    if len(title) > 80:
        info(f"PR 제목이 80자를 초과하여 잘라냅니다({len(title)}자).")
        title = title[:80]
    for header in ("## Why", "## What", "## How to Test"):
        if header not in body:
            info(f"경고: PR 본문에 '{header}' 섹션이 없습니다.")
    return title, body


# ---------------------------------------------------------------------------
# 명령 처리
# ---------------------------------------------------------------------------
def build_client():
    api_key = os.environ.get(API_KEY_ENV) or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        error(f"{API_KEY_ENV} 환경변수가 설정되지 않았습니다.")
        print(f'  예) (PowerShell) $env:{API_KEY_ENV}="YOUR_KEY"')
        print(f'  예) (bash)       export {API_KEY_ENV}="YOUR_KEY"')
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


def prepare_diff(args):
    status, diff, changed_files = collect_git_changes()
    if not changed_files and not diff:
        info("변경 사항이 없습니다. 생성하지 않고 종료합니다.")
        sys.exit(0)

    info(f"Git status 수집 완료: {len(changed_files)}개 파일 변경 감지")
    info(f"Git diff 수집 완료: {len(diff.splitlines())}줄")

    if args.safe_mode:
        diff, note = apply_safe_mode(diff, changed_files)
        info(note)

    files_text = "\n".join(changed_files) if changed_files else "(목록 없음)"
    return diff, files_text


def cmd_commit(args, client):
    diff, files_text = prepare_diff(args)
    prompt = COMMIT_PROMPT.format(files=files_text, diff=diff)

    info("AI API 요청 중... (호출 횟수: 1회)")
    message = call_ai(client, args.model, args.max_tokens, args.temperature, prompt)
    message = validate_commit(message)

    done("커밋 메시지 생성 완료")
    print(LINE)
    print("--- Commit Message ---")
    print(message)
    print(LINE)


def cmd_pr(args, client):
    info(f"현재 브랜치: {current_branch()}")
    diff, files_text = prepare_diff(args)
    prompt = PR_PROMPT.format(branch=current_branch(), files=files_text, diff=diff)

    info("AI API 요청 중... (호출 횟수: 1회)")
    text = call_ai(client, args.model, args.max_tokens, args.temperature, prompt)

    if "###BODY###" in text:
        title, body = text.split("###BODY###", 1)
    else:
        parts = text.split("\n", 1)
        title, body = parts[0], (parts[1] if len(parts) > 1 else "")
    title, body = title.strip(), body.strip()
    title, body = validate_pr(title, body)

    done("PR 초안 생성 완료")
    print(LINE)
    print("--- PR Title ---")
    print(title)
    print()
    print("--- PR Body ---")
    print(body)
    print(LINE)


# ---------------------------------------------------------------------------
# 진입점
# ---------------------------------------------------------------------------
def build_parser():
    parser = argparse.ArgumentParser(
        description="Git 변경 사항 기반 커밋 메시지 / PR 초안 AI 자동 생성기",
    )
    parser.add_argument("command", choices=["commit", "pr"],
                        help="commit: 커밋 메시지 생성 / pr: PR 제목·본문 생성")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"사용할 AI 모델 (기본값: {DEFAULT_MODEL})")
    parser.add_argument("--temperature", type=float, default=None,
                        help="생성 다양성(0~1). 낮을수록 일관적. 지원 모델에서만 적용")
    parser.add_argument("--max-tokens", type=int, default=1024,
                        help="응답 최대 토큰 수 (기본값: 1024)")
    parser.add_argument("--safe-mode", action="store_true",
                        help="민감정보 마스킹 + diff 길이 제한 후 전송")
    return parser


def main():
    args = build_parser().parse_args()
    client = build_client()
    try:
        if args.command == "commit":
            cmd_commit(args, client)
        else:
            cmd_pr(args, client)
    except anthropic.AuthenticationError:
        error("AI API 인증에 실패했습니다. API Key가 올바른지 확인하세요.")
        sys.exit(1)
    except anthropic.APIConnectionError:
        error("네트워크 오류로 AI API에 연결하지 못했습니다. 인터넷 연결을 확인하세요.")
        sys.exit(1)
    except anthropic.RateLimitError:
        error("AI API 요청 한도를 초과했습니다. 잠시 후 다시 시도하세요.")
        sys.exit(1)
    except anthropic.APIStatusError as e:
        error(f"AI API 오류({e.status_code}): {e.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
