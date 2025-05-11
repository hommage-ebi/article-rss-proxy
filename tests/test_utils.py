import datetime as dt
from unittest.mock import patch

class MockDatetime(dt.datetime):
    """A datetime class that can be mocked for testing."""
    
    @classmethod
    def now(cls, tz=None):
        """Return a fixed datetime for testing."""
        return dt.datetime(2025, 5, 1, 12, 0, 0, tzinfo=dt.timezone.utc)

def patch_datetime_now(test_func):
    """Decorator to patch datetime.now in the rss_generator module."""
    return patch('src.rss_generator.dt.datetime', MockDatetime)(test_func)
