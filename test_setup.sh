#!/bin/bash
# 프로젝트 설정 및 의존성 설치 테스트

echo "=== 프로젝트 디렉토리 구조 ==="
ls -la

echo ""
echo "=== Git 커밋 히스토리 ==="
git log --oneline

echo ""
echo "=== Python 버전 확인 ==="
python --version

echo ""
echo "=== 의존성 설치 ==="
pip install -q -r requirements.txt
echo "✓ anthropic 패키지 설치 완료"

echo ""
echo "=== 모듈 임포트 테스트 ==="
python -c "import anthropic; print(f'✓ anthropic {anthropic.__version__} 정상 로드됨')" 2>/dev/null || echo "✗ 임포트 실패"

echo ""
echo "=== 스크립트 실행 권한 ==="
chmod +x main.py
ls -l main.py | awk '{print $1, $NF}'

echo ""
echo "✓ 설정 완료. 아래 명령으로 테스트하세요:"
echo "  export AI_API_KEY='your_key'"
echo "  python main.py commit"
echo "  python main.py pr"
