"""
Customer Billing Service
Handles billing calculations and invoice generation
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.smart_meter import EnergyReading, SmartMeter
from app.models.pricing import CustomerBilling, EnergyPrice

logger = logging.getLogger(__name__)


class BillingService:
    """Service for customer billing and invoice generation"""
    
    def __init__(self):
        self.base_price = settings.BASE_ENERGY_PRICE
        self.peak_multiplier = settings.PEAK_HOUR_MULTIPLIER
        self.off_peak_multiplier = settings.OFF_PEAK_MULTIPLIER
    
    def calculate_monthly_bill(self, meter_id: str, billing_month: datetime) -> Dict:
        """Calculate monthly bill for a specific meter"""
        try:
            db = SessionLocal()
            
            # Get meter information
            meter = db.query(SmartMeter).filter(SmartMeter.meter_id == meter_id).first()
            if not meter:
                raise ValueError(f"Meter {meter_id} not found")
            
            # Calculate billing period
            start_date = billing_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if billing_month.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1)
            
            # Get energy readings for the billing period
            readings = db.query(EnergyReading).filter(
                EnergyReading.meter_id == meter_id,
                EnergyReading.timestamp >= start_date,
                EnergyReading.timestamp < end_date
            ).all()
            
            if not readings:
                logger.warning(f"No readings found for meter {meter_id} in period {start_date} to {end_date}")
                return self._create_empty_bill(meter_id, start_date, end_date)
            
            # Calculate consumption by time period
            consumption_data = self._categorize_consumption(readings)
            
            # Get pricing information
            pricing = self._get_pricing_for_period(start_date, end_date, db)
            
            # Calculate charges
            charges = self._calculate_charges(consumption_data, pricing, meter.meter_type)
            
            # Calculate total bill
            total_amount = sum(charges.values())
            
            # Create billing record
            bill = CustomerBilling(
                meter_id=meter_id,
                billing_period_start=start_date,
                billing_period_end=end_date,
                total_energy_kwh=consumption_data['total_energy'],
                peak_energy_kwh=consumption_data['peak_energy'],
                off_peak_energy_kwh=consumption_data['off_peak_energy'],
                peak_demand_kw=consumption_data['peak_demand'],
                energy_charges=charges['energy'],
                demand_charges=charges['demand'],
                transmission_charges=charges['transmission'],
                distribution_charges=charges['distribution'],
                taxes_and_fees=charges['taxes'],
                total_amount=total_amount,
                due_date=end_date + timedelta(days=30),
                payment_status='pending'
            )
            
            db.add(bill)
            db.commit()
            db.refresh(bill)
            
            db.close()
            
            return {
                'bill_id': bill.id,
                'meter_id': meter_id,
                'billing_period': {
                    'start': start_date,
                    'end': end_date
                },
                'consumption': consumption_data,
                'charges': charges,
                'total_amount': total_amount,
                'due_date': bill.due_date,
                'status': 'generated'
            }
            
        except Exception as e:
            logger.error(f"Error calculating bill for meter {meter_id}: {e}")
            raise
    
    def _categorize_consumption(self, readings: List[EnergyReading]) -> Dict:
        """Categorize energy consumption by time periods"""
        total_energy = 0
        peak_energy = 0
        off_peak_energy = 0
        standard_energy = 0
        peak_demand = 0
        
        for reading in readings:
            hour = reading.timestamp.hour
            energy = reading.active_energy or 0
            power = reading.active_power or 0
            
            total_energy += energy
            peak_demand = max(peak_demand, power)
            
            # Categorize by time of use
            if 17 <= hour <= 21:  # Peak hours
                peak_energy += energy
            elif 22 <= hour <= 6:  # Off-peak hours
                off_peak_energy += energy
            else:  # Standard hours
                standard_energy += energy
        
        return {
            'total_energy': round(total_energy, 2),
            'peak_energy': round(peak_energy, 2),
            'off_peak_energy': round(off_peak_energy, 2),
            'standard_energy': round(standard_energy, 2),
            'peak_demand': round(peak_demand, 2),
            'reading_count': len(readings)
        }
    
    def _get_pricing_for_period(self, start_date: datetime, end_date: datetime, db: Session) -> Dict:
        """Get pricing information for billing period"""
        # Get average pricing for the period
        pricing = db.query(
            func.avg(EnergyPrice.base_price_kwh).label('base_price'),
            func.avg(EnergyPrice.peak_price_kwh).label('peak_price'),
            func.avg(EnergyPrice.off_peak_price_kwh).label('off_peak_price')
        ).filter(
            EnergyPrice.timestamp >= start_date,
            EnergyPrice.timestamp < end_date
        ).first()
        
        if pricing and pricing.base_price:
            return {
                'base_price_kwh': float(pricing.base_price),
                'peak_price_kwh': float(pricing.peak_price),
                'off_peak_price_kwh': float(pricing.off_peak_price)
            }
        else:
            # Fallback to default pricing
            return {
                'base_price_kwh': self.base_price,
                'peak_price_kwh': self.base_price * self.peak_multiplier,
                'off_peak_price_kwh': self.base_price * self.off_peak_multiplier
            }
    
    def _calculate_charges(self, consumption: Dict, pricing: Dict, meter_type: str) -> Dict:
        """Calculate various charges for the bill"""
        
        # Meter type multipliers
        type_multipliers = {
            'residential': 1.0,
            'commercial': 0.95,
            'industrial': 0.90
        }
        multiplier = type_multipliers.get(meter_type, 1.0)
        
        # Energy charges
        energy_charge = (
            consumption['peak_energy'] * pricing['peak_price_kwh'] * multiplier +
            consumption['off_peak_energy'] * pricing['off_peak_price_kwh'] * multiplier +
            consumption['standard_energy'] * pricing['base_price_kwh'] * multiplier
        )
        
        # Demand charges (for commercial and industrial)
        demand_charge = 0
        if meter_type in ['commercial', 'industrial']:
            demand_rate = 15.0 if meter_type == 'commercial' else 12.0  # $/kW
            demand_charge = consumption['peak_demand'] * demand_rate
        
        # Transmission and distribution charges
        transmission_charge = consumption['total_energy'] * 0.02  # $0.02/kWh
        distribution_charge = consumption['total_energy'] * 0.03  # $0.03/kWh
        
        # Taxes and fees
        subtotal = energy_charge + demand_charge + transmission_charge + distribution_charge
        tax_rate = 0.08  # 8% tax
        taxes = subtotal * tax_rate
        
        return {
            'energy': round(energy_charge, 2),
            'demand': round(demand_charge, 2),
            'transmission': round(transmission_charge, 2),
            'distribution': round(distribution_charge, 2),
            'taxes': round(taxes, 2)
        }
    
    def _create_empty_bill(self, meter_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Create empty bill when no readings are available"""
        return {
            'meter_id': meter_id,
            'billing_period': {
                'start': start_date,
                'end': end_date
            },
            'consumption': {
                'total_energy': 0,
                'peak_energy': 0,
                'off_peak_energy': 0,
                'standard_energy': 0,
                'peak_demand': 0,
                'reading_count': 0
            },
            'charges': {
                'energy': 0,
                'demand': 0,
                'transmission': 0,
                'distribution': 0,
                'taxes': 0
            },
            'total_amount': 0,
            'status': 'no_data'
        }
    
    def generate_monthly_bills(self, billing_month: Optional[datetime] = None):
        """Generate bills for all active meters"""
        try:
            if billing_month is None:
                # Default to previous month
                today = datetime.utcnow()
                if today.month == 1:
                    billing_month = today.replace(year=today.year - 1, month=12)
                else:
                    billing_month = today.replace(month=today.month - 1)
            
            db = SessionLocal()
            
            # Get all active meters
            meters = db.query(SmartMeter).filter(SmartMeter.is_active == True).all()
            
            generated_bills = []
            failed_bills = []
            
            for meter in meters:
                try:
                    bill = self.calculate_monthly_bill(meter.meter_id, billing_month)
                    generated_bills.append(bill)
                    logger.info(f"Generated bill for meter {meter.meter_id}")
                except Exception as e:
                    logger.error(f"Failed to generate bill for meter {meter.meter_id}: {e}")
                    failed_bills.append({
                        'meter_id': meter.meter_id,
                        'error': str(e)
                    })
            
            db.close()
            
            logger.info(f"Generated {len(generated_bills)} bills, {len(failed_bills)} failures")
            
            return {
                'billing_month': billing_month,
                'generated_bills': len(generated_bills),
                'failed_bills': len(failed_bills),
                'bills': generated_bills,
                'failures': failed_bills
            }
            
        except Exception as e:
            logger.error(f"Error generating monthly bills: {e}")
            raise
    
    def get_customer_bills(self, meter_id: str, months: int = 12) -> List[Dict]:
        """Get billing history for a customer"""
        try:
            db = SessionLocal()
            
            start_date = datetime.utcnow() - timedelta(days=months * 30)
            
            bills = db.query(CustomerBilling).filter(
                CustomerBilling.meter_id == meter_id,
                CustomerBilling.billing_period_start >= start_date
            ).order_by(CustomerBilling.billing_period_start.desc()).all()
            
            db.close()
            
            return [
                {
                    'bill_id': bill.id,
                    'billing_period': {
                        'start': bill.billing_period_start,
                        'end': bill.billing_period_end
                    },
                    'total_energy_kwh': bill.total_energy_kwh,
                    'total_amount': bill.total_amount,
                    'due_date': bill.due_date,
                    'payment_status': bill.payment_status,
                    'payment_date': bill.payment_date
                }
                for bill in bills
            ]
            
        except Exception as e:
            logger.error(f"Error getting bills for meter {meter_id}: {e}")
            raise
    
    def process_payment(self, bill_id: int, payment_amount: float, payment_date: Optional[datetime] = None) -> Dict:
        """Process payment for a bill"""
        try:
            db = SessionLocal()
            
            bill = db.query(CustomerBilling).filter(CustomerBilling.id == bill_id).first()
            if not bill:
                raise ValueError(f"Bill {bill_id} not found")
            
            if payment_date is None:
                payment_date = datetime.utcnow()
            
            if payment_amount >= bill.total_amount:
                bill.payment_status = 'paid'
                bill.payment_date = payment_date
                status = 'paid_in_full'
            else:
                bill.payment_status = 'partial'
                bill.payment_date = payment_date
                status = 'partial_payment'
            
            db.commit()
            db.close()
            
            return {
                'bill_id': bill_id,
                'payment_amount': payment_amount,
                'payment_date': payment_date,
                'status': status,
                'remaining_balance': max(0, bill.total_amount - payment_amount)
            }
            
        except Exception as e:
            logger.error(f"Error processing payment for bill {bill_id}: {e}")
            raise
