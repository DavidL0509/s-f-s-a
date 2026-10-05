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
    highest_heart_rate = observations[0].heart_rate
    highest_activity = observations[0].activity_level

    for observation in observations:
        if observation.heart_rate > highest_heart_rate:
            highest_heart_rate = observation.heart_rate

        if observation.activity_level > highest_activity:
            highest_activity = observation.activity_level

    last_observation = observations[-1]

    heart_rate_drop = (
        highest_heart_rate - last_observation.heart_rate
    ) / highest_heart_rate

    if highest_activity == 0:
        activity_drop = 0
    else:
        activity_drop = (
            highest_activity - last_observation.activity_level
        ) / highest_activity

    if heart_rate_drop >= 0.30 and activity_drop >= 0.30:
        return True

    return False

##
def classify_session(observations, average_activity):
    if detect_recovery(observations):
        return (
            "recovering",
            "Heart rate and activity both declined by at least 30 percent from their session peaks."
        )

    if average_activity <= 0.33:
        return (
            "resting",
            "Average activity level is <= 0.33."
        )

    if average_activity <= 0.66:
        return (
            "moderate activity",
            "Average activity level is over 0.33 and <= 0.66."
        )

    return (
        "high activity",
        "Average activity level is > 0.66."
    )

##
def analyze_session(session):
    observations = session.observations
    usable_count = len(observations)

    if usable_count < 6:
        return {
            "session_id": session.session_id,
            "participant_id": session.participant.participant_id,
            "participant_name": session.participant.name,
            "usable_observations": usable_count,
            "classification": "insufficient data",
            "reason": "Fewer than 6 usable observations.",
            "summaries": None,
            "baseline_comparison": None
        }

    summaries = calculate_session_summaries(observations)

    classification, reason = classify_session(
        observations,
        summaries["activity_level"]["average"]
    )

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

    return {
        "session_id": session.session_id,
        "participant_id": session.participant.participant_id,
        "participant_name": session.participant.name,
        "usable_observations": usable_count,
        "classification": classification,
        "reason": reason,
        "summaries": summaries,
        "baseline_comparison": baseline_comparison
    }