from typing import List, Union

import pandas as pd
from astropy import units
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time as ATime

from .base_logger import logger
from .fits import FitsArray


class Calculator:
    def __init__(self, fits_array: FitsArray) -> None:
        """
        Constructor method.
        Creates a Calculator Object.

        :param fits_array: A FitsArray.
        :type fits_array: FitsArray
        """
        logger.info(f"Creating an instance from {self.__class__.__name__}")

        self.fits_array = fits_array

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id: {id(self)}, fits_array: {self.fits_array})"

    def __repr__(self) -> str:
        return self.__str__()

    def jd(self, key: str, new_key: str = "JD", date_format: str = "isot", scale: str = "utc") -> None:
        """
        Inserts a header wth key of new_key and value of JD which calculated from key.

        :param key: The key where DATE (UTC) is stored.
        :type key: str

        :param new_key: New key name for JD to be inserted. Default: JD.
        :type new_key: str (, optional)

        :param date_format: Time format of the DATE. Default: isot.
        :type date_format: str (, optional)

        :param scale: Scale of the DATEs. Default: utc.
        :type scale: str (, optional)

        :return: None.
        :rtype: None
        """
        logger.info(f"Calculating JD. Parameters: {key=}, {new_key=}, {date_format=}, {scale=}")
        times = self.fits_array.hselect(key)
        if len(times) == 0:
            return

        jds = ATime(times[key].to_numpy().tolist(), format=date_format, scale=scale).jd
        for fits, jd in zip(self.fits_array, jds):
            fits.hedit(new_key, str(jd))

    @classmethod
    def jd_c(cls, dates: Union[str, List[str]], date_format: str = "isot", scale: str = "utc") -> pd.DataFrame:
        """
        Returns JD of the given DATEs.

        :param dates: DATE or List of DATEs (utc).
        :type dates: str or List[str]

        :param date_format: Time format of the DATE. Default: isot.
        :type date_format: str (, optional)

        :param scale: Scale of the DATEs. Default: utc.
        :type scale: str (, optional)

        :return: List of JDs.
        :rtype: pd.DataFrame
        """
        logger.info(f"Calculating JD. Parameters: {dates=}, {date_format=}, {scale=}")
        jds = ATime(dates, format=date_format, scale=scale).jd
        return pd.DataFrame({"jd": jds})

    def hjd(self, key: str, position: SkyCoord, new_key: str = "HJD", date_format: str = "isot",
            scale: str = "utc") -> None:
        """
        Inserts a header wth key of new_key and value of HJD which calculated from key.


        :param key: The key where DATE (UTC) is stored.
        :type key: str
        
        :param position: SkyCoord object of the Object.
        :type position: SkyCoord
        
        :param new_key: New key name for HJD to be inserted. Default: HJD.
        :type new_key: str (, optional)
        
        :param date_format: Time format of the DATE. Default: isot.
        :type date_format: str (, optional)

        :param scale: Scale of the DATEs. Default: utc.
        :type scale: str (, optional)

        :return: None.
        :rtype: None
        """
        logger.info(f"Calculating JD. Parameters: {key=}, {position=}, {new_key=}, {date_format=}, {scale=}")
        times = self.fits_array.hselect(key)
        if len(times) == 0:
            return

        times = ATime(times[key].to_numpy().tolist(), format=date_format, scale=scale)
        ltt_helio = times.light_travel_time(position, 'heliocentric')
        times_heliocentre = times.utc + ltt_helio

        for fits, hjd in zip(self.fits_array, times_heliocentre):
            fits.hedit(new_key, str(hjd))

    @classmethod
    def hjd_c(cls, dates: Union[str, List[str]], position: SkyCoord, new_key: str = "HJD", date_format: str = "isot",
              scale: str = "utc") -> pd.DataFrame:
        """
        Inserts a header wth key of new_key and value of HJD which calculated from key.
        
        :param dates: DATE or List of DATEs (utc).
        :type dates: str or List[str]
        
        :param position: SkyCoord object of the Object.
        :type position: SkyCoord 
        
        :param new_key: New key name for HJD to be inserted. Default: HJD.
        :type new_key: str (, optional)
            
        :param date_format: Time format of the DATE. Default: isot.
        :type date_format: str (, optional)
        
        :param scale: Scale of the DATEs. Default: utc.
        :type scale: str (, optional)


        :return: List of HJDs.
        :rtype: pd.DataFrame
        """
        logger.info(f"Calculating JD. Parameters: {dates=}, {position=}, {new_key=}, {date_format=}, {scale=}")
        times = ATime(dates, format=date_format, scale=scale)
        ltt_helio = times.light_travel_time(position, 'heliocentric')
        times_heliocentre = times.utc + ltt_helio
        return pd.DataFrame({"hjd": times_heliocentre})

    def bjd(self, key: str, position: SkyCoord, new_key: str = "BJD", date_format: str = "isot",
            scale: str = "utc") -> None:
        """
        Inserts a header wth key of new_key and value of BJD which calculated from key.
        
        :param key: The key where DATE (utc) is stored.
        :type key: str
        
        :param position: SkyCoord object of the Object.
        :type position: SkyCoord
        
        :param new_key: New key name for HJD to be inserted. Default: BJD.
        :type new_key: str (, optional)
        
        :param date_format: Time format of the DATE. Default: isot.
        :type date_format: str (, optional)
        
        :param scale: Scale of the DATEs. Default: utc.
        :type scale: str (, optional)

        :return: None.
        :rtype: None
        """
        logger.info(f"Calculating JD. Parameters: {key=}, {position=}, {new_key=}, {date_format=}, {scale=}")
        times = self.fits_array.hselect(key)
        if len(times) == 0:
            return

        times = ATime(times[key].to_numpy().tolist(), format=date_format, scale=scale)
        ltt_helio = times.light_travel_time(position)
        times_heliocentre = times.utc + ltt_helio

        for fits, hjd in zip(self.fits_array, times_heliocentre):
            fits.hedit(new_key, str(hjd))

    @classmethod
    def bjd_c(cls, dates: Union[str, List[str]], position: SkyCoord, new_key: str = "BJD", date_format: str = "isot",
              scale: str = "utc") -> pd.DataFrame:
        """
        Inserts a header wth key of new_key and value of BJD which calculated from key.
        
        :param dates: DATE or List of DATEs (utc).
        :type dates: str or List[str]
        
        :param position: SkyCoord object of the Object.
        :type position: SkyCoord
        
        :param new_key: New key name for BJD to be inserted. Default: BJD.
        :type new_key: str (, optional)
        
        :param date_format: Time format of the DATE. Default: isot.
        :type date_format: str (, optional)
        
        :param scale: Scale of the DATEs. Default: utc.
        :type scale: str (, optional)

        :return: List of BJDs.
        :rtype: pd.DataFrame
        """
        logger.info(f"Calculating JD. Parameters: {dates=}, {position=}, {new_key=}, {date_format=}, {scale=}")
        times = ATime(dates, format=date_format, scale=scale)
        ltt_helio = times.light_travel_time(position)
        times_heliocentre = times.utc + ltt_helio
        return pd.DataFrame({"hjd": times_heliocentre})

    def astropy_time(self, key: str, date_format: str = "isot", scale: str = "utc") -> ATime:
        """
        Returns a list of astropy.time.Time from given key in header.
        
        :param key: The key where DATE (utc) is stored.
        :type key: str
        
        :param date_format: Time format of the DATE. Default: isot.
        :type date_format: str (, optional)
        
        :param scale: Scale of the DATEs. Default: utc.
        :type scale: str (, optional)

        :return: Time object.
        :rtype: astropy.time.Time
        """
        logger.info(f"Converting to astropy.time.Time. Parameters: {key=}, {date_format=}, {scale=}")
        times = self.fits_array.hselect(key)
        if len(times) == 0:
            raise ValueError("Time not found")

        return ATime(times[key].to_numpy().flatten().tolist(), format=date_format, scale=scale)

    @classmethod
    def astropy_time_c(cls, dates: Union[str, List[str]], date_format: str = "isot", scale: str = "utc") -> ATime:
        """
        Returns a list of astropy.time.Time from given DATEs in header.
        
        :param dates: The key where DATE (utc) is stored.
        :type dates: str or List[str]
        
        :param date_format: Time format of the DATE. Default: isot.
        :type date_format: str (, optional)
        
        :param scale: Scale of the DATEs. Default: utc.
        :type scale: str (, optional)

        :return: Time object.
        :rtype: astropy.time.Time
        """
        logger.info(f"Converting to astropy.time.Time. Parameters: {dates=}, {date_format=}, {scale=}")
        if len(dates) == 0:
            raise ValueError("Time not found")

        return ATime(dates, format=date_format, scale=scale)

    def sec_z(self, key: str, location: EarthLocation, position: SkyCoord, new_key: str = "ARIMASS",
              date_format: str = "isot", scale: str = "utc") -> None:
        """
        Inserts a header wth key of new_key and value of secz which calculated from key.
        
        :param key: The key where DATE (utc) is stored.
        :type key: str
        
        :param location: EarthLocation of the Observation site.
        :type location: EarthLocation
        
        :param position: SkyCoord object of the Object.
        :type position: SkyCoord
        
        :param new_key: New key name for SECZ to be inserted. Default: ARIMASS.
        :type new_key: str (, optional)
        
        :param date_format: Time format of the DATE. Default: isot.
        :type date_format: str (, optional)
        
        :param scale: Scale of the DATEs. Default: utc.
        :type scale: str (, optional)

        :return: None.
        :rtype: None

        """
        logger.info(
            f"Calculating secz. Parameters: {key=}, {location=}, {position=}, {new_key=}, {date_format=}, {scale=}")
        times = self.astropy_time(key, date_format=date_format, scale=scale)

        frame = AltAz(obstime=times, location=location)
        obj_alt_az = position.transform_to(frame)
        obj_alt = obj_alt_az.secz
        seczs = obj_alt.value.tolist()
        for fits, secz in zip(self.fits_array, seczs):
            fits.hedit(new_key, str(secz))

    @classmethod
    def sec_z_c(cls, times: ATime, location: EarthLocation, position: SkyCoord) -> pd.DataFrame:
        """
        Returns secz which calculated from DATEs and given location and position.
        
        :param times: List of dates.
        :type times: astropy.time.Time
        
        :param location: EarthLocation of the Observation site.
        :type location: EarthLocation
        
        :param position: SkyCoord object of the Object.
        :type position: SkyCoord

        :return: List of secz.
        :rtype: pd.DataFrame
        """
        logger.info(f"Calculating secz. Parameters: {times=}, {location=}, {position=}")
        frame = AltAz(obstime=times, location=location)
        obj_alt_az = position.transform_to(frame)
        obj_alt = obj_alt_az.secz
        return pd.DataFrame({"secz": obj_alt.value.tolist()})


