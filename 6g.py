import numpy as np
import matplotlib.pyplot as plt
import logging
import sys
import pandas as pd
from polarcodes import PolarCode, Construct, Encode, Decode

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

# Constants
N = 256  # Codeword length
K = 100  # Number of information bits
messages = 1000  # Number of messages for the simulation
snr_db = 5.0  # Default SNR, updated during loop

# Initialize Polar Code
myPC = PolarCode(N, K)
myPC.construction_type = 'bb'
Construct(myPC, snr_db)

# Channel models
def awgn_low_power(coded_bits, snr_db):
    logger.info("Transmitting low-power signal over AWGN channel.")
    noise_power = 10 ** (-snr_db / 10)
    received_signal = coded_bits + np.random.normal(0, np.sqrt(noise_power), coded_bits.shape)
    myPC.likelihoods = 2 * received_signal / noise_power
    return received_signal

def irs_channel(coded_bits, snr_db):
    logger.info("Simulating IRS channel.")
    reflection_coefficient = 0.9
    reflected_signal = coded_bits * reflection_coefficient
    noise = np.random.normal(0, np.sqrt(10 ** (-snr_db / 10)), len(coded_bits))
    noise_power = 10 ** (-snr_db / 10)
    received_signal = reflected_signal + noise
    myPC.likelihoods = 2 * received_signal / noise_power
    return received_signal

def thz_channel(coded_bits, snr_db):
    logger.info("Simulating THz channel with high path loss.")
    path_loss = 10 ** (2 * np.log10(1000))
    noise_power = 10 ** (-snr_db / 10)
    noise = np.random.normal(0, np.sqrt(noise_power), len(coded_bits))
    received_signal = coded_bits / path_loss + noise
    myPC.likelihoods = 2 * received_signal / noise_power
    return received_signal

def sensing_channel(coded_bits, snr_db):
    logger.info("Simulating joint communication and sensing.")
    pilot_signal = np.ones(len(coded_bits))
    received_signal = awgn_low_power(pilot_signal, snr_db)
    sensing_result = np.mean(np.abs(received_signal - pilot_signal))
    logger.info(f"Sensing result (environmental reflection): {sensing_result}")
    noise_power = 10 ** (-snr_db / 10)
    myPC.likelihoods = 2 * received_signal / noise_power
    return received_signal

def iab_channel(coded_bits, snr_db):
    logger.info("Simulating Integrated Access and Backhaul (IAB).")
    first_hop = awgn_low_power(coded_bits, snr_db)
    second_hop = awgn_low_power(first_hop, snr_db)
    noise_power = 10 ** (-snr_db / 10)
    myPC.likelihoods = 2 * second_hop / noise_power
    return second_hop

def urllc_channel(coded_bits, snr_db):
    logger.info("Simulating Ultra-Reliable Low-Latency Communication (URLLC) channel.")
    fading_coefficient = np.random.rayleigh(scale=1.0, size=len(coded_bits))
    faded_signal = coded_bits * fading_coefficient
    noise_power = 10 ** (-snr_db / 10)
    noise = np.random.normal(0, np.sqrt(noise_power), len(coded_bits))
    received_signal = faded_signal + noise
    myPC.likelihoods = 2 * received_signal / noise_power
    return received_signal

def massive_mimo_channel(coded_bits, snr_db):
    logger.info("Simulating Massive MIMO channel.")
    num_antennas = 64
    channel_matrix = np.random.randn(num_antennas, len(coded_bits)) / np.sqrt(num_antennas)
    transmitted_signal = np.dot(channel_matrix.T, coded_bits)
    noise_power = 10 ** (-snr_db / 10)
    noise = np.random.normal(0, np.sqrt(noise_power), transmitted_signal.shape)
    received_signal = transmitted_signal + noise
    myPC.likelihoods = 2 * np.mean(received_signal, axis=0) / noise_power
    return received_signal

def noma_channel(coded_bits, snr_db):
    logger.info("Simulating Non-Orthogonal Multiple Access (NOMA) channel.")
    power_allocation_user1 = 0.8
    power_allocation_user2 = 0.2
    user1_signal = coded_bits * power_allocation_user1
    user2_signal = coded_bits * power_allocation_user2
    combined_signal = user1_signal + user2_signal
    noise_power = 10 ** (-snr_db / 10)
    noise = np.random.normal(0, np.sqrt(noise_power), len(coded_bits))
    received_signal = combined_signal + noise
    myPC.likelihoods = 2 * received_signal / noise_power
    return received_signal

