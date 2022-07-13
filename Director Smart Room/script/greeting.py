"""Provides a random greeting every day."""
import logging
import random
from datetime import date

GREETINGS = [
    'Work it, Make it, Do it',
    'Don’t criticize what you can’t understand.',
    'Stay positive. Attitude is everything.',
    'If it was easy, everybody could do it!',
    'Tomorrow is a day that never arrives.',
    'Patience is a key element of success.',
]

CURRENT = GREETINGS[0]
LAST_UPDATED = 0


def get_greeting():
    """Returns the current greeting."""
    global CURRENT
    global LAST_UPDATED

    if not date.today() == LAST_UPDATED:
        CURRENT = random.choice(GREETINGS)
        LAST_UPDATED = date.today()

    return CURRENT
try:
    import custom_greetings
    GREETINGS.extend(custom_greetings.GREETINGS)
except ModuleNotFoundError:
    logging.info('Using default greetings module.')
