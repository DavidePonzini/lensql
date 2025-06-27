import random

RESPONSE_FORMAT = '''
Format the response as follows:
- SQL code (e.g. tables, columns or keywords) should be enclosed in <code></code> tags
- You should refer to records/tuples/rows as rows
'''


def get_introduction_sentence() -> str:
    introductions = [
        "Mhh... let me think about this.",
        "Let me see... I think I can help you with that.",
        "Let's see what we can do here.",
        "Hmm... yes, this is an interesting query.",
        "Alright, let's take a closer look at this query.",
        "Hmm... this is an interesting one.",
        "Alright, let's take a closer look at this.",
        "Okay, I think I understand what you're asking.",
    ]

    return random.choice(introductions) + '<br>'


def get_motivational_message_result() -> str:
    return  "BRIEF MOTIVATIONALLY-POSITIVE MESSAGE REFERRING TO LENS'S ADVENTURES IN THE QUERY'S STYLE."

def get_motivational_message_error() -> str:
    return  "BRIEF MOTIVATIONALLY-POSITIVE MESSAGE REFERRING TO LENS'S ADVENTURES RELATED TO THE ERROR."
