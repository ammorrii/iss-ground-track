from sgp4.api import Satrec, jday
from datetime import datetime, timezone
import requests
import os
import time

url = 'https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE'
file_name = 'iss.txt'
max_age = 6 * 3600 # dis is every 6 hours

def get_iss_tle():
    if os.path.exists(file_name):
        age = time.time() - os.path.getmtime(file_name)
        if age < max_age:
            print('using saved file')
            with open(file_name) as f:
                return f.read().splitlines()[1:]

    print('downloading')
    response = requests.get(url)
    lines = response.text.splitlines()

    with open(file_name, 'w') as f:
        f.write('\n'.join(lines))

    return lines[1:]


if __name__ == "__main__":
    line1, line2 = get_iss_tle()


print(get_iss_tle())

print(len(line1), len(line2))

time_now = datetime.now(timezone.utc)
print(time_now)

