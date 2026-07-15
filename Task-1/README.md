# Custom AI Chatbot with Memory

**DecodeLabs Generative AI Industrial Training Kit | Batch 2026 | Project 1**

## Overview

This project implements a **stateful conversational chatbot** on top of a
stateless LLM API (Google Gemini). Since every request to a frontier
LLM is treated as an isolated transaction, this script builds an
**artificial memory loop** by maintaining an in-memory history array that
gets resent on every conversational turn allowing the model to recall
earlier parts of the conversation during a live session.

## Features

- **Stateful session memory**  maintains an in-memory `list` of
  `Content` objects (role + parts) across turns.
- **Terminal Append Sequence** every turn: (1) ingest & append the
  user's input, (2) transmit the full history to the API, then append
  the model's response back into history.
- **Structural Validation Gate** blocks empty or whitespace-only
  input before it ever reaches the API, preventing crashes from `400
  Bad Request` errors.
- **Sliding Window (FIFO) Algorithm** automatically prunes the
  oldest message pairs once the history grows past a safe size, to
  avoid context-window / token-budget exhaustion.
- **Simple terminal interface** with `/reset` and `/exit` commands.

##  Tech Stack

- Python 3.14
- [Google Gen AI SDK](https://github.com/googleapis/python-genai) (official, `google-genai`)
- Gemini (frontier LLM) free tier available

## Project Structure

.
 chatbot_with_memory_gemini.py   # main chatbot script
 README.md                       # this file


## Setup & Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/<safianaz6777>/<DecodeLabs-Internship>.git
   cd <DecodeLabs-Internship>
   ```

2. **Install dependencies**
   ```bash
   pip install google-genai
   ```

3. **Get a free API key**

   Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey),
   sign in with a Google account, and click **Create API Key**. No
   billing/credit card is required for the free tier.

4. **Set your API key**

   Windows CMD:
   ```cmd
   set GEMINI_API_KEY="GEMINI_API_KEY"
   ```
   

5. **Run the chatbot**
   ```bash
   python chatbot_with_memory_gemini.py
   ```

## Example Session (Memory Test)

```
You: My name is Safia
Bot: Nice to meet you, Safia! How can I help you today?

You: Write a poem about tech
Bot: (generates a poem large-volume output used to "distract" the context)

You: What is my name?
Bot: Your name is Safia.
```

This confirms the chatbot correctly retains context across multiple
turns using the in-memory sliding-window history array.

## How It Works (Architecture)

```
User Input → Validation Gate → Append to History
                                     ↓
                       Send FULL History to Gemini API
                                     ↓
                    Append Model Response to History
                                     ↓
                  Apply Sliding Window (FIFO prune if needed)
```

## Commands

| Command   | Description                          |
|-----------|---------------------------------------|
| `/reset`  | Clears the in-memory conversation     |
| `/exit`   | Ends the session                      |

## License

Built as part of the DecodeLabs Generative AI Industrial Training Kit (2026).

## Contact

DecodeLabs decodelabs.tech@gmail.com | www.decodelabs.tech
