# WoofieChat - AI-Powered Pet Care Assistant


#### Video Demo: (https://youtu.be/y8G1eajXLNU)[https://youtu.be/y8G1eajXLNU]
#### Description:

WoofieChat is an intelligent, AI-powered pet care assistant designed to provide accurate and personalized advice for pet owners. Built using advanced natural language processing (NLP) and semantic search, WoofieChat understands user queries and offers reliable responses related to pet care.

#### What Motivated Me

As an extension of the[ Woofie pet management system](https://www.aashikbaruwal.com.np/projects/woofie " Woofie pet management system") developed by me, WoofieChat aims to provide interactive, accurate advice for pet owners. I have found that they often struggle to find accurate and context-specific advice about their pet's care. WoofieChat addresses this gap by offering a conversational assistant that leverages AI to deliver relevant pet care guidance. Whether it's about feeding, grooming, or health concerns, WoofieChat provides valuable insights in a user-friendly format.

### ## Key Features

- Personalized Advice: Understands pet types (dogs, cats, birds, fish, small pets) and offers tailored responses.

- Semantic Search: Uses vector embeddings for accurate response matching.

- Easy Data Management: Utilizes markdown files for structured and human-readable data storage.

- Robust API: Built with FastAPI, providing a modern and efficient web interface.

- Testing Suite: Ensures high code quality with comprehensive unit tests.

## Project Overview

WoofieChat follows a modular architecture, making it efficient and scalable. The core components are structured as follows:

### Core Components

1. **Server (`server.py`)**
   - FastAPI-based server for handling API requests.
  - Manages HTTP responses, CORS, and security.
 - Provides RESTful endpoints for chat interactions.

2. **Inference Engine (`inference.py`)**
 -  Processes user inputs and normalizes queries.
 - Identifies the pet type and extracts relevant keywords.
 - Uses vector similarity to fetch accurate responses.
 - Includes fallback responses for ambiguous queries.

3. **Embedder (`embedder.py`)**
 - Handles embedding generation using all-MiniLM-L6-v2.

 - Manages vector database operations with ChromaDB.

 - Efficiently retrieves relevant pet care information.

### Data Structure

The project uses markdown files to store pet care information, organized by pet type:
- `woofieData.md`: Dog care information
- `meowData.md`: Cat care information
- `chirpData.md`: Bird care information
- `splashData.md`: Fish care information
- `smallpetsData.md`: Small pet care information
- `allPetsData.md`: General pet care information

## Technical Approach

- NLP and Semantic Search
- Model Choice: Uses all-MiniLM-L6-v2 for text embedding, providing a balance between speed and accuracy.
- Vector Storage: ChromaDB is used to index and retrieve embeddings efficiently.
- Query Processing: Includes normalization, keyword extraction, and animal type detection.

## API Design
- Main Endpoint: /api/chat accepts a JSON object with the user's query.
- Response Structure: JSON format with fields for response, confidence score, and data source.

### Testing

The project includes a comprehensive test suite:
- `tests/test_server.py`: API endpoint tests
- `tests/test_inference.py`: Query processing tests
- `tests/test_embedder_actual.py`: Data embedding tests
- `tests/conftest.py`: Test fixtures and setup
- `tests/test_data.md`: Test data for unit tests



## Design Choices

1. **Vector Database**
   - Chose ChromaDB for its efficient vector storage and retrieval
   - Enables semantic search capabilities
   - Provides better response quality than keyword matching

2. **Markdown Storage**
   - Used markdown format for knowledge base
   - Easy to maintain and update
   - Supports rich text formatting
   - Human-readable and version-control friendly

3. **FastAPI Framework**
   - Modern, fast web framework
   - Built-in API documentation
   - Type safety and validation
   - Easy to test and maintain

4. **Modular Architecture**
   - Separated concerns into distinct modules
   - Easy to extend and modify
   - Clear separation of data, logic, and interface


## Future Improvements

Potential areas for enhancement:
1. Add more pet types and care information
2. Improve the accuracy of the insights.
3. Implement user feedback mechanism
4. Add image recognition for pet health issues
5. Integrate with veterinary databases
6. Add multi-language support

## Setup and Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python server.py
   ```

3. Access the API at `http://localhost:8000`

## API Usage

The main endpoint is `/api/chat` which accepts POST requests with a JSON body:
```json
{
    "message": "What Should I feed my Dog?"
}
```

Response format:
```json
{
    "response": "Feeding amounts depend on your dog's age, weight, activity level, and metabolism. Follow package guidelines as a starting  point, then adjust based on body condition. You should be able to feel but not see your dog's ribs..",
    "confidence": 0.95,
    "source": "woofieData.md"
}
```

## Testing

Run the test suite:
```bash
pytest
```

Made with ❤️ by [AASHIK](https://aashikbaruwal.com.np)
