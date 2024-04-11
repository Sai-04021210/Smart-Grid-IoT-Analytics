"""
Data validation utilities for Smart Grid IoT Analytics
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """Utility class for validating smart grid data"""
    
    @staticmethod
    def validate_meter_id(meter_id: str) -> bool:
        """Validate smart meter ID format"""
        if not meter_id or not isinstance(meter_id, str):
            return False
        
        # Meter ID should be alphanumeric, 3-20 characters
        pattern = r'^[A-Z0-9]{3,20}$'
        return bool(re.match(pattern, meter_id))
    
    @staticmethod
    def validate_energy_reading(reading: Dict[str, Any]) -> Dict[str, Any]:
        """Validate energy reading data"""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['meter_id', 'timestamp', 'active_energy']
        for field in required_fields:
            if field not in reading or reading[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate meter ID
        if 'meter_id' in reading:
            if not DataValidator.validate_meter_id(reading['meter_id']):
                errors.append("Invalid meter ID format")
        
        # Validate timestamp
        if 'timestamp' in reading:
            try:
                timestamp = datetime.fromisoformat(reading['timestamp'].replace('Z', '+00:00'))
                
                # Check if timestamp is reasonable (not too far in past/future)
                now = datetime.utcnow()
                if timestamp > now + timedelta(hours=1):
                    warnings.append("Timestamp is in the future")
                elif timestamp < now - timedelta(days=30):
                    warnings.append("Timestamp is more than 30 days old")
                    
            except (ValueError, AttributeError):
                errors.append("Invalid timestamp format")
        
        # Validate energy values
        energy_fields = ['active_energy', 'reactive_energy', 'apparent_energy']
        for field in energy_fields:
            if field in reading and reading[field] is not None:
                value = reading[field]
                if not isinstance(value, (int, float)) or value < 0:
                    errors.append(f"Invalid {field}: must be non-negative number")
                elif value > 10000:  # Reasonable upper limit
                    warnings.append(f"Unusually high {field}: {value}")
        
        # Validate power values
        power_fields = ['active_power', 'reactive_power']
        for field in power_fields:
            if field in reading and reading[field] is not None:
                value = reading[field]
                if not isinstance(value, (int, float)) or value < 0:
                    errors.append(f"Invalid {field}: must be non-negative number")
                elif value > 5000:  # Reasonable upper limit for power
                    warnings.append(f"Unusually high {field}: {value}")
        
        # Validate electrical parameters
        voltage_fields = ['voltage_l1', 'voltage_l2', 'voltage_l3']
        for field in voltage_fields:
            if field in reading and reading[field] is not None:
                value = reading[field]
                if not isinstance(value, (int, float)):
                    errors.append(f"Invalid {field}: must be a number")
                elif value < 100 or value > 300:  # Reasonable voltage range
                    warnings.append(f"Voltage out of normal range: {field}={value}V")
        
        # Validate current
        current_fields = ['current_l1', 'current_l2', 'current_l3']
        for field in current_fields:
            if field in reading and reading[field] is not None:
                value = reading[field]
                if not isinstance(value, (int, float)) or value < 0:
                    errors.append(f"Invalid {field}: must be non-negative number")
                elif value > 1000:  # Reasonable upper limit for current
                    warnings.append(f"Unusually high current: {field}={value}A")
        
        # Validate power factor
        if 'power_factor' in reading and reading['power_factor'] is not None:
            pf = reading['power_factor']
            if not isinstance(pf, (int, float)) or pf < 0 or pf > 1:
                errors.append("Power factor must be between 0 and 1")
            elif pf < 0.7:
                warnings.append(f"Low power factor: {pf}")
        
        # Validate frequency
        if 'frequency' in reading and reading['frequency'] is not None:
            freq = reading['frequency']
            if not isinstance(freq, (int, float)):
                errors.append("Frequency must be a number")
            elif freq < 45 or freq > 65:  # Reasonable frequency range
                warnings.append(f"Frequency out of normal range: {freq}Hz")
        
        # Validate quality flag
        if 'quality_flag' in reading:
            valid_flags = ['good', 'estimated', 'missing', 'error']
            if reading['quality_flag'] not in valid_flags:
                errors.append(f"Invalid quality flag: {reading['quality_flag']}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_renewable_data(data: Dict[str, Any], source_type: str) -> Dict[str, Any]:
        """Validate renewable energy generation data"""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['source_id', 'timestamp', 'power_output_kw']
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate source ID
        if 'source_id' in data:
            if not isinstance(data['source_id'], str) or len(data['source_id']) < 3:
                errors.append("Invalid source ID")
        
        # Validate timestamp
        if 'timestamp' in data:
            try:
                timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                now = datetime.utcnow()
                if timestamp > now + timedelta(hours=1):
                    warnings.append("Timestamp is in the future")
            except (ValueError, AttributeError):
                errors.append("Invalid timestamp format")
        
        # Validate power output
        if 'power_output_kw' in data and data['power_output_kw'] is not None:
            power = data['power_output_kw']
            if not isinstance(power, (int, float)) or power < 0:
                errors.append("Power output must be non-negative")
            elif power > 10000:  # Reasonable upper limit
                warnings.append(f"Unusually high power output: {power}kW")
        
        # Source-specific validations
        if source_type == 'solar':
            # Validate solar-specific fields
            if 'irradiance_wm2' in data and data['irradiance_wm2'] is not None:
                irradiance = data['irradiance_wm2']
                if not isinstance(irradiance, (int, float)) or irradiance < 0:
                    errors.append("Solar irradiance must be non-negative")
                elif irradiance > 1500:  # Theoretical maximum
                    warnings.append(f"Unusually high irradiance: {irradiance}W/m²")
            
            # Check for nighttime generation
            if 'timestamp' in data and 'power_output_kw' in data:
                try:
                    timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                    hour = timestamp.hour
                    if (hour < 6 or hour > 20) and data['power_output_kw'] > 0:
                        warnings.append("Solar generation during nighttime hours")
                except:
                    pass
        
        elif source_type == 'wind':
            # Validate wind-specific fields
            if 'wind_speed_ms' in data and data['wind_speed_ms'] is not None:
                wind_speed = data['wind_speed_ms']
                if not isinstance(wind_speed, (int, float)) or wind_speed < 0:
                    errors.append("Wind speed must be non-negative")
                elif wind_speed > 50:  # Reasonable upper limit
                    warnings.append(f"Unusually high wind speed: {wind_speed}m/s")
            
            if 'wind_direction_deg' in data and data['wind_direction_deg'] is not None:
                direction = data['wind_direction_deg']
                if not isinstance(direction, (int, float)) or direction < 0 or direction >= 360:
                    errors.append("Wind direction must be between 0 and 359 degrees")
        
        # Validate capacity factor
        if 'capacity_factor' in data and data['capacity_factor'] is not None:
            cf = data['capacity_factor']
            if not isinstance(cf, (int, float)) or cf < 0 or cf > 1:
                errors.append("Capacity factor must be between 0 and 1")
            elif cf > 0.9:
                warnings.append(f"Unusually high capacity factor: {cf}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_pricing_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pricing data"""
        errors = []
        warnings = []
        
        # Validate price values
        price_fields = ['base_price_kwh', 'peak_price_kwh', 'off_peak_price_kwh']
        for field in price_fields:
            if field in data and data[field] is not None:
                price = data[field]
                if not isinstance(price, (int, float)) or price < 0:
                    errors.append(f"{field} must be non-negative")
                elif price > 1.0:  # Reasonable upper limit
                    warnings.append(f"Unusually high price: {field}=${price}/kWh")
        
        # Validate time periods
        if 'peak_start_hour' in data:
            hour = data['peak_start_hour']
            if not isinstance(hour, int) or hour < 0 or hour > 23:
                errors.append("Peak start hour must be between 0 and 23")
        
        if 'peak_end_hour' in data:
            hour = data['peak_end_hour']
            if not isinstance(hour, int) or hour < 0 or hour > 23:
                errors.append("Peak end hour must be between 0 and 23")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data by removing/fixing common issues"""
        sanitized = data.copy()
        
        # Remove None values
        sanitized = {k: v for k, v in sanitized.items() if v is not None}
        
        # Convert string numbers to float
        numeric_fields = [
            'active_energy', 'reactive_energy', 'apparent_energy',
            'active_power', 'reactive_power',
            'voltage_l1', 'voltage_l2', 'voltage_l3',
            'current_l1', 'current_l2', 'current_l3',
            'power_factor', 'frequency',
            'power_output_kw', 'energy_generated_kwh',
            'irradiance_wm2', 'wind_speed_ms', 'wind_direction_deg',
            'temperature_c', 'capacity_factor', 'efficiency'
        ]
        
        for field in numeric_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                try:
                    sanitized[field] = float(sanitized[field])
                except ValueError:
                    # Remove invalid numeric values
                    del sanitized[field]
        
        # Normalize string fields
        string_fields = ['meter_id', 'source_id', 'quality_flag']
        for field in string_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                sanitized[field] = sanitized[field].strip().upper()
        
        return sanitized
    
    @staticmethod
    def validate_batch_data(data_list: List[Dict[str, Any]], data_type: str) -> Dict[str, Any]:
        """Validate a batch of data records"""
        total_records = len(data_list)
        valid_records = 0
        errors = []
        warnings = []
        
        for i, record in enumerate(data_list):
            if data_type == 'energy_reading':
                validation = DataValidator.validate_energy_reading(record)
            elif data_type == 'solar_data':
                validation = DataValidator.validate_renewable_data(record, 'solar')
            elif data_type == 'wind_data':
                validation = DataValidator.validate_renewable_data(record, 'wind')
            elif data_type == 'pricing_data':
                validation = DataValidator.validate_pricing_data(record)
            else:
                errors.append(f"Unknown data type: {data_type}")
                continue
            
            if validation['valid']:
                valid_records += 1
            else:
                errors.extend([f"Record {i+1}: {error}" for error in validation['errors']])
            
            warnings.extend([f"Record {i+1}: {warning}" for warning in validation['warnings']])
        
        return {
            'total_records': total_records,
            'valid_records': valid_records,
            'invalid_records': total_records - valid_records,
            'success_rate': valid_records / total_records if total_records > 0 else 0,
            'errors': errors,
            'warnings': warnings
        }
