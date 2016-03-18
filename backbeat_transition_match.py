import scipy.io.wavfile as wav
import numpy as np

# read in a song
fs, data = wav.read("pop_tests/cake_by_the_ocean.wav")
print data.shape
# typically there are 2 channels in a wav file. we only need one, so average the two channels into one.
dataMod = np.abs((data[:,0]+data[:,1])/2)
# this code will only search for repeatable segments in the first 25 seconds of the song.
dataMod = dataMod[6*fs:31*fs]
print dataMod.shape
# every 1001 entries in dataMod will be averaged to a single value, which will be stored in newData.
newData = np.zeros(len(dataMod)/1000)
for i in np.arange(500, len(dataMod)-501, 1000):
    newData[i/1000] = sum(dataMod[i-500:i+500])/1001

# yeah i just wanted to keep track of how many entries are in newData.
numEnts = len(newData)
print numEnts
# i then proceed to smooth out the data in newData even more, because i can. this might be unnecessary.
smoothData = np.zeros(numEnts)
for k in np.arange(2,numEnts-2):
    smoothData[k] = (sum(newData[k-2:k+2]))/5

# graph the smoothData because visualizing stuff is good and gives you an idea of where a which sections would be good to repeat.
import matplotlib.pyplot as plt
plt.plot(smoothData)
plt.show()

# right so this is where useful things happen. this is pretty lazy but for the amount of work required functions pleasantly well.
# essentially, this code goes through the smoothed data and tries to find similar section. the assumption is that if one finds sections
# A, B, and C, where B is the region between sections A and C, and A and C are similar, then one can loop (A+B). this is because B flowing into
# A should sound natural, since B flowing into C sounded natural, and A and C are similar.
# again, this technique is quite crude, but it yields okay results and runs at an acceptable speed.
# the measure of similarity between A and C (which are regions of equal length) is the sum of the absolute value of the xth element in A minus
# the xth element in C.
# crude, but for now functional. might be worth further looking into the similarity metric if there is time later.
minDiff = 10**9
minDiffLoc1 = 0
minDiffLoc2 = 0
for i in np.arange(0,numEnts-200):
    toExamine = newData[i:i+75]
    for j in np.arange(i+125, numEnts-75):
        compareTo = newData[j:j+75]
        diff = sum(abs(toExamine-compareTo))
        if diff<minDiff:
            minDiff = diff
            minDiffLoc1 = i
            minDiffLoc2 = j
print minDiff
print minDiffLoc1
print minDiffLoc2

# anyway, minDiffLoc1 is the point where region A begins, and minDiffLoc2 is the point where region C begins in the smoothed data.
# multiply both by 1000 to get the corresponding points in the unedited song data.
songLoc1 = minDiffLoc1*1000 + 6*fs
songLoc2 = minDiffLoc2*1000 + 6*fs
# create the segment that should be loopable.
cut = data[songLoc1:songLoc2, :]
# make the loop run 4 times.
cut = np.concatenate((cut,cut,cut,cut),axis=0)
print cut.shape
# output the file.
wav.write("testCut.wav", fs, cut)
