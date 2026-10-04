from fitness_app.file_handling import load_participants, load_sessions ##

##
def main():
    participants = load_participants("data/participants.csv")

    sessions = load_sessions(
        "data/fitness_sessions.csv",
        participants
    )

    for session_id in sessions:
        session = sessions[session_id]

        print(
            session.session_id,
            session.participant.name,
            len(session.observations)
        )

if __name__ == "__main__":
    main()