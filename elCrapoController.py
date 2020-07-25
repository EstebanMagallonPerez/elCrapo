#!/usr/bin/python
import threading
import usb.core
import win32api
from win32con import VK_MEDIA_PLAY_PAUSE, KEYEVENTF_EXTENDEDKEY, VK_MEDIA_NEXT_TRACK, VK_MEDIA_PREV_TRACK
import keyboard
import time
import win32gui
import pyaudio
import wave
import json
from datetime import datetime


input_device_index = 0
output_dev_index = 0
chunk = 1024
pressedKeys = []
recordKey = 93

def playAudioThread(file):
	if recordKey in pressedKeys:
		return
	p = pyaudio.PyAudio()
	for i in range(p.get_device_count()):
		dev = p.get_device_info_by_index(i)
		if 'VoiceMeeter Aux Input' in dev['name'] and dev["hostApi"] == 0:
			print(dev)
			dev_index = dev['index']
	wf = wave.open(file)
	stream = p.open(format =
					p.get_format_from_width(wf.getsampwidth()),
					channels = wf.getnchannels(),
					rate = wf.getframerate(),
					output_device_index = dev_index,
					output = True)
	data = wf.readframes(chunk)
	
	while data != b'':
		stream.write(data)
		data = wf.readframes(chunk)
	stream.close()    
	p.terminate()

def playAudio(file):
	t1 = threading.Thread(target=playAudioThread, args=(file,))
	t1.start()
	t1.join()

def recordAudioThread():
	global pressedKeys
	global keys
	dev_index = 0
	print("calling record Audio")
	p = pyaudio.PyAudio()
	for i in range(p.get_device_count()):
		dev = p.get_device_info_by_index(i)
		if 'VoiceMeeter Output (VB-Audio VoiceMeeter' in dev['name'] and dev["hostApi"] == 3:
			dev_index = dev['index']

	stream = p.open(format=pyaudio.paInt16,
					channels=2,
					rate=44100,
					frames_per_buffer=chunk,
					input_device_index = dev_index,
					input=True)

	frames = []
	keyToSet = None
	while recordKey in pressedKeys:
		temp = []+pressedKeys
		temp.remove(recordKey)
		for key in temp:
			if key != 0:
				keyToSet = key
		data = stream.read(chunk)
		frames.append(data)

	stream.stop_stream()
	stream.close()


	if keyToSet != None:
		dateTimeObj = datetime.now()
		timeObj = dateTimeObj.time()
		filename = "./soundboard/recording_"+str(timeObj.hour)+'_'+str(timeObj.minute)+'_'+str(timeObj.second)+".wav"
		p.terminate()
		wf = wave.open(filename, 'wb')
		wf.setnchannels(2)
		wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
		wf.setframerate(44100)
		wf.writeframes(b''.join(frames))
		wf.close()
	
		keys[str(key)] = [
        "playAudio",
        filename]
		updateJson()
		

def recordAudio():
	t1 = threading.Thread(target=recordAudioThread)
	t1.start()


class WindowMgr:
	"""Encapsulates some calls to the winapi for window management"""

	def __init__ (self):
		"""Constructor"""
		self._handle = None

	def _window_enum_callback(self, hwnd, name):
		"""Pass to win32gui.EnumWindows() to check all the opened windows"""
		if name ==  str(win32gui.GetWindowText(hwnd)):
			self._handle = hwnd

	def find_window(self, name):
		"""find a window whose title matches the wildcard regex"""
		self._handle = None
		win32gui.EnumWindows(self._window_enum_callback, name)

	def set_foreground(self):
		"""put the window in the foreground"""
		win32gui.SetForegroundWindow(self._handle)

def focusHop(caller, *args):
	caller( *args )
	return
	try:
		#this focused stuff is a weird workaround where media keys dont seem to work in
		#fullscreen apps, so I set the focus out of the fuscreen app, and then reset the focus
		focused = win32gui.GetForegroundWindow()
		w = WindowMgr()
		w.find_window("EXPLORER")
		w.set_foreground()
		caller( *args )
		win32gui.SetForegroundWindow(focused)
		print("did the window stuff")
	except:
		print("couldnt do the window stuff")
		#if some error happens while switching the window we just call the play pause and pray
		caller( *args )
		pass

def playPause():
	focusHop(win32api.keybd_event, VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY, 0)
	print("play/pause")

def nextTrack():
	focusHop(win32api.keybd_event, VK_MEDIA_NEXT_TRACK, 0, KEYEVENTF_EXTENDEDKEY, 0)
	print("next")

def previousTrack():
	focusHop(win32api.keybd_event, VK_MEDIA_PREV_TRACK, 0, KEYEVENTF_EXTENDEDKEY, 0)
	print("prev")

def presskey(key):
	keyboard.send(key)

def loadJson():
	global keys  
	with open('./source/keyConfig.json') as json_file: 
		keys = json.load(json_file)

def updateJson():
	global keys
	with open("./source/keyConfig.json", "w") as write_file:
		json.dump(keys, write_file, indent=4)
	print(keys)

def start():
	global keys  
	keys = {}
	loadJson()
	def pressed(sentKeys):
		global keys
		global pressedKeys
		pressCount = 0
		for key in sentKeys:
			strKey = str(key)
			if strKey != "0":
				pressCount += 1
				if key not in pressedKeys:
					if strKey not in keys:
						print("key is: ",strKey)
						print(keys)
						keys[strKey] = ""
						updateJson()
						return
					pressedKeys.append(int(strKey))
					keyFunction = keys[strKey]
					print(keyFunction)
					if type(keyFunction) == str:
						try:
							globals()[keyFunction]()
						except:
							print("key:",key," not recognized")
						
					elif type(keyFunction) == list:
						globals()[str(keyFunction[0])](keyFunction[1])
		removeList = list(set(pressedKeys) - set(sentKeys))
		for key in removeList:
			releaseKey(key)

	def releaseKey(key):
		global pressedKeys
		pressedKeys.remove(key)

	def usbListener():
		devs = usb.core.find(find_all=True)
		# loop through devices, printing vendor and product ids in decimal and hex
		dev = None
		interface = 0
		vendorID = 1241
		productID = 4611
		for cfg in devs:
			if (cfg[0][(0,0)].bInterfaceNumber == interface and cfg.idVendor == vendorID and cfg.idProduct == productID):
				dev = cfg
				break

		endpoint = dev[0][(0,0)][0]
		try:
			if dev.is_kernel_driver_active(interface):
				LOGGER.debug('Detaching kernel driver for interface %d '
							'of %r on ports %r', interface, self._device, self._ports)
				dev._device.detach_kernel_driver(interface)
		except NotImplementedError:
			pass
		while True :
			try:
				data = dev.read(endpoint.bEndpointAddress,endpoint.wMaxPacketSize)
				pressed(data[2:5])

				if str(data[2]) not in keys:
					keys[str(data[2])] = ""
				if str(data[3]) not in keys:
					keys[str(data[3])] = ""
				if str(data[4]) not in keys:
					keys[str(data[3])] = ""
							
			except usb.core.USBError as e:
				print(e)
				data = None
				if e.args == ('Operation timed out',):
					continue
					usb.util.release_interface(dev, interface)

	usbListener()