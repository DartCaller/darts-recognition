![](https://img.shields.io/github/license/DartCaller/darts-recognition)
![](https://img.shields.io/tokei/lines/github/DartCaller/darts-recognition)

# Darts Recognition
This repository contains the dart detection python server + scripts that are used on Raspberry Pis to take the images of the dartboard.
The calculated score is then sent to webserver https://github.com/DartCaller/api which will then sent it the the frontend https://github.com/DartCaller/web to display the score.


# Table of Contents
- [:package:Tech Stack](#package)  
- [:computer: Running Locally](#computer)
  - [:straight_ruler: Prerequisits](#straight_ruler)
  - [:gear: Setup](#gear)
  - [:running: Run](#running)
- [:bulb: How it works](#how)
- [:bug: Testing](#bug)
- [:lock_with_ink_pen: License](#lock_with_ink_pen)

<a name="package"/>

## :package: Tech Stack
- [Scipy](https://www.scipy.org/)
- [Numpy](https://numpy.org/)
- [Matplotlib](https://matplotlib.org/)
- [Cython](https://cython.org/)
- [Requests](https://docs.python-requests.org/en/master/)
- [OpenCV](https://docs.opencv.org/master/)

<a name="computer"/>

## :computer: Running Locally
<a name="straight_ruler"/>

### :straight_ruler: Prerequisits

This project currently runs on python `v3.6.0`
If you have a different python version it might also build but it's not tested. In any case, it has to be Python 3.

After that you can install the dependencies
```bash
# install dependencies
$ pip install -r requirements.txt
```

<a name="gear"/>

### :gear: Setup
This project needs a lot of setup if you want to run it yourself, since you have to setup the image taking raspberry pi's just like I did.
So let's get to it.

My Setup currently features one Raspberry Pi 3 Model B, one Raspberry Pi Zero with wifi (although wifi is optional on this one) and 1 camera for each of them.
Now I setup OTG on the raspberry pi zero which basically means, when I connect the pi zero only via USB-MicroUSB cable to the pi 3, then through the power of OTG the pi zero not only gets enough power over the calbe to startup, but also lets me ssh onto the pi zero from the pi 3. It's basically a master-slave structure where I now can control and synchronize the picture taking on both these raspberry pi's via SSH. A detailed description on how to setup OTG is available here https://gist.github.com/gbaman/50b6cca61dd1c3f88f41. An article on what OTG is here https://en.wikipedia.org/wiki/USB_On-The-Go

Now, if you have the cameras attached and working on both raspberry pi's and you can ssh into the pi 3 via its wifi address and then also ssh from the pi 3 onto the pi zero, you have the first and biggest step complete. Now you can put the https://github.com/DartCaller/darts-recognition/blob/main/scripts/doubleStream.py script onto the pi 3 under `home/pi/Desktop` (or alternatively adjust this line here https://github.com/DartCaller/darts-recognition/blob/97b86ac7a6459824cf5b69dd4fcd11db911b76d5/core/server.py#L27 to wherever you put the script) and the put https://github.com/DartCaller/darts-recognition/blob/97b86ac7a6459824cf5b69dd4fcd11db911b76d5/scripts/doubleStreamRemote.py script onto the pi zero under `home/pi/Desktop` (or, again, alternatively edit this line https://github.com/DartCaller/darts-recognition/blob/6ab3dcb2b3d0fe60e5a9cc4af8722c3289090643/scripts/doubleStream.py#L14)

Now make sure that you can ssh into the raspi 3 without specifying a password by creating an `~/.ssh/config` file for it and that this var here https://github.com/DartCaller/darts-recognition/blob/97b86ac7a6459824cf5b69dd4fcd11db911b76d5/core/server.py#L17 represents your host name that is specified inside the `~/.ssh/config` file. 

And that's it. Now you should be ready to fire up the server and receive and process images of the dartboard. Have fun!

<a name="running"/>

### :running: Run

```bash
# start both image taking scripts on the raspberry pi's and start the server to receive their images and process the results
$ python core/server.py
```

<a name="how"/>

## :bulb: How it works
This chapter is about how I find the darts and then calculate the darts position from it.
And it's rather simple.

My approach works by taking 4 images in order to calculate the thrown score. One x and one y axis image shortly before the dart was thrown and one x and one y axis image shortly after the dart was thrown. This way I can directly compare the before and after image and the difference between the images should be only the dart.

I wrote https://github.com/DartCaller/darts-recognition/blob/main/core/helper_functions/binary_diff_images.pyx a cython implementation where I specify a certain threshold and if the each of the rgb values between the pixel in the before image and pixel in the after image exceeds the threshold than I'll mark that pixel white, otherwise black. This way I end up with a binary image of the dart that has been added between the two frames. 

At least that is the perfect case scenario. In reality I remove noise from the diff image with the binary morphological opening operator ([link](https://scikit-image.org/docs/dev/auto_examples/applications/plot_morphology.html) for explanation). After that I often still have multiple patches of white pixels in my image so I calculate the size of each patch and choose the biggest patch since this diff patch is most likely to be caused by a dart.
After I have the biggest patch, I'll take the bottom most 20 pixels of that patch since I want to know where the location of the dart as close to the dartboard's surface as possible. I'll calculate the center of mass on the bottom most pixel and voila, I now know the pixel location of the centre of the dart.

Through calibration images that got processed at the start of the server, I know which pixel coordinates the centre of the dart board has and how many pixels equal one millimeter. Now I can calculate the position of the dart relative to the centre of the dartboard. After that I'll convert the pixel distance into millimeter and then calculate in which field on the dartboard the dart has landed.

And that's already it. A bit more logic on how to handle the contant stream of images, because sometimes a dart appears first on one axis and needs one more frame to appear on the second image. Or to handle the case when you have the hands in image to take the darts out. Then a bit of memoization when calculating the diff of two images, so that we have better performance when processing nearly 1 image per second.

And done is my dart-recognition server in python. Have fun with it :heart:

<a name="bug"/>

## :bug: Testing

```bash
# run linter
$ cd core && pytest -n auto
```
This repo currently uses parameterized integration tests to work through all the labeled images in https://github.com/DartCaller/darts-recognition/tree/main/labeled_images and tests if it's calculations match with the manually created label on the image.

In order to create labeled images more easily I created a second mode that the server can run in. We have the `standard mode` where the server extracts the dart position on the incoming images and I have created the `label mode` where after each image you are asked in the terminal to enter a label for the received image. 

```bash
# start the server in label mode
$ python core/server.py --label-mode
```
<a name="lock_with_ink_pen"/>

## :lock_with_ink_pen: License
Distributed under the GNU GPLv3 License. See [LICENSE](LICENSE) for more information.
