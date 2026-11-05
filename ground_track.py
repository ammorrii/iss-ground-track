from sgp4.api import Satrec, jday
from datetime import datetime, timezone
import requests
import os
import time
import numpy as np
import matplotlib.pyplot as plt


# /// CONSTANTS ///

url = 'https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE'
file_name = 'iss.txt'
max_age = 6 * 3600 # dis is every 6 hours
earth_radius = 6378.137 # in km ofc 


# /// FUNCTIONS ///

# --- This function gets the ISS TLE from Celestrak and saves it as a file, or use the saved file if it exists within the max_age ---
def get_iss_tle():

    if os.path.exists(file_name):

        age = time.time() - os.path.getmtime(file_name)

        if age < max_age:
            print('using saved file')
            with open(file_name) as f:
                return f.read().splitlines()[1:]
    
    print('file too old or not found, downloading new file')
    response = requests.get(url, timeout = 10)
    lines = response.text.splitlines()
    response.raise_for_status()

    with open(file_name, 'w') as f:
        f.write('\n'.join(lines))

    return lines[1:]

# --- This function propagates the ISS's positions and its time ---
def propagate(sat, jd, fr, minutes=90, step_s=30):

    positions = []
    times = []
    offsets = range(0, minutes * 60 + step_s, step_s)

    for t in offsets:
        error, r, _ = sat.sgp4(jd, fr + (t / 86400))

        if error != 0:
            raise RuntimeError(f'sgp4 failed with error code {error}')

        positions.append(r)
        times.append(jd + fr + (t / 86400))

    return np.array(positions), np.array(times)

# --- This function converts the ISS's positions and times to latitude and longitude ---
def to_lat_lon(positions, times):

    x = positions[:, 0]
    y = positions[:, 1]
    z = positions[:, 2]
    mag_x_y = ( x**2 + y**2 )**0.5
    rotation_angle = ( 280.46061837 + 360.98564736629 * ( times - 2451545.0 ) ) % 360

    latitude = np.degrees( np.arctan2(z, mag_x_y) )

    longitude_raw = np.degrees( np.arctan2(y, x) ) - rotation_angle
    longitude = ( (longitude_raw + 180) % 360 ) - 180

    return latitude, longitude

# --- This function checks the code's data to ensure all is good ---
def check_data():

    print('-----------------------------------------------')
    print(' /// CHECKING ISS DATA /// ')

    print()
    
    # --- iss altitude and speed check should be around 400km and 7.66km/s otherwise youre doomed ---
    print('ISS Altitude and Speed Check Expectation: Altitude: 350-450 km, Speed: 7.5-8.0 km/s')
    iss_altitude_speed_check = False
    if (350 < iss_altitude < 450) and (7.5 < iss_speed < 8.0):
        iss_altitude_speed_check = True

    if iss_altitude_speed_check == True:
        print('ISS altitude and speed check:          | PASSED |-', f'Altitude: {iss_altitude:.2f} km, Speed: {iss_speed:.2f} km/s')
    else:
        print('ISS altitude and speed check:          | FAILED |-', f'Altitude: {iss_altitude:.2f} km, Speed: {iss_speed:.2f} km/s')

    print()

    # --- TLE check should be 69 69 otherwise youre doomed ---
    print('TLE Check Expectation: Line 1 length: 69, Line 2 length: 69')

    TLE_check = False

    if len(line1) == 69 and len(line2) == 69:
        TLE_check = True

    if TLE_check == True:
        print('TLE check:                             | PASSED |-', f'Line 1 length: {len(line1)}, Line 2 length: {len(line2)}')
    else:
        print('TLE check:                             | FAILED |-', f'Line 1 length: {len(line1)}, Line 2 length: {len(line2)}')

    print()

    # --- propagate check should be 181 positions and times otherwise youre doomed ---
    print('Propagate Check Expectation: Positions: 181, Times: 181')

    propogate_check = False

    propogation_positions = len(positions)
    propogation_times = len(times)
    
    if propogation_positions == 181 and propogation_times == 181:
        propogate_check = True

    if propogate_check == True:
        print('Propagate check:                       | PASSED |-', f'Positions: {propogation_positions}, Times: {propogation_times}')
    else:
        print('Propagate check:                       | FAILED |-', f'Positions: {propogation_positions}, Times: {propogation_times}')

    print()

    # --- altitudes check for propagation. all altitudes yshould be between 350 and 450km otherwise youre doomed ---
    print('Altitudes Check for Propagation Expectation: Altitudes: 350-450 km')

    altitude_check = True

    for pos in positions:
        altitude = ( pos[0]**2 + pos[1]**2 + pos[2]**2 )**0.5 - earth_radius
        if not (350 < altitude < 450):
            altitude_check = False
            break

    if altitude_check == True:
        print('Altitudes check for propagation:       | PASSED |-', 'Theyre all between 350 and 450 km')
    else:
        print('Altitudes check for propagation:       | FAILED |-', 'At least one or more position is not between 350 and 450 km')

    print()

    # --- gap between start and end of propagation check. should be around 1350km otherwise youre doomed ---
    print('Gap Check for Propagation Expectation: Gap: 1300-1400 km')
    gap_check = False

    last_position = positions[-1]
    first_position = positions[0]
    gap = np.linalg.norm(last_position - first_position)

    if (1300 < gap < 1400):
        gap_check = True

    if gap_check == True:
        print('Gap check for propagation:             | PASSED |-',  f'Gap: {gap:.2f} km')
    else:
        print('Gap check for propagation:             | FAILED |-', f'Gap: {gap:.2f} km')

    print()

    # --- Latitude should be between -51.6 and 51.6 degrees otherwise youre doomed ---
    print('Latitude Check for Propagation Expectation: Latitude: -51.6 to 51.6 degrees')
    latitude_check = False
    if ( 51 <= max(latitude) < 52) and (-52 <= min(latitude) < -51):
        latitude_check = True

    if latitude_check == True:
        print('Latitude check for propagation:        | PASSED |-', 'Theyre all between -51.6 and 51.6 degrees')
    else:
        print('Latitude check for propagation:        | FAILED |-', 'At least one or more position is not between -51.6 and 51.6 degrees')

    print()

    # --- Longitude should be between -180 and 180 degrees otherwise youre doomed ---
    print('Longitude Check for Propagation Expectation: Longitude: -180 to 180 degrees')
    longitude_check = False

    for lon in longitude:
        if (-180 <= lon <= 180):
            longitude_check = True
        else:
            longitude_check = False
            break

    if longitude_check == True:
        print('Longitude check for propagation:       | PASSED |-', 'Theyre all between -180 and 180 degrees')
    else:
        print('Longitude check for propagation:       | FAILED |-', 'At least one or more position is not between -180 and 180 degrees')

    print()

    # --- Latitude and Longitude should be 181 elements each otherwise youre doomed ---
    print('Latitude and Longitude Check Expectation: Latitude: 181, Longitude: 181')
    lat_lon_check = False

    if len(latitude) == 181 and len(longitude) == 181:
        lat_lon_check = True

    if lat_lon_check == True:
        print('Latitude and Longitude check:          | PASSED |-', f'Latitude: {len(latitude)}, Longitude: {len(longitude)}')
    else:
        print('Latitude and Longitude check:          | FAILED |-', f'Latitude: {len(latitude)}, Longitude: {len(longitude)}')

    print()

    # --- No NaN values in latitude and longitude otherwise youre doomed ---
    print('NaN Check for Latitude and Longitude Expectation: No NaN values in Latitude and Longitude')
    nan_check = True

    if np.any( np.isnan(latitude) ) or np.any( np.isnan(longitude) ):
        nan_check = False

    if nan_check == True:
        print('NaN check for Latitude and Longitude:  | PASSED |-', 'No NaN values in Latitude and Longitude')
    else:
        print('NaN check for Latitude and Longitude:  | FAILED |-', 'At least one or more NaN values in Latitude and Longitude')

    print()

    print(' /// END CHECKING ISS DATA /// ')
    print('-----------------------------------------------')

