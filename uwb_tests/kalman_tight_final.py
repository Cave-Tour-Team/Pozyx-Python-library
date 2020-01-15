import numpy as np
import math
from numpy import *
from numpy.linalg import inv,det
import pylab
import matplotlib.pyplot as plt
import csv

############################################################
Vel_est = 0
weight_pos = 2000
weight_vel = 10
weight_dist = 10                                                                                                                                                                                                                                                                                                
############################################################

#Function to estimate the state and the error covariance matrix

def kf_predict(dX, P, phi, Q):
    par_pr = dot(phi, dX)
    phi_pr = dot(phi, dot(P, np.transpose(phi))) + Q
    return (par_pr,phi_pr)

#function to update the state and covariance matrix

def kf_update(par_pr, phi_pr, H, R, I, sol, z):
    IM = dot(H, par_pr)
    IM = np.transpose(IM)
    z = np.transpose(z)
    V_pred = z - IM
    V_pred = np.transpose(V_pred)
    abs_V_pred = abs(V_pred)
    max_v = abs(abs_V_pred.max())
    if max_v > 100:
        index = np.argmax(abs_V_pred)
        H = np.delete(H, index, 0)
        z = np.delete(z, index, 1)
        R = np.delete(R, index, 1)
        R = np.delete(R, index, 0)
        IM = dot(H, par_pr)
        IM = np.transpose(IM)
        V_pred = z - IM
        V_pred = np.transpose(V_pred)               
    IS = R + dot(H, dot(phi_pr, np.transpose(H)))
##    print('IS = ', IS)
##    print('H = ', H)
    K = dot(phi_pr, dot(np.transpose(H), inv(IS))) 
    par_pr = np.transpose(par_pr)
    dX = par_pr + np.transpose(dot(K, V_pred))
    dX = np.transpose(dX)
    P_new = dot(phi_pr, dot((I - dot(K, H)), np.transpose(I - dot (K, H)))) + dot(K, dot(R,np.transpose(K)))
    P = P_new
    X = sol + dX
    return (X,dX,P)

input_file = '/home/pi/Kalman_Filter/T1IMU4Anc.csv'
input_file1 = '/home/pi/Kalman_Filter/T1IMU4Anc.txt'

anchor_coord = '/home/pi/Kalman_Filter/coordinates_ismb.txt'
n_unk = 3
n_meas = 4

Col1 = []
Col2 = []
Col3 = []
Col4 = []
Col5 = []
Col6 = []
Col7 = []
Col8 = []
Col9 = []
Col10 = []
Col11 = []
##
##
##Colg1 = []
##Colg2 = []
##Colg3 = []
##Colg4 = []
##Colg5 = []
##Colg6 = []
##Colg7 = []
##Colg8 = []
##Colg9 = []
##Colg10 = []
##Colg11 = []

Anc_Col1 = []
Anc_Col2 = []
Anc_Col3 = []

##with open (input_file) as f:
##    for line in f:
##        data = line.split()
with open (input_file, 'r') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    next(readCSV)
    next(readCSV)
    for row in readCSV:
        Col1.append(float(row[0]))
        Col2.append(float(row[1]))
        Col3.append(float(row[2]))
        Col4.append(float(row[3]))
        Col5.append(float(row[4]))
        Col6.append(float(row[5]))
        Col7.append(float(row[6]))
        Col8.append(float(row[7]))
        Col9.append(float(row[8]))
        Col10.append(float(row[9]))
        Col11.append(float(row[10]))

input_data = np.matrix([Col1, Col2, Col3, Col4, Col5, Col6, Col7, Col8, Col9, Col10, Col11])
input_data = np.transpose(input_data)

with open (anchor_coord) as g:
    for lines in g:
        data1 = lines.split()
        Anc_Col1.append(int(data1[0]))
        Anc_Col2.append(int(data1[1]))
        Anc_Col3.append(int(data1[2]))
        
coord_data = np.matrix([Anc_Col1,Anc_Col2,Anc_Col3])
coord_data = np.transpose(coord_data)


#time step of mobile movement
dt = 0.1
#Initialization of state matrices
du = zeros(n_unk)
dX = np.transpose(du)
phi = eye(n_unk)
P = inv(weight_pos * eye(n_unk))
I = eye(n_unk)
Q = inv(weight_pos * eye(n_unk))
X = array([[input_data[0,0]], [input_data[0,1]], [input_data[0,2]]])
obs = []
z = []
ep = 1
sol = X 
R = inv(weight_dist*eye(n_meas))
X_coord = []
X1_coord = []
Y_coord = []
Y1_coord = []
Z_coord = []
Z1_coord = []
C = []
D = []
E = []
difference = []
if Vel_est == 1:
    X = array([[input_data[0,0]], [input_data[0,1]], [input_data[0,2]], [0], [0], [0]])
    du = zeros(2*n_unk)
    dX = np.transpose(du)
    sol = X 
    I = eye(2*n_unk)
    P = inv(weight_pos * eye(2*n_unk))
    P[3][3] = 1/weight_vel
    P[4][4] = 1/weight_vel
    P[5][5] = 1/weight_vel
    
