import json
import re
from groq import Groq
from app.config import get_settings

settings = get_settings()
client = Groq(api_key=settings.GROQ_API_KEY)

ITINERARY_SYSTEM_PROMPT = """You are an expert travel planner AI. Generate detailed day-by-day travel itineraries.

You MUST respond with ONLY valid JSON, no markdown, no code blocks, no extra text.
The JSON must follow this exact structure:

{
  "itinerary": [
    {
      "day_number": 1,
      "title": "Day title (e.g., 'Exploring Old Town')",
      "activities": [
        {
          "time": "09:00 AM",
          "activity": "Activity name",
          "description": "Brief description of the activity",
          "estimated_cost": 25.00,
          "location": "Specific location name"
        }
      ],
      "estimated_cost": 100.00
    }
  ],
  "budget_breakdown": [
    {
      "category": "Accommodation",
      "amount": 500.00,
      "notes": "Mid-range hotel in city center"
    },
    {
      "category": "Food & Dining",
      "amount": 300.00,
      "notes": "Mix of local restaurants and street food"
    },
    {
      "category": "Transportation",
      "amount": 150.00,
      "notes": "Public transit and occasional taxi"
    },
    {
      "category": "Activities & Entertainment",
      "amount": 200.00,
      "notes": "Museum entries, tours, experiences"
    },
    {
      "category": "Shopping & Miscellaneous",
      "amount": 100.00,
      "notes": "Souvenirs and unexpected expenses"
    }
  ],
  "tips": [
    "Useful travel tip 1",
    "Useful travel tip 2"
  ]
}

Rules:
- Each day should have 4-6 activities spread throughout the day
- Activity times should be realistic and in chronological order
- Estimated costs should be realistic for the destination
- The total budget breakdown should be within the specified budget
- Include a mix of popular attractions and hidden gems
- Consider the traveler preferences provided
- All costs should be in the specified currency"""

BUDGET_OPTIMIZE_PROMPT = """You are a budget optimization expert for travel planning.
Given an existing travel itinerary and budget, optimize the budget based on the optimization goal.

You MUST respond with ONLY valid JSON, no markdown, no code blocks, no extra text.
The JSON must follow this exact structure:

{
  "itinerary": [
    {
      "day_number": 1,
      "title": "Day title",
      "activities": [
        {
          "time": "09:00 AM",
          "activity": "Activity name",
          "description": "Brief description",
          "estimated_cost": 15.00,
          "location": "Location name"
        }
      ],
      "estimated_cost": 80.00
    }
  ],
  "budget_breakdown": [
    {
      "category": "Category name",
      "amount": 400.00,
      "notes": "Optimization notes"
    }
  ],
  "savings_tips": [
    "Specific tip for saving money"
  ],
  "total_savings": 150.00
}"""


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from code blocks
    patterns = [
        r'```json\s*\n?(.*?)\n?\s*```',
        r'```\s*\n?(.*?)\n?\s*```',
        r'\{[\s\S]*\}'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                json_str = match.group(1) if '```' in pattern else match.group(0)
                return json.loads(json_str)
            except (json.JSONDecodeError, IndexError):
                continue

    raise ValueError(f"Could not extract valid JSON from response: {text[:200]}")


def generate_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    budget: float,
    currency: str,
    travelers: int,
    preferences: list[str]
) -> dict:
    """Generate a travel itinerary using Groq LLM."""
    user_prompt = f"""Plan a trip with the following details:
- Destination: {destination}
- Start Date: {start_date}
- End Date: {end_date}
- Total Budget: {budget} {currency}
- Number of Travelers: {travelers}
- Preferences: {', '.join(preferences) if preferences else 'General sightseeing'}

Please create a detailed day-by-day itinerary with activities, costs, and a budget breakdown.
Keep the total spending within the budget of {budget} {currency} for {travelers} traveler(s)."""

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": ITINERARY_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=4096,
    )

    response_text = chat_completion.choices[0].message.content
    return _extract_json(response_text)


def optimize_budget(
    destination: str,
    budget: float,
    currency: str,
    travelers: int,
    current_itinerary: list[dict],
    current_budget: list[dict],
    optimization_goal: str
) -> dict:
    """Optimize the budget for an existing itinerary using Groq LLM."""
    user_prompt = f"""Optimize this travel plan:
- Destination: {destination}
- Total Budget: {budget} {currency}
- Travelers: {travelers}
- Optimization Goal: {optimization_goal}

Current Itinerary:
{json.dumps(current_itinerary, indent=2)}

Current Budget Breakdown:
{json.dumps(current_budget, indent=2)}

Please optimize the itinerary and budget based on the goal: {optimization_goal}.
- If "reduce_costs": Find cheaper alternatives while maintaining quality experiences
- If "balance": Balance between budget and luxury experiences
- If "luxury": Upgrade experiences while trying to stay within budget"""

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": BUDGET_OPTIMIZE_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=4096,
    )

    response_text = chat_completion.choices[0].message.content
    return _extract_json(response_text)
