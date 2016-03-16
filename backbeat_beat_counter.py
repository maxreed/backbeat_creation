import numpy as np
import scipy
import scipy.io.wavfile as wav          #Used to read in and write wave files
np.set_printoptions(threshold=np.nan)   #Used to print arrays to text files nicely without elipses

instrumentalFile = 'C:\Users\snaik\Desktop\Week10\Backbeat Youtube\pop_tests\sorry.wav'
fs, data = wav.read(instrumentalFile)
rows, cols = np.shape(data)

firstChannel = data[:,0]                #We only care are about the first channel. 
                                        #The second channel is expected to follow similar patterns


"""We are trying to smoothen the waveform"""
iterator = rows/2000                    #This is equal to how many windows we need to take the average amplitude of
print "ITERATE: " + str(iterator)

dataFile = 'C:\Users\snaik\Desktop\Week10\Backbeat Youtube\Average.txt'         #Text file to save arrays in for logging

average = np.zeros(iterator)            #Array to hold in the average amplitudes of windows

for i in np.arange(0, iterator):
    prevSamples = abs(firstChannel[2000*i:2000*i+2000])         #this is an absolute avergae
    #prevSamples = abs(firstChannel[i*100:i*100+800])           #this one is if we want a moving average
    average[i] = np.mean(prevSamples)
                 
scipy.savetxt(dataFile, average)        #Saves the array to a text file

"""We are trying to find the beats in the waveform (assuming they have the maximum amplitude)"""
maxAmp = np.amax(average)
tolerance = 5000                         #Any window within 500 dB of the maximum amplitude is also a beat

index = 0                               #holds the index of the window containing a beat (index obtained from "average")
beats = np.array([])
for means in average:
    if means >= (maxAmp - tolerance):
        print 'beat!'
        beats = np.append(beats, index)
    index += 1

print beats

"""Find a beat that occurs near the middle of the song. This is so we don't get weird start/end rhythms"""
len = np.size(beats)
midpoint = len/2
midBeat = beats[midpoint]
diffBtwBeats = beats[midpoint] - beats[midpoint-1]

"""This converts beat indices to sample numbers. Then it calculates the start and end of the segments"""
#start = beats[midpoint-2]*2000-1000
#end = beats[midpoint+2]*2000+1000

#pick an ending with the same amplitude as the beginning. BUT THESE ARE BEATS!
minDiff = 0
endBeat = 0
#index = 0
for i in np.arange(average.size):
    if i == 0:
        minDiff = average[midBeat-diffBtwBeats] - average[i]
    elif i == (midBeat-5):
        continue
    else:
        if (average[midBeat-diffBtwBeats] - average[i]) < minDiff:
            minDiff = average[midBeat-diffBtwBeats] - average[i]
            endBeat = i
        else:
            continue
    print i
    #index += 1
    
#pick an ending with the same amplitude as the beginning. BUT THESE ARE NOT BEATS!

     
start = (midBeat-diffBtwBeats)*2000
end = endBeat*2000
#print str(midpoint-1) + " " + str(midpoint) + " " + str(minBeat)
print str(start) + " " + str(end)

if (start < end):
    instrumentalOut = data[start:end, :]
else:
    instrumentalOut = data[end:start, :]
instrumentalOut = np.vstack((instrumentalOut, instrumentalOut))
print "SHAPE: " + str(np.shape(instrumentalOut))

#Output the wave file
wav.write('SORRYoutfile.wav', fs, instrumentalOut)
