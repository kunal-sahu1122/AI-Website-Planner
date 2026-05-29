from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from rapidfuzz import process
import re

app = FastAPI()

# session storage
current_plan = None
current_industry = None


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# request models
class UserRequest(BaseModel):
    message: str


class ConfirmRequest(BaseModel):
    answer: str


class CodeRequest(BaseModel):
    answer: str


# known industries (for spelling correction)
industries = [
    "gym",
    "restaurant",
    "coffee shop",
    "bakery",
    "hospital",
    "school",
    "perfume",
    "watch",
    "shoes",
    "hotel",
    "college",
    "University"
]


# detect industry
def detect_industry(text):

    text = text.lower().strip()

    # general case
    if text in ["make a website", "create a website", "build a website", "website"]:
        return "general"

    # extract industry before "website"
    match = re.search(r"(?:make|create|build)?\s*(?:a\s*)?(.+?)\s+website", text)

    if match:

        industry = match.group(1).strip()

        if not industry:
            return "general"

        return industry

    return "general"


# call Gemma (Ollama)
def ask_gemma(prompt):

    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "gemma:2b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    try:

        response = requests.post(url, json=payload, timeout=60)

        if response.status_code == 200:
            data = response.json()
            return data.get("response", "AI could not generate a response.")

        return "AI model not responding."

    except Exception as e:
        return f"AI connection error: {str(e)}"


# prompt builder
def build_prompt(industry):

    if industry == "general":

        return """
You are an AI Website Planner.

Generate a questionnaire for planning a website.

IMPORTANT RULES:
- Do NOT ask questions
- Only give OPTIONS
- Use bullet points

Great 👍

Before I build your website, tell me a few things 👇

1️⃣ Website Type
• Business website
• E-commerce
• Portfolio
• Blog
• Something else?

2️⃣ Design Style
• Dark theme
• Light theme
• Minimal clean design
• Modern + animations
• Professional style

3️⃣ Pages Needed
• Home
• About
• Services
• Contact
• Login / Register

4️⃣ Technology
• HTML + CSS
• HTML + CSS + JavaScript
• React website
• Full backend (Node / Python)
"""

    return f"""
You are an AI Website Planner.

Create a website planning questionnaire for a {industry} website.

Great 👍

Before I build your {industry} website, tell me a few things 👇

1️⃣ Website Type
Generate 4 possible types of {industry} website.
Use bullet points.

2️⃣ Design Style
Generate 4 possible styles suitable for a {industry} website.
Use bullet points.

3️⃣ Pages Needed
List important pages for a {industry} website.

Example pages:
• Home
• About
• Services/products
• Gallery
• Reviews/Testimonials
• Contact
• Login/Register

4️⃣ Technology
• HTML + CSS
• HTML + CSS + JavaScript
• React Website
• Full backend (Python/Node)
"""


@app.get("/")
def home():
    return {"message": "AI Website Planner running Buddy (^_^)"}


# generate plan
@app.post("/plan")
def generate_plan(data: UserRequest):

    global current_plan
    global current_industry

    user_input = data.message.lower()

    industry = detect_industry(user_input)

    prompt = build_prompt(industry)

    result = ask_gemma(prompt)

    current_plan = result
    current_industry = industry

    return {
        "plan": result,
        "message": "Are you satisfied with this plan? (Yes/No)"
    }


# confirm plan
@app.post("/confirm-plan")
def confirm_plan(data: ConfirmRequest):

    global current_plan
    global current_industry

    if current_plan is None:
        return {"message": "No plan generated yet."}

    answer = data.answer.lower()

    if answer == "yes":

        return {
            "status": "plan_accepted",
            "message": "Great 👍 Do you want to generate the website code now? (Yes/No)"
        }

    # regenerate new plan
    prompt = build_prompt(current_industry)

    new_plan = ask_gemma(prompt)

    current_plan = new_plan

    return {
        "status": "plan_regenerated",
        "plan": new_plan,
        "message": "Here is a new plan. Are you satisfied now? (Yes/No)"
    }


# generate code using team-2 backend
@app.post("/generate-code")
def generate_code_permission(data: CodeRequest):

    global current_plan
    global current_industry

    answer = data.answer.lower()

    if answer != "yes":
        return {
            "status": "cancelled",
            "message": "Code generation cancelled."
        }

    try:

        response = requests.post(
            "http://localhost:3000/api/generate",
            json={
                "plan": current_plan,
                "industry": current_industry
            },
            timeout=120
        )

        if response.status_code == 200:

            result = response.json()

            return {
                "status": "code_generated",
                "generated_code": result
            }

        return {
            "status": "error",
            "message": "Team-2 generator failed"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }