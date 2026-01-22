# Gemini Context: Text Edit Project

## Project Overview
This project is a Python-based web application built with **FastAPI** that utilizes the **OpenAI Assistants API** to generate and edit text. Its primary function is to generate text based on provided keywords, insert specific special characters, and apply various regex-based formatting rules (e.g., removing Hanja, handling specific symbols like '℃', and managing spacing around English words).

## Key Technologies
*   **Language:** Python
*   **Web Framework:** FastAPI
*   **Server:** Uvicorn
*   **AI Integration:** OpenAI API (Assistants API, beta threads/runs)
*   **Templating:** Jinja2
*   **Validation:** Pydantic

## Architecture & Directory Structure
The project follows a standard FastAPI structure:

*   **`app/`**: Root application directory.
    *   **`main.py`**: Application entry point. Initializes `FastAPI` and includes routers.
    *   **`config.py`**: Configuration management using `python-dotenv`. Intended to load `OPENAI_API_KEY` and `ASSISTANT_ID`.
    *   **`routers/`**: Contains API route definitions.
        *   `edit_router.py`: Handles the `/` (HTML) and `/edit` (POST) endpoints. Orchestrates the generation and cleaning logic.
    *   **`services/`**: Business logic and external API interactions.
        *   `edit_service.py`: Wraps OpenAI API calls (create thread, stream message, run assistant). **Note:** Contains hardcoded API keys which override configuration in some places.
    *   **`schemas/`**: Pydantic models for request/response validation.
        *   `edit_schemas.py`: Defines `OriginalText` input model.
    *   **`templates/`**: HTML templates.
        *   `index.html`: Frontend interface.

## Setup & Execution

### 1. Installation
Install dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Configuration
Environment variables are managed via a `.env` file (loaded in `app/config.py`).
Required variables typically include:
*   `OPENAI_API_KEY`
*   `ASSISTANT_ID`

### 3. Running the Application
The application is served using Uvicorn. Run from the project root:
```bash
uvicorn app.main:app --reload
```
*   The application will likely be accessible at `http://127.0.0.1:8000`.

## Logic Flow (`/edit` Endpoint)
1.  **Input:** Receives `keyword` and `specialCharacters`.
2.  **Generation:** Calls OpenAI Assistant (`service.stream_run`) to generate text based on the keyword.
3.  **Refinement:** Calls a second OpenAI Assistant to insert the provided special characters into the generated text.
4.  **Post-Processing:** Applies a series of Regex operations:
    *   Removes Hanja (Chinese characters).
    *   Replaces specific symbols (e.g., `%` -> `퍼센트`, `℃` -> `도`).
    *   Filters out non-allowed special characters.
    *   Adjusts spacing around English words.
    *   Normalizes paragraph spacing.
5.  **Output:** Returns the processed text as JSON.

## Development Notes
*   **Hardcoded Credentials:** Be aware that `app/services/edit_service.py` currently contains hardcoded OpenAI API keys and Assistant IDs, which may conflict with or override environment variables.
*   **Streaming:** The service implements manual streaming logic for the OpenAI API responses.
