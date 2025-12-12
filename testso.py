def sonify(data_list, duration, ptm=False, vol=0.5, file=False):
	"""
	sonify V7.0 - 23 marzo 2025 - Gabriele Battaglia eChatGPT O1
	Sonifies a list of float data.
	Parameters:
	  data_list: List of float (5 <= len <= 500000)
	  duration: Total duration in seconds (e.g., 2.58)
	  ptm: If True, applies glissando (continuous portamento)
	  vol: Volume factor (0.1 <= vol <= 1.0)
	  file: If True, saves the audio to sonification[datetime].wav
	Returns immediately (non-blocking playback).
	"""
	import numpy as np
	import sounddevice as sd
	import wave
	n = len(data_list)
	if n < 5 or n > 500000:
		print("sonify: data_list length out of range")
		return
	try:
		data_list = [float(v) for v in data_list]
	except ValueError:
		return
	vol = max(0.1, min(vol, 1.0))
	data_min = min(data_list)
	data_max = max(data_list)
	freq_min = 65.41
	freq_max = 4186.01
	if data_max - data_min == 0:
		frequencies = [(freq_min+freq_max)/2]*n
	else:
		frequencies = [freq_min+(v-data_min)*(freq_max-freq_min)/(data_max-data_min) for v in data_list]
	sample_rate = 44100
	total_samples = int(duration*sample_rate)
	if total_samples <= 0:
		return
	t = np.linspace(0, duration, total_samples, endpoint=False)
	if ptm:
		segment_times = np.linspace(0, duration, n, endpoint=True)
		freq_array = np.interp(t, segment_times, frequencies, left=frequencies[0], right=frequencies[-1])
	else:
		indices = np.floor(np.linspace(0, n, total_samples, endpoint=False)).astype(int)
		freq_array = np.array(frequencies)[indices]
	phase = 2.0*np.pi*np.cumsum(freq_array/sample_rate)
	audio_signal = np.sin(phase)*vol
	fade_duration_sec = 0.002
	fade_samples = int(round(fade_duration_sec*sample_rate))
	fade_samples = min(fade_samples, total_samples//2)
	fade_in = np.linspace(0, 1, fade_samples)
	fade_out = np.linspace(1, 0, fade_samples)
	audio_signal[:fade_samples] *= fade_in
	audio_signal[-fade_samples:] *= fade_out
	pan = np.linspace(-1.0, 1.0, total_samples)
	left = audio_signal*((1.0-pan)/2.0)
	right = audio_signal*((1.0+pan)/2.0)
	audio_stereo = np.column_stack((left, right))
	audio_stereo_int16 = (audio_stereo*32767).astype(np.int16)
	sd.play(audio_stereo_int16, sample_rate)
	if file:
		from datetime import datetime
		filename = "sonification" + datetime.now().strftime("%Y%m%d%H%M%S") + ".wav"
		with wave.open(filename, 'wb') as wf:
			wf.setnchannels(2)
			wf.setsampwidth(2)
			wf.setframerate(sample_rate)
			wf.writeframes(audio_stereo_int16.tobytes())
	return
