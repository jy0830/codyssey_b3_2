"""safe-mode 테스트: 민감정보가 포함된 diff 예제."""

# API 키와 이메일이 포함된 설정
CONFIG = {
    "api_key": "sk-proj-abc123def456xyz789",
    "aws_key": "AKIAIOSFODNN7EXAMPLE",
    "email": "admin@company.com",
    "token": "ghp_1234567890abcdefghijklmnop",
}

def setup_connection(api_key="secret-123"):
    """외부 서비스 연결."""
    print(f"Connecting with key: {api_key}")
    return True
