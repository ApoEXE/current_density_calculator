#!/usr/bin/env python
import serial
import time
import matplotlib.pyplot as plt
from functools import partial
import csv
import numpy as np
from scipy.integrate import simpson
from numpy import trapz

raw_data = []
shut_mv = []
busV = []
loadV = []
load_ma = []
pwr_mw = []
t_date = []


SerialObj = serial.Serial('COM5') # COMxx  format on Windows
                  # ttyUSBx format on Linux
SerialObj.baudrate = 115200  # set Baud rate to 9600
SerialObj.bytesize = 8   # Number of data bits = 8
SerialObj.parity  ='N'   # No parity
SerialObj.stopbits = 1   # Number of Stop bits = 1
time.sleep(3)


with open('data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)

    start = time.time()
    ind = 0
    while time.time()-start <= 30:
        ind = ind+1
        ReceivedString = SerialObj.readline()
        #print(ReceivedString.decode("Ascii"))
        try:
            raw = ReceivedString.decode("Ascii")
            raw_data=raw.split("|")
            time_pass = round(float(time.time()-start),3)
            print(f'{ind} {time_pass} {raw_data}')
            #print(raw_data)
           
            writer.writerow([time_pass,float(raw_data[0]),float(raw_data[1]),float(raw_data[2]),float(raw_data[3]),float(raw_data[4])])
            shut_mv.append(float(raw_data[0]))
            busV.append(float(raw_data[1]))
            loadV.append(float(raw_data[2]))
            load_ma.append(float(raw_data[3]))
            pwr_mw.append(float(raw_data[4]))
            t_date.append(time_pass)
        except:
            print("")



# The y values.  A numpy array is used here,
# but a python list could also be used.
y = np.array(load_ma)
x = np.array(t_date)

def get_next_and_before_values(arr, i):
    before = arr[i-1] if i > 0 else 0
    after = arr[i+1] if i < len(arr)-1 else 0
    return float(before), float(after)

i = 0
pos_flag = 0

for i in range(len(y)):
    before, after = get_next_and_before_values(y, i)
    if  after-before > 0.1 and float(before) <0.1  and float(y[i-2]) < 0.1 and np.mean(y[i+1:i+10]) >= 0.22:
     #print(f"positive Before: {before}, After: {after} before_before {y[i-2]} i: {i} time {x[i]}")
     break
start_j = i
for i in range(start_j,len(y)):
    before, after = get_next_and_before_values(y, i)
    if  after-before < 0  and before >0.1 and np.mean(y[i+1:i+10]) < 0.1:
     #print(f"negative Before: {before}, After: {after} before_before {y[i-2]} i: {i} time {x[i]}")
     break
stop_j = i
#----------

for i in range(stop_j,len(y)):
    before, after = get_next_and_before_values(y, i)
    if  after-before > 0.1 and float(before) <0.1  and float(y[i-2]) < 0.1 and np.mean(y[i+1:i+10]) >= 0.22:
     print(f"positive Before: {before}, After: {after} before_before {y[i-2]} i: {i} time {x[i]}")
     break
start_j = i
point_start_1 = start_j
for i in range(start_j,len(y)):
    before, after = get_next_and_before_values(y, i)
    if  after-before < 0  and before >0.1 and np.mean(y[i+1:i+10]) < 0.1:
     print(f"negative Before: {before}, After: {after} before_before {y[i-2]} i: {i} time {x[i]}")
     break
stop_j = i

point_stop_1 = stop_j

for i in range(stop_j,len(y)):
    before, after = get_next_and_before_values(y, i)
    if  after-before > 0.1 and float(before) <0.1  and  np.mean(y[i-10:i]) < 0.1 and np.mean(y[i+1:i+10]) >= 0.22:
     print(f"positive Before: {before}, After: {after} before_before {y[i-2]} i: {i} time {x[i]}")
     break
start_j = i
point_start_2 = start_j

start_T = point_start_1
stop_T = point_start_2
period = (float(x[stop_T])-float(x[start_T]))
print(f'Period in seconds: {round(period,2)} ON {round(float(float(x[point_stop_1])-x[point_start_1]),2)} SLEEP {round(float(float(x[point_start_2])-x[point_stop_1]),2)}')
# Compute the area using the composite trapezoidal rule.
area = trapz(y[int(start_T):int(stop_T)], x[int(start_T):int(stop_T)])
print(f'consumed = {round(area/period,3)} mA')

mean_mA = np.mean(y[start_T:stop_T])
print(f'mean consumed: {round(mean_mA,3)} mA')


       
plt.plot( x[start_T:stop_T], y[start_T:stop_T],marker = 'o')
plt.title("Real Time plot")
plt.xlabel("Time")
plt.ylabel("Current mA")

plt.show()