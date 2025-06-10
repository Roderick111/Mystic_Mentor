#!/usr/bin/env python3
"""
Lunar Calculator Service

Provides accurate astronomical calculations for lunar phases and current moon information.
Integrates with the Esoteric AI Agent to provide real-time lunar data.
"""

import math
import time
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Optional, Protocol

# Try to import logger, fallback to print if not available
try:
    from utils.logger import logger
except ImportError:
    class SimpleLogger:
        def debug(self, msg): pass
        def warning(self, msg): print(f"⚠️ {msg}")
        def error(self, msg): print(f"❌ {msg}")
    logger = SimpleLogger()


class LunarPhase(Enum):
    """Enumeration of lunar phases."""
    NEW_MOON = "New Moon"
    WAXING_CRESCENT = "Waxing Crescent"
    FIRST_QUARTER = "First Quarter"
    WAXING_GIBBOUS = "Waxing Gibbous"
    FULL_MOON = "Full Moon"
    WANING_GIBBOUS = "Waning Gibbous"
    THIRD_QUARTER = "Third Quarter"
    WANING_CRESCENT = "Waning Crescent"


@dataclass
class LunarPhaseInfo:
    """Information about lunar phase at a specific time."""
    phase: LunarPhase
    illumination_percentage: float
    angle: float
    date: datetime
    next_phase: LunarPhase
    distance_km: float
    days_from_new_moon: float
    days_to_full_moon: float


class LocationServiceProtocol(Protocol):
    """Protocol for location services."""
    def get_default_location(self) -> Optional[Dict[str, float]]:
        """Get default location coordinates."""
        ...


class DefaultLocationService:
    """Default location service implementation."""
    
    def get_default_location(self) -> Dict[str, float]:
        """Return default location (Greenwich, UK)."""
        return {"lat": 51.4769, "lon": 0.0}


