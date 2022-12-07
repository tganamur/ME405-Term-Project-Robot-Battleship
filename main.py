from pyb import UART
from pyb import Pin
from pyb import Timer
#from pyb import PWM
import micropython
import task_share
import task_share
import cotask
import Encoder
import L6206
import gc
import controller
import miscmethods
import battleship
import time
import MotorDriver

txtfile = open("labx05_ui_help_commands.txt", "r")
ui_help = txtfile.read()
# in order to keep this organized, put all methods in the 'miscmethods' folder - main.py is only for main and tasks

'''
FIRING TASK
- Manages actually shooting the gun
- Runs brushless DC motors and ball feed motor

State 0: Init
State 1: Wait to see if we are in autoplay mode
State 2: Go to Xpos and start flywheels
State 3: Load Ball
State 4: Fire
State 5: return to home(origin)
'''
def firing(vcp):
    state = 0
    while True:
        if state == 0:
            #esc.pulse_width_percent(0)
            count = 0
            state += 1
        elif state == 1:
            if(a_flag.get() == 1 and shoot_flag.get() == 1):
                state = 2
            else:
                state = 1
        elif state == 2:
            set_flag.put(1)
            count += 1
            if(count == 4000):
                count = 0
                state = 3
        elif state == 3:
            set_flag.put(1)
            bucket_des.put(50)
            count += 1
            if (count == 260):
                count = 0
                state = 4
                bucket_des.put(0)
        elif state == 4:
            feed_des.put(4000)
            set_flag.put(1)
            count += 1 
            if(count == 500):
                count = 0
                state = 5
        elif state == 5:
            x_des.put(0)
            speed_des.put(0)
            set_flag.put(1)
            count += 1
            if(count == 3000):
                count = 0
                state = 1
                shoot_flag.put(0)
        yield(0)


'''
MOVEMENT TASK
- Manages all aiming movement of the mechanism; getting from point a to b
- Spins motors, reads encoders, runs controllers

State 0: Init
State 1: Wait/Run Controllers
State 2: Zero encoders
State 3: Set controller targets
'''
def movement(vcp):
    state = 0
    bcounter = 0
    fcounter = 0
    while True:
        #update the encoders every pass through here
        x_enc.update()
        feed_enc.update()
        #init stuff
        if state == 0:
            x_des.put(0)
            feed_des.put(0)
            x_controller.set_Target(0)
            feed_controller.set_Target(0)
            x_controller.ki = .0001
            x_controller.kp = 1
            feed_controller.ki = 0
            feed_controller.kp = .05
            state += 1
        #maintains controllers and duties
        elif state == 1:
            #run pi controllers
            x_mot.set_duty(x_controller.pi(-x_enc.position))
            set_pt = feed_controller.pi(feed_enc.position)
            feed_mot.set_duty(miscmethods.saturate(set_pt,50,-55))

            #control feeding a single ball
            if bucket_des.get() != 0:
                bcounter += 1
                bcount.put(bcounter)
            if bcounter == 237:
                bucket_des.put(0)
                set_flag.put(1)
                bcounter = 0
                bcount.put(bcounter)

            #control firing arm
            if feed_des.get() != 0 and feed_des.get() != -4000:
                fcounter +=1
            if fcounter == 100:
                feed_des.put(-4000)
                set_flag.put(1)
                fcounter = 0

            if z_flag.get() == 1:
                state = 2
            elif set_flag.get() == 1:
                state = 3
        #zero all the encoders and set controller positions here
        elif state == 2:
            x_enc.zero()
            feed_enc.zero()
            x_des.put(0)
            feed_des.put(0)
            z_flag.put(0)
            state = 3

        #sets the controller targets and the duties
        elif state == 3:
            x_controller.set_Target(x_des.get()*67.5)
            feed_controller.set_Target(feed_des.get())
            esc.pulse_width_percent(float(speed_des.get())/20+5)
            bucket_mot.set_duty(bucket_des.get())
            state = 1
            set_flag.put(0)
        yield(0)

