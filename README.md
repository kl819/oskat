# OSKAT
***Open Source Kamera-Arts Tools***  
A set of command line tools for batch processing photos without opening up a photo-editing application.

### Current Tools (v0.1.2):
**varimat**: adds borders to fit certain aspect ratio.  
**instamat**: adds borders to fit 4:5 aspect ratio, e.g. for Instagram

## Quickstart Guide
### 1. Installation
The simplest way to install `oskat` as a globally-available command-line tool is to use `pipx`. Find the guide [here](https://pipx.pypa.io/stable/installation/).

Once you have `pipx` installed, simply run the following command from your terminal:  
```
pipx install git+https://github.com/kl819/oskat.git
```  

Once `pipx` is done installing, you should receive a message like this:
  ```installed package oskat 0.1.0, installed using Python 3.9.6
  These apps are now globally available
    - oskat
done! ✨ 🌟 ✨
```
You should be able to verify this with `pipx list`, which lists out the apps installed through `pipx`. One of them should be `oskat`. If it shows up on the list, you've successfully installed `oskat`!
  

### 2. Using `oskat`
The easiest way to use `oskat` is to navigate to the folder with the photos you'd like to process. If no path and output is specified on any `oskat` command, it will process all images in the directory in which it is run and output the results to a separate folder. 

#### ex. 1: `instamat`
You've just exported a fresh set of photos from Lightroom, almost ready to post to Instagram but *oh, no*, every photo's a different aspect ratio!

You can use `instamat` to add white borders as needed to make all the images the same (Instagram-optimal) 4:5 aspect ratio!  
First, navigate to the folder with all your photos and open a terminal there (or navigate there via the terminal). Then, just type `oskat instamat` into the terminal. Give it a few seconds, and you should see a message like this:
```
matted 3 images in 0.9s!
```

**All done!** Your Instagram-ready photos will be in a new folder within the folder in which you ran the command.
