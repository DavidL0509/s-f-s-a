import csv
import re

from pathlib import Path

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
    reason,
    session_id=None
):
    rejected_records.append({
        "file": str(file_path),
        "row": row_number,
        "field": field,
        "reason": reason,
        "session_id": session_id
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

                rejected_session_id = row.get("session_id")

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
                        str(error),
                        rejected_session_id
                    )
                    continue

                ## Read ID
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
                        "missing field",
                        rejected_session_id
                    )
                    continue

                ## Validate ID
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
                        "invalid ID",
                        rejected_session_id
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
                        "unknown participant",
                        rejected_session_id
                    )
                    continue

                ## Create session
                if session_id not in sessions:
                    sessions[session_id] = FitnessSession(
                        session_id,
                        participant
                    )

                ## Convert measurements
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
                        "missing field",
                        rejected_session_id
                    )
                    continue

                except ValueError:
                    add_rejected_record(
                        rejected_records,
                        file_path,
                        row_number,
                        current_field,
                        "invalid type",
                        rejected_session_id
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
                        reason,
                        rejected_session_id
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

##
def write_output(results, rejected_records):
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    ## Analysis summary CSV
    with open(
        output_dir / "analysis_summary.csv",
        "w",
        encoding="utf-8",
        newline=""
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "session_id",
            "participant_id",
            "usable_observations",
            "classification",
            "reason"
        ])

        for result in results:
            writer.writerow([
                result["session_id"],
                result["participant_id"],
                result["usable_observations"],
                result["classification"],
                result["reason"]
            ])

    ## Analysis report
    with open(
        output_dir / "analysis_report.txt",
        "w",
        encoding="utf-8"
    ) as file:

        for result in results:
            rejected_count = 0

            for record in rejected_records:
                if record["session_id"] == result["session_id"]:
                    rejected_count += 1

            file.write(
                "Session: "
                + result["session_id"]
                + "\n"
            )

            file.write(
                "Participant: "
                + result["participant_id"]
                + " - "
                + result["participant_name"]
                + "\n"
            )

            file.write(
                "Usable observations: "
                + str(result["usable_observations"])
                + "\n"
            )

            file.write(
                "Rejected observations: "
                + str(rejected_count)
                + "\n"
            )

            file.write(
                "Classification: "
                + result["classification"]
                + "\n"
            )

            file.write(
                "Reason: "
                + result["reason"]
                + "\n"
            )

            if result["summaries"] is not None:
                summaries = result["summaries"]
                comparison = result["baseline_comparison"]

                file.write(
                    "Heart rate average/min/max: "
                    + str(round(
                        summaries["heart_rate"]["average"], 2
                    ))
                    + " / "
                    + str(summaries["heart_rate"]["minimum"])
                    + " / "
                    + str(summaries["heart_rate"]["maximum"])
                    + "\n"
                )

                file.write(
                    "Skin response average/min/max: "
                    + str(round(
                        summaries["skin_response"]["average"], 2
                    ))
                    + " / "
                    + str(summaries["skin_response"]["minimum"])
                    + " / "
                    + str(summaries["skin_response"]["maximum"])
                    + "\n"
                )

                file.write(
                    "Temperature average/min/max: "
                    + str(round(
                        summaries["temperature"]["average"], 2
                    ))
                    + " / "
                    + str(summaries["temperature"]["minimum"])
                    + " / "
                    + str(summaries["temperature"]["maximum"])
                    + "\n"
                )

                file.write(
                    "Activity average/min/max: "
                    + str(round(
                        summaries["activity_level"]["average"], 2
                    ))
                    + " / "
                    + str(summaries["activity_level"]["minimum"])
                    + " / "
                    + str(summaries["activity_level"]["maximum"])
                    + "\n"
                )

                file.write(
                    "Differences from baseline (heart/skin/temp): "
                    + str(round(
                        comparison["heart_rate"], 2
                    ))
                    + " / "
                    + str(round(
                        comparison["skin_response"], 2
                    ))
                    + " / "
                    + str(round(
                        comparison["temperature"], 2
                    ))
                    + "\n"
                )

            file.write("\n")

    ## Rejected records
    with open(
        output_dir / "rejected_records.txt",
        "w",
        encoding="utf-8"
    ) as file:

        for record in rejected_records:
            file.write(
                record["file"]
                + " ; row "
                + str(record["row"])
                + " ; "
                + str(record["field"])
                + " ; "
                + record["reason"]
                + "\n"
            )
