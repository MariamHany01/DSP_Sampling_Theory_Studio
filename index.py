from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUiType
from os import path
import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from os import path
import os

FORM_CLASS, _ = loadUiType(
    path.join(path.dirname(__file__), "sampling_studio.ui"))


class Signal:
    def __init__(self, frequency=0, amplitude=0, signal_type='Sine', signal_name=''):
        self.frequency = frequency
        self.amplitude = amplitude
        self.signal_type = signal_type
        self.signal_name = signal_name

    def prepare_signal(self):
        if self.signal_type == 'Sine Wave':
            signal = self.amplitude * \
                np.sin(2 * np.pi * self.frequency * np.linspace(0, 1, 1000))
        else:
            signal = self.amplitude * \
                np.cos(2 * np.pi * self.frequency * np.linspace(0, 1, 1000))
        return signal

    def sincInterPolation(originalTimeArr, sampledTimerArr, sampledAmplitudeArr):
        if len(sampledTimerArr) < 2:
            return np.zeros_like(originalTimeArr)
        periodTime = sampledTimerArr[1]-sampledTimerArr[0]
        timeConvolutionShift = np.tile(originalTimeArr, (len(sampledTimerArr), 1)) - \
            np.tile(sampledTimerArr[:, np.newaxis], (1, len(originalTimeArr)))
        return np.dot(sampledAmplitudeArr, np.sinc(timeConvolutionShift/periodTime))


class Graph(FigureCanvas):
    static_yrange = False
    ymin = 0
    ymax = 0

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def draw_signal(self, signal):
        self.axes.clear()
        self.axes.plot(signal)
        self.axes.set_xlabel('Sample')
        self.axes.set_ylabel('Amplitude')
        if self.static_yrange:
            self.axes.set_ylim(self.ymin, self.ymax)

        self.draw()

    def set_static_yrange(self, ymin, ymax):
        self.static_yrange = True
        self.ymin = ymin
        self.ymax = ymax


