
### Dashtron
A simple dashboard to inference tacotron2 models. Build on flask and run on cpu.

## Pre-requisites
1. Tacotron2 Checkpoints. Train by your self from [Nvidia-Tacotron](https://github.com/NVIDIA/tacotron2), or Download from [here](https://drive.google.com/file/d/1c5ZTuT7J08wLUoVZ2KkUs_VdZuJ86ZqA/view?usp=sharing)
2. [Waveglow](https://drive.google.com/open?id=1rpK8CzAAirq9sWZhe9nlfvxMF1dRgFbF) Model. 
3. Save the models to the location that suit to your env. 


## Setup
1. Clone this repo: `git clone https://github.com/lantip/dashtron.git`
2. CD into this repo: `cd dashtron`
3. Install python requirements: `pip install -r requirements.txt`

## Run
1. Copy `env.example` to `.env` and put the right entries.
2. fire `sh start.sh`
3. Open your browser and access `http://localhost:5000`

## Create User
1. Go to `/signup` 
2. Fill the form
3. Submit

## Inference
1. Go to root url
2. Login
3. Fill the form
4. Submit

## See All Result
1. Go to `/all`

### Feature
Indonesian Cleaners included.