'''
UI TASK
- Takes all user input and interprets it
- Is the only task that can print to terminal

State 0: Init
State 1: Startup mode
State 2: Gameplay mode
'''
def ui(vcp,lookup,fullin):
    state = 0
    settings = 0     # Used to store x-pos and speed for a particular set of coord from lookup
    while True:
        if state == 0:
            vcp.write('\033c')
            vcp.write(ui_help)
            state += 1
        elif state == 1:
            #wait for user input
            if vcp.any():
                input = vcp.read(1).decode()
                #handling submenu stuff

                #set jog value
                if j_flag.get() == 1:
                    charin = input
                    #take numerical input
                    if charin in {'\n','\r'}:
                        try:
                            numinput = miscmethods.numerical_input(vcp,-1000,1000,fullin)
                            pos_new = x_des.get() + int(numinput)
                            x_des.put(pos_new)
                            set_flag.put(1)
                            vcp.write('\n\rX motor jogging by ' + str(numinput) + ' mm to a position of ' + str(x_des.get()) + ' mm')
                            state = 1
                            j_flag.put(0)
                            input = ''
                            fullin.clear()
                        except IndexError:
                            vcp.write('\n\rNumber not within acceptable bounds')
                            input = ''
                            fullin.clear()
                        except TypeError:
                            vcp.write('\n\rInput a numerical value')
                            input = ''
                            fullin.clear()
                    else:
                        fullin.append(charin)
                        vcp.write(charin)
                        input = ''

                elif s_flag.get() == 1:
                    charin = input
                    #take numerical input
                    if charin in {'\n','\r'}:
                        try:
                            numinput = miscmethods.numerical_input(vcp,0,100,fullin)
                            speed_des.put(float(numinput))
                            state = 1
                            input = ''
                            fullin.clear()
                            s_flag.put(0)
                            set_flag.put(1)
                            vcp.write('\n\rBrushless motor speed set to ' + str(numinput) + '%')
                        except IndexError:
                            vcp.write('\n\rNumber not within acceptable bounds')
                            input = ''
                            fullin.clear()
                        except TypeError:
                            vcp.write('\n\rInput a numerical value')
                            input = ''
                            fullin.clear()
                        except:
                            vcp.write('\n\rSome other error happened')
                    else:
                        fullin.append(charin)
                        vcp.write(charin)
                        input = ''

                #take setup command input
                #take z input
                elif (input == 'h') or (input == 'H'):
                    vcp.write('\033c')
                    vcp.write(ui_help)
                elif (input == 'z') or (input == 'Z'):
                    z_flag.put(1)
                    input = ''
                    vcp.write('\n\rZeroing all encoders')
                elif (input == 'o') or (input == 'O'):
                    x_des.put(0)
                    feed_des.put(0)
                    set_flag.put(1)
                    vcp.write('\n\rHoming the machine')
                    input = ''
                elif (input == 'p') or (input == 'P'):
                    input = ''
                    vcp.write('\n\rX: ' + str(x_des.get()) + ' mm     Firing Arm: ' + str(feed_des.get()) + ' ticks     Speed: ' + str(speed_des.get()) + '%')
                #take j input
                elif (input == 'j') or (input == 'J'):
                    j_flag.put(1)
                    vcp.write('\n\rHow much would you like to jog the motor?\n\r')
                    input = ''
                #take s input
                elif (input == 's') or (input == 'S'):
                    s_flag.put(1)
                    vcp.write('\n\rInput desired speed for the brushless motors')
                    input = ''
                #take l input
                elif (input == 'l') or (input == "L"):
                    vcp.write('\n\rLoading a ball')
                    bucket_des.put(50)
                    set_flag.put(1)
                    input = ''
                #take f input
                elif (input == 'f') or (input == "F"):
                    vcp.write('\n\rFiring')
                    feed_des.put(4000)
                    set_flag.put(1)
                    input = ''
                #take g input
                elif (input == 'a') or (input == 'A'):
                    state = 2
                    vcp.write('\n\rWhen it is my turn, press "y", if we won press "w", if we lost press "l"')
                    input = ''
                    a_flag.put(1)
                #take bad input
                else:
                    vcp.write(input + '\n\r')
                    vcp.write('\n\rInvalid input. Please read the table again you illiterate moron.\n\r')

        elif state == 2:
            if vcp.any():
                input = vcp.read(1).decode()
                vcp.write(input)
                #take an answer of if it's our turn/if we won
                if (input == 'y') or (input == 'Y'):
                    coords = battleShip.calc_shot_twostate()
                    settings = lookup[tuple(coords)]
                    x_des.put(settings[0])
                    speed_des.put(settings[1])
                    vcp.write('\r\nX-Pos set to: ' + str(x_des.get()) + '\r\n')
                    vcp.write('Speed set to: ' + str(speed_des.get()) + '\r\n')
                    vcp.write('Shooting at ' + str(coords) + '\n\rDid we hit? h = hit, m = miss, n = bad shot\r\n')
                    shoot_flag.put(1)
                    input = ''
                elif (input == 'w') or (input == 'W'):
                    vcp.write('\n\rTo the other team: get fucked losers')
                    input = ''
                elif (input == 'l') or (input == 'L'):
                    vcp.write('\n\rTheir win was illegitimate')
                    input = ''
                elif (input == 'h') or (input == 'H'):
                    battleShip.board[coords[0]][coords[1]] = 1
                    coords = battleShip.calc_shot_rand()
                    settings = lookup[tuple(coords)]
                    x_des.put(settings[0])
                    speed_des.put(settings[1])
                    vcp.write('\r\nX-Pos set to: ' + str(x_des.get()) + '\r\n')
                    vcp.write('Speed set to: ' + str(speed_des.get()) + '\r\n')
                    vcp.write('Shooting at ' + str(coords) + '\n\rDid we hit? h = hit, m = miss, n = bad shot\r\n')
                    shoot_flag.put(1)
                    input = ''
                elif (input == 'm') or (input == 'M'):
                    battleShip.board[coords[0]][coords[1]] = -1
                    coords = battleShip.calc_shot_twostate()
                    settings = lookup[tuple(coords)]
                    x_des.put(settings[0])
                    speed_des.put(settings[1])
                    vcp.write('\r\nX-Pos set to: ' + str(x_des.get()) + '\r\n')
                    vcp.write('Speed set to: ' + str(speed_des.get()) + '\r\n')
                    vcp.write('Shooting at ' + str(coords) + '\n\rDid we hit? h = hit, m = miss, n = bad shot\r\n')
                    shoot_flag.put(1)
                    input = ''
                elif (input == 'n') or (input == 'N'):
                    vcp.write('Bad Shot, re-taking shot')
                    x_des.put(settings[0])
                    speed_des.put(settings[1])
                    vcp.write('\r\nX-Pos set to: ' + str(x_des.get()) + '\r\n')
                    vcp.write('Speed set to: ' + str(speed_des.get()) + '\r\n')
                    vcp.write('Shooting at ' + str(coords) + '\n\rDid we hit? h = hit, m = miss, n = bad shot\r\n')
                    shoot_flag.put(1)
                    input = ''
                elif (input == 'q') or (input == 'Q'):
                    state = 1
                    vcp.write('Switched to manual mode')
                    a_flag.put(0)
                    shoot_flag.put(0)
                    input = ''
                else:
                    vcp.write('\n\rBad input, read the prompt you dunce')
        yield(0)

