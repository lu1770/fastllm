import threading
import pyaudio
import wave
import requests
import time

CHUNK = 1024 
FORMAT = pyaudio.paInt16 # 16bit编码格式
CHANNELS = 1 
RATE = 44100 # 采样率

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK) 

count = 0
url = 'http://localhost:9000/asr?task=transcribe&language=zh&encode=true&output=txt'
from queue import Queue
from threading import Thread

frame_queue = Queue()
todo_queue = Queue()
# 结果队列
result_queue = Queue() 

# 录音线程
import os

def save_audio(frames):
    filename = f"audio/audio_{int(time.time())}.wav"
    filepath = os.path.join(os.getcwd(), filename)
    
    wf = wave.open(filepath, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return filepath

def record_audio():
    stream = pyaudio.PyAudio().open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
    
    while True:
        startTime = time.time()
        frames = []
        # 开始录音,录5秒
        for _ in range(0, int(RATE / CHUNK * 8)):
            data = stream.read(CHUNK)
            frames.append(data)
        frame_queue.put(frames)
        endTime = time.time()
        print(f'\nPut {len(frames)} frames to queue. Thread Id: {threading.get_ident()}. Queue size: {frame_queue.qsize()}. Spend {endTime - startTime:.2f} seconds.')
        
def run_save_audio():
    while True:
        startTime = time.time()
        frames = frame_queue.get()
        wav_file = save_audio(frames) # 保存wav文件
        # 放到队列中
        todo_queue.put((wav_file, None))
        endTime = time.time()
        print(f'\nPut {wav_file} to queue. Thread Id: {threading.get_ident()}. Queue size: {todo_queue.qsize()}. Spend {endTime - startTime:.2f} seconds.')

        

# 发送请求线程        
def send_request():
    while True:
        startTime = time.time()
        wav_file, text = todo_queue.get()
        with open(wav_file, 'rb') as f:
            response = requests.post(url, files={'audio_file':f})
        text = response.text
        
        # 放回队列,并更新识别文本
        result_queue.put((wav_file, text)) 
        if os.path.exists(wav_file):
            os.remove(wav_file)
        endTime = time.time()
        print(f'\nResult of {wav_file} is {text}. Thread Id: {threading.get_ident()}. Queue size: {result_queue.qsize()}. Spend {endTime - startTime:.2f} seconds.')
        
# 结果处理线程
def get_results():
    while True:
        wav_file, text = result_queue.get()
        
        if text:
            print(text)
        else:
            # print(f"Processing {wav_file}...")
            pass
            
# 开启线程            
record_thread = Thread(target=record_audio) 
request_thread = Thread(target=send_request)
result_thread = Thread(target=get_results)
result_thread = Thread(target=run_save_audio)

record_thread.start()
request_thread.start() 
result_thread.start()