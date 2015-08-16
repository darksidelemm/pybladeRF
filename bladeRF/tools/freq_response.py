# Simple Frequency response measurement application.
# Sweep TX through a range of frequencies, and measure RX power, then plot results.
#
# Mark Jessop <vk5qi@rfhead.net>


import bladeRF
from bladeRF._cffi import ffi
import numpy as np
import matplotlib.pyplot as plt


freq_start = 430e6
freq_stop = 450e6
freq_steps = 100
rx_offset = 0.1e6 # Get away from the RX DC spike.

device = bladeRF.Device()

# Initial setup of TX and RX chains
device.tx.frequency = freq_start
device.tx.bandwidth = 1500000
device.tx.sample_rate = 4000000

device.rx.frequency = freq_start - rx_offset
device.rx.bandwidth = 1500000
device.rx.sample_rate = 4000000
# Probably need to tweak these to get the best linearity
device.rx.vga1 = 20
device.rx.vga2 = 5

num_buffers = 24
num_transfers = 8
num_samples = 2**14
buffer_size = 4*num_samples
timeout_ms = 3500

# At this point both tx and rx timestamp clocks start running.
device.tx.enabled = True
device.rx.enabled = True

device.tx.config(bladeRF.FORMAT_SC16_Q11_META,num_buffers,buffer_size,num_transfers,timeout_ms)
device.rx.config(bladeRF.FORMAT_SC16_Q11_META,num_buffers,buffer_size,num_transfers,timeout_ms)

# Produces an array of samples suitable for transmitting.
# In this case, we transmit a high DC value, to transmit a strong LO carrier.
tx_samples_np = 2047*np.ones((num_samples*2)).astype(np.int16)
tx_samples = ffi.cast("int16_t *",tx_samples_np.ctypes.data)

# Function to do the TXing and RXing
def txrx_burst(freq, samples):
	# Set frequency.
	device.tx.frequency = freq
	device.rx.frequency = freq - rx_offset

	# Setup TX and RX metadata structs.
	metadata_tx = ffi.new("struct bladerf_metadata [1]")
	metadata_tx[0].flags = bladeRF.BLADERF_META_FLAG_TX_BURST_START | bladeRF.BLADERF_META_FLAG_TX_BURST_END

	metadata_rx = ffi.new("struct bladerf_metadata [1]")
	metadata_rx[0].flags = 0

	# Get current timestamp
	current_tx_timestamp = device.tx.timestamp
	current_rx_timestamp = device.rx.timestamp
	print "Timestamps: TX %d, RX %d" % (current_tx_timestamp, current_rx_timestamp)

	# Set scheduled transmit and receive timestamps.
	metadata_tx[0].timestamp = current_tx_timestamp + device.tx.sample_rate/20 # 10ms into the future
	metadata_rx[0].timestamp = current_rx_timestamp + device.tx.sample_rate/20 # 10ms into the future

	# Transmit!
	device.tx(num_samples,samples=tx_samples, metadata=metadata_tx, timeout_ms=timeout_ms)
	rx_samples = device.rx(num_samples, metadata=metadata_rx, timeout_ms = timeout_ms)

	# Wait until all samples have been transmitted.
	while(device.tx.timestamp < metadata_tx[0].timestamp + 2*num_samples):
		pass

	print "RXed %d Samples." % (metadata_rx[0].actual_count)
	return bladeRF.samples_to_narray(rx_samples, metadata_rx[0].actual_count)



freq_range = np.linspace(freq_start,freq_stop,freq_steps)
power = np.zeros(freq_steps)

k = 0
for freq in freq_range:
	print "Current Freq: %d" % (int(freq))
	data = txrx_burst(int(freq),tx_samples)
	# For some reason the last half of the buffer has NaNs???
	data = data[0:len(data)/2]

	# Process data.
	data_fft = 10*np.log10(np.abs(np.fft.fft(data**2.0)))
	# Should really be looking in a particular bandwidth than doing this...
	power[k] = data_fft.max()
	print "Power: %f" % (power[k])
	k = k + 1


# Turn off RX and TX, else we keep on transmitting a carrier.
device.tx.enabled = False
device.rx.enabled = False

# Plot
plt.plot(freq_range/1e6,power-power.max())
plt.xlabel("Frequency (MHz)")
plt.ylabel("Normalised Power (dB)")
plt.show()


