from pydub import AudioSegment
import os

import soundfile as sf
import numpy as np
import socket

def compress_audio(input_path, output_path, bitrate="128k"):
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="mp3", bitrate=bitrate)
    
    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)
    
    print(f"Original size: {original_size/1024:.2f} KB")
    print(f"Compressed size: {compressed_size/1024:.2f} KB")
    print(f"Compression ratio: {original_size/compressed_size:.2f}x")
    
    return original_size, compressed_size

def calculate_loss(original_wav, compressed_mp3):
    orig_data, sr1 = sf.read(original_wav)
    
    decoded_wav = "decoded.wav"
    AudioSegment.from_mp3(compressed_mp3).export(decoded_wav, format="wav")
    
    comp_data, sr2 = sf.read(decoded_wav)
    
    min_len = min(len(orig_data), len(comp_data))
    orig_data = orig_data[:min_len]
    comp_data = comp_data[:min_len]
    
    mse = np.mean((orig_data - comp_data) ** 2)
    
    signal_power = np.mean(orig_data ** 2)
    noise_power = np.mean((orig_data - comp_data) ** 2)
    snr = 10 * np.log10(signal_power / noise_power)
    
    print(f"MSE: {mse:.6f}")
    print(f"SNR: {snr:.2f} dB")
    
    return mse, snr


def send_file(file_path, host="127.0.0.1", port=5001):
    s = socket.socket()
    s.connect((host, port))
    
    with open(file_path, "rb") as f:
        while chunk := f.read(1024):
            s.sendall(chunk)
    
    s.close()
    print("File sent successfully")

def receive_file(output_path, host="0.0.0.0", port=5001):
    s = socket.socket()
    s.bind((host, port))
    s.listen(1)
    
    conn, addr = s.accept()
    print("Connected:", addr)
    
    with open(output_path, "wb") as f:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)
    
    conn.close()
    s.close()
    print("File received")

original = "input.wav"
compressed = "compressed.mp3"

compress_audio(original, compressed)
calculate_loss(original, compressed)