import pytest
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference import (
    preprocess_query,
    get_keyword_similarity,
    detect_animal_type,
    get_fallback_response
)

def test_preprocess_query():
    # Test basic preprocessing
    assert preprocess_query("What is a dog?") == "what is a dog?"
    assert preprocess_query("How to train a DOG!") == "how to train a dog?"
    
    # Test question mark addition
    assert preprocess_query("what is a dog") == "what is a dog?"
    assert preprocess_query("how to train") == "how to train?"
    
    # Test punctuation removal
    assert preprocess_query("What is a dog?!") == "what is a dog?"
    assert preprocess_query("How to train a dog...") == "how to train a dog?"
    
    # Test whitespace normalization
    assert preprocess_query("  what   is   a   dog  ") == "what is a dog?"

def test_get_keyword_similarity():
    # Test exact match
    assert get_keyword_similarity("dog training", "dog training") == 1.0
    
    # Test partial match
    assert get_keyword_similarity("dog training", "training dog") > 0.5
    
    # Test no match
    assert get_keyword_similarity("dog training", "cat feeding") < 0.5
    
    # Test with stop words
    assert get_keyword_similarity("the dog and the training", "dog training") > 0.5
    
    # Test empty strings
    assert get_keyword_similarity("", "") == 0.0
    assert get_keyword_similarity("dog", "") == 0.0

def test_detect_animal_type():
    # Test dog detection
    assert detect_animal_type("how to train a dog") == "woofieData"
    assert detect_animal_type("puppy care") == "woofieData"
    
    # Test cat detection
    assert detect_animal_type("cat feeding") == "meowData"
    assert detect_animal_type("kitten care") == "meowData"
    
    # Test bird detection
    assert detect_animal_type("parrot training") == "chirpData"
    assert detect_animal_type("bird cage setup") == "chirpData"
    
    # Test fish detection
    assert detect_animal_type("fish tank setup") == "splashData"
    assert detect_animal_type("aquarium maintenance") == "splashData"
    
    # Test small pets detection
    assert detect_animal_type("hamster care") == "smallpetsData"
    assert detect_animal_type("guinea pig diet") == "smallpetsData"
    
    # Test default case
    assert detect_animal_type("general pet care") == "allPetsData"

def test_get_fallback_response():
    # Test food-related queries
    assert "food" in get_fallback_response("what should I feed my dog").lower()
    assert "diet" in get_fallback_response("cat food recommendations").lower()
    
    # Test health-related queries
    assert "health" in get_fallback_response("is my bird sick").lower()
    assert "veterinarian" in get_fallback_response("fish health problems").lower()
    
    # Test training-related queries
    assert "training" in get_fallback_response("how to train my hamster").lower()
    assert "behavior" in get_fallback_response("pet training tips").lower()
    
    # Test general queries
    assert "care" in get_fallback_response("general pet care").lower()
    assert "help" in get_fallback_response("pet advice").lower()

# Mock test for the main ask_question function
@pytest.mark.skip(reason="Requires database setup")
def test_ask_question():
    # This test would require a mock database and embeddings
    # It's marked as skip but included as a template for future implementation
    pass 