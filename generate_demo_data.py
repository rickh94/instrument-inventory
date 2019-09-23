import os
import random
import string
import subprocess
from multiprocessing.pool import Pool
from pathlib import Path

import names
import ujson

from app.utils.api_models import (
    InstrumentTypeEnum,
    InstrumentSizeEnum,
    LocationEnum,
    Instrument,
)

parent = Path("/tmp") / "mock_instrument_data"
os.makedirs(parent, exist_ok=True)


def run_create(data):
    event_path: Path = Path("/tmp") / "".join(random.choice(string.ascii_letters))
    event_data = {
        "body": data,
        "requestContext": {"identity": {"cognitoIdentityId": "MOCK-DATA-123"}},
    }
    with event_path.open("w") as event_file:
        ujson.dump(event_data, event_file)

    cmd = [
        "pipenv",
        "run",
        "serverless",
        "invoke",
        "--stage",
        "demo",
        "-f",
        "create",
        "-p",
        str(event_path.absolute()),
    ]
    subprocess.run(cmd)


def instrument_type():
    return random.choice(list(InstrumentTypeEnum.__members__.values()))


def instrument_size():
    return random.choice(list(InstrumentSizeEnum.__members__.values()))


def instrument_location():
    return random.choice(list(LocationEnum.__members__.values()))


def maintenance_notes():
    if random.randint(0, 1):
        return ", ".join(
            random.choice(
                [
                    "pegs slip",
                    "bridge warped",
                    "needs cleaning",
                    "needs strings",
                    "seam open",
                    "chinrest broken",
                ]
            )
            for _ in range(0, random.randint(1, 5))
        )
    return ""


def condition_notes():
    if random.randint(0, 1):
        return ", ".join(
            random.choice(
                [
                    "scratches on top",
                    "scratches on back",
                    "poor quality",
                    "writing on instrument",
                    "bad repair",
                ]
            )
            for _ in range(0, random.randint(1, 5))
        )
    return ""


def condition_rating():
    return random.randint(0, 5)


def quality_rating():
    return random.randint(0, 5)


def gifted():
    return random.choice([True, False])


def assigned_to():
    if random.randint(0, 3):
        return names.get_full_name()


def generate_instrument(number: int):
    return Instrument(
        number=number,
        size=instrument_size(),
        type=instrument_type(),
        location=instrument_location(),
        assignedTo=assigned_to(),
        maintenanceNotes=maintenance_notes(),
        conditionNotes=condition_notes(),
        condition=condition_rating(),
        quality=quality_rating(),
        gifted=gifted(),
    ).json()


def generate_and_create(number: int):
    ins = generate_instrument(number)
    run_create(ins)


if __name__ == "__main__":
    with Pool(4) as p:
        p.map(generate_and_create, range(5, 150))