# --- This function plots the ISS's ground track on a map of the Earth ---
def plot_ground_track(latitude, longitude):
    
    plt.style.use("dark_background")
    
    plot_break =  np.where( abs(np.diff(longitude)) > 100 )[0]
    
    longitude_plot = np.insert(longitude, plot_break + 1, np.nan)
    latitude_plot = np.insert(latitude, plot_break + 1, np.nan)
    plt.plot(longitude_plot, latitude_plot, color="#BFE2EE", linewidth=0.75)
    plt.plot(longitude_plot[0], latitude_plot[0], marker='o', color="#9ED5E7", markersize=5)
    plt.annotate('ISS', xytext=(longitude_plot[0] - 7, latitude_plot[0] + 6), xy=(longitude_plot[0], latitude_plot[0]), color="#9ED5E7", fontsize=8, fontweight='bold')
    plt.xlim(-180, 180)
    plt.ylim(-90, 90)

    plt.title('ISS Ground Track Over 90 Minutes')
    plt.xlabel('Longitude (degrees)')
    plt.ylabel('Latitude (degrees)')

    image = plt.imread('earth_map.png')
    plt.imshow(image, extent=[-180, 180, -90, 90])

    plt.grid(True, linestyle='--', linewidth=0.5, color="#525558", alpha=0.5)
    plt.gca().set_aspect('equal')

    plt.show()


# /// MAIN BLOCK ///

if __name__ == '__main__':  


    line1, line2 = get_iss_tle()

    sat = Satrec.twoline2rv(line1, line2)

    time_now = datetime.now(timezone.utc)
    jd, fr = jday(time_now.year, time_now.month, time_now.day,
              time_now.hour, time_now.minute, time_now.second)

    error, r, v = sat.sgp4(jd, fr)

    if error != 0:
        raise RuntimeError(f'sgp4 failed with error code {error}')


    iss_altitude = ( r[0]**2 + r[1]**2 + r[2]**2 )**0.5 - earth_radius
    iss_speed = ( v[0]**2 + v[1]**2 + v[2]**2 )**0.5

    
    positions, times = propagate(sat, jd, fr, minutes=90, step_s=30)
    latitude, longitude = to_lat_lon(positions, times)


    menu_option = input('''
-----------------------------------------------
/// Welcome to ISS Ground Track ///

( 1 ) ISS information
( 2 ) Show 90-minute ground track on world map
( 3 ) Run data checks
( 0 ) Exit
-----------------------------------------------
Please select an option:
''')

    if menu_option == '1':
        print(f'''
-----------------------------------------------
/// Current ISS Information ///

Current ISS Altitude: {iss_altitude:.2f} km
Current ISS Speed: {iss_speed:.2f} km/s
Current ISS Latitude: {latitude[0]:.2f} degrees
Current ISS Longitude: {longitude[0]:.2f} degrees
-----------------------------------------------
''')
    elif menu_option == '2':
        print('Displaying 90-minute ground track on world map...')
        plot_ground_track(latitude, longitude)
    elif menu_option == '3':
        check_data()
    elif menu_option == '0':
        print('Exiting...')
    else:
        print('Invalid option. Please select a valid option.')