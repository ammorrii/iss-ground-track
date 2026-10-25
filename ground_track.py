from sgp4.api import Satrec, jday
from datetime import datetime, timezone
import requests
import os
import time

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

    with open(file_name, 'w') as f:
        f.write('\n'.join(lines))

    return lines[1:]




if __name__ == "__main__":
    
    line1, line2 = get_iss_tle()

    tle_checker = (len(line1), len(line2))
    # print(tle_checker) # should be 69 69 otherwise youre doomed

    sat = Satrec.twoline2rv(line1, line2)

    time_now = datetime.now(timezone.utc)

    jd, fr = jday(time_now.year, time_now.month, time_now.day,
              time_now.hour, time_now.minute, time_now.second)

    error, r, v = sat.sgp4(jd, fr)

    if error != 0:
        raise RuntimeError(f"sgp4 failed with error code {error}")

    iss_altitude = ( r[0]**2 + r[1]**2 + r[2]**2 )**0.5 - earth_radius
    iss_speed = ( v[0]**2 + v[1]**2 + v[2]**2 )**0.5
    print(iss_altitude ,iss_speed)