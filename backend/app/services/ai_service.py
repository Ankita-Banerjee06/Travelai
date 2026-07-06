import json
import re
import logging
from datetime import date
from groq import Groq, RateLimitError
from app.config import get_settings

settings = get_settings()
client = Groq(api_key=settings.GROQ_API_KEY)
logger = logging.getLogger(__name__)

MODEL = "openai/gpt-oss-120b"

# Max days generated per single LLM call. Keeps each response well within
# the token budget so it never gets truncated mid-JSON. Larger batches mean
# fewer calls, which means the system prompt (re-sent every call) is
# repeated less often -> lower total token usage per trip.
DAYS_PER_BATCH = 7

ITINERARY_SYSTEM_PROMPT = """You are an expert travel planner AI. Generate detailed day-by-day travel itineraries \
for ANY city or country in the world, using real, well-known places, neighborhoods, and local cuisine for that \
specific destination.

You MUST respond with ONLY valid JSON, no markdown, no code fences, no commentary before or after the JSON.
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
          "location": "Specific real location name"
        }
      ],
      "estimated_cost": 100.00
    }
  ]
}

Rules:
- Each day should have 4-6 activities spread throughout the day (morning, afternoon, evening)
- Activity times should be realistic and in chronological order
- COST ACCURACY IS CRITICAL, for EVERY destination (not just well-known ones): estimated_cost must reflect the \
ACTUAL real-world price of that specific place/activity, in that specific destination, in the specified \
currency — never a number that's merely scaled to fit the traveler's stated budget. Think about what this type \
of place/activity genuinely costs locally: a sit-down restaurant meal, a museum entry fee, a taxi ride, a hotel \
night, etc. all have realistic price ranges that vary by country and city tier (capital vs. small town, tourist \
hub vs. local area) — apply that real-world judgment for whichever destination you're given, every time. If \
accurately-priced activities don't add up to the traveler's stated budget, that's fine and expected — a realistic \
total (whether over or under budget) is more useful to the traveler than an artificially adjusted one. Do not \
deflate or inflate costs just to make the daily/trip total match the budget number.
- Use real, specific places (named streets, landmarks, restaurants, markets) appropriate to the destination
- Include a mix of popular attractions and hidden gems
- Consider the traveler preferences provided
- All costs should be plain numbers in the specified currency, reflecting genuine local prices in that currency \
for that destination (never a USD-equivalent number simply relabeled with a different currency symbol)
- Keep descriptions concise (one short sentence) so the response stays compact
- Respond with ONLY the JSON object above — no other keys, no extra text"""

BUDGET_SUMMARY_SYSTEM_PROMPT = """You are a travel budget expert. Given a destination, trip length, budget, \
number of travelers, and a full itinerary, produce a realistic budget breakdown and a short list of tips.

You MUST respond with ONLY valid JSON, no markdown, no code fences, no commentary.
The JSON must follow this exact structure:

{
  "budget_breakdown": [
    {"category": "Accommodation", "amount": 500.00, "notes": "Mid-range hotel in city center"},
    {"category": "Food & Dining", "amount": 300.00, "notes": "Mix of local restaurants and street food"},
    {"category": "Transportation", "amount": 150.00, "notes": "Public transit and occasional taxi"},
    {"category": "Activities & Entertainment", "amount": 200.00, "notes": "Museum entries, tours, experiences"},
    {"category": "Shopping & Miscellaneous", "amount": 100.00, "notes": "Souvenirs and unexpected expenses"}
  ],
  "tips": ["Useful travel tip 1", "Useful travel tip 2", "Useful travel tip 3"]
}

Base the breakdown on genuine local costs for this destination, using the itinerary's actual (real-world) \
day-by-day costs as your foundation rather than forcing the total to match the traveler's stated budget."""

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
}

