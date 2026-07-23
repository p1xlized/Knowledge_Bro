import os
from typing import Optional

from dotenv import load_dotenv
from litellm import completion

# Loads variables from .env into os.environ
load_dotenv()

DEFAULT_MODEL = "openrouter/openrouter/free"


def generate_summary(
    text: str,
    user_api_key: Optional[str] = None,
    user_model: Optional[str] = None,
) -> str:
    selected_model = user_model if user_model else DEFAULT_MODEL

    api_key = user_api_key or os.environ.get("OPENROUTER_API_KEY")

    if not api_key and selected_model.startswith("openrouter/"):
        raise ValueError(
            "An OpenRouter API key is required! Add OPENROUTER_API_KEY to your .env file."
        )

    messages = [
        {
            "role": "system",
            "content": (
                "You are an executive assistant. Summarize the following video/audio transcript "
                "into clear, structured, and high-level bullet points. Highlight key actions, "
                "decisions, and main topics. Ignore filler words and minor tangents."
            ),
        },
        {"role": "user", "content": text},
    ]

    kwargs = {
        "model": selected_model,
        "messages": messages,
    }

    if api_key:
        kwargs["api_key"] = api_key

    try:
        response = completion(**kwargs)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {str(e)}"


if __name__ == "__main__":
    # Realistic long audio transcript (~600 words)
    sample_text = """
    Hey everyone, welcome back to the channel! Today I want to walk you through my typical morning routine
    and how unpredictable the weather has been lately. So first off, I wake up around 6:30 AM every weekday.
    I try not to hit the snooze button, though honestly, some days are harder than others depending on how late
    I was coding the night before. Once I'm out of bed, I head straight to the kitchen to grab a glass of water,
    and then I get dressed. Usually, it's just comfortable clothes—jeans and a hoodie.

    After getting ready, I start my morning commute. I walk to school every morning because it's only about a
    15-minute walk from my apartment, and I really like getting that fresh air before sitting down for lectures all day.
    I don't ride a bike because the bike lanes around here are always blocked, and I don't take the bus because
    the schedule is super unreliable in the morning. So walking is definitely my preferred way to go.

    However, today was a complete disaster with the weather. About halfway through my walk, it started to rain out of nowhere.
    I mean a total downpour. I didn't check the weather forecast before leaving, so I completely forgot my umbrella.
    I really do not like rain, especially when I'm carrying my laptop in my backpack. Luckily, I managed to take shelter
    under a coffee shop awning for about ten minutes until it calmed down to a light drizzle.

    Once I finally made it to campus, I headed to the cafeteria to eat lunch. By that time, I was starving.
    I brought a packed lunch from home—I ate a turkey sandwich and a green apple. While eating, I met up with Sarah
    and Alex to discuss our computer science group project that's due next Friday. We agreed to divide the tasks:
    Alex is handling the database schema, Sarah is building the API endpoints, and I'm responsible for setting up
    the front-end interface and integration.

    After lunch, the sun actually came out for a bit, so we decided to play outside on the quad. We tossed a frisbee
    around for about twenty minutes. I really like playing outside whenever the weather permits; it's a great way
    to destress between heavy lectures.

    Later in the afternoon, I went to the campus library to get some study time in. I read a book for my history elective
    chapter 4 on the Industrial Revolution. I honestly love reading history books when it's quiet, though I had to stop
    around 4:00 PM because my eyes were getting tired.

    Finally, around 5:00 PM, I started my walk home. I usually don't mind the walk, but today my shoes were still completely
    soaked from the morning rain, so walking home was pretty miserable. When I got back to the house, my mother was in the
    kitchen cooking a hot vegetable soup for dinner. The soup was burning hot, but it was exactly what I needed after
    being wet and cold all day. We ate dinner together as a family and talked about our week.

    By 9:30 PM, I was completely exhausted. I packed my bag for tomorrow, brushed my teeth, and went straight to bed.
    Even though I don't always like going to bed early because I feel like I lose free time, my body just needed the rest.
    Anyway, that was my day! Thanks for listening, and don't forget to hit like and subscribe!
    """

    print("--- Processing Long Transcript via OpenRouter ---")
    print(generate_summary(sample_text))
