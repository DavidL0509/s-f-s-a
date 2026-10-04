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

def calculate_summary(values):
    if len(values) == 0:
        return None

    return {
        "average": sum(values) / len(values),
        "minimum": min(values),
        "maximum": max(values)
    }

##

def compare_to_baseline(average_value, baseline_value):
    return average_value - baseline_value

##
def main():
    ## Generate raw data
    profile, observations = generate_fitness_data(
        participant_id="P001",
        scenario="recovery",
        seed=42,
        number_of_windows=10
    )

    ## Convert participant dictionary to Participant object
    participant = Participant.from_dict(profile)

    ## Convert observation dictionaries to Observation objects
    observation_objects = []

    for data in observations:
        observation_objects.append(Observation.from_dict(data))

    ## Create session and validate observations
    session = FitnessSession(participant)

    for observation in observation_objects:
        session.add_observation(observation)

    ## Check how many observations are usable
    total_observations = len(observation_objects)
    usable_observations = len(session.observations)
    rejected_observations = len(session.rejected_observations)

    if usable_observations < 6:
        print("Participant ID:", participant.participant_id)
        print("Total observations:", total_observations)
        print("Usable observations:", usable_observations)
        print("Rejected observations:", rejected_observations)
        print("Insufficient data for analysis.")
        return

    ## Collect values from usable observations
    heart_rates = []
    skin_responses = []
    temperatures = []
    activity_levels = []

    for observation in session.observations:
        heart_rates.append(observation.heart_rate)
        skin_responses.append(observation.skin_response)
        temperatures.append(observation.temperature)
        activity_levels.append(observation.activity_level)

    ## Calculate summaries
    heart_rate_summary = calculate_summary(heart_rates)
    skin_response_summary = calculate_summary(skin_responses)
    temperature_summary = calculate_summary(temperatures)
    activity_summary = calculate_summary(activity_levels)

    ## Compare averages with participant baselines
    heart_rate_difference = compare_to_baseline(
        heart_rate_summary["average"],
        participant.baseline_heart_rate
    )

    skin_response_difference = compare_to_baseline(
        skin_response_summary["average"],
        participant.baseline_skin_response
    )

    temperature_difference = compare_to_baseline(
        temperature_summary["average"],
        participant.baseline_temperature
    )

    ##

    print("Participant ID:", participant.participant_id)
    print("Total observations:", total_observations)
    print("Usable observations:", usable_observations)
    print("Rejected observations:", rejected_observations)

    print("\nHeart rate:")
    print("Baseline:", participant.baseline_heart_rate)
    print("Average:", round(heart_rate_summary["average"], 2))
    print("Difference from baseline:", round(heart_rate_difference, 2))
    print("Minimum:", heart_rate_summary["minimum"])
    print("Maximum:", heart_rate_summary["maximum"])

    print("\nSkin response:")
    print("Baseline:", participant.baseline_skin_response)
    print("Average:", round(skin_response_summary["average"], 2))
    print("Difference from baseline:", round(skin_response_difference, 2))
    print("Minimum:", skin_response_summary["minimum"])
    print("Maximum:", skin_response_summary["maximum"])

    print("\nTemperature:")
    print("Baseline:", participant.baseline_temperature)
    print("Average:", round(temperature_summary["average"], 2))
    print("Difference from baseline:", round(temperature_difference, 2))
    print("Minimum:", temperature_summary["minimum"])
    print("Maximum:", temperature_summary["maximum"])

    print("\nActivity level:")
    print("Average:", round(activity_summary["average"], 2))
    print("Minimum:", activity_summary["minimum"])
    print("Maximum:", activity_summary["maximum"])


if __name__ == "__main__":
    main()