class Coordinates:
    @classmethod
    def location_from_name(cls, name: str) -> EarthLocation:
        """
        Returns an EarthLocation from a given name.

        :param name: Name of the site.
        :type name: str

        :return: Location.
        :rtype: EarthLocation
        """
        logger.info(f"Creating EarthLocation. Parameters: {name=}")
        return EarthLocation.of_site(name)

    @classmethod
    def location(cls, longitude: float, latitude: float, altitude: float = 0) -> EarthLocation:
        """
        Returns an EarthLocation from given longitude, latitude and altitude.
        
        :param longitude: longitude of the location.
        :type longitude: float
        
        :param latitude: latitude of the location.
        :type latitude: float
        
        :param altitude: altitude of the location.
        :type altitude: float

        :return: Location.
        :rtype: EarthLocation
        """
        logger.info(f"Creating EarthLocation. Parameters: {longitude=}, {latitude=}, {altitude=}")
        return EarthLocation(longitude * units.deg, latitude * units.deg, altitude * units.m)

    @classmethod
    def position_from_name(cls, name: str) -> SkyCoord:
        """
        Returns a SkyCoord from the given name.
        
        :param name: Name of the celestial object.
        :type name: str

        :return: Position.
        :rtype: SkyCoord
        """
        logger.info(f"Creating SkyCoord. Parameters: {name=}")
        return SkyCoord.from_name(name, frame="icrs")

    @classmethod
    def position(cls, ra: float, dec: float) -> SkyCoord:
        """
        Returns a SkyCoord from given ra and dec.
        
        :param ra: right ascension.
        :type ra: float
        
        :param dec: Declination.
        :type dec: float

        :return: Position.
        :rtype: SkyCoord
        """
        logger.info(f"Creating SkyCoord. Parameters: {ra=}, {dec=}")
        return SkyCoord(ra=ra, dec=dec, unit=(units.hourangle, units.deg), frame="icrs")
