import csv

from fitness_app.models import Participant ##
##
def load_participants(file_path):
    participants = {}

    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            participant = Participant(
                participant_id=row["participant_id"],
                name=row["name"],
                baseline_heart_rate=int(row["baseline_heart_rate"]),
                baseline_skin_response=float(row["baseline_skin_response"]),
                baseline_temperature=float(row["baseline_temperature"])
            )

            participants[participant.participant_id] = participant

    return participants