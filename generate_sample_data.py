import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

SAMPLE_DIR = "sample_input"
SAMPLE_FILENAME = f"{SAMPLE_DIR}/sample_weightlifting_data.csv"

people = ["Trevor", "Chris", "Alice", "Bob", "Emily"]
exercises = ["Bench Press (Barbell)", "Deadlift (Barbell)", "Squat (Barbell)"]
num_days = 90
start_date = datetime(2024, 1, 1)


data = []
for person in people:
    for exercise in exercises:
        weight_base = random.uniform(50, 100)
        weight_variation = random.uniform(0.1, 0.5)
        weight = weight_base
        for day in range(num_days):
            date = start_date + timedelta(days=day)
            weight += np.random.normal(weight_variation, 0.1) * (
                1 + day * 0.01
            )  # Progressive increase with variation
            data.append(
                {
                    "Person": person,
                    "Date": date,
                    "Workout Name": f"{person} Workout",
                    "Duration": "1h",
                    "Exercise Name": exercise,
                    "Set Order": 1,
                    "Weight": round(weight, 2),
                    "Reps": random.randint(5, 10),
                    "Distance": 0,
                    "Seconds": 0,
                    "Notes": "",
                    "Workout Notes": "",
                    "RPE": round(random.uniform(6, 10), 1),
                }
            )

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv(SAMPLE_FILENAME, index=False)
