#!/usr/bin/python
# coding: utf-8

from time import sleep

from ev3dev.auto import *

# ------Input--------
power = 60
target = 55
kp = float(0.65) # Start value 1
kd = 1           # Start value 0
ki = float(0.02) # Start value 0
direction = -1
minRef = 41
maxRef = 63
# -------------------

# Connect two large motors on output ports B and C and check that
# the device is connected using the 'connected' property.
left_motor = LargeMotor(OUTPUT_B);  assert left_motor.connected
right_motor = LargeMotor(OUTPUT_C); assert right_motor.connected
# One left and one right motor should be connected

# Connect color and touch sensors and check that they
# are connected.
# ir = InfraredSensor(); 	assert ir.connected
ts = TouchSensor();    	assert ts.connected
col= ColorSensor(); 	assert col.connected

# Change color sensor mode
col.mode = 'COL-REFLECT'

# Adding button so it would be possible to break the loop using
# one of the buttons on the brick
btn = Button()

def steering(course, power):
	"""
	Computes how fast each motor in a pair should turn to achieve the
	specified steering.
	Input:
		course [-100, 100]:
		* -100 means turn left as fast as possible,
		*  0   means drive in a straight line, and
		*  100  means turn right as fast as possible.
		* If >100 pr = -power
		* If <100 pl = power        
	power: the power that should be applied to the outmost motor (the one
		rotating faster). The power of the other motor will be computed
		automatically.
	Output:
		a tuple of power values for a pair of motors.
	Example:
		for (motor, power) in zip((left_motor, right_motor), steering(50, 90)):
			motor.run_forever(speed_sp=power)
	"""

	pl = power
	pr = power
	s = (50 - abs(float(course))) / 50

	if course >= 0:
		pr *= s
		if course > 100:
			pr = - power
	else:
		pl *= s
		if course < -100:
			pl = - power

	return (int(pl), int(pr))

def run(power, target, kp, kd, ki, direction, minRef, maxRef):
	"""
	PID controlled line follower algoritm used to calculate left and right motor power.
	Input:
		power. Max motor power on any of the motors
		target. Normalized target value.
		kp. Proportional gain
		ki. Integral gain
		kd. Derivative gain
		direction. 1 or -1 depending on the direction the robot should steer
		minRef. Min reflecting value of floor or line
		maxRef. Max reflecting value of floor or line 
	"""
	lastError = 0
	error = 0
	integral = 0
	left_motor.run_direct()
	right_motor.run_direct()
	lap = 1
	while not btn.any() :
		if ts.value():
			print 'Breaking loop'
			break
		refRead = col.value()
		error = target - (100 * ( refRead - minRef ) / ( maxRef - minRef ))
		derivative = error - lastError
		lastError = error
		integral = float(0.5) * integral + error
		course = (kp * error + kd * derivative +ki * integral) * direction
		for (motor, pow) in zip((left_motor, right_motor), steering(course, power)):
			motor.duty_cycle_sp = pow
		lap = lap + 1
		sleep(0.01) # Aprox 100 Hz

run(power, target, kp, kd, ki, direction, minRef, maxRef)

# Stop the motors before exiting.
print 'Stopping motors'
left_motor.stop()
right_motor.stop()
