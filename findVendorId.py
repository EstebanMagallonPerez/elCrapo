#!/usr/bin/python
import threading
import sys
import usb.core
import usb.backend.libusb1
import win32api
from win32con import VK_MEDIA_PLAY_PAUSE, KEYEVENTF_EXTENDEDKEY, VK_MEDIA_NEXT_TRACK, VK_MEDIA_PREV_TRACK
import keyboard
import time
import win32gui
from playsound import playsound
import sounddevice as sd
import soundfile as sf


sd.default.device = 'voicemeeter aux input (vb-audio voicemeeter aux vaio DirectSound'


pressedKeys = []
def start():
	global keys  

	def playAudio(file):
		data, fs = sf.read(file, dtype='float32')
		sd._get_device_id('voicemeeter aux input (vb-audio voicemeeter aux vaio',"output")
		sd.play(data, fs)
		status = sd.wait()

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

	keys = {
		0: '',
		83: previousTrack,
		84: playPause,
		85: nextTrack,
		42: (playAudio,"./soundboard/Bruh.wav"),
		95: (playAudio,"./soundboard/spriteCranberry.wav"),
		96: (playAudio,"./soundboard/shinnyTeeth.wav"),
		97: (keyboard.send,"CTRL+SHIFT+l"),
		86: (keyboard.send,"CTRL+SHIFT+k"),
		92: '',
		93: '',
		94: '',
		87: '',
		89: '',
		90: '',
		91: '',
		88: '',
		98: '',
		99: ''}

	def pressed(sentKeys):
		global keys
		global pressedKeys
		pressCount = 0
		for key in sentKeys:
			if key != 0:
				pressCount += 1
				if key not in pressedKeys:
					if key not in keys:
						print("key is: ",key)
						return
					pressedKeys.append(key)
					keyFunction = keys[key]
					if callable(keyFunction):
						keyFunction()
					elif type(keyFunction) == tuple:

						keyFunction[0](keyFunction[1])
						#eg = threading.Thread(target=keyFunction[0],
						#					args = [keyFunction[1]])
						#eg.start()
						print("its a tuple :)")
					print("pressed",key)
		
		removeList = list(set(pressedKeys) - set(sentKeys))
		for key in removeList:
			releaseKey(key)

	def releaseKey(key):
		global pressedKeys
		pressedKeys.remove(key)
		print("released",key)

	def doEverything():
		devs = usb.core.find(find_all=True)
		# loop through devices, printing vendor and product ids in decimal and hex
		dev = None
		for cfg in devs:
			interface = 0
			dev = cfg
			#print('Decimal VendorID=' + str(cfg.idVendor) + ' & ProductID=' + str(cfg.idProduct) + '\n')
			#print('Hexadecimal VendorID=' + hex(cfg.idVendor) + ' & ProductID=' + hex(cfg.idProduct) + '\n\n')

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

				if data[2] not in keys:
					keys[data[2]] = ""
							
			except usb.core.USBError as e:
				data = None
				if e.args == ('Operation timed out',):
					continue
					# release the device
					usb.util.release_interface(dev, interface)

	#doEverything()
	thread2 = threading.Thread(target = doEverything)
	thread2.start()