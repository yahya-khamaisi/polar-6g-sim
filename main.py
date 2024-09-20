import numpy as np
import matplotlib.pyplot as plt
import logging
from polarcodes import PolarCode, Construct, Encode, AWGN, Decode

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

# Polar coding (Channel Coding) function
def channel_coding(bits):
    logger.info("Performing Polar Channel Coding.")
    
    # Set the message for the polar code
    myPC.set_message(bits)
    
    # Encode the message
    Encode(myPC)
    
    # Return the encoded codeword
    return myPC.get_codeword()

# Modulation (AWGN channel)
def modulation(coded_bits):
    logger.info("Transmitting over AWGN channel.")
    
    # Transmit the codeword over AWGN channel
    noise_power = 10 ** (-snr_db / 10)
    received_signal = coded_bits + np.random.normal(0, np.sqrt(noise_power), coded_bits.shape)
    
    # Calculate log-likelihood ratios (LLRs) for BPSK
    myPC.likelihoods = 2 * received_signal / noise_power
    
    return received_signal

# Low-power AWGN for mMTC++
def awgn_low_power(coded_bits, snr_db):
    logger.info("Transmitting low-power signal over AWGN channel.")
    noise_power = 10 ** (-snr_db / 10)
    received_signal = coded_bits + np.random.normal(0, np.sqrt(noise_power), coded_bits.shape)
    
    # Calculate log-likelihood ratios (LLRs)
    myPC.likelihoods = 2 * received_signal / noise_power
    
    return received_signal

# IRS Channel: Signal reflection
def irs_channel(coded_bits, snr_db):
    logger.info("Simulating IRS channel.")
    reflection_coefficient = 0.9  # Reflects 90% of the signal
    reflected_signal = coded_bits * reflection_coefficient
    noise = np.random.normal(0, np.sqrt(10 ** (-snr_db / 10)), len(coded_bits))
    received_signal = reflected_signal + noise
    
    # Calculate log-likelihood ratios (LLRs)
    myPC.likelihoods = 2 * received_signal / np.sqrt(10 ** (-snr_db / 10))
    
    return received_signal

# THz Communication: High path loss
def thz_channel(coded_bits, snr_db):
    logger.info("Simulating THz channel with high path loss.")
    path_loss = 10 ** (2 * np.log10(1000))  # Example path loss for THz
    noise_power = 10 ** (-snr_db / 10)
    noise = np.random.normal(0, np.sqrt(noise_power), len(coded_bits))
    received_signal = coded_bits / path_loss + noise
    
    # Calculate log-likelihood ratios (LLRs)
    myPC.likelihoods = 2 * received_signal / noise_power
    
    return received_signal

# Joint Communication and Sensing: Compare sent and received signals
def sensing_channel(coded_bits, snr_db):
    logger.info("Simulating joint communication and sensing.")
    # Simulate a known pilot signal for sensing
    pilot_signal = np.ones(len(coded_bits))
    received_signal = modulation(pilot_signal)
    
    # Compare transmitted and received signals to sense the environment
    sensing_result = np.mean(np.abs(received_signal - pilot_signal))
    logger.info(f"Sensing result (environmental reflection): {sensing_result}")
    
    # Calculate log-likelihood ratios (LLRs)
    myPC.likelihoods = 2 * received_signal / (10 ** (-snr_db / 10))
    
    return received_signal

# Integrated Access and Backhaul (IAB): Simulate multi-hop transmission
def iab_channel(coded_bits, snr_db):
    logger.info("Simulating Integrated Access and Backhaul (IAB).")
    # Simulate a hop to a backhaul node
    first_hop = modulation(coded_bits)
    second_hop = modulation(first_hop)  # Simulate backhaul transmission
    
    # Calculate log-likelihood ratios (LLRs)
    myPC.likelihoods = 2 * second_hop / (10 ** (-snr_db / 10))
    
    return second_hop

# BER Calculation
def calculate_ber(original_bits, decoded_bits):
    errors = np.sum(original_bits != decoded_bits)
    ber = errors / len(original_bits)
    logger.info(f"Bit Error Rate (BER): {ber}")
    return ber

