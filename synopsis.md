# Project Synopsis: Team1-Planner (AI Website Planner)

## 1. Project Overview
**Team1-Planner** is an AI-powered conversational platform designed to act as an automated website planner. By taking a simple user prompt (e.g., "Build a restaurant website"), the system intelligently detects the requested industry and utilizes a Local Large Language Model (LLM) to generate a structured, tailored website proposal. The user can then review, confirm, or regenerate this plan before proceeding to automated code generation.

## 2. Technology Stack
*   **Backend:** Python, FastAPI, Uvicorn (ASGI server)
*   **Frontend:** HTML5, CSS3, Vanilla JavaScript (Modern Glassmorphism UI)
*   **AI Engine:** Local Ollama instance running the `gemma:2b` model
*   **External Integration:** Node.js backend (Team-2 Generator on port 3000) for processing the final code generation step.

## 3. System Architecture & Workflow
The system operates in three primary phases:

1.  **Requirement Gathering (Plan Phase):**
    *   The user inputs an industry or website concept on a colorful, animated frontend interface.
    *   The frontend sends a POST request to the FastAPI backend (`/plan`).
    *   The backend's Python logic detects the specific industry using regex parsing.
    *   A structured prompt is formulated and sent to the local Ollama LLM (`gemma:2b`).
    *   The generated website blueprint (outlining pages, design style, and technology stack) is streamed back to the frontend with a simulated typing effect.

2.  **Review & Confirmation Phase:**
    *   The user is prompted to accept or reject the generated plan (`/confirm-plan`).
    *   If **rejected ("No")**, the backend instructs the LLM to formulate an alternative plan.
    *   If **accepted ("Yes")**, the application transitions to the final hand-over state.

3.  **Code Generation Phase:**
    *   Once confirmed, the user initiates the code generation process (`/generate-code`).
    *   The backend securely forwards the approved plan and industry context to a secondary auxiliary backend ("Team-2 Generator").
    *   The final website code is compiled and presented back to the user.

## 4. Recent Enhancements
*   **UI/UX Revamp:** The frontend was upgraded from a basic layout to a highly responsive, premium glassmorphism design featuring animated gradient backgrounds, modern Inter typography, and interactive hover states.
*   **JavaScript Robustness:** The client-side logic was refactored significantly to implement Promise-based typing animations, robust state management of DOM elements, and improved HTTP error handling for a seamless user experience.
