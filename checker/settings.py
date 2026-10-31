"""Settings module - reads environment variables only, no hardcoding."""


def get_model_name():
    """Get the model name from CHECKER_MODEL environment variable.

    Returns:
        str: Model name from env var, empty string if not set.
    """
    return os.environ.get('CHECKER_MODEL', '')


def get_model_url():
    """Get the model URL from CHECKER_MODEL_URL environment variable.

    Returns:
        str: Model URL from env var, default "http://localhost:11434".
    """
    return os.environ.get('CHECKER_MODEL_URL', 'http://localhost:11434')


def findings():
    """Return findings list from environment variable or empty list."""
    val = os.environ.get('CHECKER_FINDINGS', '')
    if not val:
        return []

    # Simple JSON parsing for the findings env var
    try:
        import json
        return json.loads(val)
    except Exception:
        return []
