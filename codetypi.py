import sys, time, random
from serial import Serial

serialPort = Serial("/dev/ttyAMA0",9600)

if (serialPort.isOPen() == False):
    serialPort.open()

RESET = "\x1b[0m"

SCORES = {"0": [[30,31,32],[30,32],[30,32],[30,32],[30,31,32]],
          "1": [[32],[32],[32],[32],[32]],
          "2": [[30,31,32],[32],[30,31,32],[30],[30,31,32]],
          "3": [[30,31,32],[32],[30,31,32],[32],[30,31,32]],
          "4": [[30,32],[30,32],[30,31,32],[32],[32]],
          "5": [[30,31,32],[30],[30,31,32],[32],[30,31,32]],
          "6": [[30,31,32],[30],[30,31,32],[30,32],[30,31,32]],
          "7": [[30,31,32],[32],[32],[32],[32]],
          "8": [[30,31,32],[30,32],[30,31,32],[30,32],[30,31,32]],
          "9": [[30,31,32],[30,32],[30,31,32],[32],[32]],
          "all": [[30,31,32],[30,31,32],[30,31,32],[30,31,32],[30,31,32]]}

print("\x1b[?25l")

def drawArena():
    for i in [3,7,11,15,19,23]:
        serialPort.write("\x1b[" + str(i) + ";40f\x1b[" + str(47) + "m " + RESET )
        serialPort.write("\x1b[" + str(i+1) + ";40f\x1b[" + str(47) + "m " + RESET)

def score(score1,score2):
    score1 = SCORES[str(score1)]
    score2 = SCORES[str(score2)]
    for i in range(len(score1)):
        for j in SCORES["all"][i]:
            serialPort.write("\x1b[" + str(i+2) + ";" + str(j) + "f\x1b[39m " + RESET)
            serialPort.write("\x1b[" + str(i+2) + ";" + str(18+j) + "f\x1b[39m " + RESET)
    for i in range(len(score1)):
        for j in score1[i]:
            serialPort.write("\x1b[" + str(i+2) + ";" + str(j) + "f\x1b[47m " + RESET)
        for j in score2[i]:
            serialPort.write("\x1b[" + str(i+2) + ";" + str(j+18) + "f\x1b[47m " + RESET)

def drawPaddle(pos,posv):
    serialPort.write("\x1b[" + str(13) + ";" + str(posv) + "f\x1b[" + str(42) + "m " + RESET)
    serialPort.write("\x1b[" + str(12) + ";" + str(posv) + "f\x1b[" + str(42) + "m " + RESET)
    serialPort.write("\x1b[" + str(11) + ";" + str(posv) + "f\x1b[" + str(42) + "m " + RESET)

def movePaddleUp(paddle,pos,posv):
    for i in [pos, pos+1, pos-1]:
        if pos - 1 < 2:
            return False
        if i == pos-1:           
            serialPort.write("\x1b[" + str(pos-2) + ";" + str(posv) + "f\x1b[" + str(42) + "m " + RESET)
        if i == pos:
            serialPort.write("\x1b[" + str(pos) + ";" + str(posv) + "f\x1b[" + str(42) + "m " + RESET)
        else:
            serialPort.write("\x1b[" + str(pos+1) + ";" + str(posv) + "f\x1b[" + str(39) + "m " + RESET)

def movePaddleDown(paddle,pos,posv):
    for i in [pos, pos+1, pos-1]:
        if pos + 1 >= 23:
            return False
        if i == pos-1:           
            serialPort.write("\x1b[" + str(pos-2) + ";" + str(posv) + "f\x1b[" + str(39) + "m " + RESET)
        if i == pos:
            serialPort.write("\x1b[" + str(pos) + ";" + str(posv) + "f\x1b[" + str(42) + "m " + RESET)
        else:
            serialPort.write("\x1b[" + str(pos+1) + ";" + str(posv) + "f\x1b[" + str(42) + "m " + RESET)

def drawBall(paddle): # sets up ball before the game starts to play
    if paddle == 1:
        posv = 4
    else:
        posv = 76
    serialPort.write("\x1b[" + str(12) + ";" + str(posv) + "f\x1b[" + str(42) + "m " + RESET)

def serveBall(pos,paddle): # this moves the ball with the paddle before the game has started
    if paddle == 1:
        posv = 4
    else:
        posv = 76 # again need to edit this slightly so it can move up and down with player2
    serialPort.write("\x1b[" + str(pos+1) + ";" + str(posv) + "f\x1b[" + str(39) + "m " + RESET)
    serialPort.write("\x1b[" + str(pos) + ";" + str(posv) + "f\x1b[" + str(42) + "m " + RESET)
    serialPort.write("\x1b[" + str(pos-1) + ";" + str(posv) + "f\x1b[" + str(39) + "m " + RESET)
    return posv, pos

