"""
Project 1: Custom AI Chatbot with Memory  (Gemini free-tier version)
DecodeLabs — Generative AI Industrial Training Kit (Batch 2026)

Goal:
    Build a conversational terminal that remembers previous user
    messages during a live session using a stateful in-memory
    history array (client-side session state), connected to a
    frontier LLM via its official SDK.

Why Gemini here:
    Google's Gemini API offers a free tier (no billing required to
    get started), which makes it ideal for learning/training
    projects like this one. The same architecture below would work
    unchanged with Anthropic's Claude or OpenAI's SDK — only the
    client/API call section would differ.

Key requirements implemented:
    1. Connect to a frontier LLM using an official SDK + API key.
    2. Maintain an active in-memory list to store conversation history.
    3. Append every new user input and model response to that history,
       and transmit the FULL history on every turn (stateful loop).
    4. Structural Validation Gate — block empty / whitespace-only
       inputs before they ever reach the API (prevents 400 errors).
    5. Sliding Window Algorithm — FIFO pruning of the oldest message
       pairs once the history grows past a safe size, to avoid
       context-window / token-budget exhaustion.

Setup:
    pip install google-genai
    export GEMINI_API_KEY="your-key-here"   (get one free at aistudio.google.com/apikey)
    python chatbot_with_memory_gemini.py
"""

import os
import sys
from google import genai
from google.genai import types
from google.genai.errors import APIError


MODEL_NAME = "gemini-flash-latest"     # always points to Google's current Flash model
SYSTEM_PROMPT = "You are a helpful, concise AI assistant."

# Sliding window: max number of message OBJECTS (not pairs) kept
# in the in-memory history before we start pruning the oldest ones.
# Each user turn + model turn = 2 objects, so this keeps the last
# ~10 conversational turns of context.
MAX_HISTORY_MESSAGES = 20


class MemoryChatbot:
    """
    Wraps a stateful chat session on top of a stateless LLM API by
    maintaining an in-memory array (H) of role/content objects and
    resending it on every turn.
    """

    def __init__(self, api_key: str | None = None):
        # Official SDK client — reads GEMINI_API_KEY from env if not passed.
        self.client = genai.Client(api_key=api_key)

        # --- Block 001: Context State -----------------------------
        # The in-memory "historical array" (H_t-1 in the PDF's notation).
        # Each element: types.Content(role="user"/"model", parts=[...])
        self.history: list[types.Content] = []

    
    # Structural Validation Gate
    
    @staticmethod
    def _is_valid_input(user_input: str) -> bool:
        """Reject empty or whitespace-only payloads before they hit the API."""
        return bool(user_input and user_input.strip())

   
    # Sliding Window Algorithm (FIFO pruning)
   
    def _apply_sliding_window(self) -> None:
        """
        Keep the history array bounded so we never blow past the
        model's context window / token budget. Drops the OLDEST
        messages first (FIFO), always in pairs so we never leave a
        dangling user/model turn at the front of the array.
        """
        while len(self.history) > MAX_HISTORY_MESSAGES:
            del self.history[0:2]

    
    # The Terminal Append Sequence (core loop)
   
    def send(self, user_input: str) -> str:
        """
        Executes exactly the two-step sequence described in the deck:
          1. Ingest & Append: append the validated user input.
          2. Transmit & Record: send the whole history, then append
             the model's response to the same list.
        """
        # Step 1: Ingest & Append
        self.history.append(
            types.Content(role="user", parts=[types.Part(text=user_input)])
        )

        try:
            # Step 2: Transmit & Record — send the ENTIRE history array
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=self.history,          # <-- stateful payload (M_t ∪ H_t-1)
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                ),
            )
            reply_text = response.text

        except APIError as e:
            # Roll back the unpaired user turn so history stays consistent
            self.history.pop()
            return f"[API error — message not saved to history: {e}]"

        # Record the model's response into the same list
        self.history.append(
            types.Content(role="model", parts=[types.Part(text=reply_text)])
        )

        # Enforce the token-budget safety net for the *next* turn
        self._apply_sliding_window()

        return reply_text

    def reset(self) -> None:
        self.history = []



# Terminal interface

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set the GEMINI_API_KEY environment variable first.")
        print("Get a free key at: https://aistudio.google.com/apikey")
        sys.exit(1)

    bot = MemoryChatbot(api_key=api_key)

    print("=" * 60)
    print(" Custom AI Chatbot with Memory  —  DecodeLabs Project 1")
    print("=" * 60)
    print("Type your message and press Enter.")
    print("Commands: /reset (clear memory)   /exit (quit)\n")

    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not MemoryChatbot._is_valid_input(user_input):
            print("Bot: (empty message ignored — please type something)\n")
            continue

        cmd = user_input.strip().lower()
        if cmd == "/exit":
            print("Goodbye!")
            break
        if cmd == "/reset":
            bot.reset()
            print("Bot: Memory cleared. Starting a fresh session.\n")
            continue

        reply = bot.send(user_input)
        print(f"Bot: {reply}\n")


if __name__ == "__main__":
    main()
