from numpy import cos, sin, pi, absolute, arange, std, fft, mean, exp, amax, amin, concatenate, ones, zeros
import numpy
from scipy.signal import kaiserord, lfilter, firwin, freqz
from pylab import figure, clf, plot, xlabel, ylabel, xlim, ylim, title, grid, axes, show

#------------------------------------------------
# get data.
#------------------------------------------------

data_file = open('20_sec_temp.txt')
raw_data = data_file.readlines()
y = [s for s in raw_data]

_y = [float(y) for y in y]
_t = [float(t/500) for t in range(0, len(_y)*500, 500)]

t = numpy.array(_t)
x = numpy.array(_y)
sample_rate = 2 #(1/500msec)
nsamples = len(t)

#ax = 28.29 + exp(0.0005*t)


delay = 500
time_const = 10850
ideal_unit_decay = exp( (-1*( t )) / (time_const) )

ax = 40*concatenate((ones(delay*sample_rate), ideal_unit_decay ))[:nsamples]

#
# FFT of signal
#
fourier = numpy.fft.rfft(x)
n = x.size
time_step = 1/sample_rate
k = arange(n)
T = n/sample_rate
frq = k/T # two sides frequency range
frq = frq[range(n/2)] # one side frequency range
fourier = fourier[range(n/2)]

#------------------------------------------------
# Create a FIR filter and apply it to x.
#------------------------------------------------

# The Nyquist rate of the signal.
nyq_rate = sample_rate / 2.0

# The desired width of the transition from pass to stop,
# relative to the Nyquist rate. (0.2Hz in this case)
width = 0.2/nyq_rate

# The desired attenuation in the stop band, in dB.
ripple_db = 120.0

# Compute the order and Kaiser parameter for the FIR filter.
N, beta = kaiserord(ripple_db, width)

# The cutoff frequency of the filter.
cutoff_hz_1 = 0.05

cuton_hz_2 = 6.0
cutoff_hz_2 = 6.5

# Use firwin with a Kaiser window to create a lowpass FIR filter.
#taps = firwin(N, [cutoff_hz_1/nyq_rate, cuton_hz_2/nyq_rate, cutoff_hz_2/nyq_rate], window=('kaiser', beta))
taps = firwin(N, cutoff_hz_1/nyq_rate, window=('kaiser', beta))

# Use lfilter to filter x with the FIR filter.
filtered_x = lfilter(taps, 1.0, x)

#------------------------------------------------
# Plot the FIR filter coefficients.
#------------------------------------------------

#figure(1)
#plot(taps, 'bo-', linewidth=2)
#title('Filter Coefficients (%d taps)' % N)
#grid(True)

#------------------------------------------------
# Plot the magnitude response of the filter.
#------------------------------------------------

#figure(2)
#clf()
#w, h = freqz(taps, worN=8000)
#plot((w/pi)*nyq_rate, absolute(h), linewidth=2)
#xlabel('Frequency (Hz)')
#ylabel('Gain')
#title('Frequency Response')
#ylim(-0.05, 1.05)
#grid(True)

# Upper inset plot.
#ax1 = axes([0.42, 0.6, .45, .25])
#plot((w/pi)*nyq_rate, absolute(h), linewidth=2)
#xlim(0,8.0)
#ylim(0.9985, 1.001)
#grid(True)

# Lower inset plot
#ax2 = axes([0.42, 0.25, .45, .25])
#plot((w/pi)*nyq_rate, absolute(h), linewidth=2)
#xlim(12.0, 20.0)
#ylim(0.0, 0.0025)
#grid(True)

#------------------------------------------------
# Plot the original and filtered signals.
#------------------------------------------------

# The phase delay of the filtered signal.
delay = 0.5 * (N-1) / sample_rate

figure(3)
# Plot the original signal.
#plot(t, x)
# Plot the filtered signal, shifted to compensate for the phase delay.
#plot(t-delay, filtered_x, 'r-')
# Plot just the "good" part of the filtered signal.  The first N-1
# samples are "corrupted" by the initial conditions.
plot(t[N-1:]-delay, filtered_x[N-1:], 'g', linewidth=2)

plot(t, ax, 'y', linewidth=3)

xlabel('t')
grid(True)


show()

