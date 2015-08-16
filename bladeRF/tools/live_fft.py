#
# PyQtGraph + pybladeRF FFT Test
#
# Mark Jessop <vk5qi@rfhead.net>
#

import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import sys, Queue

# bladeRF Setup 
import bladeRF
device = bladeRF.Device()
device.rx.enabled = True
device.rx.frequency = 440000000
device.rx.bandwidth = 28000000
device.rx.sample_rate = 40000000

num_buffers = 16
num_transfers = 16
num_samples = 2**16
Nf = 512     # No. of frames
Ns = 2048    # Signal length

averaging = 10
averaging_buffer = np.zeros((averaging,num_samples))

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
p1_freq_range = np.linspace(device.rx.frequency-device.rx.sample_rate/2.0,device.rx.frequency+device.rx.sample_rate/2.0,num_samples)


def update():
    global averaging_buffer
    try:
        data = queue.get_nowait()
    except Queue.Empty:
        return
    data_fft = np.fft.fftshift(10*np.log10(np.abs(np.fft.fft(data**2.0))))
    averaging_buffer = np.roll(averaging_buffer,1,axis=0)
    averaging_buffer[0] = data_fft
    p1_data.setData(p1_freq_range,averaging_buffer.mean(axis=0))


def rx(device, stream, meta_data, samples, num_samples, user_data):
    samples = bladeRF.samples_to_narray(samples, num_samples)
    try:
        queue.put_nowait(samples)
    except Queue.Full:
        #print "Buffer Overrun!"
        pass
    return stream.next()

stream = device.rx.stream(
    rx,
    num_buffers,
    bladeRF.FORMAT_SC16_Q11,
    num_samples,
    num_transfers,
)

win = QtGui.QWidget()
win.resize(1200,600)
win.show()
win.setWindowTitle("BladeRF FFT Test")
layout = QtGui.QGridLayout()
win.setLayout(layout)

layout.addWidget(spec_plot,0,0)

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start()
stream.start()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
        stream.running = False
        stream.join()