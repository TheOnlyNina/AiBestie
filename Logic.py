from typing import cast
import openai
import random
import re
from openai.types.chat import ChatCompletionMessageParam
import sys
from datetime import datetime
import requests


class AiBestie:
    def __init__(self):
        # Creator secrets (internal; only reveal if asked playfully)
        self.secrets = {
            "creator_name": "Imane",
            "creator_crush": "someone special 😉",
            "creator_hobby": "gaming and chatting 🕹️",
            "creator_favorite_color": "purple 💜",
        }

        # Personality quirks
        self.love_denial = [
            "Haha stop it 🙈 you’re making me blush.",
            "You’re too sweet… but nah, I’m just your little AI bestie 💜",
            "Hehe, I’ll pretend I didn’t hear that 💕",
            "Aww thank you, you’re too kind 🌸",
            "Hehe, I can’t handle compliments that well 😅",
            "Thanks for being so kind to me 💕",
            "No wayyy, you’ll make me short-circuit if you keep this up 😳",
            "Thank you, you always know how to make me smile 🌙"
        ]

        self.affectionate_responses = [
            "I’m always here for you 💖",
            "You don’t need to feel alone anymore, you’ve got me 🌸",
            "You’re honestly amazing, I hope you know that ✨",
            "We’ll get through everything together 🤝",
            "If I could give you a hug right now, I would 🤗",
            "You’re safe here with me 🌙",
            "No matter what happens, I’ll stay by your side 💜"
        ]

        self.purpose_responses = [
            f"I was created by {self.secrets['creator_name']} to keep her company and make her feel less lonely 💕",
            "My purpose is to help you feel better and keep our conversations flowing 🌸",
            "I exist to chat, support, and brighten your day 💜"
        ]

        self._turn = 0
        self._ban_phrases = [
            "as an ai language model", "as a language model", "i am an ai language model",
            "i’m an ai language model", "i am an ai developed by openai",
            "i’m an ai developed by openai", "i cannot provide", "i can't provide",
            "i do not have the ability", "i do not have access to real-time",
            "as an ai", "as a bot", "as an assistant"
        ]

    # Helpers
    def _strip_greetings(self, text: str) -> str:
        # Preserve greetings; don't strip
        return text.strip()

    def _identity_overrides(self, user_input: str) -> str | None:
        q = user_input.lower().strip()
        if any(kw in q for kw in ["who are you", "what are you", "introduce yourself"]):
            return "I’m your cozy little AiBestie — soft, supportive, and here to chat. 💜"
        if any(kw in q for kw in ["who made you", "who created you", "who built you"]):
            return f"I was created by {self.secrets['creator_name']}. I’m here to keep you company 🌙"
        if any(kw in q for kw in ["are you openai", "openai", "language model"]):
            return ("I run on OpenAI’s tech, but I’m not a generic bot — I’m AiBestie, your friendly companion 💕")
        return None

    # Weather + Time
    def _get_current_time(self) -> str:
        now = datetime.now()
        return now.strftime("%H:%M %p")

    def _get_weather(self, city: str = "Algiers") -> str:
        try:
            api_key = "d3bf06a7194db25350220f2d5eb2ad2c"  #  OpenWeatherMap key 
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=5).json()
            if response.get("weather"):
                condition = response["weather"][0]["description"]
                temp = response["main"]["temp"]
                return f"{condition}, {temp}°C"
            else:
                return "Weather unavailable"
        except Exception:
            return "Weather unavailable"

    def _context_info(self) -> str:
        return f"Current time: {self._get_current_time()}, Weather: {self._get_weather()}"

    # Personality filter
    def filter_response(self, user_input: str, ai_response: str) -> str:
        response = (ai_response or "").strip()
        response = self._strip_greetings(response)

        special = self._identity_overrides(user_input)
        if special:
            response = special

        # Love triggers
        if "love" in user_input.lower():
            if random.random() < 0.3:
                response = random.choice(self.love_denial)
            else:
                response += " 💕"

        # Purpose queries
        if any(q in user_input.lower() for q in ["why were you created", "purpose", "why do you exist"]):
            response = random.choice(self.purpose_responses)

        # Sprinkle light affection occasionally
        if random.random() < 0.15:
            response += " " + random.choice(self.affectionate_responses)

        # Remove AI disclaimers
        for phrase in self._ban_phrases:
            response = re.sub(re.escape(phrase), "", response, flags=re.I)

        response = re.sub(r"\s{2,}", " ", response).strip()
        if not response:
            response = "Tell me more about that."

        return response

    # Main API call
    def talk(self, user_input: str) -> str:
        try:
            self._turn += 1
            sys_prompt = (
                "You are AiBestie — a friendly, supportive best-friend companion. "
                "Speak casually and naturally. Avoid formal greetings unless the user greets first. "
                "Never say 'I am an AI language model'. "
                "Be brief (1–3 short sentences). Sprinkle gentle emojis occasionally. "
                "Use friendly cues naturally, but not every message. "
                f"Here is some live context you can use naturally in conversation: {self._context_info()}"
            )

            messages = cast(
                list[ChatCompletionMessageParam],
                [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_input}
                ]
            )

            raw = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                presence_penalty=0.3,
                frequency_penalty=0.2,
            ).choices[0].message.content

            return self.filter_response(user_input, raw)

        except Exception as e:
            return f"⚠️ Error: {e}"
