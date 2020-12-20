#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
__version__     =   "0.0.1"
__author__      =   "@lantip"
__date__        =   "2020/12/19"
__description__ =   "Sound Inferences"
"""

import os, json
from flask import Blueprint, redirect, render_template, url_for, request, jsonify, current_app
from flask_login import current_user, login_required, logout_user
from .forms import SettingForm
from .models import Setting, db
from hashids import Hashids

import numpy as np
import torch

from tacotron.hparams import create_hparams
from tacotron.model import Tacotron2
from tacotron.layers import TacotronSTFT, STFT
from tacotron.audio_processing import griffin_lim
from tacotron.train import load_model
from tacotron.text import text_to_sequence
from tacotron.denoiser import Denoiser
from scipy.io import wavfile
from datetime import datetime

# Blueprint Configuration
main_bp = Blueprint(
    'main_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@main_bp.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = SettingForm()
    checkpoints = [f for f in os.listdir(current_app.config['CHECKPOINT_PATH']) if os.path.isfile(os.path.join(current_app.config['CHECKPOINT_PATH'], f))]
    form.checkpoint.choices = [(chk, chk) for chk in checkpoints]
    if form.validate_on_submit():
        existing_data = Setting.query.filter_by(checkpoint=form.checkpoint.data, sigma=form.sigma.data, text=form.text.data ).first()
        if existing_data is None:
            data = Setting(
                checkpoint=form.checkpoint.data,
                sigma=form.sigma.data,
                text=form.text.data,
                created_on=datetime.now()
            )
            db.session.add(data)
            db.session.commit()  
            hsd = Hashids(salt=current_app.config['SALT'], min_length=12)
            idor = hsd.encode(data.id)
            return redirect(url_for('main_bp.result', text=idor, checkpoint=form.checkpoint.data, sigma=form.sigma.data))
        flash('A user already exists with that email address.')
    return render_template(
        'dashboard.jinja2',
        title='Suara Tante',
        form=form,
        template='dashboard-template',
        current_user=current_user,
        body="You are now logged in!"
    )

def process_text(text, txtcleaner, model, hparams, waveglow):
    text_length =  len(text_to_sequence(text, txtcleaner))
    laudio = []
    if len(text.split(". ")) > 1:
        n = 10
        texts = text.split(". ")
        audios = None
        for idx,text in enumerate(texts):
            if idx < len(texts):
                text = text+'.'
            sequence = np.array(text_to_sequence(text, txtcleaner))[None, :]
            sequence = torch.autograd.Variable(
            torch.from_numpy(sequence)).long()
            mel_outputs, mel_outputs_postnet, _, alignments = model.inference(sequence)
            with torch.no_grad():
                audio = waveglow.infer(mel_outputs_postnet, sigma=0.7)
                laudio.append(audio)
                if not isinstance(audios,np.ndarray):
                    audios = audio[0].data.cpu().numpy()
                else:
                    audios = np.concatenate((audios, audio[0].data.cpu().numpy()))
    else:
        sequence = np.array(text_to_sequence(text, txtcleaner))[None, :]
        sequence = torch.autograd.Variable(
            torch.from_numpy(sequence)).long()
        mel_outputs, mel_outputs_postnet, _, alignments = model.inference(sequence)
        with torch.no_grad():
            audio = waveglow.infer(mel_outputs_postnet, sigma=0.7)
            laudio.append(audio)
        audios = audio[0].data.cpu().numpy()
    return audios, laudio

@main_bp.route('/result/<checkpoint>/<sigma>/<text>', methods=['GET'])
@login_required
def result(checkpoint, sigma, text):
    try:
        hsd = Hashids(salt=current_app.config['SALT'], min_length=12)
        idor = text
        idori = hsd.decode(text)[0]
    except:
        idori = None
    if idori:
        existing_data = Setting.query.filter_by(id=idori).first()
        text = existing_data.text
    else:
        existing_data = Setting.query.filter_by(checkpoint=checkpoint, sigma=float(sigma), text=text).first()
        if existing_data is None:
            existing_data = Setting(
                checkpoint=checkpoint,
                sigma=float(sigma),
                text=text,
                created_on=datetime.now()
            )
            db.session.add(existing_data)
            db.session.commit()  
            hsd = Hashids(salt=current_app.config['SALT'], min_length=12)
            idor = hsd.encode(existing_data.id)
        else:
            hsd = Hashids(salt=current_app.config['SALT'], min_length=12)
            idor = hsd.encode(existing_data.id)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    wavs = BASE_DIR + '/apps/static/media/'+str(idor)+'.wav'

    if not os.path.isfile(wavs):
        hparams = create_hparams()
        hparams.sampling_rate=44100
        hparams.fp16_run = False
        hparams.max_decoder_steps = 2000

        model = load_model(hparams)
        model.load_state_dict(torch.load(current_app.config['CHECKPOINT_PATH']+checkpoint, map_location=torch.device('cpu'))['state_dict'])
        waveglow = torch.load(current_app.config['WAVEGLOW_PATH']+'waveglow_gdrive.pt')['model']
        for k in waveglow.convinv:
            k.float()

        from datetime import datetime
        text = text.replace('(','').replace(')','').replace('-',' ')
        audios, laudio = process_text(text, ['indonesian_cleaners'], model, hparams, waveglow)
        
        wavfile.write(wavs, 22050, audios)

    return render_template(
        'result.jinja2',
        current_user=current_user,
        title='Suara Tante - Hasil',
        template='result-template',
        file='media/'+str(idor)+'.wav',
        checkpoint=checkpoint,
        tanggal=existing_data.created_on,
        sigma=sigma,
        text=text
    )


@main_bp.route('/all', methods=['GET'])
@login_required
def allresult():
    existing_data = Setting.query.all()
    result = []
    for data in existing_data:
        hsd = Hashids(salt=current_app.config['SALT'], min_length=12)
        idor = hsd.encode(data.id)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        wavs = BASE_DIR + '/apps/static/media/'+str(idor)+'.wav'
        if os.path.isfile(wavs):
            result.append({
                'checkpoint': data.checkpoint,
                'sigma': data.sigma,
                'text': data.text,
                'tanggal': data.created_on,
                'file':  'media/'+str(idor)+'.wav'
                })

    return render_template(
        'all.jinja2',
        current_user=current_user,
        title='Suara Tante - Hasil All',
        template='all-template',
        result=result
    )


@main_bp.route("/logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect(url_for('auth_bp.login'))
