from src.simulation import Simulation
scaling = 1

sim = Simulation(
    start_date="2024-01-01",
    delta_t_days=1,  # Zeitschritt: 1 Tage
    initial_population_male=int(4514832*scaling),
    initial_population_female=int(4643918*scaling),
    scaling_factor = scaling
)



sim.simulate(total_days=2192)  # Simulation für 1 Jahr

sim.plot()