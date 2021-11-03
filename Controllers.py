#state defined, partitioned controller script
from evdev import InputDevice, categorize, ecodes
from scipy.interpolate import interp1d
import subprocess
import yaml
import numpy
import multiprocessing
import time

#Subprocess call to motor controllers
def ticcmd(*args):
  return subprocess.check_output(['ticcmd'] + list(args))

def check_kill(event):
    global gamepad
    global kill
    aBtn = 304
    try:
        #for event in gamepad.read():
        if event.type == ecodes.EV_KEY:
            if event.value == 1:
                if event.code == aBtn:
                    print("Killing Program...")
                    kill = True
    except BlockingIOError:
        return
    except AttributeError:
        return
    
#Function periodically checks if manual controls are enabled.
def check_enable(event):
    global gamepad
    global enable
    select = 158 #mapped code to select button
    try:
        #for event in gamepad.read():
        if event.type == ecodes.EV_KEY:
            if event.value == 1:
                if event.code == select:
                    if enable == 1:
                        print("Disabling Manual Controls")
                        enable = 0
                    else:
                        print("Enabling Manual Controls")
                        enable = 1
    except BlockingIOError:
        return
    except AttributeError:
        return

def check_pos():
    global motor1, motor2
    while True:
        #States = [Lup, Ldn, Llt, Lrt, Rup, Rdn, Rlt, Rrt, alert]
        status1 = yaml.safe_load(ticcmd('-d', motor1,'-s', '--full'))
        status2 = yaml.safe_load(ticcmd('-d', motor2,'-s', '--full'))
        position1 = status1['Current position']
        #print(position1)
        #print(states)
        position2 = status2['Current position']
        #print(position2)
        if position1 <= -500 and not states[8]:
            ticcmd('-d',motor1,'--exit-safe-start', '--velocity', str(0))
            states[0] = False
        elif position1 >=500 and not states[8]:
            ticcmd('-d',motor1,'--exit-safe-start', '--velocity', str(0))
            states[1] = False
        elif -500 < position1 < 500:
            states[0] = True #enable Lup
            states[1] = True #Enable Ldn
            states[8] = False #Disable Alert ud
        
        if position2 <= -500 and not states[9]:
            ticcmd('-d',motor2,'--exit-safe-start', '--velocity', str(0))
            states[2] = False
        elif position2 >=500 and not states[9]:
            ticcmd('-d',motor2,'--exit-safe-start', '--velocity', str(0))
            states[3] = False
        elif -500 < position2 < 500:
            states[2] = True #enable Llt
            states[3] = True #Enable Lrt
            states[9] = False #Disable Alert lr
            
            
# def check_pos(states, motor1, motor2):
#     #States = [Lup, Ldn, Llt, Lrt, Rup, Rdn, Rlt, Rrt, alert]
#     status1 = yaml.safe_load(ticcmd('-d', motor1,'-s', '--full'))
#     status2 = yaml.safe_load(ticcmd('-d', motor1,'-s', '--full'))
#     position1 = status1['Current position']
#     position2 = status2['Current position']
#     if position1 <= -500:
#         ticcmd('-d',motor1,'--exit-safe-start', '--velocity', str(0))
#         states[0] = 0
#     elif position1 >=500:
#         ticcmd('-d',motor1,'--exit-safe-start', '--velocity', str(0))
#         states[1] = 0
#     elif -500 < position1 < 500:
#         states[0] = 1 #enable Lup
#         states[1] = 1 #Enable Ldn
#         states[8] = 0 #Disable Alert
#     return states

def check_energized(event):
    yBtn = 308 #mapped code to y button
    global gamepad
    global energized
    global motor1, motor2
    try:
        #for event in gamepad.read():
        if event.type == ecodes.EV_KEY:
            if event.value == 1:
                if event.code == yBtn:
                    if energized:
                        energized = False
                        ticcmd('-d', motor1,'--exit-safe-start','--deenergize')
                        ticcmd('-d', motor2,'--exit-safe-start','--deenergize')
                        print("De-Energizing Motors")
                        #return energized
                    else:
                        energized = True
                        ticcmd('-d', motor1,'--exit-safe-start','--energize')
                        ticcmd('-d', motor2,'--exit-safe-start','--energize')
                        print("Energizing Motors")
                        #return energized
    except BlockingIOError:
        return
    except AttributeError:
        return

