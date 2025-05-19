import pytest
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from embedder import loadsinglefile, LoadData, embeddata
import chromadb
from chromadb.config import Settings

def test_loadsinglefile():
    # Test loading a markdown file
    test_file = os.path.join(os.path.dirname(__file__), "test_data.md")
    faq_pairs = loadsinglefile(test_file)
    
    assert isinstance(faq_pairs, list)
    assert len(faq_pairs) > 0
    assert all(isinstance(pair, dict) for pair in faq_pairs)
    assert all("question" in pair and "answer" in pair for pair in faq_pairs)

def test_LoadData():
    # Test loading data from a directory
    test_dir = os.path.dirname(__file__)
    faq_pairs = LoadData(test_dir)
    
    assert isinstance(faq_pairs, list)
    assert len(faq_pairs) > 0
    assert all(isinstance(pair, dict) for pair in faq_pairs)
    assert all("question" in pair and "answer" in pair and "source" in pair for pair in faq_pairs)

@pytest.mark.skip(reason="Requires database setup")
def test_embeddata():
    # This test would require a mock database
    # It's marked as skip but included as a template for future implementation
    pass 