import scipy.io.wavfile as wav
import numpy as np
import time

import os

def zeroCrossing(audioData):
    s= np.sign(audioData)  
    s[s==0] = -1     # replace zeros with -1  
    zero_crossings = np.where(np.diff(s))[0]
    return zero_crossings

def loop(audioData):
    zero_crossings = zeroCrossing(audioData)
    return audioData[zero_crossings[0]:zero_crossings[len(zero_crossings)-1]]

def sinebell(lengthWindow):
    """
    window = sinebell(lengthWindow)
    
    Computes a "sinebell" window function of length L=lengthWindow
    
    The formula is:
        window(t) = sin(pi * t / L), t = 0..L-1
    """
    window = np.sin((np.pi * (np.arange(lengthWindow))) \
                    / (1.0 * lengthWindow))
    return window

def stft(data, window=sinebell(2048), hopsize=256.0, nfft=2048.0, \
         fs=44100.0):
    """
    X, F, N = stft(data, window=sinebell(2048), hopsize=1024.0,
                   nfft=2048.0, fs=44100)
                   
    Computes the short time Fourier transform (STFT) of data.
    
    Inputs:
        data                  : one-dimensional time-series to be
                                analyzed
        window=sinebell(2048) : analysis window
        hopsize=1024.0        : hopsize for the analysis
        nfft=2048.0           : number of points for the Fourier
                                computation (the user has to provide an
                                even number)
        fs=44100.0            : sampling rate of the signal
        
    Outputs:
        X                     : STFT of data
        F                     : values of frequencies at each Fourier
                                bins
        N                     : central time at the middle of each
                                analysis window
    """
    
    # window defines the size of the analysis windows
    lengthWindow = window.size
    
    # !!! adding zeros to the beginning of data, such that the first
    # window is centered on the first sample of data
    data = np.concatenate((np.zeros(lengthWindow / 2.0),data))          
    lengthData = data.size
    
    # adding one window for the last frame (same reason as for the
    # first frame)
    numberFrames = np.ceil((lengthData - lengthWindow) / hopsize \
                           + 1) + 1  
    newLengthData = (numberFrames - 1) * hopsize + lengthWindow
    # zero-padding data such that it holds an exact number of frames
    data = np.concatenate((data, np.zeros([newLengthData - lengthData])))
    
    # the output STFT has nfft/2+1 rows. Note that nfft has to be an
    # even number (and a power of 2 for the fft to be fast)
    numberFrequencies = nfft / 2.0 + 1
    
    STFT = np.zeros([numberFrequencies, numberFrames], dtype=complex)
    
    for n in np.arange(numberFrames):
        beginFrame = n * hopsize
        endFrame = beginFrame + lengthWindow
        frameToProcess = window * data[beginFrame:endFrame]
        STFT[:,int(n)] = np.fft.rfft(frameToProcess, int(nfft));
        
    F = np.arange(numberFrequencies) / nfft * fs
    N = np.arange(numberFrames) * hopsize / fs
    
    return STFT, F, N

def makeBackBeat(song, begin): # song is of course the song that one wishes to generate a backbeat for. begin is the second at which to start looking for the backbeat.    
    # read in a song
    fs, data = wav.read(song)
    # typically there are 2 channels in a wav file. we only need one, so average the two channels into one.
    dataMod = np.abs((data[:,0]+data[:,1])/2)
    # find the average aplitude of this modified data.
    average = np.average(dataMod)
    # find the data point at which to begin, given the time 
    firstOcc=fs*begin
    # this bit accounts for the case where there is noise, followed by silence, followed by the actual song.
    for i in np.arange(1,10):
        # if the average amplitude over 1 second is less than 1% of the average amplitude of the song, the 1 second is effectively silence. move the spot where
        # one starts examining the data to after this second of silence.
        if np.average(dataMod[(i+begin)*fs:(i+1+begin)*fs])<(average*0.01):
            firstOcc = i*fs
    # this code will only search for repeatable segments in 25 seconds of the song.
    dataMod = dataMod[firstOcc:25*fs+firstOcc]
    
    # and here is where the FT stuff starts
    X, F, N = stft(dataMod)
    # the FT data will be complex. make it real by squaring each entry. set the minimum entry value to be greater than 0, so that one can take the log of every entry.
    SX = np.maximum(np.abs(X) ** 2, 10**-8)
    # the entries will vary by orders of magnitude. to reduce variation, take the log of every entry.
    SX = np.log(SX)
    # do some normalization stuff (the greatest value in SX will now be 1).
    maxSX = SX.max()
    SX = SX/maxSX
    
    # we can throw out the high frequencies. we can also average every 8 frequency bins into 1.
    a = len(N)/8+1
    SX_smoothed = np.zeros((200, a))
    print SX.shape
    print SX_smoothed.shape
    for i in np.arange(200):
        for j in np.arange(2, len(N)-2, 8):
            SX_smoothed[i,j/8] = sum(SX[i,j-4:j+4])/9
    
    numFrames = SX_smoothed.shape[1]
    # right so this is where useful things happen. this is pretty lazy but for the amount of work required functions really well.
    # essentially, this code goes through the smoothed data and tries to find similar sections. the assumption is that if one finds sections
    # A, B, and C, where B is the region between sections A and C, and A and C are similar, then one can loop (A+B). this is because B flowing into
    # A should sound natural, since B flowing into C sounded natural, and A and C are similar.
    # again, this technique is quite crude, but it yields good results and runs at an acceptable speed.
    # the measure of similarity between A and C (which are regions of equal length) is the sum of the absolute value of the xth element in A minus
    # the xth element in C.
    minDiff = 10**9
    minDiffLoc1 = 0
    minDiffLoc2 = 0
    numCalc = 0
    for i in np.arange(0,numFrames-80, 4):
        toExamine = SX_smoothed[:,i:i+35]
        for j in np.arange(i+45, numFrames-35):
            compareTo = SX_smoothed[:,j:j+35]
            diff = sum(sum(abs(toExamine-compareTo)))
            numCalc += 1
            if diff<minDiff:
                minDiff = diff
                minDiffLoc1 = i
                minDiffLoc2 = j
    print minDiff
    print minDiffLoc1
    print minDiffLoc2
    
    
    # anyway, minDiffLoc1 is the point where region A begins, and minDiffLoc2 is the point where region C begins in the smoothed data.
    # multiply both by 1000 to get the corresponding points in the unedited song data.
    songLoc1 = minDiffLoc1*8*256
    songLoc2 = minDiffLoc2*8*256
    
    # create the segment that should be loopable.
    cut = data[songLoc1+firstOcc:songLoc2+firstOcc, :]
    
    try:
        # reduce the blip one hears when restarting the loop.
        cut = loop(cut)
    except:
        print "i honestly have no idea why this error is happening"
    
    # make the loop run 4 times.
    cut = np.concatenate((cut,cut,cut,cut),axis=0)
    # output the file.
    wav.write("testCutFT_" + song[15:-4] + "_" + str(begin) + ".wav", fs, cut)

songs = os.listdir("all_test_songs")
print songs
for s in songs:
    print s
    for i in [0,40,80]:
        print i
        startPoint = time.clock()
        makeBackBeat("all_test_songs/" + s,i)
        stopPoint = time.clock()
        print (stopPoint-startPoint)
