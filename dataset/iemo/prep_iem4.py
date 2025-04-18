#!/usr/bin/env python
# encoding: utf-8

import os
from shutil import copyfile
import glob
import pandas as pd

def create_data_dir(pathData: str, pathDataOrig: str):
    os.makedirs(pathData, exist_ok=True)
    pathAudio = os.path.join(pathData, 'audio/')
    pathImage = os.path.join(pathData, 'image/')
    os.makedirs(pathAudio, exist_ok=True)
    os.makedirs(pathImage, exist_ok = True)

    emotions=['anger', 'happiness', 'neutral', 'sadness']

    for emotion in emotions:
        pathAudioEmotion=pathAudio + emotion
        pathImageEmotion=pathImage + emotion
        os.makedirs(pathAudioEmotion)
        os.makedirs(pathImageEmotion)

    for emotion in emotions:
        print('Emotion: ' + emotion)
        emotionFile=pd.read_csv(emotion[0:3]+'.csv')
        emotionFilenames=emotionFile['filenames']
        for filename_target in emotionFilenames:
            for filename in glob.iglob(pathDataOrig + '/**/' + filename_target + '.wav', recursive=True):
                copyfile(filename, os.path.join(
                    pathAudio + emotion, filename_target + '.wav'))
