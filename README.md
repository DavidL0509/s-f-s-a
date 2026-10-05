# Option A, Smart Fitness Session Analyzer

**David Lebedovskyi**

## Description

This program is an extended version of Assignment I. It analyzes simulated fitness data stored in CSV files.

The program loads participant profiles and fitness-session measurements, validates the input data, groups observations by session ID, connects each session to an existing participant, analyzes usable observations, and saves the results to output files.

The program also reads the intentionally invalid session file. Invalid rows are rejected without stopping the whole program, and the source file, row number, field and rejection reason are recorded.

## Project Structure

- `main.py` - starts the program, loads the official input files, analyzes the sessions, combines rejected records, creates the output files and prints the completion summary.
- `fitness_app/__init__.py` - marks `fitness_app` as the application package.
- `fitness_app/models.py` - contains the `Participant`, `Observation` and `FitnessSession` classes.
- `fitness_app/file_handling.py` - reads CSV files, validates identifiers and records, handles file and data errors, stores rejected records and writes the output files.
- `fitness_app/analysis.py` - calculates session summaries, compares values with participant baselines, detects recovery and classifies sessions.
- `data/participants.csv` - official participant profile file.
- `data/fitness_sessions.csv` - official valid fitness-session file.
- `data/fitness_sessions_invalid.csv` - official intentionally invalid fitness-session file.
- `output/analysis_summary.csv` - one summary row for each processed session.
- `output/analysis_report.txt` - readable detailed analysis report.
- `output/rejected_records.txt` - rejected rows with file, row, field and reason.
- `Assignment_1/` - files from the previous assignment kept for reference.

## Classes

### Participant

The `Participant` class stores information about one participant.

It stores:

- participant ID
- name
- baseline heart rate
- baseline skin response
- baseline temperature

### Observation

The `Observation` class represents one wearable-device observation.

It stores:

- timestamp
- heart rate
- skin response
- temperature
- activity level
- signal quality

### FitnessSession

The `FitnessSession` class represents one fitness session.

It stores:

- session ID
- the related `Participant` object
- usable `Observation` objects

A session can contain multiple observations with the same session ID.

## Composition and Encapsulation

### Composition

Composition is demonstrated in the `FitnessSession` class.

A `FitnessSession` contains a `Participant` object and multiple `Observation` objects.

### Encapsulation

Encapsulation is demonstrated using the protected-style attribute:

- `_observations`

The observations are accessed through the `observations` property, which returns a copy of the list.

## Regular Expression Validation

Two identifiers are validated using `re.fullmatch()`.

Participant ID:

`P\d{3}`

A valid example is:

`P001`

Fitness session ID:

`FIT-\d{4}-\d{3}`

A valid example is:

`FIT-2026-001`

Malformed identifiers are rejected before the row is used for analysis.

## Custom Exceptions and Error Handling

The program defines two custom exception classes:

### InvalidIdentifierError

Raised when a participant ID or session ID does not match the required format.

### InvalidRecordError

Raised when a CSV record contains a missing value and cannot be accepted.

The program also handles relevant built-in and CSV errors, including:

- `FileNotFoundError`
- `PermissionError`
- `ValueError`
- `KeyError`
- `csv.Error`

The program continues to the next row when a recoverable record error is found.

## Validation Rules and Assumptions

Each session observation is checked before it is added to a `FitnessSession`.

An observation is rejected if:

- timestamp is negative
- heart rate is outside 35-205
- skin response is negative
- temperature is outside 25-42
- activity level is outside 0-1
- signal quality is outside 0-1
- signal quality is below 0.80
- a required value is missing
- a value cannot be converted to the required numeric type
- the participant ID is unknown
- the participant ID or session ID has an invalid format

Signal quality below `0.80` is treated as poor-quality data and the observation is not used in the session analysis.

For every rejected row, the program records:

- source file
- row number
- field
- reason

## Summary Calculations

For sessions with enough usable observations, the program calculates:

- average
- minimum
- maximum

These values are calculated for:

- heart rate
- skin response
- temperature
- activity level

The average heart rate, skin response and temperature are also compared with the participant baseline values.

## Classification Rules and Assumptions

The program can classify a session as:

- `resting`
- `moderate activity`
- `high activity`
- `recovering`
- `insufficient data`

If fewer than 6 usable observations are available, the session is classified as `insufficient data`.

Recovery is checked before the normal activity classification.

Recovery is detected when heart rate and activity level both decrease by at least 30 percent from their highest values in the session to the final usable observation.

If recovery is not detected, average activity level is used:

- average activity <= 0.33: `resting`
- average activity > 0.33 and <= 0.66: `moderate activity`
- average activity > 0.66: `high activity`

## Output Files

The program creates the `output` directory automatically if it does not exist.

It writes three files:

### analysis_summary.csv

Contains one row for each processed session with:

- session ID
- participant ID
- number of usable observations
- classification
- reason

### analysis_report.txt

Contains a readable report for each processed session, including participant information, usable and rejected observation counts, classification, reason, summary values and differences from baseline when enough usable data are available.

### rejected_records.txt

Contains each rejected row with:

- source file
- row number
- field
- rejection reason

The output files are opened in write mode, so running the program again replaces the previous report content and produces predictable output.

## Installation

The program uses only the Python standard library. No external packages are required.

Python 3 is required.

## Running the Program

Open a terminal in the repository root and run:

`python main.py`

If the operating system uses `python3`, run:

`python3 main.py`

The program expects the CSV files to remain inside the `data` directory with their original names.

## Example Output

Processed sessions: 7
Accepted observations: 25
Rejected records: 15
Created files:
output/analysis_summary.csv
output/analysis_report.txt
output/rejected_records.txt

Example session result from `analysis_report.txt`:

Session: FIT-2026-001
Participant: P001 - Amina Noor
Usable observations: 6
Rejected observations: 0
Classification: resting
Reason: Average activity level is <= 0.33.
Heart rate average/min/max: 68.83 / 68 / 70
Skin response average/min/max: 1.19 / 1.17 / 1.22
Temperature average/min/max: 32.43 / 32.4 / 32.5
Activity average/min/max: 0.09 / 0.07 / 0.12
Differences from baseline (heart/skin/temp): 0.83 / -0.01 / 0.03

## Known Limitations

The activity classification is intentionally simple. The `resting`, `moderate activity` and `high activity` classifications are based only on average activity level. Heart rate, skin response and temperature are not used to choose between those three activity classifications.

Recovery is detected by comparing the highest heart rate and highest activity level in the usable observations with the final usable observation. The program does not check whether the values decrease continuously throughout the recovery period.

Sessions with fewer than 6 usable observations are classified as `insufficient data`, even if some usable observations are available.

Unexpected extra CSV values beyond the expected columns are not separately rejected as an unexpected row-length error.
