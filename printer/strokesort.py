from time import sleep

from RpiMotorLib import RpiMotorLib
from gpiozero import Servo

from printer.util import *

x_turn = True
y_turn = True
x_gate = True
y_gate = True


def sortlines(lines):
    print("optimizing stroke sequence...")
    clines = lines[:]
    slines = [clines.pop(0)]
    while clines != []:
        x, s, r = None, 1000000, False
        for l in clines:
            d = distsum(l[0], slines[-1][-1])
            dr = distsum(l[-1], slines[-1][-1])
            if d < s:
                x, s, r = l[:], d, False
            if dr < s:
                x, s, r = l[:], s, True

        clines.remove(x)
        if r == True:
            x = x[::-1]
        slines.append(x)
    return slines


def visualize(lines):
    import turtle
    wn = turtle.Screen()
    t = turtle.Turtle()
    t.speed(0)
    t.pencolor('red')
    t.pd()
    for i in range(0, len(lines)):
        for p in lines[i]:
            t.goto(p[0] * 640 / 1024 - 320, -(p[1] * 640 / 1024 - 320))
            t.pencolor('black')
        t.pencolor('red')
    turtle.mainloop()


def print_drawing(lines):
    # booleans used for while loop control a bit later
    global x_gate
    global y_gate
    global x_turn
    global y_turn
    # initialize a servo opject from the gpiozero library as GPIO pin 20
    servo = Servo(20)

    # calibrated value such that the pen will be off the paper
    servo.value = -1
    # give time for the pen to be lifted off the paper
    sleep(0.5)

    # initialize both steppers and corresponding GPIO pins (4 each)
    Motorname = "MyMotorOne"
    Motortype = "Nema"
    x_motor = RpiMotorLib.BYJMotor(Motorname, Motortype)
    A11 = 19
    A12 = 26
    B11 = 21
    B12 = 13
    GpioPins = [A11, B11, A12, B12]

    Motorname2 = "MyMotorTwo"
    Motortype2 = "Nema"
    y_motor = RpiMotorLib.BYJMotor(Motorname2, Motortype2)
    A11_2 = 5
    A12_2 = 6
    B11_2 = 12
    B12_2 = 16
    GpioPins2 = [A11_2, B11_2, A12_2, B12_2]

    # parameters for the rpigpiolib library
    verbose = False
    steptype = "half"
    initdelay = 0.001

    # record the abolsute position of the pen relative to the start (assume (0,0) start)
    absolute_pos = [0, 0]

    # iterate over the list of continuous lines
    for i in range(0, len(lines)):

        # defining movement vectors from the end of the old line to the start of the new line
        # the pen is lifted because we are moving between continuous lines, not within a continuous line
        new_line_x = (lines[i][0][0] - absolute_pos[0])
        new_line_y = (lines[i][0][1] - absolute_pos[1])
        # update the absolute position
        absolute_pos[0] += new_line_x
        absolute_pos[1] += new_line_y

        # This one is interesting
        # We found the x and y axes behave differently given the same number of stepper motor steps
        # The pully system on the y axis was significantly stiffer, manually account for this
        steps_x = abs(new_line_x) // 2  # No of step sequences
        steps_y = abs(new_line_y) // 1.5

        # define motor speeds so that neither x or y finsishes moving without the other
        if abs(new_line_x) > abs(new_line_y) and new_line_x != 0 and new_line_y != 0:
            x_wait = 0.001
            y_wait = 0.001 * abs((new_line_x / new_line_y))
        elif new_line_x != 0 and new_line_y != 0:
            y_wait = 0.001
            x_wait = 0.001 * abs((new_line_y / new_line_x))
        else:
            pass

        # define movement direction based on the sign of each vector
        if new_line_x > 0:
            x_turn = True
        else:
            x_turn = False

        if new_line_y > 0:
            y_turn = True
        else:
            y_turn = False

        # defining callback functions for the x and y motion - this is so we can thread the processes
        def new_x_motion():
            global x_turn
            global x_gate
            x_motor.motor_run(GpioPins, x_wait, steps_x, ccwise=x_turn, verbose=False, steptype='half', initdelay=0.001)
            x_gate = False

        def new_y_motion():
            global x_turn
            global y_gate
            y_motor.motor_run(GpioPins2, y_wait, steps_y, ccwise=y_turn, verbose=False, steptype='half',
                              initdelay=0.001)
            y_gate = False

        # start the thread - lets x and y move at same time
        Thread(target=new_x_motion).start()
        Thread(target=new_y_motion).start()

        # prevents execution of next movement until the threads are completed - enforces movements happen
        # in the order that they should
        while x_gate == True or y_gate == True:
            pass

        # move the servo to place the pen down
        servo.value = 0
        sleep(0.5)

        # iterate over the points in each line - pen will remain down the whole time
        for j in range(len(lines[i]) - 1):

            # used for while loop control
            x_gate = True
            y_gate = True
            print(lines[i])

            # calculate movement vector
            mov_x = (lines[i][j + 1][0] - lines[i][j][0])
            mov_y = (lines[i][j + 1][1] - lines[i][j][1])
            print(mov_x)
            # update the position
            absolute_pos[0] += mov_x
            absolute_pos[1] += mov_y

            steps_x = abs(mov_x) // 2  # No of step sequences
            steps_y = abs(mov_y) // 1.5

            # properly set servo speed (Same as above)
            if abs(mov_x) > abs(mov_y) and mov_x != 0 and mov_y != 0:
                x_wait = 0.001 * 2
                y_wait = 0.001 * abs((mov_x / mov_y))
            elif mov_x != 0 and mov_y != 0:
                y_wait = 0.001
                x_wait = 0.001 * abs((mov_y / mov_x)) * 2
            else:
                pass

            # set movement direction (same as above)
            if mov_x > 0:
                x_turn = True
            else:
                print('here')
                x_turn = False

            if mov_y > 0:
                y_turn = True
            else:
                y_turn = False

            # callback functions for x and y motion, same as above
            def x_motion():
                print('x step confirmation is' + str(mov_x))

                global x_turn
                print('x turn is' + str(x_turn))
                global x_gate
                x_motor.motor_run(GpioPins, x_wait, steps_x, ccwise=x_turn, verbose=False, steptype='half',
                                  initdelay=0.01)
                x_gate = False

            def y_motion():
                global y_turn
                global y_gate
                y_motor.motor_run(GpioPins2, y_wait, steps_y, ccwise=y_turn, verbose=False, steptype='half',
                                  initdelay=0.01)
                y_gate = False

            # start the thread

            Thread(target=x_motion).start()
            Thread(target=y_motion).start()

            # hold in while loop until the threads are complete

            while x_gate == True or y_gate == True:
                pass

            x_gate = True
            y_gate = True

        # this continuous line has finished, lift the pen
        servo.value = -1
        sleep(0.5)

    # at the very end move steppers back to start position
    x_motor.motor_run(GpioPins, 0.0015, absolute_pos[0] // 2, False, verbose, steptype, initdelay)
    y_motor.motor_run(GpioPins2, 0.0015, absolute_pos[1] // 1.5, False, verbose, steptype, initdelay)

# if __name__=="__main__":
# import linedraw
# #linedraw.draw_hatch = False
# lines = linedraw.sketch("Lenna")
# #lines = sortlines(lines)
# visualize(lines)
