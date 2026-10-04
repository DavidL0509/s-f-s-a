from data_generator import generate_fitness_data

##
class Participant:
    def __init__(
        self,
        participant_id,
        baseline_heart_rate,
        baseline_skin_response,
        baseline_temperature
    ):
        self.participant_id = participant_id
        self.baseline_heart_rate = baseline_heart_rate
        self.baseline_skin_response = baseline_skin_response
        self.baseline_temperature = baseline_temperature

    @classmethod
    def from_dict(cls, data):
        return cls(
            participant_id=data["participant_id"],
            baseline_heart_rate=data["baseline_heart_rate"],
            baseline_skin_response=data["baseline_skin_response"],
            baseline_temperature=data["baseline_temperature"]
        )

##
class Observation:
    def __init__(
        self,
        timestamp,
        heart_rate,
        skin_response,
        temperature,
        activity_level,
        signal_quality
    ):
        self.timestamp = timestamp
        self.heart_rate = heart_rate
        self.skin_response = skin_response
        self.temperature = temperature
        self.activity_level = activity_level
        self.signal_quality = signal_quality

    @classmethod
    def from_dict(cls, data):
        return cls(
            timestamp=data["timestamp"],
            heart_rate=data["heart_rate"],
            skin_response=data["skin_response"],
            temperature=data["temperature"],
            activity_level=data["activity_level"],
            signal_quality=data["signal_quality"]
        )

##
class FitnessSession:
    def __init__(self, participant):
        self.participant = participant
        self._observations = []

    @property
    def observations(self):
        return self._observations.copy()

    def add_observation(self, observation):
        self._observations.append(observation)


##
def main():
    profile, observations = generate_fitness_data(
        participant_id="P001",
        scenario="moderate_activity",
        seed=42,
        number_of_windows=10
    )

    participant = Participant.from_dict(profile)

    observation_objects = [
        Observation.from_dict(data)
        for data in observations
    ]

    session = FitnessSession(participant)

    for observation in observation_objects:
        session.add_observation(observation)

    print("Participant ID:", session.participant.participant_id)
    print("Baseline heart rate:", session.participant.baseline_heart_rate)
    print("Baseline skin response:", session.participant.baseline_skin_response)
    print("Baseline temperature:", session.participant.baseline_temperature)

    print("Number of observations:", len(session.observations))

    for observation in session.observations:
        print(
            "Timestamp:", observation.timestamp,
            "HR:", observation.heart_rate,
            "Skin:", observation.skin_response,
            "Temp:", observation.temperature,
            "Activity:", observation.activity_level,
            "Signal quality:", observation.signal_quality
        )


if __name__ == "__main__":
    main()