from numpy import cos, sin, pi, absolute, arange, std, fft, mean, exp, amax, amin, concatenate, ones, zeros, argmax, diff
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

data_file = open('20_sec_time.txt')
raw_data = data_file.readlines()
y = [s for s in raw_data]

_y = [float(y) for y in y]

r = numpy.array(_y)

#ax = 28.29 + exp(0.0005*t)

delay = 472 #800
time_const = 3150 #3150
ideal_unit_decay = exp( (-1*( t )) / (time_const) )

pwr_start = 2
pwr_stop = 122.5
pwr_time_const = 400
unit_exp_pwr = exp( t / pwr_time_const )

ax_decay = ideal_unit_decay
ax_delay_decay = (24 + (48.5 - 24)*ax_decay)[:nsamples] #38.5

#ax_pwr = concatenate( (zeros(nsamples)[:(pwr_start*sample_rate)], 29 + unit_exp_pwr[:(pwr_stop-pwr_start)*sample_rate], ones(nsamples)) )[:nsamples]
#ax_pwr = concatenate( ( 29*ones(nsamples)[:(pwr_start*sample_rate)], (29 + unit_exp_pwr)[:(pwr_stop-pwr_start)*sample_rate], \
        #                    (29+unit_exp_pwr[(pwr_stop-pwr_start)*sample_rate])*ones(nsamples) ) )[:nsamples]
#ax_pwr = concatenate( (29*ones(nsamp0.05*t + 29
ax_pwr = concatenate( ( 29*ones(nsamples)[:(pwr_start*sample_rate)], (0.05*t + 29)[:(pwr_stop-pwr_start)*sample_rate], \
                       (29+(0.05*t)[(pwr_stop-pwr_start)*sample_rate])*ones(nsamples) ) )[:nsamples]
ax = ax_pwr - ax_delay_decay
#ax = 100000 / t



#
#
# FFT of signal
#
#fourier = numpy.fft.rfft(x)
#n = x.size
#time_step = 1/sample_rate
#k = arange(n)
#T = n/sample_rate
#frq = k/T # two sides frequency range
#frq = frq[range(n/2)] # one side frequency range
#fourier = fourier[range(n/2)]
#
#
#------------------------------------------------
# Create a FIR filter and apply it to x.
#------------------------------------------------

# The Nyquist rate of the signal.
nyq_rate = sample_rate / 2.0

# The desired width of the transition from pass to stop,
# relative to the Nyquist rate. (0.2Hz in this case)
width = 0.2/nyq_rate

# The desired attenuation in the stop band, in dB.
ripple_db = 300.0

# Compute the order and Kaiser parameter for the FIR filter.
N, beta = kaiserord(ripple_db, width)

# The cutoff frequency of the filter.
cutoff_hz_1 = 0.0005

# Use firwin with a Kaiser window to create a lowpass FIR filter.
#taps = firwin(N, [cutoff_hz_1/nyq_rate, cuton_hz_2/nyq_rate, cutoff_hz_2/nyq_rate], window=('kaiser', beta))
taps = firwin(N, cutoff_hz_1/nyq_rate, window=('kaiser', beta))

# Use lfilter to filter x with the FIR filter.
filtered_x = lfilter(taps, 1.0, x)

max_index = argmax(filtered_x)



#------------------------------------------------
# Plot the original and filtered signals.
#------------------------------------------------

# The phase delay of the filtered signal.
delay = 0.5 * (N-1) / sample_rate

figure(1)
# Plot the filtered signal, shifted to compensate for the phase delay.
#plot(t-delay, filtered_x, 'r-')

# Plot just the "good" part of the filtered signal.  The first N-1
# samples are "corrupted" by the initial conditions.

plot(t[N:], filtered_x[N:], 'g', linewidth=2)
plot(t, ax_delay_decay, 'y', linewidth=3)

plot(t, ax, 'k', linewidth=2)

#dfs = diff(ideal_unit_decay) / diff(t)

#print dfs

#plot(-1*dfs)
#plot(ideal_unit_decay)
plot(t, x, 'b', linewidth=2)

plot(t, ax_pwr, 'm')

#plot(t, r, 'r')

xlabel('t')
grid(True)

print amin(filtered_x[N-1:])
print amax(filtered_x)
print argmax(filtered_x)/sample_rate

show()