# Network slicing
def network_slicing(slice_type, coded_bits):
    logger.info(f"Simulating network slicing for {slice_type} slice.")
    if slice_type == 'eMBB':
        return awgn_low_power(coded_bits, snr_db)
    elif slice_type == 'URLLC':
        return urllc_channel(coded_bits, snr_db)
    elif slice_type == 'mMTC':
        return noma_channel(coded_bits, snr_db)
    else:
        logger.error(f"Invalid slice type: {slice_type}")
        sys.exit(1)

# Resource allocation
def resource_allocation(algorithm, coded_bits):
    logger.info(f"Simulating resource allocation using {algorithm} algorithm.")
    if algorithm == 'Round Robin':
        # Implement Round Robin allocation
        allocated_bits = np.zeros_like(coded_bits)
        for i in range(len(coded_bits)):
            if i % 2 == 0:
                allocated_bits[i] = coded_bits[i]
        return allocated_bits
    elif algorithm == 'Proportional Fair':
        # Implement Proportional Fair allocation
        fairness_weight = np.random.uniform(0.5, 1.5, size=len(coded_bits))
        allocated_bits = coded_bits * fairness_weight
        return allocated_bits
    elif algorithm == 'Reinforcement Learning':
        # Implement RL-based allocation (simplified example)
        action = np.random.choice([0, 1], size=len(coded_bits))
        allocated_bits = coded_bits * action
        return allocated_bits
    else:
        logger.error(f"Invalid resource allocation algorithm: {algorithm}")
        sys.exit(1)

# Mobility model
def mobility_model(user_speed, coded_bits):
    logger.info(f"Simulating mobility with user speed {user_speed} m/s.")
    if user_speed > 0:
        handover_probability = min(user_speed / 100, 1.0)
        logger.info(f"Handover probability: {handover_probability}")
        if np.random.rand() < handover_probability:
            logger.info("Handover occurred.")
            coded_bits = np.roll(coded_bits, shift=1)  # Simulate handover by shifting bits
    return awgn_low_power(coded_bits, snr_db)

# Interference management
def interference_management(coded_bits):
    logger.info("Simulating interference management.")
    interference_signal = np.random.normal(0, 0.1, len(coded_bits))
    interference_cancellation = 0.5  # Assume 50% interference cancellation efficiency
    received_signal = coded_bits + (interference_signal * (1 - interference_cancellation))
    myPC.likelihoods = 2 * received_signal / (10 ** (-snr_db / 10))
    return received_signal

# Edge computing
def edge_computing(coded_bits):
    logger.info("Simulating edge computing for task offloading.")
    processing_delay = np.random.uniform(0, 5)  # Random delay between 0-5 ms
    logger.info(f"Processing delay: {processing_delay} ms")
    # Simulate task offloading effect by modifying coded bits
    offloading_factor = np.random.uniform(0.8, 1.2)
    offloaded_bits = coded_bits * offloading_factor
    return offloaded_bits, processing_delay

# Channel estimation
def channel_estimation(coded_bits):
    logger.info("Simulating channel estimation.")
    estimation_error = np.random.normal(0, 0.05, len(coded_bits))
    estimated_signal = coded_bits + estimation_error
    return estimated_signal

# Security simulation
def security_simulation(coded_bits):
    logger.info("Simulating quantum-safe encryption.")
    encryption_key = np.random.choice([1, -1], size=len(coded_bits))
    encrypted_signal = coded_bits * encryption_key
    return encrypted_signal

# Energy efficiency
def energy_efficiency(coded_bits):
    logger.info("Simulating energy efficiency analysis.")
    power_consumption = np.sum(coded_bits ** 2) / len(coded_bits)
    logger.info(f"Power consumption: {power_consumption} W")
    # Adjust the coded bits to simulate energy-saving measures
    energy_saving_factor = np.random.uniform(0.9, 1.1)
    efficient_bits = coded_bits * energy_saving_factor
    return efficient_bits, power_consumption

channel_models = {
    'AWGN': awgn_low_power,
    'IRS': irs_channel,
    'THz': thz_channel,
    'Sensing': sensing_channel,
    'IAB': iab_channel,
    'URLLC': urllc_channel,
    'Massive MIMO': massive_mimo_channel,
    'NOMA': noma_channel
}

# BER Calculation
def calculate_ber(original_bits, decoded_bits):
    errors = np.sum(original_bits != decoded_bits)
    ber = errors / len(original_bits)
    logger.info(f"Bit Error Rate (BER): {ber}")
    return ber

