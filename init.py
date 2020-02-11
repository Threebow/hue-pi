# coding: utf-8

#Import tkinter
try:
	import Tkinter as tk
except ImportError:
	import tkinter as tk

#Import modules
import phue, util, math, threading
from prettytable import PrettyTable
from constants import *
import logging

#Allow phue logging
logging.basicConfig()

#Instantiate bridge
bridge = phue.Bridge(BRIDGE_IP)

#Initialize window
root = tk.Tk(DISPLAY)
root.overrideredirect(True)
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
root.focus_set()
root.bind("<Escape>", lambda e: root.destroy())
root.configure(bg=COLORS['bgDarker'])

#Top bar
taskbar = tk.PanedWindow(root)
taskbar.pack(side=tk.TOP, fill=tk.X)
taskbar.configure(bg=COLORS['bgDarker'])

#Close button
close = tk.Button(taskbar, text="×", font=("Roboto", 18), bg=COLORS['danger'], fg=COLORS['text'], command=util.terminate)
close.pack(side=tk.RIGHT, fill=tk.Y)

#On/Off
isOn = tk.IntVar()
toggle = tk.Checkbutton(taskbar, text=" On ", variable=isOn, bg=COLORS['bg'], fg=COLORS['success'], activebackground=COLORS['bg'], activeforeground=COLORS['success'])
toggle.pack(side=tk.RIGHT, fill=tk.Y)

brightnessTimer = None
def brightnessChanged(a):
	global brightnessTimer

	if brightnessTimer is not None:
		brightnessTimer.cancel()

	def setBrightness():
		getCurrentGroup().brightness = int(a)

	brightnessTimer = threading.Timer(0.1, setBrightness)
	brightnessTimer.start()

#Brightness slider
brightness = tk.Scale(taskbar, from_=1, to=254, orient=tk.HORIZONTAL, command=brightnessChanged, bg=COLORS['bg'], fg=COLORS['text'])
brightness.pack(side=tk.RIGHT, fill=tk.X, expand=1)

def getCurrentGroup():
	for group in bridge.groups:
		if group.name == selectedGroup.get():
			return group

def lightToggled(a, b, c):
	group = getCurrentGroup()
	group.on = bool(isOn.get())

isOn.trace("w", lightToggled)

#Group Dropdown
groupList = map(lambda g: g.name, bridge.groups)

selectedGroup = tk.StringVar(root)

def setCurrentGroup(group):
	print(group)
	isOn.set(group.on)
	brightness.set(group.brightness)

selectedGroup.trace("w", lambda a, b, c: setCurrentGroup(getCurrentGroup()))

selectedGroup.set(bridge.groups[0].name)

groupMenu = tk.OptionMenu(taskbar, selectedGroup, *groupList)
groupMenu.pack(side=tk.LEFT, fill=tk.Y)
groupMenu.config(bg=COLORS['bg'], fg=COLORS['text'])

#Main body
tk.Grid.rowconfigure(root, 0, weight=1)
tk.Grid.columnconfigure(root, 0, weight=1)

body = tk.Frame(root)
body.pack(fill=tk.BOTH, expand=1)

for y in range(ROWS):
	tk.Grid.rowconfigure(body, y, weight=1)
	for x in range(COLUMNS):
		tk.Grid.columnconfigure(body, x, weight=1)

def getScenes():
	return filter(lambda sc: not sc.locked, bridge.scenes)

def changeScene(scene):
	bridge.run_scene(selectedGroup.get(), scene.name)
	print("Changed scene to " + scene.name + " in " + selectedGroup.get())
	brightness.set(getCurrentGroup().brightness)

def populate():
	for (idx, scene) in enumerate(getScenes()):
		x = idx % COLUMNS
		y = int(math.floor(idx/COLUMNS))

		def makeLambda(sc):
			return lambda: changeScene(sc)

		btn = tk.Button(body, text=scene.name, command=makeLambda(scene), bg=COLORS['bgDarker'], fg=COLORS['text'], activebackground=COLORS['bg'], activeforeground=COLORS['success'])
		btn.grid(column=x, row=y, sticky="NSEW")

populate()

#Run UI
root.mainloop()