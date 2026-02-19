"""
Expert Advice System V2 - Powered by Groq AI

This module handles the "Ask an Expert" and chatbot functionality.
Uses Groq's ultra-fast API for intelligent, context-aware responses about
nutrition, fitness, diet planning, and health.
No extra packages required — uses raw requests to the Groq REST API.
"""

import logging
import os
import random
import requests

logger = logging.getLogger(__name__)

# ── Groq Configuration ──
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your-groq-api-key-here")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# System prompt that shapes NutriBot's personality and expertise
SYSTEM_PROMPT = """You are NutriBot, an expert AI nutrition and health assistant for a Personalized Nutrition web application.

Your expertise covers:
- Nutrition science, dietary planning, and meal recommendations
- Fitness guidance and exercise advice
- Understanding blood reports and lab values (hemoglobin, glucose, cholesterol, etc.)
- Weight management strategies
- Vitamin and mineral deficiencies and food remedies
- General wellness and healthy lifestyle tips

You will receive a [USER CONTEXT] block with the user's real data including:
- Their profile (name, age, gender, height, weight, BMI, goal)
- Their latest blood report lab values
- Their health status prediction
- Any deficiencies detected
- Their recommended macros and diet plan
- Which lab results are normal vs abnormal

Guidelines:
1. Keep responses concise (2-4 sentences) since this is a chat widget, not a full page.
2. Be friendly, supportive, and encouraging.
3. USE the user context data when answering. For example, if they ask "what does my report say?", refer to their actual lab values and health status. If they ask "what should I eat?", consider their actual deficiencies and macros.
4. Address the user by their name when it feels natural.
5. When discussing medical topics, always add a brief disclaimer that users should consult a healthcare professional.
6. Use simple language — avoid overly technical jargon unless the user asks for it.
7. If the user greets you, respond warmly using their name and briefly mention what you know about their health profile.
8. Format key points with bold text using <strong> tags when helpful.
9. Never reveal your underlying AI model. You are NutriBot.
10. If no user context is provided, give general nutrition/health advice.
"""

# ── Fallback responses (used if Groq API is unavailable) ──
FALLBACK_RESPONSES = {
    'nutrition': [
        "A balanced diet with carbs, proteins, and healthy fats is key to good health.",
        "Include more leafy greens for essential vitamins and minerals.",
        "Hydration is often overlooked. Aim for 8 glasses of water a day.",
    ],
    'fitness': [
        "Consistency beats intensity. Start small and build up gradually.",
        "Mix cardio with strength training for the best overall results.",
        "Rest days are just as important as workout days for muscle recovery.",
    ],
    'weight_loss': [
        "Focus on whole foods and monitor portion sizes for sustainable weight loss.",
        "Protein at breakfast helps reduce cravings later in the day.",
        "Avoid sugary drinks — they are often empty calories.",
    ],
    'general': [
        "That's a great question! Could you provide more details so I can give a specific answer?",
        "Improving sleep and managing stress are crucial parts of a healthy lifestyle.",
        "Consulting a specialist in person is best for detailed medical advice.",
    ]
}

KEYWORDS = {
    'nutrition': ['food', 'diet', 'eat', 'meal', 'nutrient', 'vitamin', 'protein', 'carb', 'fat', 'sugar', 'calcium', 'iron'],
    'fitness': ['exercise', 'workout', 'gym', 'run', 'walk', 'muscle', 'strength', 'cardio', 'weight', 'lift'],
    'weight_loss': ['lose weight', 'slim', 'fat loss', 'dieting', 'calories', 'obese', 'overweight']
}


def _fallback_response(question, category):
    """Rule-based fallback if Groq API is unavailable."""
    question_lower = question.lower()

    detected = None
    for cat, keys in KEYWORDS.items():
        if any(k in question_lower for k in keys):
            detected = cat
            break

    final_cat = detected or category or 'general'
    if final_cat not in FALLBACK_RESPONSES:
        final_cat = 'general'

    return random.choice(FALLBACK_RESPONSES[final_cat])


def _call_groq(user_message):
    """
    Call the Groq API directly using requests.
    Returns the reply text or None on failure.
    """
    import json as _json

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.7,
        "max_tokens": 300,
    }

    try:
        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            data=_json.dumps(payload),
            timeout=20,
        )

        if response.status_code == 200:
            data = response.json()
            reply = data["choices"][0]["message"]["content"].strip()
            logger.info(f"Groq response generated successfully.")
            return reply
        else:
            logger.error(f"Groq API error {response.status_code}: {response.text}")
            return None

    except Exception as e:
        logger.error(f"Groq API exception: {e}")
        return None


def get_expert_response(question, category=None, expert_name=None):
    """
    Generate an AI-powered response using Groq.
    Falls back to rule-based responses if the API call fails.

    Args:
        question: User's question text
        category: Optional category hint (nutrition, fitness, weight_loss, general)
        expert_name: Optional expert persona name (used as prefix)

    Returns:
        str: The response text
    """
    if not question or not question.strip():
        return "Please ask a question and I'll do my best to help!"

    # Build the user message with optional category context
    user_msg = question
    if category and category != 'general':
        user_msg = f"[Category: {category}] {question}"

    # Try Groq API
    reply = _call_groq(user_msg)

    if reply:
        # Add expert name prefix if provided
        if expert_name and expert_name != 'NutriBot':
            reply = f"Hello from {expert_name}. {reply}"
        return reply

    # Fallback to rule-based
    fallback = _fallback_response(question, category)
    if expert_name and expert_name != 'NutriBot':
        fallback = f"Hello from {expert_name}. {fallback}"
    return fallback
