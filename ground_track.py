from sgp4.api import Satrec, jday
from datetime import datetime, timezone
import requests
import os
import time
import numpy as np


url = 'https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE'
file_name = 'iss.txt'
max_age = 6 * 3600 # dis is every 6 hours
earth_radius = 6378.137 # in km ofc 

def get_iss_tle():

    if os.path.exists(file_name):

        age = time.time() - os.path.getmtime(file_name)

        if age < max_age:
            print('using saved file')
            with open(file_name) as f:
                return f.read().splitlines()[1:]
    
    print('downloading')
    response = requests.get(url, timeout = 10)
    lines = response.text.splitlines()
    response.raise_for_status()

    with open(file_name, 'w') as f:
        f.write('\n'.join(lines))

    return lines[1:]



def propagate(sat, jd, fr, minutes=90, step_s=30):

    positions = []
    times = []
    offsets = range(0, minutes * 60 + step_s, step_s)

    for i in offsets:
        error, r, _ = sat.sgp4(jd, fr + (i / 86400))

        if error != 0:
            raise RuntimeError(f"sgp4 failed with error code {error}")

        positions.append(r)
        times.append(jd + fr + (i / 86400))

    return np.array(positions), np.array(times)



if __name__ == "__main__":  

    line1, line2 = get_iss_tle()

    sat = Satrec.twoline2rv(line1, line2)

    time_now = datetime.now(timezone.utc)

    jd, fr = jday(time_now.year, time_now.month, time_now.day,
              time_now.hour, time_now.minute, time_now.second)

    error, r, v = sat.sgp4(jd, fr)

    if error != 0:
        raise RuntimeError(f"sgp4 failed with error code {error}")

    iss_altitude = ( r[0]**2 + r[1]**2 + r[2]**2 )**0.5 - earth_radius
    iss_speed = ( v[0]**2 + v[1]**2 + v[2]**2 )**0.5
    
    positions, times = propagate(sat, jd, fr, minutes=90, step_s=30)

    print(positions)

    ' /// SECTION TO CHECK /// '

    print(' /// CHECKING ISS DATA /// ')



    'iss altitude and speed check' # should be around 400km and 7.66km/s otherwise youre doomed

    iss_altitude_speed_check = False
    if (350 < iss_altitude < 450) and (7.5 < iss_speed < 8.0):
        iss_altitude_speed_check = True

    if iss_altitude_speed_check == True:
        print('ISS altitude and speed check:  PASSED')
    else:
        print('ISS altitude and speed check: FAILED')



    'TLE check' # should be 69 69 otherwise youre doomed

    TLE_check = False

    if len(line1) == 69 and len(line2) == 69:
        TLE_check = True

    if TLE_check == True:
        print('TLE check:  PASSED')
    else:
        print('TLE check:  FAILED')



    'propagate check' # should be 181 positions and times otherwise youre doomed

    propogate_check = False

    propogation_positions = len(positions)
    propogation_times = len(times)
    
    if propogation_positions == 181 and propogation_times == 181:
        propogate_check = True

    if propogate_check == True:
        print('Propagate check:  PASSED')
    else:
        print('Propagate check:  FAILED')


  
    'altitude check for propagation' # should be between 350 and 450km otherwise youre doomed

    altitude_check = False

    for pos in positions:
        altitude = ( pos[0]**2 + pos[1]**2 + pos[2]**2 )**0.5 - earth_radius
        if (350 < altitude < 450):
            altitude_check = True

    if altitude_check == True:
        print('Altitude check for propgation:  PASSED')
    else:
        print('Altitude check for propagation:  FAILED')



    ' gap between start and end of propagation check' # should be around 90 minutes otherwise youre doomed

    gap_check = False

    last_position = positions[-1]
    first_position = positions[0]
    gap = np.linalg.norm(last_position - first_position)

    if (1300 < gap < 1400):
        gap_check = True

    if gap_check == True:
        print('Gap check for propgation:  PASSED')
    else:
        print('Gap check for propagation:  FAILED')



    print(' /// END CHECKING ISS DATA /// ')

    ' /// END SECTION /// '