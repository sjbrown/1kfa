#! /bin/bash

#ffmpeg -loop 1 -i playtest_may10_2018.jpg -i playtest_may10_2018.wav -c:v libx264 -tune stillimage -strict -2 -c:a aac -b:a 192k -pix_fmt yuv420p -shortest playtest_may10_2018.mp4

ffmpeg -r 1 -loop 1 -i playtest_may10_2018.jpg \
 -i playtest_may10_2018.wav \
 -acodec libvo_aacenc \
 -tune stillimage \
 -r 1 -shortest -vf scale=1280:720 -framerate 1 -vcodec libx264 \
 playtest_may10_2018.avi

 
# @Amit I need to combine a set of images, video clips and an audio track to 
# create a single video file (preferably ogg, but that is less relevant at this
# point). In addition, I need to create some transition effects between 
# adjacent images. Is there any way to script this whole task using ffmpeg 
# and/or other command line tools? The goal is to automate the task and using 
# a command line process

# @Web User - First make individual videos for each image and corresponding
# audio using cmd -
#
# ffmpeg -loop 1 -i <imgName>  -i <audioFileName> -c:v libx264
# -tune stillimage -c:a aac -strict experimental -b:a 192k -pix_fmt yuv420p
# -shortest <videoOutFilename>
#
# Then use following to concatenate all videos to amke a single one..
# ffmpeg -f concat -i <listfilename> -c copy <outputpath>
# where listfilename is a file containng names of all video files
