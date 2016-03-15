import numpy as np
import scipy
import scipy.io.wavfile as wav
np.set_printoptions(threshold=np.nan)

instrumentalFile = 'C:\Users\snaik\Desktop\Week10\Backbeat Youtube\pop_tests\let_it_go.wav'
fs, data = wav.read(instrumentalFile)

firstChannel = data[:,0]
rows, cols = np.shape(data)
midFile = rows/2


#aim to find peaks in the file
index = 1
prevSamples = abs(firstChannel[0:2000])
peaks = np.zeros(rows)

dataFile = 'C:\Users\snaik\Desktop\Week10\Backbeat Youtube\Average.txt'
iterator = rows/2000
print "ITERATE: " + str(iterator)

average = np.zeros(iterator)

for i in np.arange(0, iterator):
    average[i] = np.mean(prevSamples)
    prevSamples = abs(firstChannel[2000*i:2000*i+2000])         #this is an absolute avergae
    #prevSamples = abs(firstChannel[i*100:i*100+800])           #this one is if we want a moving average
    
scipy.savetxt(dataFile, average)

#find the max beats
maxBeat = np.amax(average)
tolerance = 500

index = 0
beats = np.array([])
for means in average:
    if means >= (maxBeat - 5000):
        print 'beat!'
        beats = np.append(beats, index)
    index += 1

print beats

#print a very preliminary crude segment
len = np.size(beats)
midpoint = len/2
print midpoint

pointer = beats[midpoint]*2000
start = beats[midpoint-2]*2000-1000
end = beats[midpoint+2]*2000+1000

#pick an ending with the same amplitude as the beginning
minDiff = 0
minBeat = 0
index = 0
for i in beats:
    if i == 0:
        minDiff = average[midpoint-1] - average[i]
    elif i == (midpoint-1):
        continue
    else:
        if (average[midpoint-1] - average[i]) < minDiff:
            minDiff = average[midpoint-1] - average[i]
            minBeat = index
        else:
            continue
    print i
    index += 1
     
pointer = beats[midpoint]*2000
start = beats[midpoint-1]*2000-1000
end = beats[minBeat]*2000+1000
print str(midpoint-1) + " " + str(midpoint) + " " + str(minBeat)
print str(start) + " " + str(end)


instrumentalOut = data[end:start, :]
instrumentalOut = np.vstack((instrumentalOut, instrumentalOut))
print "SHAPE: " + str(np.shape(instrumentalOut))

#Output the wave file
wav.write('FROZENoutfile.wav', fs, instrumentalOut)
