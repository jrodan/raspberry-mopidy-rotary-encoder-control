# TODO stabilize script
# TODO play sounds on detected rotary event -> louder, quieter, start, stop

# coding=utf-8
import RPi.GPIO as GPIO
import time
import requests
import json

playStatus = 0

def setVolume(status):

    volume = int(getState('core.mixer.get_volume'))

    if(status == 0):
        volume -= 20
    else:
        volume += 20

    getStateParams('core.mixer.set_volume',{'volume':volume})

def getState(method):
    headers = {
        'Content-Type': 'application/json',
    }

    data = {'jsonrpc': '2.0', 'id': 1, 'method': method}
    response = requests.post('http://192.168.178.192:6680/mopidy/rpc', headers=headers, json=data)
    #print(response.json())
    result = response.json()['result']
    print(result)
    return result

def getStateParams(method, params):
    headers = {
        'Content-Type': 'application/json',
    }

    data = {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}
    response = requests.post('http://192.168.178.192:6680/mopidy/rpc', headers=headers, json=data)
    result = response.json()['result']
    print(result)
    return result

def setInitalPlayState():
    global playStatus
    state = getState('core.playback.get_state')
    if state == "playing":
        playStatus = 1

setInitalPlayState()

GPIO.setmode(GPIO.BCM)

PIN_CLK = 11
PIN_DT = 8
BUTTON_PIN = 23

GPIO.setup(PIN_CLK, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(PIN_DT, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)

counter = 0
direction = True
PIN_CLK_LAST = 0
PIN_CLK_CURRENT = 0
delayTime = 0.05

PIN_CLK_LAST = GPIO.input(PIN_CLK)

def getDirection(null):
    global counter
    PIN_CLK_CURRENT = GPIO.input(PIN_CLK)

    if PIN_CLK_CURRENT != PIN_CLK_LAST:
        if GPIO.input(PIN_DT) != PIN_CLK_CURRENT:
            counter += 1
            direction = True;
        else:
            direction = False
            counter = counter - 1

        if direction:
            print ("lauter")
            setVolume(1)
        else:
            print ("leiser")
            setVolume(0)

def clickCallback(null):
    global playStatus
    if playStatus == 0:
        print("start playing now")
        getState('core.playback.play')
        playStatus = 1
    else:
        getState('core.playback.stop')
        print("stop playing now")
        playStatus = 0

GPIO.add_event_detect(PIN_CLK, GPIO.BOTH, callback=getDirection, bouncetime=50)
GPIO.add_event_detect(BUTTON_PIN, GPIO.RISING, callback=clickCallback, bouncetime=50)

try:
        while True:
	#while GPIO.input(PIN_CLK) != GPIO.LOW:
            time.sleep(delayTime)

except KeyboardInterrupt:
        GPIO.cleanup()