def moveBall(x,y,ballXDir, ballYDir,speed, score1, score2):
    x = x + ballXDir
    y = y - ballYDir
    colour = 39
    space = 42
    numbers = [2,3,4,5,6]
    if y in numbers:
        score1 = SCORES[str(score1)]
        score2 = SCORES[str(score2)]
        for i in range(len(score1)):
            for j in score1[i]:
                if x == j:
                    colour = 47
            for z in score2[i]:
                if x == z:
                    colour = 47
    if x == 40:
        if y in [3,4,7,8,11,12,15,16,19,20,23,24]:
            colour = 47
                    
    serialPort.write("\x1b[" + str(y) + ";" + str(x) + "f\x1b[" + str(space) + "m " + RESET)
    time.sleep(speed)
    serialPort.write("\x1b[" + str(y) + ";" + str(x) + "f\x1b[" + str(colour) + "m " + RESET)
    return x,y

def checkEdgeCollision(x,y,ballXDir,ballYDir,score1,score2):
    if y == 23 or y == 0:
        ballYDir = ballYDir * -1
    if x == 0:
        score2 += 1
        main(score1,score2)
    if x == 80:
        score1 +=1
        main(score1,score2)
    return ballYDir,score1,score2

def checkHitBall(x, y, ballXDir, pos1, pos2, speed):
    if ballXDir == -1 and y in [pos1+1, pos1, pos1-1] and x == 4:
        ballXDir = ballXDir * -1
        speed = (random.uniform(0.1,0.5))
    if ballXDir == 1 and y in [pos2+1,pos2, pos2-1] and x == 76:
        ballXDir = ballXDir * -1
        speed = (random.uniform(0.01,0.07))
    return ballXDir, speed

def reset(pos2,pos2v,pos1,pos1v):

    # did it to put the game back to the starting positions but will keep the score, we may need to build that into this function
    for i in range(24): # rewrites where the paddles end in white space (i.e removes them)
        serialPort.write("\x1b[" + str(i) + ";" + str(3) + "f\x1b[" + str(39) + "m " + RESET)
        time.sleep(0.05)
        serialPort.write("\x1b[" + str(i) + ";" + str(77) + "f\x1b[" + str(39) + "m " + RESET)
        time.sleep(0.05)
    drawPaddle(pos2,pos2v) # redraws the paddles at the starting position (pos, i.e 12)
    drawPaddle(pos1,pos1v)
    for i in range(24): # rewrites where the ball ended with white space (i.e removes the ball)
        serialPort.write("\x1b[" + str(i) + ";" + str(4) + "f\x1b[" + str(39) + "m " + RESET)
        time.sleep(0.05)
        serialPort.write("\x1b[" + str(i) + ";" + str(76) + "f\x1b[" + str(39) + "m " + RESET)
        time.sleep(0.05)
    drawBall(2) # redraws the ball at the starting position (which is 12)
    time.sleep(0.5)

def main(score1,score2):

    ballXDir = 1
    ballYDir = 1

    pos1 = 12
    pos2 = 12
    pos1v = 3
    pos2v = 77

    speed = 0.04
    # test functions
##    drawPaddle(pos1,pos1v)
##    drawPaddle(pos2,pos2v)
##    drawBall(1)

    reset(pos2,pos2v,pos1,pos1v)
    score(score1,score2)

    for i in range(5):
        if movePaddleDown(1,pos1,pos1v) == False:
            pos1 = pos1
        else:
            x,y = serveBall(pos1,1)
            pos1 += 1
        time.sleep(0.1)

    for i in range(2):
        if movePaddleUp(1,pos1,pos1v) == False:
            pos1 = pos1
        else:
            pos1 -= 1
            x,y = serveBall(pos1,1)
        time.sleep(0.1)

    for i in range(360):
        ballYDir,score1,score2 = checkEdgeCollision(x,y,ballXDir,ballYDir,score1,score2)
        ballXDir,speed = checkHitBall(x, y, ballXDir, pos1,pos2, speed)
        x,y = moveBall(x,y,ballXDir, ballYDir,speed, score1, score2)

def end(winner):
    serialPort.write(str(winner) + "is the winner")
        
if __name__=='__main__':
    drawArena()
    main(0,0)

# need the game to end and a winner to be declared
# need to implement making the bats bigger
# need to put white spaces after the ball is served
# need to work out the order of service
# need to work out how the buttons and controllers etc are gonna work with this 
