from time import sleep

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.OUT)
p = GPIO.PWM(20, 50)

while True:
    p.start(30)
    sleep(2)
    p.ChangeDutyCycle(10)
    sleep(2)