# Visualization of Signals and BER vs SNR
def visualize_results(original_bits, modulated_signal, received_signal, decoded_signal, ber_values, snr_values, channel_name):
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot Original Bits
    axs[0, 0].stem(original_bits[:50])
    axs[0, 0].set_title('Original Bits')
    
    # Plot Modulated Signal
    axs[0, 1].plot(np.real(modulated_signal[:50]))
    axs[0, 1].set_title('Modulated Signal')
    
    # Plot Received Signal
    axs[1, 0].plot(np.real(received_signal[:50]))
    axs[1, 0].set_title(f'Received Signal ({channel_name} Channel)')
    
    # Plot BER vs SNR
    axs[1, 1].plot(snr_values, ber_values, marker='o', label=channel_name)
    axs[1, 1].set_xlabel('SNR (dB)')
    axs[1, 1].set_ylabel('Bit Error Rate (BER)')
    axs[1, 1].set_title('BER vs SNR')
    axs[1, 1].set_yscale('log')
    axs[1, 1].legend()
    axs[1, 1].grid(True)
    
    plt.tight_layout()
    plt.show()

# Main simulation function to compute BER over SNR for the chosen channel
def simulate_ber_for_channel(channel_name):
    if channel_name not in channel_models:
        logger.error(f"Invalid channel name: {channel_name}")
        sys.exit(1)
    
    channel_model = channel_models[channel_name]
    snr_values = range(0, 31, 5)  # SNR values from 0 dB to 30 dB
    ber_values = []
    results_data = []
    
    # Simulate the chosen channel over all SNR values
    for snr in snr_values:
        global snr_db
        snr_db = snr  # Update the global SNR value
        
        logger.info(f"Simulating {channel_name} channel for SNR = {snr} dB")
        
        # Step 1: Generate random bits
        original_bits = np.random.randint(0, 2, K)
        
        # Step 2: Encode the bits using Polar Codes
        myPC.set_message(original_bits)
        Encode(myPC)
        coded_bits = myPC.get_codeword()
        
        # Step 3: Apply resource allocation
        coded_bits = resource_allocation('Proportional Fair', coded_bits)
        
        # Step 4: Apply network slicing (eMBB as default)
        coded_bits = network_slicing('eMBB', coded_bits)
        
        # Step 5: Transmit through the channel and receive the signal
        received_signal = channel_model(coded_bits, snr_db)
        
        # Step 6: Apply channel estimation
        received_signal = channel_estimation(received_signal)
        
        # Step 7: Apply interference management
        received_signal = interference_management(received_signal)
        
        # Step 8: Apply edge computing
        received_signal, processing_delay = edge_computing(received_signal)
        
        # Step 9: Apply mobility model
        received_signal = mobility_model(user_speed=30, coded_bits=received_signal)  # Example speed of 30 m/s
        
        # Step 10: Apply security simulation
        received_signal = security_simulation(received_signal)
        
        # Step 11: Apply energy efficiency
        received_signal, power_consumption = energy_efficiency(received_signal)
        
        # Step 12: Decode the signal using Polar Code decoding
        Decode(myPC)
        decoded_bits = myPC.message_received
        
        # Step 13: Calculate BER
        ber = calculate_ber(original_bits, decoded_bits)
        ber_values.append(ber)
        
        # Collect results for the table
        results_data.append({
            'SNR (dB)': snr,
            'BER': ber,
            'Processing Delay (ms)': processing_delay,
            'Power Consumption (W)': power_consumption
        })
    
    # Create a results DataFrame
    results_df = pd.DataFrame(results_data)
    print(results_df)
    
    # Visualize the results
    visualize_results(original_bits, coded_bits, received_signal, myPC.message_received, ber_values, snr_values, channel_name)

# Command-line interface to choose the channel and run the simulation
def main():
    print("Available channels:")
    for i, channel in enumerate(channel_models.keys()):
        print(f"{i + 1}. {channel}")
    
    try:
        choice = int(input("Enter the number corresponding to the channel you want to simulate: "))
        if choice < 1 or choice > len(channel_models):
            raise ValueError("Invalid choice. Please enter a valid number.")
    except ValueError as e:
        print(e)
        sys.exit(1)
    
    channel_name = list(channel_models.keys())[choice - 1]
    simulate_ber_for_channel(channel_name)

if __name__ == "__main__":
    main()
