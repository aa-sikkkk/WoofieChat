import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app
import chromadb
from chromadb.config import Settings
import shutil
from embedder import loadsinglefile

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest.fixture
def test_db():
    """Create a test database for vector storage."""
    # Create a temporary directory for the test database
    test_db_path = "test_db"
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)
    os.makedirs(test_db_path)
    
    # Create a test client
    client = chromadb.PersistentClient(path=test_db_path)
    
    # Create a test collection
    collection = client.create_collection(
        name="test_collection",
        metadata={"description": "Test collection for unit tests"}
    )
    
    # Load test data
    test_data_path = os.path.join(os.path.dirname(__file__), "test_data.md")
    faq_pairs = loadsinglefile(test_data_path)
    
    # Add test data to collection
    for i, pair in enumerate(faq_pairs):
        text = f"{pair['question']} {pair['answer']}"
        collection.add(
            documents=[text],
            metadatas=[{
                "question": pair["question"],
                "answer": pair["answer"],
                "source": "test_data.md"
            }],
            ids=[f"test_{i}"]
        )
    
    yield collection
    
    # Cleanup after tests
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)

@pytest.fixture
def sample_questions():
    """Provide a list of sample questions for testing."""
    return [
        "How to train a dog?",
        "What should I feed my cat?",
        "How to set up a bird cage?",
        "What size tank for a goldfish?",
        "How to care for a hamster?"
    ]

@pytest.fixture
def sample_answers():
    """Provide a list of sample answers for testing."""
    return [
        "Start with basic commands like sit and stay.",
        "Cats need a balanced diet of wet and dry food.",
        "Choose a cage that's at least twice the bird's wingspan.",
        "A goldfish needs at least 20 gallons of water.",
        "Provide a clean cage, fresh food, and water daily."
    ] 