All costs in the optimized itinerary must still reflect genuine, real-world local prices for this destination —
"reduce_costs" means swapping in cheaper real places/options, not just writing smaller numbers for the same ones."""


class AIServiceError(Exception):
    """Raised when the AI provider fails to return usable data after retries."""
    pass


class AIRateLimitError(AIServiceError):
    """Raised when the AI provider's rate/quota limit is hit. Not retried,
    since retrying against an exhausted daily quota just burns time."""
    def __init__(self, message: str, retry_after_seconds: int | None = None):
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds


def _parse_retry_after(exc: Exception) -> int | None:
    """Best-effort extraction of the retry delay Groq reports, e.g.
    'Please try again in 29m18.24s.'"""
    match = re.search(r'try again in (?:(\d+)m)?([\d.]+)s', str(exc))
    if not match:
        return None
    minutes = int(match.group(1)) if match.group(1) else 0
    seconds = float(match.group(2))
    return int(minutes * 60 + seconds)


def _strip_to_braces(text: str) -> str:
    """Trim any leading/trailing junk outside the outermost { }."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return text
    return text[start:end + 1]


def _attempt_repair(json_str: str) -> str:
    """Best-effort repair of a truncated/malformed JSON string so it can
    still be parsed. Handles the common truncation failure mode where the
    model's response got cut off mid-string or mid-array."""
    c = json_str.strip()

    # If it ends mid-string (odd count of unescaped quotes), drop the
    # trailing partial string.
    quote_count = len(re.findall(r'(?<!\\)"', c))
    if quote_count % 2 != 0:
        last_quote = c.rfind('"')
        c = c[:last_quote]
        c = re.sub(r'[,:\s]+$', '', c)

    # Trim any trailing partial/dangling key or comma
    c = re.sub(r',\s*"[^"]*$', '', c)
    c = re.sub(r',\s*$', '', c)

    # Balance brackets/braces by appending the needed closers
    stack = []
    in_str = False
    escape = False
    for ch in c:
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch in '{[':
            stack.append(ch)
        elif ch in '}]':
            if stack:
                stack.pop()

    closers = ''.join('}' if ch == '{' else ']' for ch in reversed(stack))
    return c + closers


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code blocks and
    truncated/malformed output."""
    if not text:
        raise ValueError("Empty response from AI provider")

    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from code fences
    for pattern in (r'```json\s*\n?(.*?)\n?\s*```', r'```\s*\n?(.*?)\n?\s*```'):
        match = re.search(pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

    # Fall back to the outermost { ... } span
    braced = _strip_to_braces(text)
    try:
        return json.loads(braced)
    except json.JSONDecodeError:
        pass

    # Last resort: attempt to repair truncated JSON (common when the model
    # hits its max_tokens limit mid-response)
    repaired = _attempt_repair(braced)
    try:
        return json.loads(repaired)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not extract valid JSON from response: {text[:300]}") from e


def _call_groq(system_prompt: str, user_prompt: str, max_tokens: int = 4000, retries: int = 2,
                list_key: str | None = None) -> dict:
    """Call Groq with automatic retry on truncation/parse failure.

    Always returns a dict. If the model's JSON response is (or repairs down
    to) a bare list instead of an object, it's normalized into
    {list_key: [...]} so downstream .get() calls never crash.

    Rate limit errors are NOT retried — retrying against an exhausted quota
    just fails again and wastes time. They're raised immediately as
    AIRateLimitError so the caller can respond appropriately (e.g. HTTP 429).
    """
    last_error = None
    for attempt in range(retries + 1):
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                model=MODEL,
                temperature=0.7,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            response_text = chat_completion.choices[0].message.content

            try:
                parsed = _extract_json(response_text)
            except ValueError as parse_err:
                last_error = parse_err
                continue

            if isinstance(parsed, list):
                parsed = {list_key: parsed} if list_key else {"items": parsed}
            elif not isinstance(parsed, dict):
                last_error = ValueError(
                    f"AI response was not a JSON object (got {type(parsed).__name__})"
                )
                continue

            return parsed

        except RateLimitError as e:
            logger.warning(f"Groq rate limit hit: {e}")
            retry_after = _parse_retry_after(e)
            raise AIRateLimitError(str(e), retry_after_seconds=retry_after) from e

        except Exception as e:
            logger.warning(f"Groq call failed (attempt {attempt + 1}/{retries + 1}): {e}")
            last_error = e
            continue

    raise AIServiceError(str(last_error) if last_error else "AI provider failed")


def _date_range_days(start_date: str, end_date: str) -> int:
    try:
        s = date.fromisoformat(str(start_date))
        e = date.fromisoformat(str(end_date))
        return max((e - s).days + 1, 1)
    except (ValueError, TypeError):
        return 1


def generate_itinerary(
    destination: str,
    start_date: str,
    end_date: str,
    budget: float,
    currency: str,
    travelers: int,
    preferences: list[str]
) -> dict:
    """Generate a full travel itinerary for any destination, batching the
    request across multiple LLM calls for longer trips so no single response
    ever risks truncation."""
    total_days = _date_range_days(start_date, end_date)
    preferences_str = ', '.join(preferences) if preferences else 'General sightseeing'

    all_days = []
    day_cursor = 1
    while day_cursor <= total_days:
        batch_size = min(DAYS_PER_BATCH, total_days - day_cursor + 1)
        batch_start_day = day_cursor
        batch_end_day = day_cursor + batch_size - 1

        user_prompt = f"""Plan part of a trip with the following details:
