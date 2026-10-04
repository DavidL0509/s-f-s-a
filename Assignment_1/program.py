

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
def calculate_session_summaries(observations):
    heart_rates = []
    skin_responses = []
    temperatures = []
    activity_levels = []

    for observation in observations:
        heart_rates.append(observation.heart_rate)
        skin_responses.append(observation.skin_response)
        temperatures.append(observation.temperature)
        activity_levels.append(observation.activity_level)

    return {
        "heart_rate": calculate_summary(heart_rates),
        "skin_response": calculate_summary(skin_responses),
        "temperature": calculate_summary(temperatures),
        "activity_level": calculate_summary(activity_levels)
    }

##
def detect_recovery(observations):
    first_observation = observations[0]
    last_observation = observations[-1]

    heart_rate_decline = (
        (first_observation.heart_rate - last_observation.heart_rate)
        / first_observation.heart_rate
    ) * 100

    if first_observation.activity_level == 0:
        activity_decline = 0
    else:
        activity_decline = (
            (first_observation.activity_level - last_observation.activity_level)
            / first_observation.activity_level
        ) * 100

    if heart_rate_decline >= 30 and activity_decline >= 30:
        return True
    else:
        return False

##
def classify_session(observations, average_activity):
    recovery = detect_recovery(observations)

    if recovery:
        classification = "recovering"
        reason = "Both heart rate and activity declined by at least 30%."

    elif average_activity <= 0.33:
        classification = "resting"
        reason = "Average activity level is <= 0.33."

    elif average_activity <= 0.66:
        classification = "moderate activity"
        reason = "Average activity level is over 0.33 and <= 0.66."

    else:
        classification = "high activity"
        reason = "Average activity level is > 0.66."

    return classification, reason

##
def analyze_session(session):
    usable = session.observations
    rejected = session.rejected_observations

    usable_count = len(usable)
    rejected_count = len(rejected)
    total_count = usable_count + rejected_count

    ## Stop if there is not enough usable data
    if usable_count < 6:
        return {
            "participant_id": session.participant.participant_id,
            "total_observations": total_count,
            "usable_observations": usable_count,
            "rejected_observations": rejected_count,
            "classification": "insufficient data",
            "reason": "Fewer than 6 usable observations.",
            "summaries": None,
            "baseline_comparison": None
        }

    ## Calculate summaries
    summaries = calculate_session_summaries(usable)

    average_activity = summaries["activity_level"]["average"]

    ## Classify session
    classification, reason = classify_session(
        usable,
        average_activity
    )

    ## Compare averages with baselines
    baseline_comparison = {
        "heart_rate": (
            summaries["heart_rate"]["average"]
            - session.participant.baseline_heart_rate
        ),

        "skin_response": (
            summaries["skin_response"]["average"]
            - session.participant.baseline_skin_response
        ),

        "temperature": (
            summaries["temperature"]["average"]
            - session.participant.baseline_temperature
        )
    }

    ## Create final result
    result = {
        "participant_id": session.participant.participant_id,
        "total_observations": total_count,
        "usable_observations": usable_count,
        "rejected_observations": rejected_count,

        "baselines": {
            "heart_rate": session.participant.baseline_heart_rate,
            "skin_response": session.participant.baseline_skin_response,
            "temperature": session.participant.baseline_temperature
        },

        "summaries": summaries,
        "baseline_comparison": baseline_comparison,
        "classification": classification,
        "reason": reason
    }

    return result

##
def print_report(result):
    print("\nSession Report")

    print("Participant ID:", result["participant_id"])
    print("Total observations:", result["total_observations"])
    print("Usable observations:", result["usable_observations"])
    print("Rejected observations:", result["rejected_observations"])

    ## Stop if there was not enough usable data
    if result["summaries"] is None:
        print("\nClassification:", result["classification"])
        print("Reason:", result["reason"])
        return

    summaries = result["summaries"]
    baselines = result["baselines"]
    comparison = result["baseline_comparison"]

    print("\nHeart rate:")
    print("Baseline:", baselines["heart_rate"])
    print("Average:", round(summaries["heart_rate"]["average"], 2))
    print("Difference from baseline:", round(comparison["heart_rate"], 2))
    print("Minimum:", summaries["heart_rate"]["minimum"])
    print("Maximum:", summaries["heart_rate"]["maximum"])

    print("\nSkin response:")
    print("Baseline:", baselines["skin_response"])
    print("Average:", round(summaries["skin_response"]["average"], 2))
    print("Difference from baseline:", round(comparison["skin_response"], 2))
    print("Minimum:", summaries["skin_response"]["minimum"])
    print("Maximum:", summaries["skin_response"]["maximum"])

    print("\nTemperature:")
    print("Baseline:", baselines["temperature"])
    print("Average:", round(summaries["temperature"]["average"], 2))
    print("Difference from baseline:", round(comparison["temperature"], 2))
    print("Minimum:", summaries["temperature"]["minimum"])
    print("Maximum:", summaries["temperature"]["maximum"])

    print("\nActivity level:")
    print("Average:", round(summaries["activity_level"]["average"], 2))
    print("Minimum:", summaries["activity_level"]["minimum"])
    print("Maximum:", summaries["activity_level"]["maximum"])

    print("\nClassification:", result["classification"])
    print("Reason:", result["reason"])