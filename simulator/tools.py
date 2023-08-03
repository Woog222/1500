from config import *

def can_time_cal(arrival_time:int, start:int ,end:int):
    quotient = arrival_time // DAY
    remainder = arrival_time % DAY

    if start < end:
        if start<= remainder and remainder <= end:
            return arrival_time
        elif remainder < start:
            return quotient*DAY + start
        else: # end < remainder
            return (quotient+1)*DAY + start
    else:
        if end < remainder and remainder < start:
            return quotient*DAY + start
        else:
            return arrival_time





