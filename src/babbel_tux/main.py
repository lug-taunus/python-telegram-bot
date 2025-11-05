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
    """Send a welcome message on the first interaction with the bot."""
    user = update.effective_user
    text = rf"""Hi {user.mention_html()}! I am Babbel Tux, nice to meet you.

For more information about what I can do type the /help command.
"""
    await update.message.reply_html(
        text,
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a short help text and a list of commands."""
    commands = ""
    for handler_group in context.application.handlers.values():
        for handler in handler_group:
            if isinstance(handler, CommandHandler):
                command_str = ", /".join(handler.commands)
                commands += f"/{command_str} - {handler.callback.__doc__}\n"
    text = rf"""I can help you find out more about the LUG-Taunus.

Following a list of commands you can use:

{commands}"""
    await update.message.reply_text(text)


async def dates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with the next dates for the LUG-Taunus meetings."""
    response = await client.get("https://www.lug-taunus.org/termine")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    meta_description = soup.html.head.find("meta", itemprop="description")
    content = meta_description["content"]
    dates = content.replace("\v", "\n").replace("-- ", "")
    await update.message.reply_text(dates)


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
    application.add_handler(CommandHandler({"dates", "termine"}, dates))

    # Run the bot until the user presses Ctrl-C
    # Drop pending updates (e.g. messages received while the bot was offline)
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
