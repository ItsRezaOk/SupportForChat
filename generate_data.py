# generate_data.py
from faker import Faker
import random
import pandas as pd

fake = Faker()
tickets = []

categories = [
    'Login Issue',
    'Payment Failed',
    'Account Locked',
    'App Crash',
    'Slow App',
    'Missing Features',
    'Bug Report',
    'Poor Support',
    'UI Confusion'
]

for _ in range(1000):
    ticket = {
        'ticket_id': fake.uuid4(),
        'user': fake.name(),
        'issue': fake.sentence(nb_words=12),
        'category': random.choice(categories),
        'timestamp': fake.date_time_this_year()
    }
    tickets.append(ticket)

df = pd.DataFrame(tickets)
df.to_csv('support_tickets.csv', index=False)

print("support_tickets.csv created.")
