#!/usr/bin/env python
# ruff: noqa: ARG001 (unused-function-argument)

"""Telegram bot for the LUG-Taunus group.

Usage:
Execute script to start the bot, which will answer to commands.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

import httpx
from bs4 import BeautifulSoup
from telegram import ForceReply, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

from babbel_tux import settings

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

client = httpx.AsyncClient()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def termine(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /termine is issued."""
    response = await client.get("https://www.lug-taunus.org/termine")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    meta_description = soup.html.head.find("meta", itemprop="description")
    termine_content = meta_description["content"]
    termine = termine_content.replace("\v", "\n").replace("-- ", "")
    await update.message.reply_text(termine)


async def post_shutdown(application: Application) -> None:
    """Callback that is executed after shutting down the application."""
    # Close async HTTP client
    await client.aclose()


def main() -> None:
    """Start the telegram bot."""
    # Create the application and pass it the bot's token
    application = (
        Application.builder()
        .token(settings.TELEGRAM_TOKEN)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Add handlers to answer to commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("termine", termine))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
