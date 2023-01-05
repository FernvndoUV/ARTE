#!/usr/bin/python3
from astropy.coordinates import SkyCoord, Galactocentric, EarthLocation, AltAz
import astropy.coordinates as coord
from astropy.time import TimeDelta
from astropy import units as u
from PyAstronomy import pyasl
from datetime import datetime
from astropy.time import Time
import ephem
import time


def galactic_center_tracker(date, sky_coord, local_coord, elipse_params, min_elevation):
    A = round(sky_coord.galactic.l.value)
    D = round(sky_coord.galactic.b.value)*-1
    RA = sky_coord.ra.hourangle
    Dec = sky_coord.dec.deg
    
    a = elipse_params['a']
    be = elipse_params['be']
    epsilon = elipse_params['epsilon']
    ref = elipse_params['ref']

    #elipse in the tangent plane
    anxi = np.arange(A-a, A+a, epsilon)
    aneta = be*np.sqrt(1-(anxi-A)**2/ a**2)
      


     




if __name__ == '__main__': 
    calan_loc = EarthLocation(lat=-33.3961*u.deg, lon=-70.537*u.deg, height=867*u.m)
    galactic_coord = SkyCoord.from_name('Galactic Center')
    elipse_params = {
            "a": 38.,
            "be": 8.,
            "epsilon":1,
            "ref": 5*u.deg
            }
    


