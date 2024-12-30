from datetime import datetime, timedelta
from collections import deque

import matplotlib.pyplot as plt #for the plot
import numpy as np #for the plot
import pandas as pd #for the plot

# Simulation Class
class Simulation:
    def __init__(self, start_date, delta_t_days, initial_population_male, initial_population_female):
        # Initial settings
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.delta_t = timedelta(days=delta_t_days)
        self.current_date = self.start_date
        self.pregnancy_latency = timedelta(days=270)  # Hardcoded latency for pregnancy (e.g., 9 months)
        self.population_male = initial_population_male
        self.population_female = initial_population_female
        self.dates = []  # To store dates for plotting
        self.total_population = []  # To store total population for plotting
        self.male_population = []  # To store male population for plotting
        self.female_population = []  # To store female population for plotting
        self.birth_female = []
        self.birth_male = []

        # Reference date (1.1.2011)
        self.reference_date = datetime.strptime("2023-01-01", "%Y-%m-%d")
        
        # Define rate functions with adjusted start time
        self.birth_rate_male = lambda t: 0.01 + 0.0001 * t 
        self.birth_rate_female = lambda t: 0.02 + 0.0001 * t
        self.death_rate_male = lambda t:0# 0.001 + 0.00005 * t
        self.death_rate_female = lambda t:0# 0.001 + 0.00004 * t
        self.emigration_rate_male = lambda t:0# 0.001 + 0.00001 * t
        self.emigration_rate_female = lambda t:0# 0.0012 + 0.00001 * t
        self.immigration_rate_male = lambda t:0# 0.0020 + 0.00002 * t
        self.immigration_rate_female = lambda t:0# 0.0021 + 0.00002 * t

        # Schwangerschafts-Latenzzeit
        self.pregnancy_queue_female = deque()  # Pregnancy queue for females 
        self.pregnancy_queue_male = deque()  # Pregnancy queue for males 
    
    def calculate_event(self, rate_function, population):
        """Berechnet die Veränderung für ein Event basierend auf der Rate und der Population."""
        days_since_reference = (self.current_date - self.reference_date).days
        rate = rate_function(days_since_reference)
        change = int(rate * population)
        return change

    def event_emigration_male(self):
        change_population_male = self.calculate_event(self.emigration_rate_male, self.population_male)
        self.population_male -= change_population_male

    def event_emigration_female(self):
        change_population_female = self.calculate_event(self.emigration_rate_female, self.population_female)
        self.population_female -= change_population_female

    def event_immigration_male(self):
        change_population_male = self.calculate_event(self.immigration_rate_male, self.population_male)
        self.population_male += change_population_male

    def event_immigration_female(self):
        change_population_female = self.calculate_event(self.immigration_rate_female, self.population_female)
        self.population_female += change_population_female

    def event_birth_male(self):
        change_population_male = self.calculate_event(self.birth_rate_male, self.population_female)
        self.population_male += change_population_male

    def event_birth_female(self):
        change_population_female = self.calculate_event(self.birth_rate_female, self.population_female)
        self.population_female += change_population_female

    def event_death_male(self):
        change_population_male = self.calculate_event(self.death_rate_male, self.population_male)
        self.population_male -= change_population_male

    def event_death_female(self):
        change_population_female = self.calculate_event(self.death_rate_female, self.population_female)
        self.population_female -= change_population_female

    def event_pregnancy(self):
        """Handles pregnancies and births for both males and females with a latency period."""
        # Process births for females
        births_due_female = 0
        if self.pregnancy_queue_female and self.pregnancy_queue_female[0][0] <= self.current_date:
            _, births_due_female = self.pregnancy_queue_female.popleft()
        if self.population_female > 0:
            self.population_female += int(births_due_female)

        # Process births for males
        births_due_male = 0
        if self.pregnancy_queue_male and self.pregnancy_queue_male[0][0] <= self.current_date:
            _, births_due_male = self.pregnancy_queue_male.popleft()
        if self.population_female > 0:
            self.population_male += int(births_due_male)

        # Handle new pregnancies for females and males babies
        new_pregnancies_female = int(self.calculate_event(self.birth_rate_female, self.population_female))
        self.pregnancy_queue_female.append((self.current_date + self.pregnancy_latency, new_pregnancies_female))

        new_pregnancies_male = int(self.calculate_event(self.birth_rate_male, self.population_male))
        self.pregnancy_queue_male.append((self.current_date + self.pregnancy_latency, new_pregnancies_male))

        self.birth_male.append(new_pregnancies_male)
        self.birth_female.append(new_pregnancies_female)

        print(f"Initialized female pregnancy due on {self.current_date} with {new_pregnancies_female} births, Population {self.population_female}")

    def initialize_pregnancies(self):
        self.mdate = self.current_date
        self.current_date -= self.pregnancy_latency
        while(self.current_date <= self.mdate):
            pregnancies_female = int(self.calculate_event(self.birth_rate_female, self.population_female))
            self.pregnancy_queue_female.append((self.current_date, pregnancies_female))
            print(f"Initialized female pregnancy due on {self.current_date} with {pregnancies_female} births, Population {self.population_female}")
            pregnancies_male = int(self.calculate_event(self.birth_rate_male, self.population_male))
            self.pregnancy_queue_male.append((self.current_date, pregnancies_male))
            self.current_date += timedelta(days=1)

    def run_cycle(self):
        """Simuliert einen Zyklus."""
        self.event_emigration_male()
        self.event_emigration_female()
        self.event_immigration_male()
        self.event_immigration_female()
        if self.population_male < 0:
            self.population_male = 0
        if self.population_female < 0:
            self.population_female = 0    
        if self.population_male > 0:
            self.event_death_male()
        if self.population_female > 0:
            self.event_death_female()
        self.event_pregnancy()

        # Zeit und Schritte aktualisieren
        self.current_date += self.delta_t

    def simulate(self, total_days):
        """Führt die Simulation über eine bestimmte Zeitspanne aus."""
        end_date = self.current_date + timedelta(days=total_days)
        self.initialize_pregnancies()
        while self.current_date < end_date:
            self.run_cycle()
            self.dates.append(self.current_date)
            self.total_population.append(self.population_male + self.population_female)
            self.male_population.append(self.population_male)
            self.female_population.append(self.population_female)
            #print(f"Date: {self.current_date.date()}, Males: {self.population_male}, Females: {self.population_female}")

    def plot(self):        
        plt.figure(figsize=(10, 6))
        plt.plot(self.dates, self.total_population, label="Total Population", marker="o")
        plt.plot(self.dates, self.male_population, label="Male Population", marker="o")
        plt.plot(self.dates, self.female_population, label="Female Population", marker="o")
        plt.plot(self.dates, self.birth_female, label="Birth  Female", marker="o")
        plt.plot(self.dates, self.birth_male, label="Birth Male", marker="o")
        # Add labels, title, and legend

        plt.title("Population Growth Over Time", fontsize=16)
        plt.xlabel("days", fontsize=12)
        plt.ylabel("Population ", fontsize=12)
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)

        # Show the plot
        plt.show()


        
