# Signal Sampling and Recovery Application

Welcome to the Signal Sampling and Recovery Application! This desktop application is designed to illustrate the significance of the Nyquist rate in signal processing. Explore the features below to understand the impact of different sampling frequencies, signal composition, noise addition, and real-time visualization.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
   - [Sample & Recover](#sample-and-recover)
   - [Load & Compose](#load-and-compose)
   - [Additive Noise](#additive-noise)
   - [Real-time](#real-time)
   - [Resize](#resize)
   - [Different Sampling Scenarios](#different-sampling-scenarios)

## Overview

The Signal Sampling and Recovery Application is a powerful tool for visualizing and understanding the consequences of sampling at different frequencies. It demonstrates the Nyquist rate through the sampling and recovery of mid-length signals, providing real-time insights into signal composition and noise effects.

## Features

### Sample & Recover

1. **Load and Visualize Signal:** Load a mid-length signal (around 1000 points) and visualize it on the first graph.

2. **Sample at Different Frequencies:** Sample the loaded signal at various frequencies. The sampling frequency is displayed in either the actual frequency or normalized form (0×fmax to 4×fmax).

3. **Recover Using Whittaker–Shannon Interpolation:** Utilize the Whittaker–Shannon interpolation formula to recover the original signal using the sampled points. View the original signal with sampled points on the first graph and the reconstructed signal on the second graph.

4. **Difference Visualization:** The third graph illustrates the difference between the original signal and the reconstructed one, highlighting the impact of different sampling frequencies.

### Load & Compose

5. **Load Signal from File or Composer:** Load a signal from a file or use the signal mixer/composer within the application. The composer allows users to add, remove, and adjust multiple sinusoidal signals of different frequencies and magnitudes.

### Additive Noise

6. **Customizable Noise Addition:** Add noise to the loaded signal with a controllable Signal-to-Noise Ratio (SNR) level. Visualize the dependency of noise effect on the signal frequency.

### Real-time

7. **Real-time Sampling and Recovery:** Experience real-time updates as you make changes. Sampling and recovery occur instantly upon user modifications, ensuring a seamless user experience.

### Resize

8. **Resizable User Interface:** Easily resize the application without compromising the user interface. The responsive design ensures a consistent and user-friendly experience.

