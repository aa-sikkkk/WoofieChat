from sentence_transformers import SentenceTransformer, util
import chromadb
from chromadb.config import Settings
import re
import time
import sys
from typing import List, Dict, Any


def load_vector_store(collection_name="allPetsData"):
    """
    Load the vector store collection.

    Args:
        collection_name: Name of the collection to load. Default is the combined collection.

    Returns:
        The ChromaDB collection
    """
    chroma_client = chromadb.PersistentClient(path="db")

    # Check if the collection exists, if not, return the default collection
    try:
        collection = chroma_client.get_collection(name=collection_name)
    except (ValueError, chromadb.errors.NotFoundError):
        # Fallback to woofieData if the requested collection doesn't exist
        try:
            collection = chroma_client.get_collection(name="woofieData")
        except (ValueError, chromadb.errors.NotFoundError):
            # If no collections exist, raise an error
            raise ValueError("No vector database collections found. Please run embedder.py first.")

    return collection


def load_embedder():
    """Load the sentence transformer model for embeddings"""
    # Using a more powerful model for better semantic understanding
    return SentenceTransformer("all-MiniLM-L6-v2")


def preprocess_query(query: str) -> str:
    """Clean and normalize the user query for better matching."""
    # Convert to lowercase
    query = query.lower()
    # Remove punctuation except question marks
    query = re.sub(r'[^\w\s\?]', '', query)
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query).strip()
    # Add question mark if missing and query is a question
    question_starters = ['what', 'how', 'why', 'when', 'where', 'who', 'can', 'should', 'is', 'are', 'do', 'does']
    if not query.endswith('?') and any(query.startswith(starter) for starter in question_starters):
        query += '?'
    return query


def get_keyword_similarity(query: str, stored_question: str) -> float:
    """Calculate keyword overlap similarity between query and stored question."""
    query_words = set(query.lower().split())
    stored_words = set(stored_question.lower().split())

    # Remove common stop words
    stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
                 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'like', 'from'}
    query_words = query_words - stop_words
    stored_words = stored_words - stop_words

    if not query_words or not stored_words:
        return 0.0

    # Calculate Jaccard similarity (intersection over union)
    intersection = len(query_words.intersection(stored_words))
    union = len(query_words.union(stored_words))
    return intersection / union


def rerank_results(query: str, results: List[Dict[str, Any]],
                  embedder: SentenceTransformer) -> List[Dict[str, Any]]:
    """Rerank results using a combination of semantic and keyword similarity."""
    if not results:
        return []

    # Get embeddings for more accurate comparison
    query_embedding = embedder.encode(query, convert_to_tensor=True)

    for result in results:
        # Get semantic similarity using cosine similarity
        question_embedding = embedder.encode(result['question'], convert_to_tensor=True)
        semantic_sim = util.pytorch_cos_sim(query_embedding, question_embedding).item()

        # Get keyword similarity
        keyword_sim = get_keyword_similarity(query, result['question'])

        # Combined score (weighted average)
        # Adjust weights based on what works better for your dataset
        combined_score = 0.7 * semantic_sim + 0.3 * keyword_sim

        # Update the score
        result['original_score'] = result['score']
        result['score'] = combined_score

    # Sort by the new combined score (higher is better)
    return sorted(results, key=lambda x: x['score'], reverse=True)


def detect_animal_type(query: str) -> str:
    """
    Detect which animal type the query is about.

    Args:
        query: The user's question

    Returns:
        The collection name to use for the query
    """
    query = query.lower()

    # Define keywords for each animal type
    dog_keywords = ['dog', 'puppy', 'canine', 'breed', 'bark', 'leash', 'walk']
    cat_keywords = ['cat', 'kitten', 'feline', 'meow', 'purr', 'litter']
    bird_keywords = ['bird', 'parrot', 'parakeet', 'budgie', 'cockatiel', 'feather', 'cage', 'avian', 'beak', 'wing']
    fish_keywords = ['fish', 'aquarium', 'tank', 'goldfish', 'betta', 'guppy', 'tetra', 'swim', 'gill', 'fin']
    small_pet_keywords = ['hamster', 'gerbil', 'guinea pig', 'rabbit', 'ferret', 'rat', 'mouse', 'chinchilla', 'hedgehog']

    # Check for matches
    if any(keyword in query for keyword in dog_keywords):
        return "woofieData"
    elif any(keyword in query for keyword in cat_keywords):
        return "meowData"
    elif any(keyword in query for keyword in bird_keywords):
        return "chirpData"
    elif any(keyword in query for keyword in fish_keywords):
        return "splashData"
    elif any(keyword in query for keyword in small_pet_keywords):
        return "smallpetsData"

    # Default to the combined collection if no specific animal is detected
    return "allPetsData"


