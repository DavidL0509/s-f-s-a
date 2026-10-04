# Option A, Smart Fitness Session Analyzer

**student**

## Description

This program analyzes simulated fitness data from wearable devices.
It creates a participant and a fitness session, validates observations, calculates summary values, compares measurements with participant baseline values, detects recovery, and classifies the session.

## Project Files
- `main.py` - starts the program, generates the selected fitness scenario, analyzes the session and prints the final report. The scenario is selected manually in this file by changing the `scenario=` value.
- `program.py` - contains the classes, validation, calculations, analysis and report.
- `data_generator.py` - supplied data generator. This file was not modified.
- `example_usage.py` - supplied example of how to use the generator. 
- `test_main01.py` - development test file used to check the basic object-oriented structure. It creates the `Participant`, `Observation` and `FitnessSession` classes and uses the `moderate_activity` scenario. 
- `test_main02.py` - development test file used to check observation validation. It uses the `poor_quality` scenario and shows usable and rejected observations together with rejection reasons. 
- `test_main03.py` - development test file used to check summary calculations and comparison with participant baseline values. It uses the `recovery` scenario and calculates average, minimum and maximum values.



## Project Files

- `main.py` - starts the program.
- `program.py` - contains the classes, validation, calculations, analysis and report.
- `data_generator.py` - supplied data generator.
- `example_usage.py` - supplied example of how to use the generator.

## Classes

### Participant

`Participant` class stores information about one participant.

It stores:

- participant ID
- baseline heart rate
- baseline skin response
- baseline temperature

The class also uses the `from_dict()` class method to create a `Participant` object from the participant dictionary returned by the supplied data generator.

### Observation

`Observation` class represents one observation from the wearable device.

It stores:

- timestamp
- heart rate
- skin response
- temperature
- activity level
- signal quality

The class also uses the `from_dict()` class method to create an `Observation` object from an observation dictionary returned by the supplied data generator.

### FitnessSession

`FitnessSession` class represents one fitness session.

It stores the participant, usable observations and rejected observations.

## Composition, Encapsulation, Inheritance and Overriding

### Composition

Composition is demonstrated in the `FitnessSession` class.

A `FitnessSession` contains a `Participant` object and multiple `Observation` objects.

### Encapsulation

Encapsulation is demonstrated using the protected-style attributes:

- _observations
- _rejected_observations

### Inheritance and Overriding

Inheritance and method overriding are not used in this project.

Composition is more suitable because a fitness session contains a participant and observations.

## Validation

Each observation is checked before it is used.

An observation is rejected if:

- timestamp is missing or negative
- heart rate is missing or outside 35-205
- skin response is missing or negative
- temperature is missing or outside 25-42
- activity level is missing or outside 0-1
- signal quality is missing, below 0.80 or above 1

## Summary Calculations

For usable observations, the program calculates:

- average
- minimum
- maximum

These values are calculated for heart rate, skin response, temperature and activity level.

The average heart rate, skin response and temperature are also compared with the participant baseline values.

## Classification Rules and Assumptions

The program can classify a session as:

- resting
- moderate activity
- high activity
- recovering
- insufficient data

If fewer than 6 usable observations are available, the session is classified as `insufficient data`.

Recovery is checked before the normal activity classification.

Recovery is detected when heart rate and activity level both decrease by at least 30% between the first and last usable observations.

If recovery is not detected, average activity level is used:

- average activity <= 0.33: `resting`
- average activity > 0.33 and <= 0.66: `moderate activity`
- average activity > 0.66: `high activity`

## Running the Program

Download and extract the ZIP file.

Open a terminal in the project folder and run:

- python3 main.py

If the operating system uses `python` instead of `python3`, run:

- python main.py

To run another scenario, only the value after `scenario=` needs to be changed manually. 
Available scenarios are:
- `scenario="resting"` - resting session
- `scenario="moderate_activity"` - moderate activity
- `scenario="high_activity"` - high activity
- `scenario="recovery"` - activity followed by recovery
- `scenario="poor_quality"` - poor-quality or invalid sensor data

## Example Output

Session Report
Participant ID: P001
Total observations: 10
Usable observations: 10
Rejected observations: 0

Heart rate:
Baseline: 78
Average: 136.8
Difference from baseline: 58.8
Minimum: 123
Maximum: 150

Skin response:
Baseline: 1.17
Average: 1.83
Difference from baseline: 0.66
Minimum: 1.3
Maximum: 2.1

Temperature:
Baseline: 32.76
Average: 33.33
Difference from baseline: 0.57
Minimum: 33.17
Maximum: 33.43

Activity level:
Average: 0.81
Minimum: 0.69
Maximum: 0.91

Classification: high activity
Reason: Average activity level is > 0.66.

## Known Limitations

The activity classification is very simple.
The `resting`, `moderate activity` and `high activity` classifications are based only on the average activity level. Heart rate, skin response and temperature are not used to decide between these three classifications.

Recovery is detected only by comparing the first and last usable observations. The program does not check if heart rate and activity decrease continuously during the session.