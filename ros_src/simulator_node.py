#Guining Pertin
#Simulator node - 12-05-20

'''
This node runs the entire simulation(only)
Subcribed topics:
    mopat/robot_postion     -   std_msgs/String #ToBeChanged
    mopat/robot_info        -   std_msgs
Published topics:
    mopat/raw_image         -   sensor_msgs/Image (BGR)
    mopat/robot_info        -   std_msgs/??
'''

#Import libraries
#ROS
import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from std_msgs.msg import String
#Others
import sys
import numpy as np
import os
#Mopat
from mopat_lib import *

#Global varibales
screen_size = (500,500)
steps = 50
got_starts = False
got_goals = False
bridge = CvBridge()
robot_shapes = {}
robot_starts = {}
robot_goals = {}

def simulator_node():
    '''
    Function to run the simulation
    '''
    global got_starts
    global got_goals
    global robot_info
    #Game initialization
    pygame.init()
    pygame.display.set_caption("MoPAT Multi-Robot Simulator MkII")
    screen = pygame.display.set_mode(screen_size)
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    clock = pygame.time.Clock()
    #Create space
    space = pymunk.Space()
    #Create node
    rospy.init_node("simulator_node")
    print("LOG: Started MoPAT Multi-Robot Simulator MkII node")
    got_mouse_click = False
    robot_index = 0
    #Subscribe to individual robot controller
    ####################################################
    #Publish simulator raw image
    pub_raw = rospy.Publisher("mopat/raw_image", Image, queue_size=5)
    #Create map
    generate_test_map(space)
    print("USER: Enter initial positions now")
    #Run the simulator
    while not rospy.is_shutdown():
        for event in pygame.event.get():
            #Exiting
            if event.type == QUIT:
                print("LOG: Exiting simulation")
                sys.exit(0)
            elif event.type == KEYDOWN and (event.key in [K_ESCAPE, K_q]):
                print("LOG: Exiting simulation")
                sys.exit(0)
            #Get user input
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_y = screen_size[1] - mouse_y
                got_mouse_click = True
            if (event.type == KEYDOWN) and (event.key == K_w) and not got_goals:
                print("USER: Enter goals now")
                robot_index = 0
                got_starts = True   #Take goals
            elif (event.type == KEYDOWN) and (event.key == K_s) and got_starts and not got_goals:
                if robot_index != len(robot_starts):
                    print("USER: Goals != Robots, Please enter again!")
                    robot_index = 0
                    continue
                print("LOG: Starting simulation...")
                got_goals = True    #Start simulation
        #Update screen
        screen.fill((0,0,0))
        space.step(1/steps)
        space.debug_draw(draw_options)
        #Until goals are found
        if not got_goals:
            #If mouse click found
            if got_mouse_click:
                #If not all starts found
                if not got_starts:
                    robot_starts[robot_index] = (mouse_x, mouse_y)
                    print("LOG: Got Robot", robot_index,
                          "Start:", mouse_x,";",mouse_y)
                    robot_shapes[robot_index] = add_robot(space,
                                                         (mouse_x,
                                                          mouse_y),
                                                         colors[robot_index])
                    robot_index += 1
                #Otherwise get goals
                else:
                    robot_goals[robot_index] = (mouse_x, mouse_y)
                    print("LOG: Got Robot", robot_index,
                          "Goal:", mouse_x,";",mouse_y)
                    robot_index += 1
                got_mouse_click = False
        if got_starts:
            for i in range(robot_index):
                draw_goal(screen, screen_size, robot_goals[i], i)
        pygame.display.flip()
        #Get raw iamge
        raw_image = conv2matrix(screen, space, draw_options)
        #Publish raw data
        pub_raw.publish(bridge.cv2_to_imgmsg(raw_image, encoding="passthrough"))
        clock.tick(steps)
        # print(clock.get_fps())

if __name__ == "__main__":
    try:
        simulator_node()
    except rospy.ROSInterruptException:
        pass
