import datetime
import random
from typing import Union, Callable, Dict


# ─────────────────────────────────────────────────────────────
# KNOWLEDGE BASE
# Maps a *normalised* user phrase → a response (string or
# callable that returns a string, for dynamic answers).
# ─────────────────────────────────────────────────────────────
KNOWLEDGE_BASE: Dict[str, Union[str, Callable[[], str]]] = {

    # ── Greetings ──────────────────────────────────────────
    "hello":        "Hello! 👋  How can I help you today?",
    "hi":           "Hi there! What's on your mind?",
    "hey":          "Hey! Great to see you. What can I do for you?",
    "good morning": "Good morning! ☀️  Hope you have a wonderful day ahead.",
    "good evening": "Good evening! 🌙  How has your day been?",
    # ── Farewells ──────────────────────────────────────────
    "bye":       "Goodbye! 👋  Take care and come back anytime.",
    "goodbye":   "See you later! Have a great one. 😊",
    "see you":   "See you! Feel free to chat whenever you need me.",

    # ── Time & Date ────────────────────────────────────────
    "what time is it": lambda: (
        f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}. 🕐"
    ),
    "what is the time": lambda: (
        f"Right now it's {datetime.datetime.now().strftime('%I:%M %p')}. 🕐"
    ),
    "what is today's date": lambda: (
        f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}. 📅"
    ),
    "what day is it": lambda: (
        f"Today is {datetime.datetime.now().strftime('%A')}. 📅"
    ),

    # ── Weather ────────────────────────────────────────────
    "what is the weather": (
        "I don't have live weather data, but you can check "
        "https://weather.com or ask your phone's assistant! 🌤️"
    ),
    "how is the weather": (
        "I wish I could peek outside for you! 😄  "
        "Try a weather app for the latest forecast."
    ),
    "will it rain today": (
        "I can't access live forecasts, but a quick search for your city "
        "on weather.com will tell you instantly. ☔"
    ),

    # ── Bot identity ───────────────────────────────────────
    "what is your name":  "I'm PyBot 🤖 — your rule-based Python assistant!",
    "who are you":        "I'm PyBot, a simple rule-based chatbot built in Python.",
    "who made you":       "I was crafted in pure Python using the IPO model. 🐍",
    "are you a robot":    "Technically yes — I'm a program, not a human. 🤖",
    "are you human":      "Nope! I'm PyBot, a Python chatbot. No coffee breaks for me. ☕",

    # ── Capabilities ───────────────────────────────────────
    "what can you do": (
        "I can:\n"
        "  • Tell you the current time and date 🕐📅\n"
        "  • Share weather guidance 🌤️\n"
        "  • Answer questions about myself 🤖\n"
        "  • Tell you a joke 😄\n"
        "  • Offer a motivational quote 💪\n"
        "  • Help with basic maths ➕\n"
        "Just type one of those topics!"
    ),
    "help": (
        "Here are some things you can ask me:\n"
        "  what time is it | what is today's date | what is the weather\n"
        "  tell me a joke  | motivate me          | what can you do\n"
        "  who are you     | bye\n"
        "Type 'exit' or 'quit' to leave."
    ),

    # ── Jokes ──────────────────────────────────────────────
    "tell me a joke": lambda: random.choice([
        "Why do Python programmers prefer dark mode? "
        "Because light attracts bugs! 🐛",

        "How many programmers does it take to change a light bulb? "
        "None — that's a hardware problem. 💡",

        "Why was the computer cold? Because it left its Windows open. 🪟",

        "I told my computer I needed a break. "
        "Now it won't stop sending me Kit-Kat ads. 🍫",
    ]),
    "joke": lambda: KNOWLEDGE_BASE["tell me a joke"](),

    # ── Motivation ─────────────────────────────────────────
    "motivate me": lambda: random.choice([
        "\"The secret of getting ahead is getting started.\" — Mark Twain 🚀",
        "\"It always seems impossible until it's done.\" — Nelson Mandela 💪",
        "\"Code is like humour. When you have to explain it, it's bad.\" — Cory House 😄",
        "\"First, solve the problem. Then, write the code.\" — John Johnson 🧠",
    ]),
    "give me a quote":     lambda: KNOWLEDGE_BASE["motivate me"](),
    "inspiration":         lambda: KNOWLEDGE_BASE["motivate me"](),

    # ── Basic maths ────────────────────────────────────────
    "what is 2 + 2":   "2 + 2 = 4. Easy one! 😄",
    "what is 10 / 2":  "10 ÷ 2 = 5. 🧮",
    "what is 3 * 3":   "3 × 3 = 9. 🧮",
    "what is 100 - 1": "100 − 1 = 99. 🧮",

    # ── Small talk ─────────────────────────────────────────
    "how are you": (
        "I'm just a program, so I don't have feelings — "
        "but my circuits are running smoothly! ⚡  How about you?"
    ),
    "i am fine":   "Glad to hear it! 😊  What can I help you with?",
    "i am great":  "Awesome! 🎉  Let me know if there's anything you need.",
    "i am sad":    (
        "I'm sorry to hear that. 💙  "
        "Remember: every storm runs out of rain. Things will get better!"
    ),
    "thank you":   "You're welcome! 😊  Happy to help.",
    "thanks":      "No problem at all! Let me know if you need anything else.",
}

# Fallback for unrecognised input (used by .get() default parameter)
FALLBACK: str = (
    "🤔  I'm not sure how to help with that.\n"
    "   Type 'help' to see what I can do, or try rephrasing your question."
)

# Commands that terminate the loop
EXIT_COMMANDS: frozenset[str] = frozenset({"exit", "quit", "q", "close", "stop"})


# ─────────────────────────────────────────────────────────────
# PROCESS LAYER
# Responsible for sanitising input and resolving a response.
# ─────────────────────────────────────────────────────────────

def sanitise(raw: str) -> str:
    """
    INPUT  → normalised string
    Strips leading/trailing whitespace and converts to lowercase so
    that 'Hello', 'HELLO', and '  hello  ' all map to the same key.
    """
    return raw.strip().lower()


def resolve_response(intent: str) -> str:
    """
    PROCESS → OUTPUT string
    Performs an O(1) dictionary look-up via .get().
    If the value stored is callable (a lambda), it is invoked to
    produce a dynamic response (e.g. real-time clock/date/joke).
    """
    response = KNOWLEDGE_BASE.get(intent, FALLBACK)   # O(1) hash-table lookup
    return response() if callable(response) else response


# ─────────────────────────────────────────────────────────────
# MAIN LOOP  (Input → Process → Output)
# ─────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  PyBot 🤖  |  Rule-Based AI Chatbot (IPO Model)")
    print("  Type 'help' for options  |  'exit' to quit")
    print("=" * 60)

    while True:
        # ── INPUT ────────────────────────────────────────
        raw_input: str = input("\nYou: ")

        # ── PROCESS ──────────────────────────────────────
        intent: str = sanitise(raw_input)          # normalise

        if intent in EXIT_COMMANDS:                # check exit first
            print("\nPyBot: Goodbye! 👋  It was nice chatting with you.\n")
            break
        bot_reply: str = resolve_response(intent)  # O(1) lookup

        # ── OUTPUT ───────────────────────────────────────
        print(f"\nPyBot: {bot_reply}")


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()