# Employee Shift Scheduler

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![OR-Tools](https://img.shields.io/badge/OR--Tools-9.12.4544-green.svg)](https://developers.google.com/optimization)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/downloads/)

## Project Overview

Employee Shift Scheduler is an advanced shift scheduling system built with Google's OR-Tools constraint programming library. The system optimizes weekly employee schedules based on availability preferences, shift requirements, and various workplace constraints.

## Features

- **Optimal Schedule Generation**: Creates optimized weekly employee schedules
- **Constraint-Based Modeling**: Handles complex scheduling constraints
- **Multiple Shift Types**: Supports morning and afternoon shift assignments
- **Employee Preferences**: Accounts for shift type preferences
- **Working Hours Limits**: Respects maximum weekly working hour constraints
- **Consecutive Days Limitation**: Prevents excessive consecutive workdays
- **Coverage Requirements**: Ensures minimum staff coverage for each shift
- **Solution Visualization**: Detailed output of generated schedules
- **Multiple Solutions**: Generates and compares alternative schedules
- **Scheduling Diagnosis**: Analyzes schedules and suggests improvements for under-utilized employees or coverage gaps

## Problem Description

The scheduler solves the following problem:

- Schedule employees across 7 days of the week
- Two shift types: morning (8 hours) and afternoon (6.5 hours)
- Each employee has:
  - Maximum weekly working hours
  - Availability for specific days and shifts
  - Shift type preferences

The system aims to:
1. Satisfy all hard constraints (availability, maximum hours, etc.)
2. Minimize coverage shortages
3. Maximize employee preference satisfaction
4. Distribute work hours fairly among employees

## How It Works

The system uses constraint programming (CP) to model the scheduling problem:

1. **Variables**: Binary variables representing whether an employee works a shift on a specific day
2. **Hard Constraints**:
   - Employees can work at most one shift per day
   - Employees only work shifts they're available for
   - Employees work at most 5 days per week
   - Employees don't exceed their maximum weekly hours
   - Employees don't work more than a set number of consecutive days
3. **Soft Constraints**:
   - Cover all required shifts (with shortage variables to handle infeasibility)
   - Maximize fulfillment of shift preferences
   - Balance workload across employees


## Diagnostic Features

The system not only generates the schedules but also provides detailed diagnostics to help improve the shift allocation:

**Employee Under-Utilization Detection**
 - Identifies when employees work significantly fewer hours than their availability permits.
Example:
```
Godziny pracy:
Ola pracuje 21.0h/40h | 52.5% dyspozycji | [za mało godzin]
```

Example:
```
Dzień 1
Marek pracuje na zmianie 1
Kasia pracuje na zmianie 1
[KRYTYCZNY] Braki pracowników na dzień 1 na zmianę 0
Dostępni, nieprzypisani: ['Ola']
Poproś o przyjęcie zmiany: ['Ola', 'Kasia 2', 'Jan', 'Zosia', 'Grzegorz', 'Ania', 'Krzysiek']
```
 - Proposes distribution of shifts in case of shortages in the disposition for a given day.

Example:
```
Dzień 2
Ola pracuje na zmianie 1
Marek pracuje na zmianie 0
Krzysiek pracuje na zmianie 0
[KRYTYCZNY] Braki pracowników na dzień 2 na zmianę 1
Dostępni, nieprzypisani: []
Poproś o przyjęcie zmiany: ['Kasia', 'Kasia 2', 'Jan', 'Zosia', 'Grzegorz', 'Ania']
```

### Input Data

The system uses predefined employee data structures:

```python
# Create employee objects with their constraints and preferences
employees = [
    Employees(
        "Ola",
        [0, 1],  # Preferred shifts (0=morning, 1=afternoon)
        {
            0: [0, 1],  # Day 0 (Monday): available for both shifts
            1: [0, 1],  # Day 1 (Tuesday): available for both shifts
            # ... and so on
        },
        [],  # Special shift requests (not implemented)
        40   # Maximum weekly hours
    ),
    # More employees...
]
```

### Output

The system generates detailed schedule solutions showing:

- Which employee works which shift on each day
- Any coverage shortages and available employees to fill them
- Total working hours and utilization percentage for each employee
- Summary of constraint violations


## Implementation Details

### Key Components

1. **Employees Class**: Stores employee data including availability and preferences
2. **Constraint Model Builder**: Constructs the CP model with variables and constraints
3. **Solution Printer**: Processes and displays the optimized schedules
4. **Diagnostic Tools**: Analyzes scheduling feasibility before solving

### Algorithm Flow

1. **Initialization**: Define employees, shifts, and coverage requirements
2. **Diagnosis**: Check if the problem is feasible based on available hours
3. **Model Building**: Create the constraint model and add constraints
4. **Optimization**: Solve the model to find optimal or near-optimal solutions
5. **Solution Processing**: Sort and display the best solutions found

## Project Structure

```
employee-shift-scheduler/
├── scheduling_script.py         # Main scheduling algorithm
├── test_scheduling.py/               # Test cases
└── README.md            # Project documentation
```

## Example Output

```
Dzień 1
Ola pracuje na zmianie 0
Marek pracuje na zmianie 1
Grzegorz pracuje na zmianie 1

Dzień 2
Ola pracuje na zmianie 0
Marek pracuje na zmianie 0
Kasia pracuje na zmianie 1
Krzysiek pracuje na zmianie 1

...

Godziny pracy:
Ola pracuje 32.0h/40h | 80.0% dyspozycji
Marek pracuje 24.0h/30h | 80.0% dyspozycji
Kasia pracuje 16.0h/20h | 80.0% dyspozycji
...
```

## Future Improvements

- Web-based user interface for easier data input and visualization
- Support for more complex shift types and break patterns
- Import/export functionality for employee data
- Rolling horizon planning for continuous scheduling
- Historical data analysis for better preference learning

## Requirements

- Python 3.6+
- Google OR-Tools 9.12.4544
- datetime (standard library)
- collections (standard library)

## Installation

```bash
# Clone the repository
git clone https://github.com/darkchiii/employee-shift-scheduler.git
cd employee-shift-scheduler

# Install required packages
pip install ortools==9.12.4544
```

## Usage

```bash
# Run the scheduler with default settings
python scheduling_script.py
```

