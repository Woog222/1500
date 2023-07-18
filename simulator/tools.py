from config import *

def can_time_cal(arrival_time:int, start:int ,end:int):
    quotient = arrival_time // DAY
    remainder = arrival_time % DAY

    if start < end:
        if start<= remainder and remainder <= end:
            return arrival_time
        else:
            return (quotient+1)*DAY + start
    else:
        if start < remainder and remainder < end:
            return (quotient+1)*DAY + start
        else:
            return arrival_time

