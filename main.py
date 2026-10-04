from pathlib import Path

from fitness_app.file_handling import load_participants, load_sessions


def main():
    data_dir = Path("data")

    participants, rejected_participants = load_participants(
        data_dir / "participants.csv"
    )

    valid_sessions, rejected_valid = load_sessions(
        data_dir / "fitness_sessions.csv",
        participants
    )

    invalid_sessions, rejected_invalid = load_sessions(
        data_dir / "fitness_sessions_invalid.csv",
        participants
    )

    print("Participants:", len(participants))
    print("Valid sessions:", len(valid_sessions))
    print("Rejected from valid file:", len(rejected_valid))

    print()
    print("Invalid-file sessions:", len(invalid_sessions))
    print("Rejected from invalid file:", len(rejected_invalid))

    print()
    print("Rejected records:")

    for record in rejected_invalid:
        print(record)


if __name__ == "__main__":
    main()