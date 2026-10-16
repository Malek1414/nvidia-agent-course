from src.retry_policy import with_retry


def test_retry_returns_value():
    assert with_retry(lambda: 42) == 42
