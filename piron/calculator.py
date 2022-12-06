from typing import List, Union

import pandas as pd
from astropy import units
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time as TM

from .base_logger import logger
from .errors import ImageCountError
from .fits import FitsArray


class Calculator:
    """
    fa = FitsArray.from_pattern('pattern')
    Calculator(fa)

    Creates a Calculator Object

    :param fits_array: A FitsArray
    :type fits_array: FitsArray
    """

    def __init__(self, fits_array: FitsArray) -> None:
        """Constructor method
        """
        logger.info(f"Creating an instnce from {self.__class__.__name__}")

        self.fits_array = fits_array

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(id: {id(self)}, fits_array: {self.fits_array})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def jd(
            self,
            key: str,
            new_key: str = "JD",
            format: str = "isot",
            scale: str = "utc") -> None:
        """
        fa = FitsArray.from_pattern('pattern')
        ca = Calculator(fa)
        ca.jd('DATE-OBS', new_key='JD')


        Inserts a header wth key of `new_key` and value of JD which calculated from `key`

        :param key: The key where DATE (UTC) is stored.
        :type key: str

        :param new_key: New key name for JD to be inserted. Defalut: `JD`
        :type new_key: str (, optional)

        :param format: Time format of the DATE. Default: isot
        :type format: str (, optional)

        :param scale: Scale of the DATEs. Defalut: `utc`
        :type scale: str (, optional)

        :return: none
        :rtype: None
        """
        logger.info(
            f"Calculating JD. Prameters: {key=}, {new_key=}, {format=}, {scale=}"
        )
        times = self.fits_array.hselect(key)
        if len(times) == 0:
            return pd.DataFrame()

        jds = TM(times[key].to_numpy().tolist(), format=format, scale=scale).jd
        for fits, jd in zip(self.fits_array, jds):
            fits.hedit(new_key, str(jd))

    @classmethod
    def jd_c(cls,
             dates: Union[str,
                          List[str]],
             format: str = "isot",
             scale: str = "utc") -> pd.DataFrame:
        """
        Calculator.jd_c('DATE')

        Returns JD of the given DATE(s)

        :param dates: DATE or List of DATEs (utc)
        :type dates: str or List[str]

        :param format: Time format of the DATE. Default: isot
        :type format: str (, optional)

        :param scale: Scale of the DATEs. Defalut: `utc`
        :type scale: str (, optional)

        :return: List of JDs
        :rtype: pd.DataFrame
        """
        logger.info(
            f"Calculating JD. Prameters: {dates=}, {format=}, {scale=}")
        jds = TM(dates, format=format, scale=scale).jd
        return pd.DataFrame({"jd": jds})

    def hjd(
            self,
            key: str,
            position: SkyCoord,
            new_key: str = "HJD",
            format: str = "isot",
            scale: str = "utc") -> None:
        """
        fa = FitsArray.from_pattern('pattern')
        obj = Coordinates.position_from_name('Object Name')
        ca = Calculator(fa)
        ca.hjd('DATE-OBS', obj, new_key='JD')


        Inserts a header wth key of `new_key` and value of HJD which calculated from `key`


        :param key: The key where DATE (UTC) is stored.
        :type key: str
        
        :param position: SkyCoord object of the Object.
        :type position: SkyCoord
        
        :param new_key: New key name for JD to be inserted. Defalut: `HJD`.
        :type new_key: str (, optional)
        
        :param format: Time format of the DATE. Default: isot
        :type format: str (, optional)

        :param scale: Scale of the DATEs. Defalut: `utc`
        :type scale: str (, optional)

        :return: none
        :rtype: None
        """
        logger.info(
            f"Calculating JD. Prameters: {key=}, {position=}, {new_key=}, {format=}, {scale=}"
        )
        times = self.fits_array.hselect(key)
        if len(times) == 0:
            return pd.DataFrame()

        times = TM(times[key].to_numpy().tolist(), format=format, scale=scale)
        ltt_helio = times.light_travel_time(position, 'heliocentric')
        times_heliocentre = times.utc + ltt_helio

        for fits, hjd in zip(self.fits_array, times_heliocentre):
            fits.hedit(new_key, str(hjd))

    def hjd_c(self,
              dates: Union[str,
                           List[str]],
              position: SkyCoord,
              new_key: str = "HJD",
              format: str = "isot",
              scale: str = "utc") -> pd.DataFrame:
        """
        obj = Coordinates.position_from_name('Object Name')
        Calculator.hjd_c('DATE(s)', obj, new_key='JD')


        Inserts a header wth key of `new_key` and value of HJD which calculated from `key`
        
        :param dates: DATE or List of DATEs (utc)
        :type dates: str or List[str]
        
        :param position: SkyCoord object of the Object.
        :type position: SkyCoord 
        
        :param new_key: New key name for JD to be inserted. Defalut: `HJD`.
        :type new_key: str (, optional)
            
        :param format: Time format of the DATE. Default: isot
        :type format: str (, optional)
        
        :param scale: Scale of the DATEs. Defalut: `utc`
        :type scale: str (, optional)


        :return: List of HJDs
        :rtype: pd.DataFrame
        """
        logger.info(
            f"Calculating JD. Prameters: {dates=}, {position=}, {new_key=}, {format=}, {scale=}"
        )
        times = TM(dates, format=format, scale=scale)
        ltt_helio = times.light_travel_time(position, 'heliocentric')
        times_heliocentre = times.utc + ltt_helio
        return pd.DataFrame({"hjd": times_heliocentre})

    def bjd(
            self,
            key: str,
            position: SkyCoord,
            new_key: str = "BJD",
            format: str = "isot",
            scale: str = "utc") -> None:
        """
        fa = FitsArray.from_pattern('pattern')
        obj = Coordinates.position_from_name('Object Name')
        ca = Calculator(fa)
        ca.hjd('DATE-OBS', obj, new_key='JD')


        Inserts a header wth key of `new_key` and value of BJD which calculated from `key`
        
        :param key: The key where DATE (UTC) is stored.
        :type key: str
        
        :param position: SkyCoord object of the Object.
        :type position: SkyCoord
        
        :param new_key: New key name for JD to be inserted. Defalut: `BJD`.
        :type new_key: str (, optional)
        
        :param format: Time format of the DATE. Default: isot
        :type format: str (, optional)
        
        :param scale: Scale of the DATEs. Defalut: `utc`
        :type scale: str (, optional)

        :return: none
        :rtype: None
        """
        logger.info(
            f"Calculating JD. Prameters: {key=}, {position=}, {new_key=}, {format=}, {scale=}"
        )
        times = self.fits_array.hselect(key)
        if len(times) == 0:
            return pd.DataFrame()

        times = TM(times[key].to_numpy().tolist(), format=format, scale=scale)
        ltt_helio = times.light_travel_time(position)
        times_heliocentre = times.utc + ltt_helio

        for fits, hjd in zip(self.fits_array, times_heliocentre):
            fits.hedit(new_key, str(hjd))

    def bjd_c(self,
              dates: Union[str,
                           List[str]],
              position: SkyCoord,
              new_key: str = "BJD",
              format: str = "isot",
              scale: str = "utc") -> None:
        """
        obj = Coordinates.position_from_name('Object Name')
        Calculator.hjd_c('DATE(s)', obj, new_key='JD')


        Inserts a header wth key of `new_key` and value of BJD which calculated from `key`
        
        :param dates: DATE or List of DATEs (utc)
        :type dates: str or List[str]
        
        :param position: SkyCoord object of the Object.
        :type position: SkyCoord
        
        :param new_key: New key name for JD to be inserted. Defalut: `BJD`.
        :type new_key: str (, optional)
        
        :param format: Time format of the DATE. Default: isot
        :type format: str (, optional)
        
        :param scale: Scale of the DATEs. Defalut: `utc`
        :type scale: str (, optional)

        :return: List of BJDs
        :rtype: pd.DataFrame
        """
        logger.info(
            f"Calculating JD. Prameters: {dates=}, {position=}, {new_key=}, {format=}, {scale=}"
        )
        times = TM(dates, format=format, scale=scale)
        ltt_helio = times.light_travel_time(position)
        times_heliocentre = times.utc + ltt_helio
        return pd.DataFrame({"hjd": times_heliocentre})

    def astropy_time(self, key: str, format="isot", scale="utc") -> TM:
        """
        fa = FitsArray.from_pattern('pattern')
        ca = Calculator(fa)
        ca.astropy_time('DATE-OBS')

        Returns a list of astropy.time.Time from given `key` in header
        
        :param key: The key where DATE (UTC) is stored.
        :type key: str
        
        :param format: Time format of the DATE. Default: isot
        :type format: str (, optional)
        
        :param scale: Scale of the DATEs. Defalut: `utc`
        :type scale: str (, optional)

        :return: Time object
        :rtype: astropy.time.Time
        """
        logger.info(
            f"Converting to astropy.time.Time. Prameters: {key=}, {format=}, {scale=}"
        )
        times = self.fits_array.hselect(key)
        if len(times) == 0:
            raise ValueError("Time not found")

        return TM(
            times[key].to_numpy().flatten().tolist(),
            format=format,
            scale=scale)

    @classmethod
    def astropy_time_c(cls,
                       dates: Union[str,
                                    List[str]],
                       format: str = "isot",
                       scale: str = "utc") -> TM:
        """
        Calculator.astropy_time_c('DATE(s)')

        Returns a list of astropy.time.Time from given `DATEs` in header
        
        :param dates: The key where DATE (UTC) is stored.
        :type dates: str or List[str]
        
        :param format: Time format of the DATE. Default: isot
        :type format: str (, optional)
        
        :param scale: Scale of the DATEs. Defalut: `utc`
        :type scale: str (, optional)

        :return: Time object
        :rtype: astropy.time.Time
        """
        logger.info(
            f"Converting to astropy.time.Time. Prameters: {dates=}, {format=}, {scale=}"
        )
        if len(dates) == 0:
            raise ValueError("Time not found")

        return TM(dates, format=format, scale=scale)

    def sec_z(
        self,
        key: str,
        location: EarthLocation,
        position: SkyCoord,
        new_key: str = "ARIMASS",
        format: str = "isot",
        scale: str = "utc",
    ) -> None:
        """
        fa = FitsArray.from_pattern('pattern')
        site = Coordinates.location_from_name('Location Name')
        obj = Coordinates.position_from_name('Object Name')
        ca = Calculator(fa)
        ca.sec_z('DATE-OBS', site, obj, new_key='ARIMASS')


        Inserts a header wth key of `new_key` and value of secz which calculated from `key`
        
        :param key: The key where DATE (UTC) is stored.
        :type key: str
        
        :param location: EarthLocation of the Observation site.
        :type location: EarthLocation
        
        :param position: SkyCoord object of the Object.
        :type position: SkyCoord
        
        :param new_key: New key name for JD to be inserted. Defalut: `ARIMASS`.
        :type new_key: str (, optional)
        
        :param format: Time format of the DATE. Default: isot
        :type format: str (, optional)
        
        :param scale: Scale of the DATEs. Defalut: `utc`
        :type scale: str (, optional)

        :return: none
        :rtype: None

        """
        logger.info(
            f"Calculating secz. Prameters: {key=}, {location=}, {position=}, {new_key=}, {format=}, {scale=}"
        )
        times = self.astropy_time(key, format=format, scale=scale)

        frame = AltAz(obstime=times, location=location)
        obj_alt_az = position.transform_to(frame)
        obj_alt = obj_alt_az.secz
        seczs = obj_alt.value.tolist()
        for fits, secz in zip(self.fits_array, seczs):
            fits.hedit(new_key, str(secz))

    @classmethod
    def sec_z_c(
        cls, times: TM, location: EarthLocation, position: SkyCoord
    ) -> pd.DataFrame:
        """
        site = Coordinates.location_from_name('Location Name')
        obj = Coordinates.position_from_name('Object Name')
        Calculator.sec_z_c('DATE(s)', site, obj, new_key='ARIMASS')


        Returns secz which calculated from `DATE(s)` and given location and position
        
        :param dates: List of dates
        :type dates: astropy.time.Time
        
        :param location: EarthLocation of the Observation site.
        :type location: EarthLocation
        
        :param position: SkyCoord object of the Object.
        :type position: SkyCoord

        :return: List of Airmass
        :rtype: pd.DataFrame
        """
        logger.info(
            f"Calculating secz. Prameters: {times=}, {location=}, {position=}")
        frame = AltAz(obstime=times, location=location)
        obj_alt_az = position.transform_to(frame)
        obj_alt = obj_alt_az.secz
        return pd.DataFrame({"secz": obj_alt.value.tolist()})


