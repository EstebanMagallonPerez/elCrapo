# elCrapo
I didn't want to buy a stream deck, so I made this

### FAQ(and by this I mean litterally the only question)
Q: Why don't I just use AutoHotkey?  
A: Because I am listening to the USB input and not keypresses so there is no key overlaps, and one keyboard can have all the default keypresses while a secondary keyboard with the libusb driver can perform any actions. Additionaly you can also listen on a per device basis, so there are theoretically an unlimited number of hotkeys available to you 

### Setup
- Find a usb keyboard
- Use https://zadig.akeo.ie/ to load the libusb-win32 (v1.2.6.0) driver for that USB device
- Open the Configurator.exe to get setup
  - Step 1   
![Image of Device Config](https://imgur.com/z5RynJP.jpg)  
  Only libUSB is required for step 2, after selecting your device click "Connect Device" to begin listening to the usb device
  - Step 2  
![Image of Layout Config](https://imgur.com/ope14xe.jpg)  
  Click the Add row button to begin the setup for your keyboard layout. 
  - Step 3  
![Image of Layout Config](https://imgur.com/Y0Rq7rJ.jpg)  
  After setting up your keyboard layout use the mouse to select the key that you want to edit, and then assign the desired action
  
### Want to get involved?
Bruh just make some changes im tired of coding




