from fitness_app.file_handling import load_participants

##
def main():
    participants = load_participants("data/participants.csv")

    for participant_id in participants:
        participant = participants[participant_id]

        print(
            participant.participant_id,
            participant.name,
            participant.baseline_heart_rate,
            participant.baseline_skin_response,
            participant.baseline_temperature
        )

if __name__ == "__main__":
    main()