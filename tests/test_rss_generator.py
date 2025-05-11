import pytest
import os
import sys
import datetime as dt
from unittest.mock import patch, MagicMock
import pathlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from test_utils import patch_datetime_now

from rss_generator import _format_paper_entry, _format_other_papers_description, generate

SAMPLE_PAPER = {
    "id": "2025.12345",
    "title": "Test Paper Title",
    "link": "http://arxiv.org/abs/2025.12345",
    "summary": "This is a test paper summary.",
    "summary_ja": "これはテスト論文の要約です。",
    "authors": ["Author One", "Author Two"],
    "category": "cs.AI",
    "updated": dt.datetime(2025, 5, 1, 0, 0, 0, tzinfo=dt.timezone.utc),
    "affils": ["University of Science", "Research Institute"],
    "figs": [
        {"src": "https://arxiv.org/html/2025.12345/figure1.png", "caption": "This is figure 1"},
        {"src": "https://arxiv.org/html/2025.12345/figure2.png", "caption": "This is figure 2"}
    ]
}

SAMPLE_FILTERED_PAPERS = [SAMPLE_PAPER]
SAMPLE_OTHER_PAPERS = [
    {
        "id": "2025.54321",
        "title": "Another Test Paper",
        "link": "http://arxiv.org/abs/2025.54321",
        "summary": "This is another test paper summary.",
        "authors": ["Author Three"],
        "category": "cs.CL",
        "updated": dt.datetime(2025, 5, 1, 0, 0, 0, tzinfo=dt.timezone.utc)
    }
]

def test_format_paper_entry_without_translation():
    """Test _format_paper_entry function without translation."""
    result = _format_paper_entry(SAMPLE_PAPER, with_translation=False)
    
    assert "[Test Paper Title](http://arxiv.org/abs/2025.12345)" in result
    assert "This is a test paper summary." in result
    assert "これはテスト論文の要約です。" not in result

def test_format_paper_entry_with_translation():
    """Test _format_paper_entry function with translation."""
    result = _format_paper_entry(SAMPLE_PAPER, with_translation=True)
    
    assert "[Test Paper Title](http://arxiv.org/abs/2025.12345)" in result
    assert "This is a test paper summary." not in result
    assert "これはテスト論文の要約です。" in result

def test_format_other_papers_description():
    """Test _format_other_papers_description function."""
    result = _format_other_papers_description(SAMPLE_OTHER_PAPERS)
    
    assert "[Another Test Paper](http://arxiv.org/abs/2025.54321)" in result
    assert "This is another test paper summary." in result
    assert "---" in result  # Separator between papers

@patch_datetime_now
def test_generate():
    """Test generate function with a simplified approach using MockDatetime."""
    
    with patch('pathlib.Path') as mock_path_class, \
         patch('feedgen.feed.FeedGenerator.rss_file') as mock_rss_file:
        
        mock_path = MagicMock()
        mock_path_class.return_value = mock_path
        mock_path.parent = MagicMock()
        
        generate(SAMPLE_FILTERED_PAPERS, SAMPLE_OTHER_PAPERS, "test_output.xml")
        
        mock_path.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_rss_file.assert_called_once_with(mock_path)

if __name__ == "__main__":
    pytest.main(["-v", __file__])