# Visualization of Signals and BER vs SNR in a single page
def visualize_all_in_one_page(original_bits, modulated_signal, received_signals, decoded_signals, ber_dict, snr_values, channel_names):
    fig, axs = plt.subplots(3, 2, figsize=(16, 14))
    
    # Plot Original Bits
    axs[0, 0].stem(original_bits[:50])
    axs[0, 0].set_title('Original Bits (Common for All Channels)')
    
    # Plot Modulated Signal
    axs[0, 1].plot(np.real(modulated_signal[:50]))
    axs[0, 1].set_title('Modulated Signal (Common for All Channels)')
    
    # Plot Received Signals for all channels
    for i, received_signal in enumerate(received_signals):
        axs[1, 0].plot(np.real(received_signal[:50]), label=channel_names[i])
    axs[1, 0].set_title('Received Signals (All Channels)')
    axs[1, 0].legend()
    
    # Plot Decoded Signals for all channels
    for i, decoded_signal in enumerate(decoded_signals):
        axs[1, 1].plot(np.real(decoded_signal[:50]), label=channel_names[i])
    axs[1, 1].set_title('Decoded Signals (All Channels)')
    axs[1, 1].legend()
    
    # Plot BER vs SNR for all channels
    for channel_name, ber_values in ber_dict.items():
        axs[2, 0].plot(snr_values, ber_values, marker='o', label=channel_name)
    axs[2, 0].set_xlabel('SNR (dB)')
    axs[2, 0].set_ylabel('Bit Error Rate (BER)')
    axs[2, 0].set_title('BER vs SNR (All Channels)')
    axs[2, 0].set_yscale('log')  # Set y-axis to logarithmic scale for BER
    axs[2, 0].legend()
    axs[2, 0].grid(True)
    
    # Empty the final subplot
    axs[2, 1].axis('off')
    
    plt.tight_layout()
    plt.show()

# Main simulation function to compute BER over SNR for all channels and visualize signals
def simulate_ber_and_signals_for_all_channels():
    snr_values = range(0, 31, 5)  # SNR values from 0 dB to 30 dB
    ber_dict = {  # Dictionary to store BER results for each channel
        'IRS': [],
        'THz': [],
        'Sensing': [],
        'IAB': [],
        'Low Power AWGN': []
    }
    
    # Define the channel models to simulate
    channel_models = {
        'IRS': irs_channel,
        'THz': thz_channel,
        'Sensing': sensing_channel,
        'IAB': iab_channel,
        'Low Power AWGN': awgn_low_power
    }
    
    channel_names = list(channel_models.keys())
    
    # Store received and decoded signals for each channel (for signal visualization)
    received_signals = []
    decoded_signals = []
    
    # Simulate each channel over all SNR values
    for snr in snr_values:
        global snr_db
        snr_db = snr  # Update the global SNR value
        
        logger.info(f"Simulating for SNR = {snr} dB")
        
        # Step 1: Generate random bits
        original_bits = np.random.randint(0, 2, K)
        
        # Step 2: Encode the bits using Polar Codes
        coded_bits = channel_coding(original_bits)
        
        # Simulate each channel
        for channel_name, channel_model in channel_models.items():
            logger.info(f"Simulating {channel_name} channel at {snr} dB...")
            
            # Transmit through the channel and receive the signal
            received_signal = channel_model(coded_bits, snr_db)
            
            # Decode the signal using Polar Code decoding
            Decode(myPC)
            decoded_bits = myPC.message_received
            
            # Calculate BER
            ber = calculate_ber(original_bits, decoded_bits)
            
            # Append BER result for this SNR and channel
            ber_dict[channel_name].append(ber)
            
            # Store the received and decoded signals for later visualization
            if snr == 5:  # Store signals for signal visualization at a specific SNR (5 dB in this case)
                received_signals.append(received_signal)
                decoded_signals.append(decoded_bits)
    
    # Visualize all the results on one page
    visualize_all_in_one_page(original_bits, coded_bits, received_signals, decoded_signals, ber_dict, snr_values, channel_names)

# Run the simulation to generate BER vs SNR and signal plots for all channels
simulate_ber_and_signals_for_all_channels()
