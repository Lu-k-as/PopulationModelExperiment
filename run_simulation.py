from src.simulation import Simulation

sim = Simulation(
    start_date="2024-01-01",
    delta_t_days=1,  # Zeitschritt: 1 Tage
    initial_population_male=4514832,
    initial_population_female=4643918,
    total_days=70000
)

sim.simulate(total_days=70000)  # Simulation für 1 Jahr

sim.plot()