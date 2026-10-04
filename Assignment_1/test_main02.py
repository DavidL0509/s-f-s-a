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

def validate_observation(observation):
    reasons = []

    if observation.timestamp is None:
        reasons.append("missing timestamp")
    elif observation.timestamp < 0:
        reasons.append("invalid timestamp")

    if observation.heart_rate is None:
        reasons.append("missing heart rate")
    elif observation.heart_rate < 35 or observation.heart_rate > 205:
        reasons.append("invalid heart rate")

    if observation.skin_response is None:
        reasons.append("missing skin response")
    elif observation.skin_response < 0:
        reasons.append("invalid skin response")

    if observation.temperature is None:
        reasons.append("missing temperature")
    elif observation.temperature < 25 or observation.temperature > 42:
        reasons.append("invalid temperature")

    if observation.activity_level is None:
        reasons.append("missing activity level")
    elif observation.activity_level < 0 or observation.activity_level > 1:
        reasons.append("invalid activity level")

    if observation.signal_quality is None:
        reasons.append("missing signal quality")
    elif observation.signal_quality < 0.80 or observation.signal_quality > 1:
        reasons.append("poor signal quality")

    if len(reasons) == 0:
        return True, reasons
    else:
        return False, reasons


##
class FitnessSession:
    def __init__(self, participant):
        self.participant = participant
        self._observations = []
        self._rejected_observations = []

    @property
    def observations(self):
        return self._observations.copy()

    @property
    def rejected_observations(self):
        return self._rejected_observations.copy()

    def add_observation(self, observation):
        is_valid, reasons = validate_observation(observation)

        if is_valid:
            self._observations.append(observation)
        else:
            self._rejected_observations.append((observation, reasons))

##
def main():
    profile, observations = generate_fitness_data(
        participant_id="P001",
        scenario="poor_quality",
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

    print("Participant ID:", participant.participant_id)
    print("Baseline heart rate:", participant.baseline_heart_rate)
    print("Baseline skin response:", participant.baseline_skin_response)
    print("Baseline temperature:", participant.baseline_temperature)

    print("Total observations:", len(observation_objects))
    print("Usable observations:", len(session.observations))
    print("Rejected observations:", len(session.rejected_observations))

    if len(session.rejected_observations) > 0:
        print("Rejected Observations:")

        for observation, reasons in session.rejected_observations:
            print(
                "Timestamp:", observation.timestamp,
                "Reasons:", reasons
            )


if __name__ == "__main__":
    main()