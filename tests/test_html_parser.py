import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from html_parser import _get_html_soup, extract

SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<body>
    <div class="ltx_authors">
        <span class="ltx_personname">John Doe<sup>1</sup></span>
        <span class="ltx_personname">Jane Smith<sup>2</sup></span>
        <span class="ltx_contact">University of Science</span>
        <span class="ltx_contact">Research Institute</span>
        <span class="ltx_contact">john.doe@example.com</span>
    </div>
    <div class="ltx_figure">
        <img src="figure1.png" alt="Figure 1">
        <figcaption>This is figure 1</figcaption>
    </div>
    <div class="ltx_figure">
        <img src="figure2.png" alt="Figure 2">
        <figcaption>This is figure 2</figcaption>
    </div>
</body>
</html>
"""

@patch('requests.get')
def test_get_html_soup_success(mock_requests):
    """Test _get_html_soup function with a successful response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = SAMPLE_HTML
    mock_requests.return_value = mock_response
    
    status, soup = _get_html_soup("2025.12345")
    
    assert status == 200
    assert soup is not None
    assert len(soup.select('.ltx_figure')) == 2
    assert len(soup.select('.ltx_personname')) == 2
    
    mock_requests.assert_called_once_with("https://arxiv.org/html/2025.12345", timeout=30)

@patch('requests.get')
def test_get_html_soup_failure(mock_requests):
    """Test _get_html_soup function with a failed response."""
    mock_requests.side_effect = Exception("Connection error")
    
    status, soup = _get_html_soup("2025.12345")
    
    assert status == 500
    assert soup is not None
    assert len(soup.select('*')) == 0  # Empty soup

@patch('html_parser._get_html_soup')
def test_extract_success(mock_get_soup):
    """Test extract function with successful HTML parsing."""
    mock_soup = MagicMock()
    mock_soup.select.side_effect = lambda selector: {
        '.ltx_figure > img': [
            MagicMock(__getitem__=lambda self, key: 'figure1.png' if key == 'src' else None),
            MagicMock(__getitem__=lambda self, key: 'figure2.png' if key == 'src' else None)
        ],
        '.ltx_figure > figcaption': [
            MagicMock(get_text=lambda strip=False: 'This is figure 1'),
            MagicMock(get_text=lambda strip=False: 'This is figure 2')
        ]
    }[selector]
    
    authors_section = MagicMock()
    person_spans = [
        MagicMock(find_all=lambda tag_list: [], get_text=lambda sep, strip: 'John Doe'),
        MagicMock(find_all=lambda tag_list: [], get_text=lambda sep, strip: 'Jane Smith')
    ]
    contact_spans = [
        MagicMock(get_text=lambda sep, strip: 'University of Science'),
        MagicMock(get_text=lambda sep, strip: 'Research Institute'),
        MagicMock(get_text=lambda sep, strip: 'john.doe@example.com')
    ]
    authors_section.find_all.side_effect = lambda tag, **kwargs: person_spans if tag == 'span' and kwargs.get('class_') == 'ltx_personname' else contact_spans
    
    mock_soup.find.return_value = authors_section
    
    mock_get_soup.return_value = (200, mock_soup)
    
    result = extract("2025.12345")
    
    assert "figs" in result
    assert "authors" in result
    assert "affils" in result
    
    assert len(result["figs"]) == 2
    assert result["figs"][0]["src"] == "https://arxiv.org/html/2025.12345/figure1.png"
    assert result["figs"][0]["caption"] == "This is figure 1"
    
    assert "John Doe" in result["authors"]
    assert "Jane Smith" in result["authors"]
    assert "University of Science" in result["affils"]
    assert "Research Institute" in result["affils"]
    assert "john.doe@example.com" not in result["affils"]  # Email should be filtered out

@patch('html_parser._get_html_soup')
def test_extract_failure(mock_get_soup):
    """Test extract function with failed HTML retrieval."""
    mock_get_soup.return_value = (404, MagicMock())
    
    result = extract("2025.12345")
    
    assert "figs" in result
    assert "authors" in result
    assert "affils" in result
    assert len(result["figs"]) == 0
    assert len(result["authors"]) == 0
    assert len(result["affils"]) == 0

if __name__ == "__main__":
    pytest.main(["-v", __file__])
