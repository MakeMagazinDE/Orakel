import time
import board
import os
import sys
import subprocess
LED_WiFi = ['sudo', 'python3', '/home/pi/Desktop/Glaskugel/LED_WiFi.py']
LED_Idle = ['sudo', 'python3', '/home/hpi/Desktop/Glaskugel/LED_Idle.py']
LED_Orakel_Start = ['sudo', 'python3', '/home/pi/Desktop/Glaskugel/LED_Orakel_Start.py']
LED_Off = ['sudo', 'python3', '/home/pi/Desktop/Glaskugel/LED_Off.py']

import vlc
import pygame
pygame.mixer.init()

import openai
from openai import OpenAI
import json
import requests

import sounddevice as sd
import wave

# Input Parameter
openai.api_key = "HIER OPENAI API KEY EINTRAGEN"
ChatGPT_API = 'Bearer ' + openai.api_key
keyword_paths = ['/home/pi/Desktop/Glaskugel/Orakel_de_raspberry-pi_v3_0_0.ppn']
wake_word_access_key='HIER PICOVOICE API KEY EINGEBEN'
Wake_Word_Detection_path = '/home/pi/Desktop/Glaskugel/Wake_Word_Detection.wav'
model_path= '/home/pi/Desktop/Glaskugel/porcupine_params_de.pv'
filename = '/home/pi/Desktop/Glaskugel/downloaded_video.mp4'
Aufnahmedauer = 7
wav_Input = '/home/pi/Desktop/Glaskugel/input.wav'
Abspieldauer = 10
pexels_header = {
  'Authorization': 'HIER PEXELS API KEY EINGEBEN',
  'Cookie': '__cf_bm=Mb4qE1vTAlDuXj1ilgRK9KtApYix5sKsXtajf23.upg-1703869334-1-AaOnms2lErNlJKVDtiHo5JZhATyHkkgTeur5rJdMhoAGayjJMiEUYzT83l7ewzotHsCiCGfc4JIPLR37Pf3eDW4='
}


def download_video(url, filename):
    response = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

