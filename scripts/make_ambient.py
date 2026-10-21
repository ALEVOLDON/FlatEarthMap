import numpy as np
import scipy.io.wavfile as wav
import os

WORKDIR = r"C:\Users\alevo\.gemini\antigravity\scratch\femap_presentation"
MUSIC_PATH = os.path.join(WORKDIR, "ambient_bg.wav")

sr = 44100
total_dur = 400.0 # ~6.6 minutes
total_samples = int(sr * total_dur)

# Chord progression frequencies (Hz):
# Dm9 (D3, A3, C4, E4, F4)
# Bbmaj7 (Bb2, F3, A3, D4, F4)
# Fmaj7 (F2, C3, E3, A3, C4)
# C (C3, G3, B3, E4, G4)
chords = [
    [146.83, 220.0, 261.63, 329.63, 349.23], # Dm9
    [116.54, 174.61, 220.0, 293.66, 349.23], # Bbmaj7
    [87.31, 130.81, 164.81, 220.0, 261.63],  # Fmaj7
    [130.81, 196.0, 246.94, 329.63, 392.0]   # C
]
chord_duration = 16.0 # seconds per chord
n_chords = len(chords)

print("Synthesizing gentle ambient soundtrack...")
t = np.linspace(0, total_dur, total_samples, False)
music = np.zeros(total_samples, dtype=np.float32)

num_bars = int(np.ceil(total_dur / (chord_duration * n_chords)))

for bar in range(num_bars):
    for c_idx, freqs in enumerate(chords):
        t_start = (bar * n_chords + c_idx) * chord_duration
        if t_start >= total_dur:
            break
        t_end = min(total_dur, t_start + chord_duration)
        idx_start = int(t_start * sr)
        idx_end = int(t_end * sr)
        seg_len = idx_end - idx_start
        if seg_len <= 0:
            continue
        
        seg_t = np.linspace(0, (t_end - t_start), seg_len, False)
        # Smooth envelope (fade in 3s, fade out 3s)
        fade_len = int(min(seg_len // 2, sr * 3.0))
        env = np.ones(seg_len, dtype=np.float32)
        if fade_len > 0:
            env[:fade_len] = np.sin(np.linspace(0, np.pi/2, fade_len))**2
            env[-fade_len:] = np.cos(np.linspace(0, np.pi/2, fade_len))**2
            
        chord_signal = np.zeros(seg_len, dtype=np.float32)
        for f in freqs:
            # Main tone + slight detune for lush analog pad texture
            chord_signal += np.sin(2 * np.pi * f * seg_t) * 0.3
            chord_signal += np.sin(2 * np.pi * (f * 1.002) * seg_t) * 0.15
            chord_signal += np.sin(2 * np.pi * (f * 0.998) * seg_t) * 0.15
            # Sub octave
            chord_signal += np.sin(2 * np.pi * (f * 0.5) * seg_t) * 0.1
            
        music[idx_start:idx_end] += chord_signal * env * 0.25

# Gentle low pass filter (simple moving average)
print("Applying soft filter...")
window_size = 15
kernel = np.ones(window_size) / window_size
music = np.convolve(music, kernel, mode='same')

# Normalize to -18 dB
max_val = np.max(np.abs(music))
if max_val > 0:
    music = (music / max_val) * 0.15 # quiet background level

wav.write(MUSIC_PATH, sr, (music * 32767).astype(np.int16))
print(f"Ambient music generated: {MUSIC_PATH} ({os.path.getsize(MUSIC_PATH)/1024/1024:.2f} MB)")
