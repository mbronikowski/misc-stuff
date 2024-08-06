import random
import tkinter as tk
import numpy as np
from scipy import special
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg     # , NavigationToolbar2Tk
from matplotlib.figure import Figure


def no_of_dice_outcomes(dice_sum, n_dice, s_sides):
    upper_sum_end = (dice_sum - n_dice) // s_sides
    result = 0
    for k in range(upper_sum_end + 1):          # +1 because range returns ints from 0 to n-1.
        result += ((-1) ** k) * special.comb(n_dice, k) *\
                  special.comb(dice_sum - s_sides * k - 1, n_dice - 1)
    return result


class DiceModel:
    def __init__(self):
        self.no_of_dice = 0
        self.die_sides = 0
        self.theoretical_distribution = None
        self.simulated_distribution = None
        self.no_of_points = 0
        self.computing_delay = 0
        self.continue_computing = 1

    def _compute_theoretical(self):
        no_of_bins = (self.die_sides - 1) * self.no_of_dice + 1
        self.theoretical_distribution = np.empty(no_of_bins, dtype=np.double)
        for i in range(no_of_bins):
            self.theoretical_distribution[i] = no_of_dice_outcomes(i + self.no_of_dice, self.no_of_dice, self.die_sides)
        self.theoretical_distribution /= self.die_sides ** self.no_of_dice

    def set_model(self, no_of_dice, die_sides):
        if no_of_dice != self.no_of_dice or die_sides != self.die_sides:        # Avoid unnecessary recalculations
            self.no_of_dice = no_of_dice
            self.die_sides = die_sides
            self._compute_theoretical()
        self.simulated_distribution = np.zeros(self.theoretical_distribution.shape, dtype=int)
        self.no_of_points = 0

    def normalized_simulated_distribution(self):
        return self.simulated_distribution / np.sum(self.simulated_distribution)

    def set_delay(self, delay):
        self.computing_delay = delay

    def compute_distribution(self):
        sum_of_dice = 0
        for i in range(self.no_of_dice):
            sum_of_dice += random.randint(1, self.die_sides)
        self.simulated_distribution[sum_of_dice - self.no_of_dice] += 1
        self.no_of_points += 1
        if self.continue_computing:
            root.after(self.computing_delay, self.compute_distribution)


model = DiceModel()


class PlotHandler:
    def __init__(self):
        self.plotting_delay = 100
        self.continue_replotting = 1

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure_parent = None
        self.main_subfig = self.figure.add_subplot()

    def draw_figure(self):
        x_axis_bins = np.arange(model.no_of_dice, model.no_of_dice * model.die_sides + 1)
        theoretic_distr = model.theoretical_distribution
        sim_distr = model.normalized_simulated_distribution()

        self.main_subfig.clear()

        self.main_subfig.set_xlabel("Sum of dice")
        self.main_subfig.set_ylabel("Frequency of occurence")
        self.main_subfig.set_ylim(0, max((sim_distr.max(), 1.2 * theoretic_distr.max())))
        self.main_subfig.set_xlim(x_axis_bins[0] - 0.5, x_axis_bins[-1] + 0.5)

        sim_label = "Simulated distr.; " + str(model.no_of_points) + " die rolls"
        self.main_subfig.bar(x_axis_bins, theoretic_distr, label="Theoretical distribution")
        self.main_subfig.plot(x_axis_bins, sim_distr, "ro", label=sim_label)

        self.main_subfig.legend(loc="upper right")

        self.figure_parent.draw()

    def replotting_loop(self):
        if self.continue_replotting:
            self.draw_figure()
            root.after(self.plotting_delay, self.replotting_loop)


plot_handler = PlotHandler()


