#
# PyQtGraph + pybladeRF FFT Test
# This version attempt to use the synchronous bladeRF interface.
#
# Mark Jessop <vk5qi@rfhead.net>
#

import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import sys, Queue

# bladeRF Setup 
import bladeRF
from bladeRF._cffi import ffi
device = bladeRF.Device()

device.rx.frequency = 440000000
device.rx.bandwidth = 2800000
device.rx.sample_rate = 4000000

num_buffers = 16
num_transfers = 8
buffer_size = 2**16
nFFT = buffer_size/2
timeout_ms = 3500
Nf = 512     # No. of frames
Ns = 2048    # Signal length

averaging = 100
averaging_buffer = np.zeros((averaging,nFFT))


queue = Queue.Queue(num_buffers)

# PyQtGraph Setup Stuff
app = QtGui.QApplication([])

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

# Graph Area
spec_plot = pg.GraphicsLayoutWidget()
# Spectrum Plot
p1 = spec_plot.addPlot()
p1.showGrid(x=True, y=True)
p1.setLabel('bottom',"Frequency (Hz)")
p1.setLabel('left',"Power (dBFS)")
p1_data = p1.plot([0])
p1_freq_range = np.linspace(device.rx.frequency-device.rx.sample_rate/2.0,device.rx.frequency+device.rx.sample_rate/2.0,nFFT)


metadata = ffi.new("struct bladerf_metadata [1]")
metadata[0].flags = bladeRF.BLADERF_META_FLAG_RX_NOW

def update():
    global metadata, averaging_buffer
    samples = device.rx(buffer_size, metadata=metadata, timeout_ms = timeout_ms)
    num_samples = metadata[0].actual_count
    metadata[0].timestamp = 0
    data = bladeRF.samples_to_narray(samples, num_samples)
    data = data[:nFFT]
    try:
        # For some reason we seem to get a lot of NaNs in our received sample data.
        # This is a bit of a hack to avoid allowing any NaN values into our averaging array.
        data_fft = np.fft.fftshift(10*np.log10(np.abs(np.fft.fft(data**2.0))))
        if(not np.isnan(data_fft).any()):
            averaging_buffer = np.roll(averaging_buffer,1,axis=0)
            averaging_buffer[0] = data_fft
            p1_data.setData(p1_freq_range,averaging_buffer.mean(axis=0))
    except:
        pass


win = QtGui.QWidget()
win.resize(1200,600)
win.show()
win.setWindowTitle("BladeRF FFT Test")
layout = QtGui.QGridLayout()
win.setLayout(layout)

layout.addWidget(spec_plot,0,0)

timer = QtCore.QTimer()
timer.timeout.connect(update)

# Configure and start BladeRF RXing
device.rx.config(bladeRF.FORMAT_SC16_Q11_META,num_buffers,buffer_size,num_transfers,timeout_ms)


device.rx.enabled = True

timer.start()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
