from data_generator import generate_fitness_data

from program import (
    Participant,
    Observation,
    FitnessSession,
    analyze_session,
    print_report
)


def main():
    profile, observations = generate_fitness_data(
        participant_id="P001",
        scenario="high_activity",
        seed=42,
        number_of_windows=10
    )

    participant = Participant.from_dict(profile)

    session = FitnessSession(participant)

    for data in observations:
        observation = Observation.from_dict(data)
        session.add_observation(observation)

    result = analyze_session(session)

    print_report(result)


if __name__ == "__main__":
    main()