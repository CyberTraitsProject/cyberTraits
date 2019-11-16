"""
1. pass on the gps files and take the data for every day from the hours 9:00-18:00.
2. take the data of every 5 minutes. if we dont have information on specific time, we need to take the last parameters.
3. calculate the Standard Deviation -  SD (סטיית תקן). n=9*12=108

1. pass on the gps files and take the data for every day from the hours 18:00-00:00.
2. take the data of every 5 minutes. if we dont have information on specific time, we need to take the last parameters.
3. calculate the Standard Deviation(סטיית תקן). n=6*12=72

1. pass on the gps files and take the data for every day from the hours 00:00-9:00.
2. take the data of every 5 minutes. if we dont have information on specific time, we need to take the last parameters.
3. calculate the Standard Deviation(סטיית תקן). n=9*12=108

-------------------------------------------------------------------------------------------

to do average of SD's for the days, nights and evenings - 3 values.

"""