def show_loading_indicator():
    """Display a simple loading indicator without technical details"""
    print("\nThinking", end="", flush=True)
    for _ in range(3):
        time.sleep(0.3)
        print(".", end="", flush=True)
    print("\n")


def ask_question(query: str, top_k: int = 5, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Search for answers to the user's question with improved accuracy.

    Args:
        query: The user's question
        top_k: Number of initial results to retrieve
        confidence_threshold: Minimum score to consider a result relevant

    Returns:
        List of relevant answers with their metadata
    """
    # Show a simple loading indicator
    show_loading_indicator()

    # Preprocess the query
    processed_query = preprocess_query(query)

    # Detect which animal type the query is about (silently)
    collection_name = detect_animal_type(processed_query)

    # Load models and data
    embedder = load_embedder()

    try:
        collection = load_vector_store(collection_name)
    except (ValueError, chromadb.errors.NotFoundError):
        # If the specific collection doesn't exist, fall back to the default (silently)
        collection = load_vector_store("woofieData")

    # Encode the query
    query_embedding = embedder.encode(processed_query).tolist()

    # Get more initial results to allow for better reranking
    # We'll filter them later
    search_k = min(top_k * 3, 10)  # Get more results than needed for reranking

    # Search in vector store
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=search_k
    )

    # No results found
    if not results["documents"][0]:
        return []

    # Process initial results
    result_list = []
    for i in range(len(results["documents"][0])):
        question = results["metadatas"][0][i]["question"]
        answer = results["metadatas"][0][i]["answer"]
        score = results["distances"][0][i]
        # Add the collection name to track which dataset the answer came from
        result_list.append({
            "question": question,
            "answer": answer,
            "score": score,
            "source": collection_name
        })

    # Rerank results using combined similarity metrics
    reranked_results = rerank_results(processed_query, result_list, embedder)

    # Filter by confidence threshold
    filtered_results = [r for r in reranked_results if r['score'] > confidence_threshold]

    # Return top results after reranking and filtering
    return filtered_results[:top_k]


def get_fallback_response(query: str) -> str:
    """
    Generate a fallback response when no good matches are found.
    Customizes the response based on the detected animal type.
    """
    # Detect which animal type the query is about
    animal_type = detect_animal_type(query)

    # Get the animal name based on the collection
    if animal_type == "woofieData":
        animal = "dog"
        young = "puppy"
    elif animal_type == "meowData":
        animal = "cat"
        young = "kitten"
    elif animal_type == "chirpData":
        animal = "bird"
        young = "young bird"
    elif animal_type == "splashData":
        animal = "fish"
        young = "young fish"
    elif animal_type == "smallpetsData":
        animal = "small pet"
        young = "young pet"
    else:
        animal = "pet"
        young = "young pet"

    # Simple rule-based fallbacks customized by animal type
    if re.search(r'food|feed|eat|diet|nutrition', query, re.I):
        return f"For specific dietary questions about your {animal}, it's best to consult with a veterinarian as nutritional needs vary by species, breed, age, and health condition."

    if re.search(r'sick|ill|vomit|diarrhea|health|disease|symptoms', query, re.I):
        return f"If your {animal} is showing signs of illness, please consult with a veterinarian experienced with {animal}s as soon as possible."

    if re.search(r'young|baby|infant|newborn', query, re.I):
        return f"{young.capitalize()}s have special needs for nutrition, care, and healthcare. Consider consulting with a vet who specializes in {animal}s for personalized advice."

    if re.search(r'train|behavior|discipline', query, re.I):
        return f"Training and behavior management varies greatly between different {animal}s. For the best results, consider consulting with a professional {animal} trainer or behaviorist."

    if re.search(r'breed|species|type', query, re.I):
        return f"Different {animal} breeds/species have unique characteristics, care requirements, and temperaments. Research specific breeds or consult with a specialist for detailed information."

    # Default fallback
    return f"I don't have specific information about that aspect of {animal} care. For the most accurate advice, please consult with a veterinarian or specialist who can provide guidance tailored to your {animal}'s specific needs."


def handle_greetings(query: str) -> str:
    """
    Handle common greetings and casual interactions.
    
    Args:
        query: The user's input
        
    Returns:
        A response string if it's a greeting/interaction, None otherwise
    """
    query = query.lower().strip()
    
    # Common greetings
    greetings = {
        'hi': 'Hello! How can I help you with your pet today?',
        'hello': 'Hi there! What would you like to know about your pet?',
        'hey': 'Hey! I\'m here to help with any pet-related questions you have!',
        'how are you': 'I\'m doing great, thanks for asking! How can I help you with your pet today?',
        'how\'s it going': 'All good! Ready to help you with any pet care questions!',
        'good morning': 'Good morning! How can I assist you with your pet today?',
        'good afternoon': 'Good afternoon! What would you like to know about your pet?',
        'good evening': 'Good evening! How can I help you with your pet?',
        'thanks': 'You\'re welcome! Let me know if you have any other questions about your pet!',
        'thank you': 'You\'re welcome! Feel free to ask if you need more help with your pet!',
        'bye': 'Goodbye! Take good care of your pets! 🐾',
        'goodbye': 'Goodbye! Take good care of your pets! 🐾',
        'see you': 'See you later! Take good care of your pets! 🐾'
    }
    
    # Check for exact matches
    if query in greetings:
        return greetings[query]
    
    # Check for partial matches (e.g., "hi there", "hello there")
    for greeting in greetings:
        if query.startswith(greeting):
            return greetings[greeting]
    
    return None


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🐾 Welcome to the Pet Care Assistant! 🐾".center(60))
    print("="*60)
    print("\nI can answer questions about dogs, cats, birds, fish, and small pets.")
    print("Ask me about nutrition, health, training, or general care tips!")

    while True:
        user_input = input("\n💬 Ask a pet health question (or type 'exit'): ")
        
        # Handle greetings and common interactions first
        greeting_response = handle_greetings(user_input)
        if greeting_response:
            print(f"\n🤖 PetBot says:")
            print(greeting_response)
            if user_input.lower() in ["exit", "quit", "bye", "goodbye", "see you"]:
                break
            continue
            
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye! Take good care of your pets! 🐾")
            break

        # Handle potential errors gracefully
        try:
            # Get more potential matches initially
            results = ask_question(user_input, top_k=3, confidence_threshold=0.6)
        except Exception as e:
            # Log the error (but don't show to user)
            with open("error_log.txt", "a") as f:
                f.write(f"Error processing query '{user_input}': {str(e)}\n")
            # Provide a friendly message instead of technical error
            print("\n🤖 PetBot says:")
            print("I'm having trouble processing your question right now. Could you try rephrasing it or asking something else?")
            continue

        # Determine which animal the response is about
        if results:
            source = results[0].get('source', 'allPetsData')
            if source == "woofieData":
                bot_name = "🐶 Woofie"
            elif source == "meowData":
                bot_name = "🐱 Meow"
            elif source == "chirpData":
                bot_name = "🐦 Chirp"
            elif source == "splashData":
                bot_name = "🐠 Splash"
            elif source == "smallpetsData":
                bot_name = "🐹 Whiskers"
            else:
                bot_name = "🤖 PetBot"
        else:
            # For fallbacks, use the animal type from the query
            animal_type = detect_animal_type(user_input)
            if animal_type == "woofieData":
                bot_name = "🐶 Woofie"
            elif animal_type == "meowData":
                bot_name = "🐱 Meow"
            elif animal_type == "chirpData":
                bot_name = "🐦 Chirp"
            elif animal_type == "splashData":
                bot_name = "🐠 Splash"
            elif animal_type == "smallpetsData":
                bot_name = "🐹 Whiskers"
            else:
                bot_name = "🤖 PetBot"

        if results and results[0]['score'] > 0.7:  # High confidence match
            print(f"\n{bot_name} says:")
            print(f"A: {results[0]['answer']}")

            # If there are other good matches, offer them
            if len(results) > 1 and results[1]['score'] > 0.65:
                print("\nYou might also be interested in:")
                print(f"Q: {results[1]['question']}")

        elif results:  # Lower confidence matches
            print(f"\n{bot_name} says:")
            print(f"A: {results[0]['answer']}")
            print("\nNote: I'm not 100% certain this answers your question. Please rephrase if needed.")

        else:  # No good matches
            fallback = get_fallback_response(user_input)
            print(f"\n{bot_name} says:")
            print(fallback)