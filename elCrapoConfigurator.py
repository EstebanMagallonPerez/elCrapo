import eel 
import usb.core
import json
import pyaudio
import threading

configFile = "./config/config.json"
keyConfigFile = "./config/keyConfig.json"
config = {}
keyConfig = {}

try:
	with open(keyConfigFile) as json_file: 
		keyConfig = json.load(json_file)
except:
	keyConfig = {}

try:
	with open(configFile) as json_file: 
		config = json.load(json_file)
except:
	config = {}

@eel.expose
def getConfig(key = None):
	if str(key) in config:
		return config[str(key)]
	else:
		return config


@eel.expose
def getKeyOrder():
	outputArray = []
	for elem in keyConfig:
		outputArray.append(elem)
	return outputArray

@eel.expose
def getKeyConfig(key = None):
	print(key)
	if str(key) in keyConfig:
		return keyConfig[str(key)]
	else:
		return keyConfig

@eel.expose
def updateConfig(key,val):
	print(key,val)
	if key != None:
		config[key] = val
		with open(configFile, 'w') as outfile:
			json.dump(config, outfile, indent=4)

@eel.expose
def updateKeyConfig(key,val):
	print("updateKeyConfig",key,val)
	if key != None:
		keyConfig[key] = val
		with open(keyConfigFile, 'w') as outfile:
			json.dump(keyConfig, outfile, indent=4)

@eel.expose
def get_playback_devices():
	devs = []
	p = pyaudio.PyAudio()
	for i in range(p.get_device_count()):
		dev = p.get_device_info_by_index(i)
		if dev["hostApi"] == 0 and dev["maxOutputChannels"] > 0:
			prop = {
				"deviceID": dev['index'],
				"name":dev['name']
			}
			devs.append(prop)
	return devs

@eel.expose
def get_recording_devices():
	devs = []
	p = pyaudio.PyAudio()
	for i in range(p.get_device_count()):
		dev = p.get_device_info_by_index(i)
		if dev["hostApi"] == 3 and dev["maxInputChannels"] > 0:
			prop = {
				"deviceID": dev['index'],
				"name":dev['name']
			}
			devs.append(prop)
	return devs

@eel.expose
def get_libUSB_devices():
	devs = usb.core.find(find_all=True)
	vals = []
	for cfg in devs:
		devProps = {
			"interface":cfg[0][(0,0)].bInterfaceNumber,
			"idVendor":cfg.idVendor,
			"idProduct":cfg.idProduct,
			}
		vals.append(devProps)
	return vals
pressedKeys = []

def updateJson():
	global keyConfig
	with open(keyConfigFile, "w") as write_file:
		json.dump(keyConfig, write_file, indent=4)
	print(keyConfig)

def pressed(sentKeys):
	global keyConfig
	global pressedKeys
	pressCount = 0
	for key in sentKeys:
		strKey = str(key)
		if strKey != "0":
			pressCount += 1
			if key not in pressedKeys:
				if strKey not in keyConfig:
					keyConfig[strKey] = ""
					updateJson()
					eel.registerKey(key)
					return
				


@eel.expose
def usbListener():
	t1 = threading.Thread(target=usbListenerThread)
	t1.start()

def usbListenerThread():
	global config
	global keyConfig
	print("config is:",config )
	devs = usb.core.find(find_all=True)
	# loop through devices, printing vendor and product ids in decimal and hex
	dev = None
	interface = config["interface"]
	vendorID = config["vendorID"]
	productID = config["productID"]
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

			if str(data[2]) not in keyConfig and data[2] != 0:
				keyConfig[str(data[2])] = ""
			if str(data[3]) not in keyConfig and data[3] != 0:
				keyConfig[str(data[3])] = ""
			if str(data[4]) not in keyConfig and data[4] != 0:
				keyConfig[str(data[3])] = ""
						
		except usb.core.USBError as e:
			print(e)
			data = None
			if e.args == ('Operation timed out',):
				usb.util.release_interface(dev, interface)
				continue


def start():
	eel.init('source')
	eel.start('index.html')