def Left_JS_ud(event):
    global motor1, motor2
    global JS, pos_speed, neg_speed
    LJud = 1
    #print(states)
    try:
        #for event in gamepad.read():
        if event.type == 3:
            if event.code == LJud:
                if (-15 < JS(event.value) < 15):
                    #print("Setting Velocity to 0")
                    ticcmd('-d',motor1,'--exit-safe-start', '--velocity', str(0))
                elif ((15 <= JS(event.value) <= 100) and states[1]):
                    vel = int(numpy.around(pos_speed(JS(event.value))))
                    #print("Setting Velocity to ", str(vel))
                    ticcmd('-d',motor1,'--exit-safe-start', '--velocity', str(vel))
                elif ((-100 <= JS(event.value) <= -15) and states[0]):
                    vel = int(numpy.around(neg_speed(JS(event.value))))
                    #print("Setting Velocity to ", str(vel))
                    ticcmd('-d',motor1,'--exit-safe-start', '--velocity', str(vel))
                elif ((JS(event.value) > 15) and (not states[1]) and not states[8]):
                    ticcmd('-d',motor1,'--exit-safe-start', '--velocity', str(0))
                    print("End of Motion!")
                    states[8] = True
                elif ((JS(event.value) < -15) and (not states[0]) and not states[8]):
                    ticcmd('-d',motor1,'--exit-safe-start', '--velocity', str(0))
                    print("End of Motion!")
                    states[8] = True
                elif ((JS(event.value) > 15) and (not states[1]) and states[8]):
                    pass
                elif (JS(event.value) < -15) and not states[0] and states[8]:
                    pass
                else:
                    print("Commands Error... Halting Motor")
                    ticcmd('-d',motor1,'--exit-safe-start', '--halt-and-hold')
    except BlockingIOError:
        return
    except AttributeError:
        return

def Left_JS_lr(event):
    global motor1, motor2
    global JS, pos_speed, neg_speed
    LJrl = 0
    #print(states)
    try:
        #for event in gamepad.read():
        if event.type == 3:
            if event.code == LJrl:
                if (-15 < JS(event.value) < 15):
                    #print("Setting Velocity to 0")
                    ticcmd('-d',motor2,'--exit-safe-start', '--velocity', str(0))
                elif ((15 <= JS(event.value) <= 100) and states[3]):
                    vel = int(numpy.around(pos_speed(JS(event.value))))
                    #print("Setting Velocity to ", str(vel))
                    ticcmd('-d',motor2,'--exit-safe-start', '--velocity', str(vel))
                elif ((-100 <= JS(event.value) <= -15) and states[2]):
                    vel = int(numpy.around(neg_speed(JS(event.value))))
                    #print("Setting Velocity to ", str(vel))
                    ticcmd('-d',motor2,'--exit-safe-start', '--velocity', str(vel))
                elif ((JS(event.value) > 15) and (not states[3]) and not states[9]):
                    ticcmd('-d',motor2,'--exit-safe-start', '--velocity', str(0))
                    print("End of Motion!")
                    states[9] = True
                elif ((JS(event.value) < -15) and (not states[2]) and not states[9]):
                    ticcmd('-d',motor2,'--exit-safe-start', '--velocity', str(0))
                    print("End of Motion!")
                    states[9] = True
                elif ((JS(event.value) > 15) and (not states[3]) and states[9]):
                    pass
                elif (JS(event.value) < -15) and not states[2] and states[9]:
                    pass
                else:
                    print("Commands Error... Halting Motor")
                    ticcmd('-d',motor2,'--exit-safe-start', '--halt-and-hold')
    except BlockingIOError:
        return
    except AttributeError:
        return

def homing(event):
    start = 315 #mapped code to start button
    global gamepad
    global motor1, motor2
    try:
        #for event in gamepad.read():
        if event.type == ecodes.EV_KEY:
            if event.value == 1:
                if event.code == start:
                    print("returning Motors to Home Position")
                    ticcmd('-d',motor1,'--exit-safe-start', '--position', str(0))
                    ticcmd('-d',motor2,'--exit-safe-start', '--position', str(0))
    except BlockingIOError:
        return
    except AttributeError:
        return

if __name__=="__main__":
    #creates object 'gamepad' to store the data
    gamepad = InputDevice('/dev/input/event0')
    states_manager = multiprocessing.Manager()
    
    #prints out device info at start
    print(gamepad)
    #Default start status is motors deenergized and manual controls disabled
    energized = False
    #global enable
    enable = 0
    states = states_manager.list([True,True,True,True,True,True,True,True,False,False])
    #states = [True,True,True,True,True,True,True,True,False]
    JS = interp1d([0,65535],[-100,100])
    Trig = interp1d([0,1023],[0,100])
    pos_speed = interp1d([15,100],[100000,3000000])
    neg_speed = interp1d([-15,-100],[-100000,-3000000])
    #Motor Serial Numbers
    motor1 = "00366893"
    motor2 = "00366755"
    kill = False
    state_control = multiprocessing.Process(target=check_pos)
    state_control.start()
    while not kill:
        event = gamepad.read_one()
        check_enable(event)
        check_kill(event)
        if enable:
            check_energized(event)
            if energized:

                if (states[0] or states[1]):
                    Left_JS_ud(event)
                if (states[2] or states[3]):
                    Left_JS_lr(event)
            
    #Safe Exit procedure
    print("    Returning Motors to Home Position...")
    state_control.terminate()
    ticcmd('-d',motor1,'--exit-safe-start','--energize')
    ticcmd('-d',motor2,'--exit-safe-start','--energize')
    ticcmd('-d',motor1,'--exit-safe-start', '--position', str(0))
    ticcmd('-d',motor2,'--exit-safe-start', '--position', str(0))
    #time.sleep(5)
    print("    Deenergizing Motors...")
    ticcmd('-d', motor1,'--exit-safe-start','--deenergize')
    ticcmd('-d', motor2,'--exit-safe-start','--deenergize')
    print("    Closing all Processes...")
    
    print("Safe Exit Complete!")