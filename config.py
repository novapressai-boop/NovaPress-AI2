"""
NovaPress AI
Configuration
Version: 2.0
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
SOURCE_DIR = os.path.join(DATA_DIR, "sources")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

NEWS_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "news_output.json")

MAX_NEWS_PER_SOURCE = 5

USER_AGENT = "NovaPressAI/2.0"