"""Module for reading the applications settings from the environment file."""

from os import environ

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = environ["TELEGRAM_TOKEN"]
