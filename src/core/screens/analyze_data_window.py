"""popout window to analyze session data"""
import tkinter as tk
import matplotlib.pyplot as plt

class AnalyzeDataWindow:
    def __init__(self, data):
        self.data = data
        self.root = tk.Tk()
        self.root.title("Analyze Data")
        self.root.geometry("800x600")

    def show_plot(self):
        fig, ax = plt.subplots()
        ax.plot(self.data)
        plt.show()
