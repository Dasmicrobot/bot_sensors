#!/usr/bin/env python

import time
import rospy
from std_msgs.msg import String
import RPi.GPIO as GPIO

PUBLISH_RATE = rospy.get_param('PUBLISH_RATE', 10) # Hz
GPIO_PIN_SIG = rospy.get_param('GPIO_PIN_SIG')
EMIT_LOW_DURATION = 0.2
EMIT_HIGH_DURATION = 0.5
SOUND_SPEED_CM = 34300 # (cm/s)
TOPIC_NAME = rospy.get_param('TOPIC_NAME', 'bot_sensors_ultrasound')

def measurementInCM():

    # setup the GPIO_PIN_SIG as output
    GPIO.setup(GPIO_PIN_SIG, GPIO.OUT)

    GPIO.output(GPIO_PIN_SIG, GPIO.LOW)
    time.sleep(EMIT_LOW_DURATION)
    GPIO.output(GPIO_PIN_SIG, GPIO.HIGH)
    time.sleep(EMIT_HIGH_DURATION)
    GPIO.output(GPIO_PIN_SIG, GPIO.LOW)
    start = time.time()

    # setup GPIO_PIN_SIG as input
    GPIO.setup(GPIO_PIN_SIG, GPIO.IN)

    # get duration from Ultrasonic SIG pin
    while GPIO.input(GPIO_PIN_SIG) == 0:
        start = time.time()

    while GPIO.input(GPIO_PIN_SIG) == 1:
        stop = time.time()

    measurementPulse(start, stop)


def measurementPulse(start, stop):

    # Calculate pulse length
    elapsed = stop-start

    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s)
    distance = elapsed * SOUND_SPEED_CM

    # That was the distance there and back so halve the value
    distance / 2

def ultrasound():
    pub = rospy.Publisher(TOPIC_NAME, String, queue_size=10)
    rospy.init_node('ultrasound', anonymous=True)
    rate = rospy.Rate(PUBLISH_RATE)
    while not rospy.is_shutdown():
        distance = measurementInCM()
        formatted_distance = "Distance : %.1f CM" % distance
        rospy.loginfo(formatted_distance)
        pub.publish(formatted_distance)
        rate.sleep()

if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
    try:
        ultrasound()
    except rospy.ROSInterruptException:
        pass
    finally:
        GPIO.cleanup()