class MainApp(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowTitle("Sampling Studio")
        self.setupUi(self)
        self.added_signals = []
        self.max_freq = 0
        self.signal_frequencies = []
        self.noisy = []

        self.layout_left = QVBoxLayout(self.generated_signal_viewer)
        self.layout_right = QVBoxLayout(self.viewers_widget)

        self.created_signal = Graph()
        self.original_signal = Graph()
        self.recovered_signal = Graph()
        self.error_signal = Graph()

        self.layout_left.addWidget(self.created_signal)
        self.layout_right.addWidget(self.original_signal)
        self.layout_right.addWidget(self.recovered_signal)
        self.layout_right.addWidget(self.error_signal)

        self.snr_slider.setRange(15, 80)
        self.snr_slider.setSingleStep(1)
        self.snr_slider.setValue(80)  # Set initial value to maximum SNR

        self.snr_slider.valueChanged.connect(
            self.update_original_signal_with_noise)

        # Inside the MainApp class initialization
        # Set to a range suitable for your needs
        self.sampling_frequency_slider.setRange(0, 400)
        self.sampling_frequency_slider.setValue(0)  # Setting an initial value
        self.sampling_frequency_slider.setSingleStep(
            1)  # To jump in steps of 10 (1, 10, 20,...)

        self.freq_combobox.currentIndexChanged.connect(
            self.update_sampling_frequency_slider)
        self.sampling_frequency_slider.valueChanged.connect(
            self.sample_and_reconstruct_signal)
        self.sampling_frequency_slider.valueChanged.connect(
            self.update_frequency_label)
        self.upload_signal_button_2.triggered.connect(self.upload_csv)

        self.generated_amplitude_spin_box.valueChanged.connect(
            lambda: self.plot_signal(self.created_signal))
        
        self.generated_frequency_spin_box.valueChanged.connect(
            lambda: self.plot_signal(self.created_signal))
        self.add_to_viewers_button.clicked.connect(
            lambda: self.add_to_viewer(self.original_signal))
        self.remove_button.clicked.connect(self.remove_from_viewer)

    def update_sampling_frequency_slider(self):
        selected_index = self.freq_combobox.currentIndex()

        if selected_index == 0:
            # If the selected index is the last one (maximum frequency), set slider values accordingly
            self.sampling_frequency_slider.setRange(0, 4 * self.max_freq)
            self.sampling_frequency_slider.setSingleStep(1)
            freq_value = self.sampling_frequency_slider.value()
            if self.selected_signal_combo_box.currentText() != "":
                relative_freq = freq_value / self.max_freq
                self.frequency_label.setText(
                    f"Frequency: {relative_freq} fmax")
                if relative_freq == 0.0:
                    self.recovered_signal.axes.clear()
                    self.recovered_signal.draw()
                    self.error_signal.axes.clear()
                    self.error_signal.draw()
        else:
            # If the selected index is not the maximum frequency, set normal slider values
            self.sampling_frequency_slider.setRange(0, 4 * self.max_freq)
            self.sampling_frequency_slider.setSingleStep(1)
            freq_value = self.sampling_frequency_slider.value()
            self.frequency_label.setText(f"Frequency: {freq_value} fmax")

    def plot_signal(self, graph):
        signal = Signal(
            amplitude=self.generated_amplitude_spin_box.value(),
            frequency=self.generated_frequency_spin_box.value(),
            signal_type=self.generated_type_combo_box.currentText()
        )
        prepared_signal = signal.prepare_signal()
        graph.draw_signal(prepared_signal)

    def add_to_viewer(self, viewer):
        frequency = self.generated_frequency_spin_box.value()
        if frequency > self.max_freq:
            self.max_freq = frequency
        amplitude = self.generated_amplitude_spin_box.value()
        signal_name = self.generated_signal_name_line_Edit.text().strip()
        if amplitude == 0:
            QMessageBox.warning(
                self, "Error", "You can't add a signal with 0 amplitude.")
            return
        if frequency == 0:
            QMessageBox.warning(
                self, "Error", "You can't add a signal with 0 frequency.")
            return
        if not signal_name:
            QMessageBox.warning(
                self, "Error", "You can't add a signal with a blank name.")
            return
        if signal_name in [self.selected_signal_combo_box.itemText(i) for i in range(self.selected_signal_combo_box.count())]:
            QMessageBox.warning(
                self, "Error", "This signal name is a duplicate. Please choose a unique name.")
            return
        signal = Signal(
            frequency=frequency,
            amplitude=amplitude,
            signal_type=self.generated_type_combo_box.currentText(),
            signal_name=signal_name
        )
        prepared_signal = signal.prepare_signal()
        if self.added_signals:
            self.added_signals.append(prepared_signal)
            final_signal = sum(self.added_signals)
            noisy_signal = self.add_noise_to_signal(final_signal)
            self.noisy = noisy_signal
            self.original_signal.draw_signal(self.noisy)
        else:
            self.added_signals.append(prepared_signal)
            noisy_signal = self.add_noise_to_signal(prepared_signal)
            self.noisy = noisy_signal
            viewer.draw_signal(self.noisy)

# mina
        self.signal_frequencies.append(frequency)
        self.max_freq = max(self.signal_frequencies)

        self.selected_signal_combo_box.addItem(signal_name)
        self.generated_type_combo_box.setCurrentIndex(
            0)  # Reset the combo box to the first item
        self.generated_amplitude_spin_box.setValue(
            0)  # Reset the amplitude spin box to 0
        self.generated_frequency_spin_box.setValue(
            0)  # Reset the frequency spin box to 0
        self.generated_signal_name_line_Edit.clear()  # Clear the name line edit
        self.created_signal.axes.clear()  # Clear the axes
        self.created_signal.draw()  # Redraw the graph
        self.update_sampling_frequency_slider()

    def remove_from_viewer(self):
        if not self.added_signals:
            QMessageBox.warning(self, "Error", "No signals to remove.")
            return

        selected_signal_index = self.selected_signal_combo_box.currentIndex()

        if selected_signal_index != -1:  # If there's a selected signal
            removed_frequency = self.signal_frequencies.pop(
                selected_signal_index)
            self.selected_signal_combo_box.removeItem(selected_signal_index)
            self.added_signals.pop(selected_signal_index)

            if removed_frequency == self.max_freq:
                if self.signal_frequencies:
                    self.max_freq = max(self.signal_frequencies)
                else:
                    self.max_freq = 0

        if not self.added_signals:
            self.original_signal.axes.clear()
            self.original_signal.draw()
            self.recovered_signal.axes.clear()
            self.recovered_signal.draw()
            self.error_signal.axes.clear()
            self.error_signal.draw()
            self.sampling_frequency_slider.setValue(0)
        else:
            final_signal = sum(self.added_signals)
            noisy_signal = self.add_noise_to_signal(final_signal)
            self.noisy = noisy_signal
            self.original_signal.draw_signal(self.noisy)
        self.update_sampling_frequency_slider()

    def add_noise_to_signal(self, signal):
        snr = self.snr_slider.value()
        noise_power = np.var(signal) / (10**(snr / 10))
        noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
        noisy_signal = signal + noise
        return noisy_signal

    def update_original_signal_with_noise(self):
        if self.added_signals:
            final_signal = sum(self.added_signals)
            self.noisy = self.add_noise_to_signal(final_signal)
            # self.noisy = noisy_signal
            self.original_signal.draw_signal(self.noisy)
            self.sample_and_reconstruct_signal()

    def sample_and_reconstruct_signal(self):
        # Sampling
        if self.added_signals:
            final_signal = sum(self.added_signals)
            print(self.noisy)
            sampling_frequency = self.sampling_frequency_slider.value()
            if sampling_frequency > 0:
                total_points = len(final_signal)
                Ts = total_points / (sampling_frequency * total_points / 1000)
                t = np.linspace(0, total_points, total_points)
                sampled_signal = self.noisy[::int(Ts)]

                # Reconstruct using sinc interpolation
                t_sampled = np.arange(0, total_points, int(Ts))
                reconstructed_signal = Signal.sincInterPolation(
                    t, t_sampled, sampled_signal)

                # Displaying Original Signal with Sampled Points
                self.original_signal.draw_signal(self.noisy)
                self.original_signal.axes.scatter(
                    t_sampled, sampled_signal, color='red')
                self.original_signal.draw()

                # Displaying Reconstructed Signal
                self.recovered_signal.set_static_yrange(
                    min(self.noisy)-1, max(self.noisy))
                self.recovered_signal.draw_signal(reconstructed_signal)

                # Displaying Error Signal (Difference between original and reconstructed)
                error = final_signal - reconstructed_signal
                self.error_signal.set_static_yrange(
                    min(self.noisy)-1, max(self.noisy))
                self.error_signal.draw_signal(error)
            else:
                self.recovered_signal.axes.clear()
                self.recovered_signal.draw()
                self.error_signal.axes.clear()
                self.error_signal.draw()

                # if len(sampled_signal) < 2:
                #     # If less than two samples, clear the other plots and return
                #     self.recovered_signal.axes.clear()
                #     self.recovered_signal.draw()
                #     self.error_signal.axes.clear()
                #     self.error_signal.draw()
                #     return

    def update_frequency_label(self):
        selected_index = self.freq_combobox.currentIndex()
        if selected_index == 1:
            freq_value = self.sampling_frequency_slider.value()
            self.frequency_label.setText(f"Frequency: {freq_value} Hz")
        else:
            freq_value = self.sampling_frequency_slider.value()
            if self.selected_signal_combo_box.currentText() != "":
                relative_freq = freq_value / self.max_freq
                self.frequency_label.setText(
                    f"Frequency: {relative_freq} fmax")

    def upload_csv(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Signal 1",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )
        if file_path:
            self.added_signals.clear()
            self.recovered_signal.axes.clear()
            self.error_signal.axes.clear()
            self.recovered_signal.draw()  # Clear the display of the recovered_signal graph
            self.error_signal.draw()
            title = os.path.basename(file_path)
            if title:
                # Load the CSV file
                csv_data = pd.read_csv(file_path)
                self.max_freq = 23

                # Update the label or wherever you want to display max_freq
                self.frequency_label.setText(f"Frequency: {self.max_freq} Hz")

                # Add your code to handle the rest of the CSV data as needed

                new_signal_data = np.loadtxt(
                    file_path, delimiter=",",  usecols=(1), skiprows=1, max_rows=1000)

                self.added_signals.append(new_signal_data)

                self.original_signal.draw_signal(
                    new_signal_data)
                signal_names = "data"
                self.selected_signal_combo_box.addItem(signal_names)
                self.signal_frequencies.append(self.max_freq)
                self.max_freq = max(self.signal_frequencies)
                self.update_original_signal_with_noise()

    def exit_program(self):
        sys.exit()


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
