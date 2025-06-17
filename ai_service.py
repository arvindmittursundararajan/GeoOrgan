import os
import requests
from datetime import datetime, timedelta
from mongo import metrics_data, alerts, machines, parts
from config import GEMINI_API_KEY # Import API key from config

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

def get_realtime_metrics_summary():
    """Fetches and summarizes the latest key metrics."""
    latest_metrics = metrics_data.find_one(sort=[('timestamp', -1)])
    if not latest_metrics:
        return "No recent metrics available."

    total_flights = latest_metrics.get('total_flights', 0)
    total_medical_organs = latest_metrics.get('total_medical_organs', 0)
    active_failures = latest_metrics.get('active_failures', 0)
    success_rate = latest_metrics.get('success_rate', '0.0%')
    total_available_organs = latest_metrics.get('total_available_organs', 0)
    total_in_transit_organs = latest_metrics.get('total_in_transit_organs', 0)

    return (
        f"Current Status: There are {total_flights} active flights, "
        f"{total_medical_organs} organs managed ({total_available_organs} available, {total_in_transit_organs} in transit). "
        f"There are {active_failures} active failures. Overall success rate: {success_rate}."
    )

def get_critical_alerts_summary():
    """Fetches and summarizes recent critical alerts."""
    # Fetch alerts from the last 24 hours as "today's" alerts
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    critical_alerts = list(alerts.find({
        'severity': 'critical',
        'timestamp': {'$gte': twenty_four_hours_ago}
    }).sort('timestamp', -1).limit(5)) # Limit to 5 most recent critical alerts

    if not critical_alerts:
        return "No critical alerts reported recently."

    summary_messages = []
    for alert in critical_alerts:
        timestamp_str = alert.get('timestamp').strftime('%Y-%m-%d %H:%M') if hasattr(alert.get('timestamp'), 'strftime') else str(alert.get('timestamp'))
        summary_messages.append(f"- At {timestamp_str}, {alert.get('alert_type', 'unknown')}: {alert.get('message', 'No details.')}")
    return "Recent Critical Alerts:\n" + "\n".join(summary_messages)


def generate_gemini_pre_prompt(user_question):
    """Generates the full pre-prompt with context, metrics, and alerts for Gemini."""
    persona = "You are Klaudia, the manager of SaveALife, an organ transport and asset management system. "
    background = "Your role is to provide concise, factual, and actionable answers regarding the system's operational status, flights, organ transport, and device health."
    strict_rules = """
    Strict Rules:
    1. Always respond in 1-2 sentences maximum.
    2. Use plain text only - no markdown, no special characters, no formatting.
    3. No prefixes or suffixes - just the direct answer.
    4. No bullet points, no lists, no quotes.
    5. Keep it simple and straightforward.
    """

    metrics_summary = get_realtime_metrics_summary()
    alerts_summary = get_critical_alerts_summary()

    full_pre_prompt = (
        f"{persona}{background}\n\n"
        f"Real-time Data Overview:\n{metrics_summary}\n\n"
        f"{alerts_summary}\n\n"
        f"{strict_rules}\n\n"
        f"User Question: {user_question}"
    )
    return full_pre_prompt

def ask_gemini_with_context(user_question):
    """Sends a question to Gemini with full context and gets the response."""
    full_prompt = generate_gemini_pre_prompt(user_question)

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": full_prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        if 'candidates' in result and len(result['candidates']) > 0:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "No response from Gemini"

    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def get_embedding(text):
    """Get embedding vector for the given text using Gemini API."""
    embedding_url = f"https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "models/embedding-001",
        "content": {
            "parts": [{"text": text}]
        }
    }
    try:
        response = requests.post(embedding_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["embedding"]["values"]
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None 