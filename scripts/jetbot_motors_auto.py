#!/usr/bin/env python
import rospy
import time

from Adafruit_MotorHAT import Adafruit_MotorHAT
from std_msgs.msg import String
from geometry_msgs.msg import Twist




# sets motor speed between [-1.0, 1.0]
def set_speed(motor_ID, value):
	max_pwm = 115.0
	speed = int(min(max(abs(value * max_pwm), 0), max_pwm))
	a = b = 0

	if motor_ID == 1:
		motor = motor_left
		a = 1
		b = 0
	elif motor_ID == 2:
		motor = motor_right
		a = 2
		b = 3
	else:
		rospy.logerror('set_speed(%d, %f) -> invalid motor_ID=%d', motor_ID, value, motor_ID)
		return
	
	motor.setSpeed(speed)

	# Motor Direction for Jetbot Waveshare
	if value < 0:
		motor.run(Adafruit_MotorHAT.FORWARD)
		motor.MC._pwm.setPWM(a, 0, 0)
		motor.MC._pwm.setPWM(b, 0, speed*16)
	elif value > 0:
		motor.run(Adafruit_MotorHAT.BACKWARD)
		motor.MC._pwm.setPWM(a, 0, speed*16)
		motor.MC._pwm.setPWM(b, 0, 0)
	else:
		motor.run(Adafruit_MotorHAT.RELEASE)
		motor.MC._pwm.setPWM(a, 0, 0)
		motor.MC._pwm.setPWM(b, 0, 0)


# stops all motors
def all_stop():
	motor_left.setSpeed(0)
	motor_right.setSpeed(0)
	set_speed(motor_left_ID, 0.0)
	set_speed(motor_right_ID, 0.0)

	motor_left.run(Adafruit_MotorHAT.RELEASE)
	motor_right.run(Adafruit_MotorHAT.RELEASE)


# directional commands (degree, speed)
def on_cmd_dir(msg):
	rospy.loginfo(rospy.get_caller_id() + ' cmd_dir=%s', msg.data)

# raw L/R motor commands (speed, speed)
def on_cmd_raw(msg):
	rospy.loginfo(rospy.get_caller_id() + ' cmd_raw=%s', msg.data)

# simple string commands (left/right/forward/backward/stop)
def on_cmd_str(msg):
	rospy.loginfo(rospy.get_caller_id() + ' cmd_str=%s', msg.data)

	if msg.data.lower() == "left":
		set_speed(motor_left_ID,  -1.0)
		set_speed(motor_right_ID,  1.0) 
	elif msg.data.lower() == "right":
		set_speed(motor_left_ID,   1.0)
		set_speed(motor_right_ID, -1.0) 
	elif msg.data.lower() == "forward":
		set_speed(motor_left_ID,   1.0)
		set_speed(motor_right_ID,  1.0)
	elif msg.data.lower() == "backward":
		set_speed(motor_left_ID,  -1.0)
		set_speed(motor_right_ID, -1.0)  
	elif msg.data.lower() == "stop":
		all_stop()
	else:
		rospy.logerror(rospy.get_caller_id() + ' invalid cmd_str=%s', msg.data)

# twist command (linear x, y, z, angular x, y, z)
def on_cmd_twist(msg):
	# Check all msg data
	rospy.loginfo(rospy.get_caller_id() + '\n\
		cmd_twist.linear.x=%s\n \
		cmd_twist.linear.y=%s\n \
		cmd_twist.linear.z=%s\n \
		cmd_twist.angular.x=%s\n \
		cmd_twist.angular.y=%s\n \
		cmd_twist.angular.z=%s\n', 
		msg.linear.x, msg.linear.y, msg.linear.z, 
		msg.angular.x, msg.angular.y, msg.angular.z)
	velocity = msg.linear.x
	if velocity >= 1.0:
		velocity = 1.0
	rotation = msg.angular.z
	rotation_str = ''
	if rotation > 0:
		rotation_str = 'left'
	elif rotation < 0:
		rotation_str = 'right'
	else:
		rotation_str = 'straight'
	# rospy.loginfo(rospy.get_caller_id() + '\n\
	# 	velocity : %s\n \
	# 	rotation : %s\t%s\n', velocity, rotation, rotation_str)

	set_speed(motor_left_ID, velocity*3 - rotation)
	set_speed(motor_right_ID, velocity*3 + rotation)




# initialization
if __name__ == '__main__':

	# setup motor controller
	motor_driver = Adafruit_MotorHAT(i2c_bus=1)

	motor_left_ID = 1
	motor_right_ID = 2

	motor_left = motor_driver.getMotor(motor_left_ID)
	motor_right = motor_driver.getMotor(motor_right_ID)

	# stop the motors as precaution
	all_stop()

	# setup ros node
	rospy.init_node('jetbot_motors')
	
	rospy.Subscriber('~cmd_dir', String, on_cmd_dir)
	rospy.Subscriber('~cmd_raw', String, on_cmd_raw)
	rospy.Subscriber('~cmd_str', String, on_cmd_str)
	rospy.Subscriber('cmd_vel', Twist, on_cmd_twist)

	# start running
	rospy.spin()

	# stop motors before exiting
	all_stop()

