from pathlib import Path

from fitness_app.file_handling import (
    load_participants,
    load_sessions,
    write_output
)

from fitness_app.analysis import analyze_session


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

    sessions = {}
    sessions.update(valid_sessions)
    sessions.update(invalid_sessions)

    results = []

    for session_id in sessions:
        result = analyze_session(sessions[session_id])
        results.append(result)

    rejected_records = (
        rejected_participants
        + rejected_valid
        + rejected_invalid
    )

    accepted_observations = 0

    for result in results:
        accepted_observations += result["usable_observations"]

    write_output(results, rejected_records)

    print("Processed sessions:", len(results))
    print("Accepted observations:", accepted_observations)
    print("Rejected records:", len(rejected_records))
    print("Created files:")
    print("output/analysis_summary.csv")
    print("output/analysis_report.txt")
    print("output/rejected_records.txt")


if __name__ == "__main__":
    main()