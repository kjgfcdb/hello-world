import re
import random
import math
import numpy as np

def wgn(x,snr):
    '''
        White noise
    '''
    snr = 10**(snr/10.0)
    xpower = np.sum([i*i for i in x])/len(x)
    return np.random.randn(len(x)) * np.sqrt(xpower / snr)

def randPick(A1,A2):
    temp = [i for i in range(len(A1))]
    random.shuffle(temp)
    temp = temp[0:80]
    temp.sort()
    return [A1[i] for i in temp],[A2[i] for i in temp]

def filte(pitch):
    l = 0
    n = len(pitch)
    for i in range(0,n-1,1):
        if (pitch[i]>180):
            l = i
            break
    return l,l+149

def distance(S1_Ax,S1_Ay,S1_Az,tS1_Ax,tS1_Ay,tS1_Az):
    return math.sqrt((S1_Ax-tS1_Ax)**2+(S1_Ay-tS1_Ay)**2+(S1_Az-tS1_Az)**2)

def closest(x,ten,nine,eight,seven,six):
    return np.argmin([abs(x-six),abs(x-seven),abs(x-eight),abs(x-nine),abs(x-ten)])
def readFile(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        pitch,S1,S2 = [],[],[]
        for line in lines:
            temp = ret.findall(line)
            if "roll1" in line:
                pitch.append(float(temp[1][1:-1]))
                S1.append([float(temp[3][1:-1]),float(temp[4][1:-1]),float(temp[5][1:-1])])
            elif "roll2" in line:
                S2.append([float(temp[3][1:-1]),float(temp[4][1:-1]),float(temp[5][1:-1])])
    return pitch,S1,S2

#regular expression
ret = re.compile(r":.*?\]")

pitch,Sensor1,Sensor2 = readFile("./straightPunch/61.txt")
AcceleratedSpeed = [Sensor1[i] for i in range(len(Sensor2))]

print(len(AcceleratedSpeed))
# AcceleratedSpeed = randPick(AcceleratedSpeed)
l,r = filte(pitch)
r -= 70
AcceleratedSpeed = AcceleratedSpeed[l:r+1]
print("Standard data generated successfully.")
print("Standard data length : %d"%(len(AcceleratedSpeed)))
FILE_NUM = 120
dtwDistance = []
ten,nine,eight,seven,six = [],[],[],[],[]
for index in range(FILE_NUM):
    tpitch,tSensor1,tSensor2 = [],[],[]
    tAcceleratedSpeed = []
    tpitch,tSensor1,tSensor2 = readFile("./straightPunch/"+str(index)+".txt")
    label = int(open("./straightPunch/"+str(index)+".txt").readlines()[-1])
    for i in range(len(tSensor1)):
        tAcceleratedSpeed.append(tSensor1[i])
    bl,br = filte(tpitch)
    tAcceleratedSpeed = tAcceleratedSpeed[bl:bl+80]
    if len(tAcceleratedSpeed)==80:
        D = [[0 for i in range(len(tAcceleratedSpeed)+1)] for j in range(len(AcceleratedSpeed)+1)]
        for i in range(1,len(AcceleratedSpeed)+1):
            for j in range(1,len(tAcceleratedSpeed)+1):
                D[i][j] = distance(AcceleratedSpeed[i-1][0],AcceleratedSpeed[i-1][1],AcceleratedSpeed[i-1][2],\
                                tAcceleratedSpeed[j-1][0],tAcceleratedSpeed[j-1][1],tAcceleratedSpeed[j-1][2])\
                                +min(D[i][j-1],D[i-1][j],D[i-1][j-1])
        dtwDistance.append(D[len(AcceleratedSpeed)][len(tAcceleratedSpeed)])
        if label==10:
            ten.append(D[len(AcceleratedSpeed)][len(tAcceleratedSpeed)])
        elif label==9:
            nine.append(D[len(AcceleratedSpeed)][len(tAcceleratedSpeed)])
        elif label==8:
            eight.append(D[len(AcceleratedSpeed)][len(tAcceleratedSpeed)])
        elif label==7:
            seven.append(D[len(AcceleratedSpeed)][len(tAcceleratedSpeed)])
        elif label==6:
            six.append(D[len(AcceleratedSpeed)][len(tAcceleratedSpeed)])
        else:
            pass
#eight = [i-36 for i in eight]
print("Six : %f"%(np.mean(six)))
print("Seven : %f"%(np.mean(seven)))
print("Eight : %f"%(np.mean(eight)))
print("Nine : %f"%(np.mean(nine)))
print("Ten : %f"%(np.mean(ten)))

threshold = np.mean(six)
Matrix = np.matrix((np.ones((480,1))))
Label = np.matrix((np.ones((1,1))))
for ite in range(1):
    print(ite)
    mat = np.matrix((np.ones((480,1))))
    dtwDistance = []
    for index in range(FILE_NUM):
        tAcceleratedSpeed1 = []
        tAcceleratedSpeed2 = []
        tpitch,tSensor1,tSensor2 = readFile("./straightPunch/"+str(index)+".txt")
        for i in range(len(tSensor1)):
            tAcceleratedSpeed1.append(tSensor1[i])
            tAcceleratedSpeed2.append(tSensor2[i])
        bl,br = filte(tpitch)
        # 窗口滑动
        bias = random.randint(-5,5)
        bl = bl+bias
        tAcceleratedSpeed1 = tAcceleratedSpeed1[bl:-1]
        tAcceleratedSpeed2 = tAcceleratedSpeed2[bl:-1]
        # 白噪声
        ax = [i[0] for i in tAcceleratedSpeed1]+wgn([i[0] for i in tAcceleratedSpeed1],20)
        ay = [i[1] for i in tAcceleratedSpeed1]+wgn([i[1] for i in tAcceleratedSpeed1],20)
        az = [i[2] for i in tAcceleratedSpeed1]+wgn([i[2] for i in tAcceleratedSpeed1],20)
        tAcceleratedSpeed1 = [[ax[i],ay[i],az[i]] for i in range(len(tAcceleratedSpeed1))]
        ax = [i[0] for i in tAcceleratedSpeed2]+wgn([i[0] for i in tAcceleratedSpeed2],20)
        ay = [i[1] for i in tAcceleratedSpeed2]+wgn([i[1] for i in tAcceleratedSpeed2],20)
        az = [i[2] for i in tAcceleratedSpeed2]+wgn([i[2] for i in tAcceleratedSpeed2],20)
        tAcceleratedSpeed2 = [[ax[i],ay[i],az[i]] for i in range(len(tAcceleratedSpeed2))]
        # 随机取80个点
        tAcceleratedSpeed1,tAcceleratedSpeed2 = randPick(tAcceleratedSpeed1,tAcceleratedSpeed2)
        if len(tAcceleratedSpeed1)==80:
            D = [[0 for i in range(len(tAcceleratedSpeed1)+1)] for j in range(len(AcceleratedSpeed)+1)]
            for i in range(1,len(AcceleratedSpeed)+1):
                for j in range(1,len(tAcceleratedSpeed1)+1):
                    D[i][j] = distance(AcceleratedSpeed[i-1][0],AcceleratedSpeed[i-1][1],AcceleratedSpeed[i-1][2],\
                                    tAcceleratedSpeed1[j-1][0],tAcceleratedSpeed1[j-1][1],tAcceleratedSpeed1[j-1][2])\
                                    +min(D[i][j-1],D[i-1][j],D[i-1][j-1])

            if D[len(AcceleratedSpeed)][len(tAcceleratedSpeed1)] <= threshold+30:
                AcceleratedSpeed = AcceleratedSpeed[:80]
                dtwDistance.append(D[len(AcceleratedSpeed)][len(tAcceleratedSpeed1)])
                ax1 = [tAcceleratedSpeed1[i][0] for i in range(len(tAcceleratedSpeed1))]
                ay1 = [tAcceleratedSpeed1[i][1] for i in range(len(tAcceleratedSpeed1))]
                az1 = [tAcceleratedSpeed1[i][2] for i in range(len(tAcceleratedSpeed1))]
                ax2 = [tAcceleratedSpeed2[i][0] for i in range(len(tAcceleratedSpeed2))]
                ay2 = [tAcceleratedSpeed2[i][1] for i in range(len(tAcceleratedSpeed2))]
                az2 = [tAcceleratedSpeed2[i][2] for i in range(len(tAcceleratedSpeed2))]
                mat = np.column_stack((mat,np.matrix(np.array(ax1+ay1+az1+ax2+ay2+az2)).T))
    label = [closest(i,np.mean(ten),np.mean(nine),np.mean(eight),np.mean(seven),np.mean(six)) for i in dtwDistance]
    Label = np.column_stack((Label,np.asmatrix(label)))
    Matrix = np.column_stack((Matrix,mat[:,1:]))
Label = Label[:,1:]
Matrix = Matrix[:,1:]
np.savetxt("Matrix.txt",Matrix)
np.savetxt("Label.txt",Label)
