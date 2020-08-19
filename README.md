# KG-video

## Introduction

This a project aimed at generating Knowledge Graph from video files. In general, it can be splitted into three parts: Speech Recognition, Face Recognition and Object Detection.

For Speech Recoginition, we use the demo from IFLYTEK Open Platform which depends on Bi-FSMN model. For Face Recoginition task, we use the face location techniques from GitHub project Face Recognition and IFLYTEK Open Platform. And for object detction, we choose to call TensorFlow Object Detection API.

## File Description

/face --- Storing exsiting face files and personal profiles

/font --- Storing Chinese font

/img --- Storing face files cacthed from video

addMusic.py --- Add mp3 file to the final output

demo.py --- Face recoginition API from IFLYTEK Open Platform

facial.py --- Extract faces from the video and make the comparison

vocal.py --- Compare voice files using IFLYTECK Open Platform demo

 