class ResultField(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        # matplotlib plot with results

        self.canvas = FigureCanvasTkAgg(plot_handler.figure, master=root)
        plot_handler.figure_parent = self.canvas
        self.canvas.get_tk_widget().pack(side="left", fill="both", expand=True)


class InputField(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.default_dice_number = 2
        self.default_die_sides = 6
        self.default_delay = 10                 # ms
        self.start_stop_button_state = 0       # 0 is in start position
        self.simulation_paused = 0
        self.entry_input_status = "enabled"

        # Number of dice

        self.dice_no_input_frame = tk.Frame(master=self)

        self.dice_no_label = tk.Label(master=self.dice_no_input_frame,
                                      text="No of dice:")
        self.dice_no_val = tk.IntVar(master=self)
        self.dice_no_entry = tk.Entry(master=self.dice_no_input_frame,
                                      width=5,
                                      textvariable=self.dice_no_val)
        self.dice_no_val.set(self.default_dice_number)

        self.dice_no_label.pack(side="left")
        self.dice_no_entry.pack(side="right")
        self.dice_no_input_frame.pack(side="top", fill="x")

        # Number of sides on a die

        self.die_side_input_frame = tk.Frame(master=self)

        self.die_side_label = tk.Label(master=self.die_side_input_frame,
                                       text="No of sides:")
        self.die_side_val = tk.IntVar(master=self)
        self.die_side_entry = tk.Entry(master=self.die_side_input_frame,
                                       width=5,
                                       textvariable=self.die_side_val)
        self.die_side_val.set(self.default_die_sides)

        self.die_side_label.pack(side="left")
        self.die_side_entry.pack(side="right")
        self.die_side_input_frame.pack(side="top", fill="x")

        # Simulation loop delay

        self.delay_input_frame = tk.Frame(master=self)

        self.delay_label = tk.Label(master=self.delay_input_frame,
                                    text="Delay [ms]:")
        self.delay_val = tk.IntVar(master=self)
        self.delay_entry = tk.Entry(master=self.delay_input_frame,
                                    width=5,
                                    textvariable=self.delay_val)
        self.delay_val.set(self.default_delay)

        self.delay_label.pack(side="left")
        self.delay_entry.pack(side="right")
        self.delay_input_frame.pack(side="top", fill="x")

        # Control buttons

        self.control_button_outer_frame = tk.Frame(master=self, pady=20)
        self.control_button_frame = tk.Frame(master=self.control_button_outer_frame)

        # Start/Stop
        self.start_stop_str = tk.StringVar(master=self.control_button_frame)
        self.start_stop_str.set("Start")
        self.start_stop_button = tk.Button(master=self.control_button_frame,
                                           textvariable=self.start_stop_str,
                                           command=self.start_stop_button_handler,
                                           width=6)

        # Reset
        self.reset_button = tk.Button(master=self.control_button_frame,
                                      text="Reset",
                                      command=self.reset_button_handler,
                                      width=6)

        self.start_stop_button.pack(side="left")
        self.reset_button.pack(side="left")
        self.control_button_frame.pack()
        self.control_button_outer_frame.pack(side="top", fill="x")

    def start_stop_button_handler(self):
        if self.start_stop_button_state:
            self.stop_sim()
            self.simulation_paused = 1
        else:
            if self.simulation_paused:
                self.delay_entry.config(state='disabled')

                self.resume_sim()
            else:
                # TODO: check input sanity
                self.start_sim()
            self.simulation_paused = 0
        self.start_stop_button_flip()

    def start_stop_button_flip(self):
        if self.start_stop_button_state:
            self.start_stop_button_state = 0
            self.start_stop_str.set("Start")
            self.reset_button.config(state="normal")
        else:
            self.start_stop_button_state = 1
            self.start_stop_str.set("Pause")
            self.reset_button.config(state="disabled")

    def start_sim(self):
        self.dice_no_entry.config(state='disabled')
        self.die_side_entry.config(state='disabled')
        self.delay_entry.config(state='disabled')
        no_of_dice = self.dice_no_val.get()
        die_sides = self.die_side_val.get()
        delay = self.delay_val.get()
        model.set_model(no_of_dice, die_sides)
        model.set_delay(delay)
        model.continue_computing = 1
        model.compute_distribution()
        plot_handler.continue_replotting = 1
        root.after(plot_handler.plotting_delay, plot_handler.replotting_loop())

    def resume_sim(self):
        self.delay_entry.config(state='disabled')
        delay = self.delay_val.get()
        model.set_delay(delay)
        model.continue_computing = 1
        model.compute_distribution()
        plot_handler.continue_replotting = 1
        root.after(plot_handler.plotting_delay, plot_handler.replotting_loop())

    def stop_sim(self):
        self.delay_entry.config(state='normal')
        model.continue_computing = 0
        plot_handler.continue_replotting = 0

    def reset_button_handler(self):
        # TODO: full clear of sim necessary? I think it does it on its own...
        self.simulation_paused = 0
        self.dice_no_entry.config(state='normal')
        self.die_side_entry.config(state='normal')
        self.delay_entry.config(state='normal')


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.result_field = ResultField(self)
        self.input_field = InputField(self)

        self.parent.title("Dice Simulation")
        self.result_field.pack(side="left", fill="both", expand=True)
        self.input_field.pack(side="right", fill="x", padx=20)


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
