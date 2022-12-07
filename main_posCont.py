from pyb import UART
from pyb import Pin
from pyb import Timer
import micropython
import task_share
import task_share
import cotask
import Encoder
import L6206
import controller
import time
def control():
    state = 1 
    x_meas_pos = 0
    feed_mot_pos = 0
    while True:
        if state == 1:
            enc1.update()
            bucket_mot.set_duty(5)
            x_meas_pos = -enc1.position # mm
            mot_A.set_duty(x_posControl.pi(x_meas_pos))
            vcp.write('XPos at: ' + str(x_meas_pos) + ' ticks\r\n')
            vcp.write('Mot B Duty set to: ' + str(x_posControl.p(x_meas_pos)) + '\r\n')
            if(x_posControl.pi(x_meas_pos) <= 5):
                state = 2
                vcp.write('Feed Control')
        elif state == 2:
            enc2.update()
            feed_mot_pos = (enc2.position/(16*256*4))*6.283*57.2958 # degrees
            mot_B.set_duty(tilt_control.p(feed_mot_pos))
            vcp.write('Feed at: ' + str(feed_mot_pos) + ' degrees\r\n')
            vcp.write('Mot B Duty set to: ' + str(tilt_control.p(feed_mot_pos)) + '\r\n')
            if(tilt_control.p(feed_mot_pos) <= 20):
                state = 3
                vcp.write('Next Pos\r\n')
        elif state == 3: 
            enc1.update()
            x_posControl.set_Target(0)
            state = 1
            vcp.write('state 3\r\n')
        yield(0)

if __name__ == '__main__':
    #timer 4 ch2: b7, ch1: b6
    #timer 8 ch2: c7, ch1: c6
    print('Running')
    vcp = pyb.USB_VCP()
    #encoder setup stuff
    print('Encoder Enabled')
    cpr = 256
    gearrat = 16
    tim_enc1 = Timer(4,period = 65535, prescaler = 0)
    enc1 = Encoder.Encoder(tim_enc1,Pin.cpu.B7,Pin.cpu.B6)
    tim_enc2 = Timer(8,period =  65535, prescaler = 0)
    enc2  = Encoder.Encoder(tim_enc2, Pin.cpu.C6,Pin.cpu.C7)

    #motor setup stuff
    print('Motor Enabled')
    tim_A = Timer(3, freq = 20000)
    tim_B = Timer(2, freq = 20000)
    tim_C = Timer(1, freq = 20000)
    mot_A = L6206.L6206(tim_A, Pin.cpu.B4, Pin.cpu.B5,Pin.cpu.A10)
    mot_A.enable()
    mot_B = L6206.L6206(tim_B, Pin.cpu.A0, Pin.cpu.A1,Pin.cpu.C1)
    mot_B.enable() 
    bucket_mot = L6206.L6206(tim_C, Pin.cpu.A8, Pin.cpu.A9, Pin.cpu.C1)
    bucket_mot.enable()
    #closed loop controller
    x_posControl = controller.controller()
    tilt_control = controller.controller()
    #set ki, kp for pos control 
    x_posControl.set_kp(1)
    x_posControl.set_ki(0.0001)

    tilt_control.set_ki(0)
    tilt_control.set_kp(0.5)

    #encoder pos in ticks and degrees
    x_posControl.set_Target(5000)
    tilt_control.set_Target(90)
    
    
    pin_for_ESC = Pin(Pin.cpu.A6, mode=Pin.OUT_PP)
    timer_pwm = Timer(16, freq=50)
    esc = timer_pwm.channel(1, mode=Timer.PWM, pin=pin_for_ESC, pulse_width_percent=10)
    esc.pulse_width_percent(5)
    

    task_control = cotask.Task(control(), name = 'Task_Control', priority = 1, period = 5, profile = True, trace = False)
    cotask.task_list.append(task_control)
    enc1.zero()
    try:
        while(True):
            cotask.task_list.pri_sched()
    except KeyboardInterrupt:
        print('\n\r> Program Terminated')
        mot_B.set_duty(-50)
        time.sleep(0.5)
        mot_B.set_duty(0)
        mot_A.set_duty(0)
        bucket_mot.set_duty(0)
