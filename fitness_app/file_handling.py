import csv

from fitness_app.models import Participant, Observation, FitnessSession ##

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

##
def load_sessions(file_path, participants):
    sessions = {}

    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            session_id = row["session_id"]
            participant_id = row["participant_id"]

            participant = participants[participant_id]

            timestamp = int(row["timestamp"])
            heart_rate = int(row["heart_rate"])
            skin_response = float(row["skin_response"])
            temperature = float(row["temperature"])
            activity_level = float(row["activity_level"])
            signal_quality = float(row["signal_quality"])

            observation = Observation(
                timestamp,
                heart_rate,
                skin_response,
                temperature,
                activity_level,
                signal_quality
            )

            if session_id not in sessions:
                sessions[session_id] = FitnessSession(
                    session_id,
                    participant
                )

            sessions[session_id].add_observation(observation)

    return sessions