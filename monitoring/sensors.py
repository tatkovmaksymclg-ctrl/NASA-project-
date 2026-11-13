"""Генератор демонстраційних біометричних даних."""
from datetime import datetime, timedelta
import random
import pandas as pd

ASTRONAUTS = ["Командир місії", "Бортінженер", "Фахівець місії"]

def generate_history(hours: int = 24, seed: int = 7) -> pd.DataFrame:
    """Генерує вимірювання кожні 5 хвилин для трьох умовних космонавтів."""
    rng = random.Random(seed)
    now = datetime.now().replace(second=0, microsecond=0)
    rows = []

    for person_index, person in enumerate(ASTRONAUTS):
        for step in range(hours * 12 + 1):
            timestamp = now - timedelta(minutes=5 * (hours * 12 - step))
            heart_rate = rng.gauss(72 + person_index * 2, 5)
            systolic = rng.gauss(118, 8)
            diastolic = rng.gauss(76, 6)
            temperature = rng.gauss(36.7, 0.18)
            spo2 = rng.gauss(98, 0.7)
            respiration = rng.gauss(15, 1.8)

            # Навмисно змодельовані епізоди для перевірки системи сповіщень.
            if person_index == 1 and 190 <= step <= 205:
                heart_rate += 38
                spo2 -= 5
            if person_index == 2 and 245 <= step <= 258:
                temperature += 1.1

            rows.append({
                "timestamp": timestamp,
                "astronaut": person,
                "heart_rate": round(max(35, heart_rate), 1),
                "systolic": round(max(70, systolic), 1),
                "diastolic": round(max(40, diastolic), 1),
                "temperature": round(temperature, 2),
                "spo2": round(min(100, max(70, spo2)), 1),
                "respiration": round(max(5, respiration), 1),
            })

    return pd.DataFrame(rows)
