 # README: 6G Communication System Simulation

This repository contains the implementation of a **6G Communication System Simulation** with detailed channel models, resource allocation strategies, mobility, interference management, and security features. Below is a visual representation of the system flow.

![image](https://github.com/user-attachments/assets/ac5f1a35-4b48-469f-9345-22f822bbaa89)

### Overview

- **User Input:** Channel selection through the command line.
- **Random Bit Generation:** Generates the original message bits.
- **Polar Code Encoding:** Encodes the bits using Polar coding techniques.
- **Network Slicing:** Supports eMBB, URLLC, and mMTC slices.
- **Resource Allocation:** Implements Round Robin, Proportional Fair, and Reinforcement Learning algorithms.
- **Channel Transmission:** Models channels like AWGN, IRS, THz, IAB, and others.
- **Signal Processing:** Includes channel estimation, interference management, and edge computing.
- **Mobility Model:** Simulates handovers based on user speed.
- **Security & Energy Efficiency:** Features quantum-safe encryption and power consumption analysis.
- **BER Calculation:** Evaluates the system’s performance by calculating Bit Error Rate.
- **Results:** Outputs the results in both a table format and visualizations.

## Quick Start

1. Clone the repository:
   ```bash
   git clone [<repository_url>](https://github.com/dr-yahya/6G-For-I5.git)
   cd 6G-FOR-I5
   ```
2. Run the simulation:
   ```bash
   python 6g.py
   ```
3. Follow the command-line instructions to choose a channel and view results.

## Diagram Link

visit [6G Communication System Flow Diagram](https://www.blocksandarrows.com/editor/EPxkswM33RvPhgt4).
