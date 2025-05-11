import pytest
import datetime as dt
from zoneinfo import ZoneInfo
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from arxiv_fetcher import _jst_range_for_last_cycle, fetch_new_papers, CATEGORIES, BASE_URL

TEST_DATE = dt.datetime(2025, 5, 1, 12, 0, 0)  # 2025/5/1 12:00 UTC

def test_jst_range_for_last_cycle():
    """Test the _jst_range_for_last_cycle function with a fixed date."""
    expected_start = dt.datetime(2025, 4, 30, 10, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo")).timestamp()
    expected_end = dt.datetime(2025, 5, 1, 10, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo")).timestamp()
    
    start, end = _jst_range_for_last_cycle(TEST_DATE)
    
    assert int(start) == int(expected_start)
    assert int(end) == int(expected_end)
    
    start_dt = dt.datetime.fromtimestamp(start, ZoneInfo("Asia/Tokyo"))
    end_dt = dt.datetime.fromtimestamp(end, ZoneInfo("Asia/Tokyo"))
    
    assert start_dt.day == 30
    assert start_dt.month == 4
    assert start_dt.year == 2025
    assert start_dt.hour == 10
    assert start_dt.minute == 0
    
    assert end_dt.day == 1
    assert end_dt.month == 5
    assert end_dt.year == 2025
    assert end_dt.hour == 10
    assert end_dt.minute == 0

@patch('src.arxiv_fetcher.requests.get')
@patch('src.arxiv_fetcher.feedparser.parse')
@patch('src.arxiv_fetcher.dt.datetime')
def test_fetch_new_papers(mock_dt, mock_feedparser, mock_requests):
    """Test the fetch_new_papers function with mocked dependencies."""
    mock_dt.utcnow.return_value = TEST_DATE
    
    mock_response = MagicMock()
    mock_response.text = "mock_feed_content"
    mock_requests.return_value = mock_response
    
    author1 = MagicMock()
    author1.name = "Author One"
    author2 = MagicMock()
    author2.name = "Author Two"
    
    mock_entry = MagicMock()
    mock_entry.id = "http://arxiv.org/abs/2025.12345"
    mock_entry.title = "Test Paper Title"
    mock_entry.link = "http://arxiv.org/abs/2025.12345"
    mock_entry.summary = "This is a test paper summary."
    mock_entry.authors = [author1, author2]
    mock_entry.updated = "2025-05-01T00:00:00Z"
    
    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]
    mock_feedparser.return_value = mock_feed
    
    papers = fetch_new_papers()
    
    assert mock_requests.call_count == len(CATEGORIES)
    
    assert len(papers) == len(CATEGORIES)
    
    for paper in papers:
        assert "id" in paper
        assert "title" in paper
        assert "link" in paper
        assert "summary" in paper
        assert "authors" in paper
        assert "category" in paper
        assert "updated" in paper
        
        assert paper["id"] == "2025.12345"
        assert paper["title"] == "Test Paper Title"
        assert paper["link"] == "http://arxiv.org/abs/2025.12345"
        assert paper["summary"] == "This is a test paper summary."
        assert paper["authors"] == ["Author One", "Author Two"]
        assert paper["updated"] == "2025-05-01T00:00:00Z"

if __name__ == "__main__":
    pytest.main(["-v", __file__])
