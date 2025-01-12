from datetime import datetime, timedelta
from collections import deque

import matplotlib.pyplot as plt #for the plot
plt.style.use('default') #for the plot
import numpy as np #for the plot
import pandas as pd #for the plot

# Simulation Class
class Simulation:
    def __init__(self, start_date, delta_t_days, initial_population_male, initial_population_female,scaling_factor):
        # Initial settings
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.delta_t = timedelta(days=delta_t_days)
        self.current_date = self.start_date
        self.pregnancy_latency = timedelta(days=270)  # Hardcoded latency for pregnancy (e.g., 9 months)
        self.population_male = initial_population_male
        self.population_female = initial_population_female
        self.dates = []
        self.total_population = []
        self.male_population = []
        self.female_population = []
        self.birth_female = []
        self.birth_male = []
        self.death_female =[]
        self.death_male=[]

        # Reference date (1.1.2011)
        self.reference_date = datetime.strptime("2024-01-01", "%Y-%m-%d")
        
      
    
    
        # Define rate functions with adjusted start time
        self.birth_rate_male = lambda t: (45905/365 + (366.1090909/365/365) * t ) * scaling_factor
        self.birth_rate_female = lambda t: (43814/365 + (417.4/365/365) * t ) * scaling_factor
        self.death_rate_male = lambda t: (46478/365 + (811.2545455/365/365) * t ) * scaling_factor
        self.death_rate_female = lambda t: (46840/365 + (506.51818181/365/365) * t ) * scaling_factor
        self.emigration_rate_male = lambda t: (46545/365 + (627.3/365/365) * t) * scaling_factor
        self.emigration_rate_female = lambda t: (45849/365 + (377.1363636/365/365) * t) * scaling_factor
        self.immigration_rate_male = lambda t: (88009/365 - (46.52727273/365/365) * t) * scaling_factor
        self.immigration_rate_female = lambda t: (68297/365 + (2.418181818/365/365) * t) * scaling_factor

        # Schwangerschafts-Latenzzeit
        self.pregnancy_queue_female = deque()  # Pregnancy queue for females 
        self.pregnancy_queue_male = deque()  # Pregnancy queue for males 
    
    def calculate_event(self, rate_function, population):
        """Berechnet die Veränderung für ein Event basierend auf der Rate und der Population."""
        days_since_reference = (self.current_date - self.reference_date).days
        rate = rate_function(days_since_reference)
        return int(rate)

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
        self.death_male.append(change_population_male)

    def event_death_female(self):
        change_population_female = self.calculate_event(self.death_rate_female, self.population_female)
        self.population_female -= change_population_female
        self.death_female.append(change_population_female)

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

    def initialize_pregnancies(self):
        self.mdate = self.current_date
        self.current_date -= self.pregnancy_latency
        while(self.current_date <= self.mdate):
            pregnancies_female = int(self.calculate_event(self.birth_rate_female, self.population_female))
            self.pregnancy_queue_female.append((self.current_date, pregnancies_female))
            pregnancies_male = int(self.calculate_event(self.birth_rate_male, self.population_male))
            self.pregnancy_queue_male.append((self.current_date, pregnancies_male))
            self.current_date += timedelta(days=1)

    def run_cycle(self):
        """Simuliert einen Zyklus."""
        self.event_emigration_male()
        self.event_emigration_female()
        self.event_immigration_male()
        self.event_immigration_female()
        self.event_death_male()
        self.event_death_female()
        self.event_pregnancy()
        if self.population_male < 0:
            self.population_male = 0
        if self.population_female < 0:
            self.population_female = 0    

        # Zeit und Schritte aktualisieren
        self.current_date += self.delta_t
        print(f"Population total: {self.population_male + self.population_female} on {self.current_date}")

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

    def plot(self):        
        
        plt.figure(figsize=(10, 6))
        plt.plot(self.dates, self.total_population, label="Total Population", marker="o",linewidth=0.5)
        #plt.plot(self.dates, self.male_population, label="Male Population", marker="o")
        #plt.plot(self.dates, self.female_population, label="Female Population", marker="o")
        #plt.plot(self.dates, self.birth_female, label="Birth  Female", marker="o")
        #plt.plot(self.dates, self.birth_male, label="Birth Male", marker="o")
        #plt.plot(self.dates, self.death_female, label="Death  Female", marker="o")
        #plt.plot(self.dates, self.death_male, label="Death Male", marker="o")
        
        # Add labels, title, and legend
        plt.title("Population Growth Over Time", fontsize=16)
        plt.xlabel("days", fontsize=12)
        plt.ylabel("Population ", fontsize=12)
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)

        # Show the plot
        plt.show()


        
