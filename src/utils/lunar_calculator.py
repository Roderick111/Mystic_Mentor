

class LunarCalculatorService:
    """
    Handles astronomical calculations only.
    
    This service is responsible for pure astronomical calculations
    without any esoteric knowledge or context generation.
    """
    
    def __init__(self, location_service: LocationServiceProtocol):
        """Initialize lunar calculator with location service."""
        self.location_service = location_service
        self._cache_stats = {"hits": 0, "misses": 0}
    
    @lru_cache(maxsize=1000)
    def calculate_phase_for_date(self, 
                               date_str: str,  # Use string for caching
                               location_lat: Optional[float] = None,
                               location_lon: Optional[float] = None) -> LunarPhaseInfo:
        """
        Calculate lunar phase for a specific date and location.
        
        Args:
            date_str: ISO format date string for caching
            location_lat: Latitude (optional)
            location_lon: Longitude (optional)
            
        Returns:
            LunarPhaseInfo object with calculated phase data
        """
        self._cache_stats["misses"] += 1
        
        try:
            date = datetime.fromisoformat(date_str)
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_str}") from e
        
        # Get location or use default
        if location_lat is None or location_lon is None:
            default_location = self.location_service.get_default_location()
            location_lat = location_lat or (default_location.get("lat") if default_location else 0.0)
            location_lon = location_lon or (default_location.get("lon") if default_location else 0.0)
        
        # Perform astronomical calculations
        # This would integrate with the existing lunar calculation logic
        # For now, we'll create a basic implementation
        phase_info = self._perform_astronomical_calculation(date, location_lat, location_lon)
        
        logger.debug(f"Calculated lunar phase for {date}: {phase_info.phase}")
        return phase_info
    
    def _perform_astronomical_calculation(self, 
                                        date: datetime,
                                        lat: float,
                                        lon: float) -> LunarPhaseInfo:
        """
        Perform the actual astronomical calculation using PyEphem.
        
        This method uses accurate astronomical calculations from PyEphem
        to determine the current lunar phase and illumination.
        """
        try:
            import ephem as pyephem
            
            # Convert to UTC if timezone-aware
            if date.tzinfo is not None:
                date = date.astimezone(timezone.utc).replace(tzinfo=None)
            
            # Create observer
            observer = pyephem.Observer()
            observer.lat = str(lat)
            observer.lon = str(lon)
            observer.date = date
            
            # Create moon object
            moon = pyephem.Moon()
            moon.compute(observer)
            
            # Calculate phase information
            illumination = moon.phase  # Percentage illuminated
            
            # Calculate phase angle (0-360 degrees)
            phase_angle = self._calculate_phase_angle(observer, moon)
            
            # Calculate days from new moon
            previous_new_moon = pyephem.previous_new_moon(date)
            days_from_new = date - previous_new_moon.datetime()
            days_from_new = days_from_new.total_seconds() / (24 * 3600)
            
            # Calculate days to full moon
            if illumination < 99:  # If not at full moon
                next_full_moon = pyephem.next_full_moon(date)
                days_to_full = next_full_moon.datetime() - date
                days_to_full = days_to_full.total_seconds() / (24 * 3600)
            else:
                days_to_full = 0
            
            # Determine phase name
            phase = self._determine_phase_from_angle(phase_angle, illumination)
            
            return LunarPhaseInfo(
                phase=phase,
                illumination_percentage=max(0, min(100, illumination)),
                angle=phase_angle,
                date=date,
                next_phase=self._get_next_phase(phase),
                distance_km=384400.0  # Average Earth-Moon distance
            )
            
        except ImportError:
            # Fallback to simplified calculation if PyEphem not available
            logger.warning("PyEphem not available, using simplified calculation")
            return self._simplified_calculation_fallback(date, lat, lon)
        except Exception as e:
            logger.error(f"Astronomical calculation failed: {e}")
            return self._simplified_calculation_fallback(date, lat, lon)
    
    def _calculate_phase_angle(self, observer, moon) -> float:
        """Calculate the phase angle of the moon (0-360 degrees)."""
        import ephem as pyephem
        
        sun = pyephem.Sun()
        sun.compute(observer)
        
        # Calculate the elongation (angular distance from sun)
        elongation = float(pyephem.separation(sun, moon))
        
        # Convert to degrees and handle the phase progression
        elongation_degrees = math.degrees(elongation)
        
        # Determine if waxing or waning based on moon's position relative to sun
        moon_ra = float(moon.ra)
        sun_ra = float(sun.ra)
        
        # Calculate phase angle (0-360)
        if moon_ra >= sun_ra:
            phase_angle = elongation_degrees
        else:
            phase_angle = 360 - elongation_degrees
        
        return phase_angle
    
    def _determine_phase_from_angle(self, phase_angle: float, illumination: float) -> LunarPhase:
        """Determine the phase name based on angle and illumination."""
        # Normalize angle to 0-360
        angle = phase_angle % 360
        
        # Define phase ranges based on angle
        if angle < 45 or angle >= 315:
            if illumination < 5:
                return LunarPhase.NEW_MOON
            else:
                return LunarPhase.WAXING_CRESCENT
        elif 45 <= angle < 90:
            return LunarPhase.WAXING_CRESCENT
        elif 90 <= angle < 135:
            return LunarPhase.FIRST_QUARTER
        elif 135 <= angle < 180:
            return LunarPhase.WAXING_GIBBOUS
        elif 180 <= angle < 225:
            return LunarPhase.FULL_MOON
        elif 225 <= angle < 270:
            return LunarPhase.WANING_GIBBOUS
        elif 270 <= angle < 315:
            return LunarPhase.THIRD_QUARTER
        else:
            return LunarPhase.WANING_CRESCENT
    
    def _simplified_calculation_fallback(self, date: datetime, lat: float, lon: float) -> LunarPhaseInfo:
        """Fallback to simplified calculation if PyEphem fails."""
        # Calculate basic lunar phase based on date
        # This is a simplified version - real implementation would use proper astronomy
        days_since_new_moon = (date.toordinal() - datetime(2000, 1, 6).toordinal()) % 29.53
        
        if days_since_new_moon < 1:
            phase = LunarPhase.NEW_MOON
            illumination = 0.0
        elif days_since_new_moon < 7:
            phase = LunarPhase.WAXING_CRESCENT
            illumination = days_since_new_moon / 14.77 * 50
        elif days_since_new_moon < 9:
            phase = LunarPhase.FIRST_QUARTER
            illumination = 50.0
        elif days_since_new_moon < 14:
            phase = LunarPhase.WAXING_GIBBOUS
            illumination = 50 + (days_since_new_moon - 7) / 7.77 * 50
        elif days_since_new_moon < 16:
            phase = LunarPhase.FULL_MOON
            illumination = 100.0
        elif days_since_new_moon < 22:
            phase = LunarPhase.WANING_GIBBOUS
            illumination = 100 - (days_since_new_moon - 14.77) / 7.77 * 50
        elif days_since_new_moon < 24:
            phase = LunarPhase.THIRD_QUARTER
            illumination = 50.0
        else:
            phase = LunarPhase.WANING_CRESCENT
            illumination = 50 - (days_since_new_moon - 22.27) / 7.77 * 50
        
        angle = (days_since_new_moon / 29.53) * 360
        
        return LunarPhaseInfo(
            phase=phase,
            illumination_percentage=max(0, min(100, illumination)),
            angle=angle,
            date=date,
            next_phase=self._get_next_phase(phase),
            distance_km=384400.0  # Average Earth-Moon distance
        )
    
    def _get_next_phase(self, current_phase: LunarPhase) -> LunarPhase:
        """Get the next lunar phase in sequence."""
        phases = list(LunarPhase)
        current_index = phases.index(current_phase)
        next_index = (current_index + 1) % len(phases)
        return phases[next_index]
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics for monitoring."""
        total = self._cache_stats["hits"] + self._cache_stats["misses"]
        hit_rate = self._cache_stats["hits"] / total if total > 0 else 0
        return {
            **self._cache_stats,
            "total_requests": total,
            "hit_rate": hit_rate
        }
    
    def clear_cache(self) -> None:
        """Clear the calculation cache."""
        self.calculate_phase_for_date.cache_clear()
        self._cache_stats = {"hits": 0, "misses": 0}

