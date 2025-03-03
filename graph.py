import matplotlib.pyplot as plt
import json


class DataGraph():
    def __init__(self, attempts_tracker):
        self.attempts_tracker = attempts_tracker

    def save_attempts(self):
        with open("attempts.json", "w") as f:
            json.dump(self.attempts_tracker, f)

    def plot_attempts(self):
        levels = list(self.attempts_tracker.keys())
        attempts = list(self.attempts_tracker.values())
        plt.figure(figsize=(8, 5))
        plt.bar(levels, attempts, color='blue')
        plt.xlabel("Levels")
        plt.ylabel("Number of Attempts")
        plt.title("User Attempts Per Level")

        plt.xticks(range(1, len(levels) + 1))
        plt.yticks(range(min(attempts), max(attempts) + 1))

        plt.savefig("attempts_plot.png")
<<<<<<< HEAD
        plt.show()
=======
        plt.show()
>>>>>>> UI_feature
