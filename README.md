# Discrete Event Simulation

This project implements a Discrete Event Simulation in Python to model population dynamics over time. The simulation tracks male and female populations while accounting for births, deaths, immigration, emigration, and pregnancy events.

## Features
- **Time-dependent rates**: Events (e.g., birth, death, emigration, imigration) are governed by rates that change linearly with time.
- **Configurable time steps**: The simulation supports flexible time steps (`delta_t`) in days.
- **Event independence**: Events are calculated independently in each cycle.
- **Population tracking**: Male and female populations are updated at each step based on event outcomes.

## Prerequisites
- Python 3.7 or higher
- Required libraries:
  - `datetime`
  - `collections`

## Setup

Clone the repository and ensure Python is installed.

```bash
# Clone the repository
git clone https://github.com/Lu-k-as/PopulationModelExperiment

# Navigate to the project directory
cd PopulationModelExperiment
```

## How to Run the Simulation
1. Create an instance of the `Simulation` class by providing the following:
   - Start date (in `YYYY-MM-DD` format)
   - Time step (`delta_t`) in days
   - Initial male and female population sizes

2. Call the `simulate` method with the total number of days to run the simulation.

### Example
```python
from simulation import Simulation

# Initialize the simulation
sim = Simulation(
    start_date="2024-01-01",
    delta_t_days=30,  # Time step: 30 days
    initial_population_male=500,
    initial_population_female=500
)

# Run the simulation for 1 year
sim.simulate(total_days=365)
```

### Output
The simulation will print the population counts after each cycle:
```
Date: 2024-01-31, Males: 505, Females: 510
Date: 2024-03-01, Males: 510, Females: 520
...
```

## Simulation Logic
1. **Initialization**:
   - The simulation sets initial populations and event rates, scaled by the time step (`delta_t`).
2. **Cyclic Events**:
   - Events such as emigration, immigration, births, and deaths are calculated independently using the population and time-dependent rates.
3. **Pregnancy Handling**:
   - Pregnancies are tracked with a queue, and births are added to the population after the latency period.

## Configuration Options
- `start_date`: Start date of the simulation (e.g., `"2024-01-01"`).
- `delta_t_days`: Length of each time step in days (e.g., `30` for monthly updates).
- `initial_population_male`: Initial number of males.
- `initial_population_female`: Initial number of females.