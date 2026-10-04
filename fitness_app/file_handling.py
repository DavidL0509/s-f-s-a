import csv
import re

from fitness_app.models import Participant, Observation, FitnessSession

##
class InvalidIdentifierError(ValueError):
    """Raised when an identifier has an invalid format."""
    pass

##
class InvalidRecordError(ValueError):
    """Raised when a CSV record cannot be accepted."""
    pass

##
def add_rejected_record(
    rejected_records,
    file_path,
    row_number,
    field,
    reason
):
    rejected_records.append({
        "file": str(file_path),
        "row": row_number,
        "field": field,
        "reason": reason
    })

##
def validate_participant_id(participant_id):
    if not re.fullmatch(r"P\d{3}", participant_id):
        raise InvalidIdentifierError("invalid ID")

##
def validate_session_id(session_id):
    if not re.fullmatch(r"FIT-\d{4}-\d{3}", session_id):
        raise InvalidIdentifierError("invalid ID")


##
def validate_observation(observation):
    if observation.timestamp < 0:
        return "timestamp", "out of range"

    if observation.heart_rate < 35 or observation.heart_rate > 205:
        return "heart_rate", "out of range"

    if observation.skin_response < 0:
        return "skin_response", "out of range"

    if observation.temperature < 25 or observation.temperature > 42:
        return "temperature", "out of range"

    if observation.activity_level < 0 or observation.activity_level > 1:
        return "activity_level", "out of range"

    if observation.signal_quality < 0 or observation.signal_quality > 1:
        return "signal_quality", "out of range"

    if observation.signal_quality < 0.80:
        return "signal_quality", "poor signal"

    return None, None


##
def load_participants(file_path):
    participants = {}
    rejected_records = []

    try:
        with open(file_path, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):

                ## Check missing values
                try:
                    for column_name, value in row.items():
                        if column_name is not None:
                            if value is None or value.strip() == "":
                                raise InvalidRecordError("missing value")

                except InvalidRecordError as error:
                    add_rejected_record(
                        rejected_records,
                        file_path,
                        row_number,
                        column_name,
                        str(error)
                    )
                    continue

                ## Read required fields
                try:
                    current_field = "participant_id"
                    participant_id = row[current_field]

                    current_field = "name"
                    name = row[current_field]

                    current_field = "baseline_heart_rate"
                    baseline_heart_rate = row[current_field]

                    current_field = "baseline_skin_response"
                    baseline_skin_response = row[current_field]

                    current_field = "baseline_temperature"
                    baseline_temperature = row[current_field]

                except KeyError:
                    add_rejected_record(
                        rejected_records,
                        file_path,
                        row_number,
                        current_field,
                        "missing field"
                    )
                    continue

                ## Validate participant ID
                try:
                    validate_participant_id(participant_id)

                except InvalidIdentifierError:
                    add_rejected_record(
                        rejected_records,
                        file_path,
                        row_number,
                        "participant_id",
                        "invalid ID"
                    )
                    continue

                ## Convert numbers
                try:
                    current_field = "baseline_heart_rate"
                    baseline_heart_rate = int(baseline_heart_rate)

                    current_field = "baseline_skin_response"
                    baseline_skin_response = float(
                        baseline_skin_response
                    )

                    current_field = "baseline_temperature"
                    baseline_temperature = float(
                        baseline_temperature
                    )

                except ValueError:
                    add_rejected_record(
                        rejected_records,
                        file_path,
                        row_number,
                        current_field,
                        "invalid type"
                    )
                    continue

                participant = Participant(
                    participant_id,
                    name,
                    baseline_heart_rate,
                    baseline_skin_response,
                    baseline_temperature
                )

                participants[participant_id] = participant

    except FileNotFoundError:
        print("File not found:", file_path)

    except PermissionError:
        print("Cannot access file:", file_path)

    except csv.Error:
        print("CSV error:", file_path)

    return participants, rejected_records


##
def load_sessions(file_path, participants):
    sessions = {}
    rejected_records = []

    try:
        with open(file_path, "r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):

                ## Check missing values
                try:
                    for column_name, value in row.items():
                        if column_name is not None:
                            if value is None or value.strip() == "":
                                raise InvalidRecordError("missing value")

                except InvalidRecordError as error:
                    add_rejected_record(
                        rejected_records,
                        file_path,
                        row_number,
                        column_name,
                        str(error)
                    )
                    continue

                ## Read IDs
                try:
                    current_field = "session_id"
                    session_id = row[current_field]

                    current_field = "participant_id"
                    participant_id = row[current_field]

                except KeyError:
                    add_rejected_record(
                        rejected_records,
                        file_path,
                        row_number,
                        current_field,
                        "missing field"
                    )
                    continue

                ## Validate IDs
                try:
                    current_field = "session_id"
                    validate_session_id(session_id)

                    current_field = "participant_id"
                    validate_participant_id(participant_id)

                except InvalidIdentifierError:
                    add_rejected_record(
                        rejected_records,
                        file_path,
                        row_number,
                        current_field,
                        "invalid ID"
                    )
                    continue

                ## Find participant
                try:
                    participant = participants[participant_id]

                except KeyError:
                    add_rejected_record(
                        rejected_records,
                        file_path,
                        row_number,
                        "participant_id",
                        "unknown participant"
                    )
                    continue

                ## Create session
                if session_id not in sessions:
                    sessions[session_id] = FitnessSession(
                        session_id,
                        participant
                    )

                # Convert measurements
                try:
                    current_field = "timestamp"
                    timestamp = int(row[current_field])

                    current_field = "heart_rate"
                    heart_rate = int(row[current_field])

                    current_field = "skin_response"
                    skin_response = float(row[current_field])

                    current_field = "temperature"
                    temperature = float(row[current_field])

                    current_field = "activity_level"
                    activity_level = float(row[current_field])

                    current_field = "signal_quality"
                    signal_quality = float(row[current_field])

                except KeyError:
                    add_rejected_record(
                        rejected_records,
                        file_path,
                        row_number,
                        current_field,
                        "missing field"
                    )
                    continue

                except ValueError:
                    add_rejected_record(
                        rejected_records,
                        file_path,
                        row_number,
                        current_field,
                        "invalid type"
                    )
                    continue

                observation = Observation(
                    timestamp,
                    heart_rate,
                    skin_response,
                    temperature,
                    activity_level,
                    signal_quality
                )

                ## Validate measurements
                current_field, reason = validate_observation(observation)

                if reason is not None:
                    add_rejected_record(
                        rejected_records,
                        file_path,
                        row_number,
                        current_field,
                        reason
                    )
                    continue

                sessions[session_id].add_observation(observation)

    except FileNotFoundError:
        print("File not found:", file_path)

    except PermissionError:
        print("Cannot access file:", file_path)

    except csv.Error:
        print("CSV error:", file_path)

    return sessions, rejected_records