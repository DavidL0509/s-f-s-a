##
class Participant:
    def __init__(
        self,
        participant_id,
        name,
        baseline_heart_rate,
        baseline_skin_response,
        baseline_temperature
    ):
        self.participant_id = participant_id
        self.name = name
        self.baseline_heart_rate = baseline_heart_rate
        self.baseline_skin_response = baseline_skin_response
        self.baseline_temperature = baseline_temperature

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

##
class FitnessSession:
    def __init__(self, session_id, participant):
        self.session_id = session_id
        self.participant = participant
        self._observations = []

    @property
    def observations(self):
        return self._observations.copy()

    def add_observation(self, observation):
        self._observations.append(observation)