def Dialogschleife():
    Dialog = True
    
    process_LED_Orakel_Start = subprocess.Popen(LED_Orakel_Start)
    
    while Dialog:
        def record_audio(file_path, threshold=0.01, sample_rate=44100, channels=1, duration=Aufnahmedauer):
            ###############################################################################################################
            # Spracheingabe
            print("Recording...")
            audio_data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=channels, dtype='int16')
            sd.wait()
            print("Recording finished.")
            # Spracheingabe als WAV Datei speichern
            with wave.open(file_path, 'wb') as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)  # 2 bytes for 16-bit audio (int16)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data.tobytes())
                
        if __name__ == "__main__":
            record_audio(wav_Input)               
        print("Audio saved as WAV:", wav_Input)
        print()

        audio_file= open(wav_Input, "rb")

        input_txt = openai.audio.translations.create(
            model="whisper-1", 
            file=audio_file, 
            response_format="text"
        )
        print("Translate completed:")

        print(input_txt)
        
        if 'Orakel' in input_txt or 'orakel' in input_txt or'Oracle' in input_txt or'oracle' in input_txt:
            print('Orakel beenden')
            process_LED_Orakel_Start.terminate()
            process_LED_Off = subprocess.Popen(LED_Off)
            from subprocess import call
            call("sudo shutdown -h now", shell=True)
            #subprocess.call(['pm2', 'stop 0'])
            #sys.exit()

        Dialog_Gesamt = [{'role': 'system', 'content': "You are an AI agent given the sole task of summarizing an audio transcript to keywords that can be used for a seach field. \
                        The transcript can either be of poor or good quality. The transcript generated from the audio file is given below. \
                        If the transcript is of poor quality or some words have been poorly transcribed, make sure to guess what the word is supposed to be \
                        and return all the important information from the transcript in exactly 2 english nouns.\
                        If you do not understand anything at all, just generate 2 english nouns. IMPORTANT: No explanation needed, only the two nouns and nothing else."}]
                        #If the text contains 'Orakel beenden', 'Tschuess Orakel', or similar then the two keywords are 'Orakel' and 'beenden'."}]
        Dialog_Gesamt.append({'role': 'user', 'content': input_txt})

        # ChatGPT Anfrage senden
        url = "https://api.openai.com/v1/chat/completions?messages=<array>&max_tokens=<integer>&model=<string>"

        payload = json.dumps({
          "messages": Dialog_Gesamt,
          "temperature": 0.7,
          "max_tokens": 300,
          "model": "gpt-3.5-turbo"
        })
        headers = {
          'Content-Type': 'application/json',
          'Authorization': ChatGPT_API
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        json_string = response.json()
        response_json = json_string['choices'][0]['message']['content']
        Antwort = response_json

        print(Antwort)       
        Dialog = False
                    
        url = "https://api.pexels.com/videos/search?query=" + Antwort + "&per_page=1&type=videos"

        payload = {}
        headers = pexels_header

        response = requests.request("GET", url, headers=headers, data=payload)

        print("response.text: ")
        print(response.text)

        json_string = response.json()
        
        counter = 0
        response_json_width = json_string['videos'][0]['video_files'][counter]['width']
        print("Width: " + str(response_json_width))
        while response_json_width > 1920:
            counter += 1
            response_json_width = json_string['videos'][0]['video_files'][counter]['width']
            print("Width: " + str(response_json_width))
        response_json_quality = json_string['videos'][0]['video_files'][counter]['quality']
        response_json_video = json_string['videos'][0]['video_files'][counter]['link']
        response_json_width = json_string['videos'][0]['video_files'][counter]['width']
        response_json_height = json_string['videos'][0]['video_files'][counter]['height']
        print("Selected Quality: " + response_json_quality)
        print("Link: " + response_json_video)
        print("Width: ", response_json_width)
        print("Height: ", response_json_height)        

        download_video(response_json_video, filename)
        print("Video downloaded successfully!")
        
        process_LED_Orakel_Start.terminate()
        Dialog_Gesamt = ""
        
        Instance = vlc.Instance('--input-repeat=9 --width 1920 --height 1080')
        #Instance = vlc.Instance('--input-repeat=9 --fullscreen')
        VLC_player = Instance.media_player_new()
        Media_1 = Instance.media_new(filename)
	# Hier wird das Video rangezoomt
        Weite = 1920 / (response_json_width+100)
        VLC_player.video_set_scale(Weite)
        VLC_player.toggle_fullscreen()
        VLC_player.set_media(Media_1)
        VLC_player.play()
        vid_len = 0
        while vid_len < Abspieldauer:
            time.sleep(1)
            vid_len += 1
        VLC_player.stop()
        VLC_player.release()

# Wake Word Detection ########################################################
def main():
       
    from datetime import datetime
    import struct
    from pvrecorder import PvRecorder
    import pvporcupine
    import tempfile

    from dotenv import load_dotenv
    load_dotenv()

    try:
        porcupine = pvporcupine.create(
            access_key=wake_word_access_key,
            keyword_paths=keyword_paths,
            model_path=model_path
        )
    except pvporcupine.PorcupineActivationError as e:
        print("AccessKey activation error")
        raise e
    except pvporcupine.PorcupineError as e:
        print("Failed to initialize Porcupine")
        raise e

    keywords = list()
    for x in keyword_paths:
        keyword_phrase_part = os.path.basename(x).replace('.ppn', '').split('_')
        print(keyword_phrase_part)
        if len(keyword_phrase_part) > 6:
            keywords.append(' '.join(keyword_phrase_part[0:-6]))
        else:
            keywords.append(keyword_phrase_part[0])

        print('Porcupine version: %s' % porcupine.version)

        recorder = PvRecorder(
            frame_length=porcupine.frame_length,
            device_index=-1)
        recorder.start()

        wav_file = None
        wav_file = wave.open(Wake_Word_Detection_path, "w")
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)

        print('Listening ... (press Ctrl+C to exit)')
        
        try:
            startup = 0
            while True:
                pcm = recorder.read()
                result = porcupine.process(pcm)

                if wav_file is not None:
                    wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))
                    if startup == 0:                        
                        while True:
                            process_LED_WiFi = subprocess.Popen(LED_WiFi)
                            time.sleep(1)
                            ps = subprocess.Popen(['iwgetid'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            try:
                                output = subprocess.check_output(('grep', 'ESSID'), stdin=ps.stdout)
                                print(output)
                                print("Connected")
                                process_LED_WiFi.terminate()
                                break  # Exit the loop when connection is established
                            except subprocess.CalledProcessError:
                                # grep did not match any lines
                                print("No wireless networks connected")
                                time.sleep(1)                    
                        
                        process_LED_Idle = subprocess.Popen(LED_Idle)
                        startup = 1
                        #print("Warten auf Wake Word ...")

                if result >= 0:
                    print('[%s] Detected %s' % (str(datetime.now()), keywords[result]))
                    process_LED_Idle.terminate()
                    startup = 0
                    Dialogschleife()

        except KeyboardInterrupt:
            print('Stopping ...')
        finally:
            recorder.delete()
            porcupine.delete()
            if wav_file is not None:
                wav_file.close()

if __name__ == '__main__':
    main()