if __name__ == "__main__":

    #define lookup table - [coords] : [x_pos,brushless_speed]
    lookup = {
                tuple([0,0]): [60,8.7],     #D1
                tuple([0,1]): [60,9.4],     #C1
                tuple([0,2]): [60,10],      #B1
                tuple([0,3]): [60,10.35],   #A1
                tuple([1,0]): [340,8.7],    #D2
                tuple([1,1]): [340,9.4],    #C2 
                tuple([1,2]): [340,10],     #B2
                tuple([1,3]): [340,10.35],  #A2
                tuple([2,0]): [690,8.7],    #D3
                tuple([2,1]): [690,9.4],    #C3
                tuple([2,2]): [690,10],     #B3
                tuple([2,3]): [690,10.35],  #A3
                tuple([3,0]): [820,8.7],    #D4
                tuple([3,1]): [820,9.4],    #C4
                tuple([3,2]): [820,10],     #B4
                tuple([3,3]): [820,10.35]   #A4
                }

    #make shares/queues                      
    x_des = task_share.Share ('h', thread_protect = False, name = "x_des")              # desired x pos [mm]
    feed_des = task_share.Share ('h', thread_protect = False, name = "feed_des")        # desired feed angle [rad]
    bucket_des = task_share.Share ('h', thread_protect = False, name = "bucket_des")    # desired bucket motor angle [rad]
    shot = task_share.Share ('h', thread_protect = False, name = "shot")                # contains motor positions/speeds for the shot
    jog = task_share.Share ('h', thread_protect = False, name = "jog")                  # contains how much to jog the selected motor
    bl_speed = task_share.Share ('h', thread_protect = False, name = "bl_speed")        # contains brushless motor speed
    speed_des = task_share.Share ('f', thread_protect = False, name = "speed_des")      # desired brushless speed
    

    #flags
    z_flag = task_share.Share ('h', thread_protect = False, name = "z_flag")            # flag that says to zero everything
    m_flag = task_share.Share ('h', thread_protect = False, name = "m_flag")            # flag that says to switch to motor selection menu
    j_flag = task_share.Share ('h', thread_protect = False, name = "j_flag")            # flag that says to switch to jog menu
    a_flag = task_share.Share ('h', thread_protect = False, name = "j_flag")            # flag that says whether autoplay is on/off
    s_flag = task_share.Share ('h', thread_protect = False, name = "s_flag")            # flag that says to switch to brushless speed menu    
    shoot_flag = task_share.Share ('h', thread_protect = False, name = "shooting_flag")            # flag that says the shot is being taken
    set_flag = task_share.Share ('h', thread_protect = False, name = "set_flag")        # flag that says to set controller targets
    bcount = task_share.Share ('h', thread_protect = False, name = "bcount_flag")

    vcp = pyb.USB_VCP()
    fullin = list()
    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task_ui = cotask.Task(ui(vcp,lookup,fullin), name = 'Task_Ui', priority = 1, period = 5, profile = True, trace = False)
    task_movement = cotask.Task(movement(vcp), name = 'Task_Movement', priority = 1, period = 5, profile = True, trace = False)
    task_firing = cotask.Task(firing(vcp), name = 'Task_Firing', priority = 1, period = 5, profile = True, trace = False)
    cotask.task_list.append(task_ui)
    cotask.task_list.append(task_movement)
    cotask.task_list.append(task_firing)

    #making objects:
    #battleship 
    battleShip = battleship.battleship()

    #encoders
    print('\033c')
    print('\nEncoders Enabled')
    tim_enc1 = Timer(4,period = 65535, prescaler = 0)
    x_enc = Encoder.Encoder(tim_enc1,Pin.cpu.B7,Pin.cpu.B6)
    tim_enc2 = Timer(8,period = 65535, prescaler = 0)
    feed_enc = Encoder.Encoder(tim_enc2,Pin.cpu.C6,Pin.cpu.C7)
    #tim_enc3 = Timer(6,period = 65535, prescaler = 0)
    #feed_enc = Encoder.Encoder(tim_enc3,Pin.cpu.C7,Pin.cpu.C6) #need to set cpu pins for this one
    #tim_enc4 = Timer(6,period = 65535, prescaler = 0) #need a different timer

    #brushed motors
    print('Brushed Motors Enabled')
    tim_A = Timer(3, freq = 20000)
    tim_B = Timer(2, freq = 20000)
    tim_C = Timer(1, freq = 20000)
    x_mot = L6206.L6206(tim_A, Pin.cpu.B4, Pin.cpu.B5, Pin.cpu.A10)
    feed_mot = L6206.L6206(tim_B, Pin.cpu.A0, Pin.cpu.A1, Pin.cpu.C1)
    bucket_mot = MotorDriver.MotorDriver(tim_C, Pin.cpu.A8, Pin.cpu.A9)
    x_mot.enable()
    feed_mot.enable() #enables both bucket and feed motor cause same pin

    #brushless motors (80 mhz, 80 prescaler, each tick is 1 us)
    print('Brushless Motors Enabled')
    pin_for_ESC = Pin(Pin.cpu.A6, mode=Pin.OUT_PP)
    #pin_for_leftESC = Pin(Pin.cpu.A9, mode=Pin.OUT_PP)
    timer_pwm = Timer(16, freq=50)
    # direction based from looking towards motors looking towards direction that ball shoots
    #left_esc = timer_pwm.channel(2, mode=Timer.PWM, pin=pin_for_leftESC, pulse_width_percent=10)
    esc = timer_pwm.channel(1, mode=Timer.PWM, pin=pin_for_ESC, pulse_width_percent=10)

    #controllers
    x_controller = controller.controller()
    feed_controller = controller.controller()
    #misc

    input("Press enter once you have turned the power supply on")
    esc.pulse_width_percent(5)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()
    
    try:
        while(True):
            cotask.task_list.pri_sched()
    except KeyboardInterrupt:
        print('\n\r\r> Program Terminated')
        esc.pulse_width_percent(0)
        x_mot.set_duty(0)

    