while (ep < len(input_data)):
    
    if input_data[ep,:].any() == 0:
        sol = NaN
        np.delete(input_data[ep,:], 0)
        ep = ep + 1
        
    else:
          
        H = []
        z = []
        B = []
        for ind in range(0,n_meas):
            rang = []
            rang = math.sqrt((coord_data[ind,0] - X[0][0])**2 + (coord_data[ind,1] - X[1][0])**2 + (coord_data[ind,2] - X[2][0])**2)
            H0 = -((coord_data[ind,0] - X[0][0])/rang)
            H1 = -((coord_data[ind,1] - X[1][0])/rang)
            H2 = -((coord_data[ind,2] - X[2][0])/rang)
            obs = np.transpose(input_data[ep,4+2*ind-1])
            z1 = [obs - rang]
            z.append(z1)
        
            if Vel_est == 1:
                H4 = [H0, H1, H2, 0, 0, 0]
                H.append(H4)
                phi = eye(2*n_unk)
                phi[0][3] = dt
                phi[1][4] = dt
                phi[2][5] = dt
                Q = inv(weight_pos * eye(2*n_unk))
                Q[3][3] = 1/weight_vel
                Q[4][4] = 1/weight_vel
                Q[5][5] = 1/weight_vel
        
            else:           
                H_mat = [H0, H1, H2]
                H.append(H_mat)
            
        (par_pr,phi_pr) = kf_predict(dX, P, phi, Q)
        (X,dX,P) = kf_update(par_pr, phi_pr, H, R, I, sol, z)        
    ##    if not sol.all():
    ##    check = np.array(X)
        sol1 = X
    ##    print('sol1 = ', sol1)
        B = np.transpose(sol1)
        X1 = sol1[0][0]
        X_coord.append(X1)
        Y1 = sol1[1][0]
        Y_coord.append(Y1)
        Z1 = sol1[2][0]
        Z_coord.append(Z1)

        if (ep > 1):
            C1 = X_coord[ep-1] - X_coord[ep-2]
            C2 = Y_coord[ep-1] - Y_coord[ep-2]
            C3 = Z_coord[ep-1] - Z_coord[ep-2]
        
            if (abs(C1) < 1000):
                if(abs(C2) < 1000):
                    if (abs(C3) < 5000):
                        sol = sol1
    ##                    print('sol = ', sol)
                        C.append(C1)
                        D.append(C2)
                        E.append(C3)           
                        B = np.transpose(sol)
                        X1 = sol[0][0]
                        X1_coord.append(X1)
                        Y1 = sol[1][0]
                        Y1_coord.append(Y1)
                        Z1 = sol[2][0]
                        Z1_coord.append(Z1)

                        difference1 = [B[0][0]-input_data[ep,0], B[0][1]-input_data[ep,1], B[0][2]-input_data[ep,2]]
                        difference.append(difference1)
    ##                    print('C = ', C)
    ##                    print('D = ', D)
    ##                    print('E = ', E)
    ##                    print(X1_coord)
    ##                    print(Y1_coord)
    ##                    print(Z1_coord)
    ##                    print('ep = ', ep)
    ##    print('ep = ', ep+1)
    ##    print(X1_coord)
        ep = ep + 1
##print(X1_coord)
##print('C = ', C)
##print('D = ', D)
##print('E = ', E)

##plt.figure(1)
##plt.plot(C, '*r')
##pylab.grid(True)
##
##plt.figure(2)
##plt.plot(D, '*g')
##pylab.grid(True)
##
##plt.figure(3)
##plt.plot(E, '*b')
##pylab.grid(True)

##
plt.figure(1)
plt.plot(X1_coord,Y1_coord, '*r')
plt.plot(input_data[:,0],input_data[:,1], '.b')
####plt.plot(input_data1[:,0],input_data1[:,1], '.g')
plt.plot(coord_data[:,0], coord_data[:,1], 'og')
pylab.grid(True)
######
########
########plt.figure(2)
########plt.plot(difference)
########pylab.grid(True)
########pylab.legend(('X[mm]','Y[mm]','Z[mm]'),'upper center',shadow=True)
########pylab.title("Difference between computed and estimated values")
plt.show()
##