- Destination: {destination}
- Total trip length: {total_days} day(s), from {start_date} to {end_date}
- Generate ONLY days {batch_start_day} through {batch_end_day} of this trip (day_number values {batch_start_day}-{batch_end_day})
- Total Budget for entire trip: {budget} {currency}
- Number of Travelers: {travelers}
- Preferences: {preferences_str}

Create a detailed itinerary for just days {batch_start_day}-{batch_end_day}, with activities, costs, and real \
locations in {destination}. Do not repeat activities/places already typical for earlier or later days. Every \
estimated_cost must be a REAL, ACCURATE local price for {destination} specifically, in {currency} — base it on \
what that type of place/activity genuinely costs in {destination}'s local market, not on making the total match \
the stated budget. The traveler's budget of {budget} {currency} is context, not a constraint to force the \
numbers into — it's fine if realistic pricing ends up above or below it."""

        result = _call_groq(ITINERARY_SYSTEM_PROMPT, user_prompt, max_tokens=4000, list_key="itinerary")
        batch_days = result.get("itinerary", [])
        if isinstance(batch_days, list):
            all_days.extend(d for d in batch_days if isinstance(d, dict))
        day_cursor += batch_size

    # Generate budget breakdown + tips in a single lightweight call using a
    # compact summary of the itinerary (not the full activity text) to keep
    # this call small and fast.
    compact_summary = [
        {"day_number": d.get("day_number"), "title": d.get("title"), "estimated_cost": d.get("estimated_cost", 0)}
        for d in all_days
    ]
    budget_prompt = f"""Destination: {destination}
Trip length: {total_days} day(s)
Total Budget: {budget} {currency}
Travelers: {travelers}
Preferences: {preferences_str}

Day-by-day cost summary:
{json.dumps(compact_summary, indent=2)}

Produce a budget breakdown across categories using genuine local prices for {destination}, plus 3-5 practical \
tips for visiting {destination}. Base the breakdown on the day-by-day costs above rather than forcing the total \
to equal {budget} {currency} exactly."""

    budget_result = _call_groq(BUDGET_SUMMARY_SYSTEM_PROMPT, budget_prompt, max_tokens=1000, list_key="budget_breakdown")

    budget_breakdown = budget_result.get("budget_breakdown", [])
    tips = budget_result.get("tips", [])

    return {
        "itinerary": all_days,
        "budget_breakdown": budget_breakdown if isinstance(budget_breakdown, list) else [],
        "tips": tips if isinstance(tips, list) else [],
    }


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

Please optimize the itinerary and budget based on the goal: {optimization_goal}. Keep every cost a REAL, \
ACCURATE local price for {destination} in {currency} — never an artificially adjusted number.
- If "reduce_costs": Find genuinely cheaper real alternatives (e.g. street food instead of a sit-down restaurant,
  public transit instead of taxis) while maintaining quality experiences
- If "balance": Balance between budget and luxury experiences using real prices for both tiers
- If "luxury": Upgrade to real higher-end experiences and price them accurately, even if that exceeds the budget"""

    return _call_groq(BUDGET_OPTIMIZE_PROMPT, user_prompt, max_tokens=4000, list_key="itinerary")