class LunarCalculatorService:
    """
    Handles astronomical calculations for lunar phases and moon information.
    
    This service provides accurate lunar calculations using astronomical formulas
    and integrates with the Esoteric AI Agent for real-time lunar guidance.
    """
    
    def __init__(self, location_service: Optional[LocationServiceProtocol] = None):
        """Initialize lunar calculator with location service."""
        self.location_service = location_service or DefaultLocationService()
        self._cache_stats = {"hits": 0, "misses": 0}
    
    def get_current_lunar_info(self, 
                              location_lat: Optional[float] = None,
                              location_lon: Optional[float] = None) -> LunarPhaseInfo:
        """
        Get current lunar phase information for today.
        
        Args:
            location_lat: Latitude (optional, uses default if not provided)
            location_lon: Longitude (optional, uses default if not provided)
            
        Returns:
            LunarPhaseInfo object with current lunar data
        """
        current_date = datetime.now(timezone.utc)
        return self.calculate_phase_for_date(
            current_date.isoformat(),
            location_lat,
            location_lon
        )
    
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
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_str}") from e
        
        # Get location or use default
        if location_lat is None or location_lon is None:
            default_location = self.location_service.get_default_location()
            location_lat = location_lat or (default_location.get("lat") if default_location else 0.0)
            location_lon = location_lon or (default_location.get("lon") if default_location else 0.0)
        
        # Perform astronomical calculations
        phase_info = self._perform_astronomical_calculation(date, location_lat, location_lon)
        
        logger.debug(f"Calculated lunar phase for {date}: {phase_info.phase.value}")
        return phase_info
    
    def _perform_astronomical_calculation(self, 
                                        date: datetime,
                                        lat: float,
                                        lon: float) -> LunarPhaseInfo:
        """
        Perform astronomical calculation using accurate lunar algorithms.
        
        This method calculates lunar phase using established astronomical formulas
        for accurate moon phase determination.
        """
        try:
            # Try using PyEphem if available for maximum accuracy
            return self._pyephem_calculation(date, lat, lon)
        except ImportError:
            # Fall back to mathematical calculation
            logger.debug("PyEphem not available, using mathematical calculation")
            return self._mathematical_calculation(date, lat, lon)
        except Exception as e:
            logger.debug(f"PyEphem calculation failed: {e}, using fallback")
            return self._mathematical_calculation(date, lat, lon)
    
    def _pyephem_calculation(self, date: datetime, lat: float, lon: float) -> LunarPhaseInfo:
        """Calculate using PyEphem library for maximum accuracy."""
        import ephem
        
        # Convert to UTC if timezone-aware
        if date.tzinfo is not None:
            date = date.astimezone(timezone.utc).replace(tzinfo=None)
        
        # Create observer
        observer = ephem.Observer()
        observer.lat = str(lat)
        observer.lon = str(lon)
        observer.date = date
        
        # Create moon object
        moon = ephem.Moon()
        moon.compute(observer)
        
        # Calculate phase information
        illumination = float(moon.phase)  # Percentage illuminated
        
        # Calculate phase angle (0-360 degrees)
        phase_angle = self._calculate_phase_angle_ephem(observer, moon)
        
        # Calculate days from new moon
        previous_new_moon = ephem.previous_new_moon(date)
        days_from_new = date - previous_new_moon.datetime()
        days_from_new = days_from_new.total_seconds() / (24 * 3600)
        
        # Calculate days to next full moon
        if illumination < 99:  # If not at full moon
            next_full_moon = ephem.next_full_moon(date)
            days_to_full = next_full_moon.datetime() - date
            days_to_full = days_to_full.total_seconds() / (24 * 3600)
        else:
            days_to_full = 0
        
        # Determine phase name
        phase = self._determine_phase_from_illumination(illumination, days_from_new)
        
        return LunarPhaseInfo(
            phase=phase,
            illumination_percentage=max(0, min(100, illumination)),
            angle=phase_angle,
            date=date,
            next_phase=self._get_next_phase(phase),
            distance_km=float(moon.earth_distance) * 149597870.7,  # Convert AU to km
            days_from_new_moon=days_from_new,
            days_to_full_moon=max(0, days_to_full)
        )
    
    def _calculate_phase_angle_ephem(self, observer, moon) -> float:
        """Calculate the phase angle using PyEphem."""
        import ephem
        
        sun = ephem.Sun()
        sun.compute(observer)
        
        # Calculate the elongation (angular distance from sun)
        elongation = float(ephem.separation(sun, moon))
        elongation_degrees = math.degrees(elongation)
        
        return elongation_degrees
    
    def _mathematical_calculation(self, date: datetime, lat: float, lon: float) -> LunarPhaseInfo:
        """
        Calculate lunar phase using mathematical formulas.
        
        This is a fallback method that uses established astronomical algorithms
        for lunar phase calculation when PyEphem is not available.
        """
        # Convert to UTC if timezone-aware
        if date.tzinfo is not None:
            date = date.astimezone(timezone.utc).replace(tzinfo=None)
        
        # Calculate Julian Day Number
        julian_day = self._calculate_julian_day(date)
        
        # Calculate days since known new moon (January 6, 2000 18:14 UTC)
        known_new_moon_jd = 2451549.258  # Julian day for Jan 6, 2000 new moon
        days_since_known_new = julian_day - known_new_moon_jd
        
        # Lunar cycle length (synodic month)
        lunar_cycle = 29.53058867  # days
        
        # Calculate current position in lunar cycle
        cycles = days_since_known_new / lunar_cycle
        current_cycle_position = (cycles - math.floor(cycles)) * lunar_cycle
        
        # Calculate illumination percentage
        # Illumination follows a cosine curve
        illumination_angle = (current_cycle_position / lunar_cycle) * 2 * math.pi
        illumination = (1 - math.cos(illumination_angle)) * 50
        
        # Determine phase
        phase = self._determine_phase_from_cycle_position(current_cycle_position)
        
        # Calculate days from new moon and to full moon
        days_from_new = current_cycle_position
        days_to_full = (lunar_cycle / 2) - current_cycle_position
        if days_to_full < 0:
            days_to_full = lunar_cycle + days_to_full
        
        # Calculate phase angle
        phase_angle = (current_cycle_position / lunar_cycle) * 360
        
        return LunarPhaseInfo(
            phase=phase,
            illumination_percentage=max(0, min(100, illumination)),
            angle=phase_angle,
            date=date,
            next_phase=self._get_next_phase(phase),
            distance_km=384400.0,  # Average Earth-Moon distance
            days_from_new_moon=days_from_new,
            days_to_full_moon=max(0, days_to_full)
        )
    
    def _calculate_julian_day(self, date: datetime) -> float:
        """Calculate Julian Day Number for given date."""
        a = (14 - date.month) // 12
        y = date.year + 4800 - a
        m = date.month + 12 * a - 3
        
        jdn = date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        
        # Add fractional day
        fraction = (date.hour + date.minute / 60.0 + date.second / 3600.0) / 24.0
        
        return jdn + fraction - 0.5  # Astronomical convention
    
    def _determine_phase_from_illumination(self, illumination: float, days_from_new: float) -> LunarPhase:
        """Determine phase based on illumination percentage and days from new moon."""
        if illumination < 1:
            return LunarPhase.NEW_MOON
        elif illumination < 45:
            return LunarPhase.WAXING_CRESCENT if days_from_new < 14.77 else LunarPhase.WANING_CRESCENT
        elif illumination < 55:
            return LunarPhase.FIRST_QUARTER if days_from_new < 14.77 else LunarPhase.THIRD_QUARTER
        elif illumination < 99:
            return LunarPhase.WAXING_GIBBOUS if days_from_new < 14.77 else LunarPhase.WANING_GIBBOUS
        else:
            return LunarPhase.FULL_MOON
    
    def _determine_phase_from_cycle_position(self, cycle_position: float) -> LunarPhase:
        """Determine phase based on position in lunar cycle."""
        if cycle_position < 1:
            return LunarPhase.NEW_MOON
        elif cycle_position < 6.38:
            return LunarPhase.WAXING_CRESCENT
        elif cycle_position < 8.38:
            return LunarPhase.FIRST_QUARTER
        elif cycle_position < 13.77:
            return LunarPhase.WAXING_GIBBOUS
        elif cycle_position < 16.77:
            return LunarPhase.FULL_MOON
        elif cycle_position < 22.15:
            return LunarPhase.WANING_GIBBOUS
        elif cycle_position < 24.15:
            return LunarPhase.THIRD_QUARTER
        else:
            return LunarPhase.WANING_CRESCENT
    
    def _get_next_phase(self, current_phase: LunarPhase) -> LunarPhase:
        """Get the next lunar phase in sequence."""
        phases = [
            LunarPhase.NEW_MOON,
            LunarPhase.WAXING_CRESCENT,
            LunarPhase.FIRST_QUARTER,
            LunarPhase.WAXING_GIBBOUS,
            LunarPhase.FULL_MOON,
            LunarPhase.WANING_GIBBOUS,
            LunarPhase.THIRD_QUARTER,
            LunarPhase.WANING_CRESCENT
        ]
        
        current_index = phases.index(current_phase)
        next_index = (current_index + 1) % len(phases)
        return phases[next_index]
    
    def get_lunar_summary(self) -> str:
        """
        Get a formatted summary of current lunar information.
        
        Returns:
            Human-readable string with current lunar phase and illumination
        """
        lunar_info = self.get_current_lunar_info()
        
        summary_parts = [
            f"🌙 Current Date: {lunar_info.date.strftime('%B %d, %Y')}",
            f"🌙 Lunar Phase: {lunar_info.phase.value}",
            f"🌙 Illumination: {lunar_info.illumination_percentage:.1f}%",
            f"🌙 Days from New Moon: {lunar_info.days_from_new_moon:.1f}",
        ]
        
        if lunar_info.days_to_full_moon > 0:
            summary_parts.append(f"🌙 Days to Full Moon: {lunar_info.days_to_full_moon:.1f}")
        
        return "\n".join(summary_parts)
    
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


# Global instance for easy access
lunar_calculator = LunarCalculatorService()


def get_current_lunar_phase() -> str:
    """
    Convenience function to get current lunar phase information.
    
    Returns:
        Formatted string with current lunar information
    """
    return lunar_calculator.get_lunar_summary()


def get_current_lunar_data() -> LunarPhaseInfo:
    """
    Convenience function to get current lunar phase data.
    
    Returns:
        LunarPhaseInfo object with current lunar data
    """
    return lunar_calculator.get_current_lunar_info()


if __name__ == "__main__":
    # Test the lunar calculator
    print("🌙 Lunar Calculator Test")
    print("=" * 40)
    
    try:
        current_info = get_current_lunar_phase()
        print(current_info)
        
        # Test specific date (June 10, 2025)
        test_date = datetime(2025, 6, 10, 12, 0, 0, tzinfo=timezone.utc)
        test_info = lunar_calculator.calculate_phase_for_date(test_date.isoformat())
        
        print(f"\n🗓️ Test Date: June 10, 2025")
        print(f"🌙 Phase: {test_info.phase.value}")
        print(f"🌙 Illumination: {test_info.illumination_percentage:.1f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")

