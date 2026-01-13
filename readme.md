# Receipt Expense Viewer Bot

A Discord bot that uses AI (Google Gemini 1.5 Flash) to analyze receipt images, extract items and prices (handling discounts automatically), and generate expense pie charts.

## Prerequisites

- **Python 3.10+** installed on your system.
- A **Discord Bot Token** (from the [Discord Developer Portal](https://discord.com/developers/applications)).
- A **Google Gemini API Key** (free from [Google AI Studio](https://aistudio.google.com/)).

## Installation

1.  **Clone or Download** this repository.
2.  **Open a terminal** in the project folder.
3.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    ```
4.  **Activate the virtual environment**:
    - **Windows**: `.\venv\Scripts\activate`
    - **Mac/Linux**: `source venv/bin/activate`
5.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Copy the example environment file:
    ```bash
    cp .env.example .env
    # OR just create a new file named .env
    ```
2.  Open `.env` and add your keys:
    ```env
    DISCORD_TOKEN=your_discord_bot_token_here
    GEMINI_API_KEY=your_gemini_api_key_here
    ```

## Running the Bot

1.  Start the bot:
    ```bash
    python bot.py
    ```
2.  **Slash Command Registration**:
    - If you don't see the commands immediately, type `!sync` in your Discord server to force-register them.

## Usage

- Type `/analyze` in Discord.
- **Attach a receipt image** (JPG/PNG).
- The bot will reply with:
    - A list of items and their net prices (discounts subtracted).
    - A pie chart showing the top expenses (with quantities aggregated).