class Coordinates:
    @classmethod
    def location_from_name(cls, name: str) -> EarthLocation:
        """
        site = Coordinates.location_from_name('Location Name')

        Returns an EarthLocation from a given name

        :param name: Name of the site
        :type name: str

        :return: Location
        :rtype: EarthLocation
        """
        logger.info(f"Creating EarthLocation. Prameters: {name=}")
        return EarthLocation.of_site(name)

    @classmethod
    def location(
        cls, longitude: float, latitude: float, altitude: float = 0
    ) -> EarthLocation:
        """
        site = Coordinates.location(LONGITUDE, LATITUDE, ALTITUDE)

        Returns an EarthLocation from given longitude, latitude and altitude
        
        :param longitude: longitude of the location
        :type longitude: float
        
        :param latitude: latitude of the location
        :type latitude: float
        
        :param altitude: altitude of the location
        :type altitude: float

        :return: Location
        :rtype: EarthLocation
        """
        logger.info(
            f"Creating EarthLocation. Prameters: {longitude=}, {latitude=}, {altitude=}"
        )
        return EarthLocation(
            longitude * units.deg, latitude * units.deg, altitude * units.m
        )

    @classmethod
    def position_from_name(cls, name: str) -> SkyCoord:
        """
        site = Coordinates.location_from_name('Location Name')

        Returns a SkyCoord from the given ra and dec
        
        :param ra: Right Ascension of the object in hourangle
        :type ra: float
        
        :param dec: Declination of the object in degrees
        :type dec: float

        :return: Position
        :rtype: SkyCoord
        """
        logger.info(f"Creating SkyCoord. Prameters: {name=}")
        return SkyCoord.from_name(name, frame="icrs")

    @classmethod
    def position(cls, ra: float, dec: float) -> SkyCoord:
        """
        site = Coordinates.location(RA, DEC)

        Returns a SkyCoord from given ra and dec
        
        :param longitude: longitude of the location
        :type longitude: float
        
        :param latitude: latitude of the location
        :type latitude: float
        
        :param altitude: altitude of the location
        :type altitude: float

        :return: Position
        :rtype: SkyCoord
        """
        logger.info(f"Creating SkyCoord. Prameters: {ra=}, {dec=}")
        return SkyCoord(
            ra=ra,
            dec=dec,
            unit=(
                units.hourangle,
                units.deg),
            frame="icrs")
