"""
Generate Historical Training Data for LSTM Model
Creates realistic historical energy consumption data for the past 30 days
"""

import os
import sys
import math
import random
import psycopg2
from datetime import datetime, timedelta
from typing import List, Dict

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "smartgrid"),
    "user": os.getenv("DB_USER", "smartgrid_user"),
    "password": os.getenv("DB_PASSWORD", "smartgrid_pass")
}

# Smart meters configuration
METERS = [
    {"id": "SM001", "type": "residential", "base_consumption": 3.5},
    {"id": "SM002", "type": "residential", "base_consumption": 4.2},
    {"id": "SM003", "type": "commercial", "base_consumption": 15.0},
    {"id": "SM004", "type": "industrial", "base_consumption": 45.0},
    {"id": "SM005", "type": "residential", "base_consumption": 5.5}
]

def generate_realistic_consumption(meter: Dict, timestamp: datetime) -> Dict:
    """Generate realistic energy consumption data based on time patterns"""
    
    hour = timestamp.hour
    day_of_week = timestamp.weekday()
    month = timestamp.month
    
    # Base consumption
    base = meter["base_consumption"]
    
    # Time of day pattern (peak hours: 7-9 AM, 5-9 PM)
    if 7 <= hour <= 9 or 17 <= hour <= 21:
        time_factor = 1.5  # Peak hours
    elif 0 <= hour <= 6:
        time_factor = 0.5  # Night hours
    else:
        time_factor = 1.0  # Normal hours
    
    # Day of week pattern (weekends slightly different)
    if day_of_week >= 5:  # Weekend
        if meter["type"] == "commercial" or meter["type"] == "industrial":
            day_factor = 0.3  # Lower consumption on weekends
        else:
            day_factor = 1.2  # Higher residential consumption on weekends
    else:
        day_factor = 1.0
    
    # Seasonal pattern (summer/winter higher due to AC/heating)
    if month in [6, 7, 8, 12, 1, 2]:
        season_factor = 1.3
    else:
        season_factor = 1.0
    
    # Calculate active power (kW)
    active_power = base * time_factor * day_factor * season_factor
    
    # Add random variation (±15%)
    active_power *= random.uniform(0.85, 1.15)
    
    # Calculate energy for 1-hour interval
    active_energy = active_power
    
    # Electrical parameters
    voltage_l1 = 230 + random.uniform(-5, 5)
    current_l1 = active_power * 1000 / voltage_l1 / math.sqrt(3)
    power_factor = random.uniform(0.92, 0.98)
    frequency = 50.0 + random.uniform(-0.05, 0.05)
    
    return {
        "meter_id": meter["id"],
        "timestamp": timestamp,
        "active_energy": round(active_energy, 3),
        "reactive_energy": round(active_energy * 0.1, 3),
        "apparent_energy": round(active_energy * 1.05, 3),
        "active_power": round(active_power, 2),
        "reactive_power": round(active_power * 0.1, 2),
        "power_factor": round(power_factor, 3),
        "voltage_l1": round(voltage_l1, 1),
        "voltage_l2": round(voltage_l1 + random.uniform(-2, 2), 1),
        "voltage_l3": round(voltage_l1 + random.uniform(-2, 2), 1),
        "current_l1": round(current_l1, 2),
        "current_l2": round(current_l1 + random.uniform(-0.5, 0.5), 2),
        "current_l3": round(current_l1 + random.uniform(-0.5, 0.5), 2),
        "frequency": round(frequency, 2),
        "quality_flag": "good"
    }

def insert_historical_data(conn, readings: List[Dict]):
    """Insert historical readings into database"""
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO energy_readings (
        meter_id, timestamp, active_energy, reactive_energy, apparent_energy,
        active_power, reactive_power, power_factor,
        voltage_l1, voltage_l2, voltage_l3,
        current_l1, current_l2, current_l3,
        frequency, quality_flag
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    );
    """

    for reading in readings:
        try:
            cursor.execute(insert_query, (
                reading["meter_id"],
                reading["timestamp"],
                reading["active_energy"],
                reading["reactive_energy"],
                reading["apparent_energy"],
                reading["active_power"],
                reading["reactive_power"],
                reading["power_factor"],
                reading["voltage_l1"],
                reading["voltage_l2"],
                reading["voltage_l3"],
                reading["current_l1"],
                reading["current_l2"],
                reading["current_l3"],
                reading["frequency"],
                reading["quality_flag"]
            ))
        except Exception:
            # Skip duplicates silently
            pass

    conn.commit()
    cursor.close()

def main():
    """Generate and insert historical data"""
    print("🔄 Generating historical training data...")
    print(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")

    # Connect to database
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

    # Generate data for the past 30 days (720 hours)
    days_to_generate = 30
    hours_to_generate = days_to_generate * 24

    print(f"\n📊 Generating {hours_to_generate} hours of data for {len(METERS)} meters...")
    print(f"   Total readings to generate: {hours_to_generate * len(METERS):,}")

    # Start from 30 days ago
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days_to_generate)

    batch_size = 100
    readings_batch = []
    total_inserted = 0

    # Generate hourly data
    current_time = start_time
    while current_time <= end_time:
        for meter in METERS:
            reading = generate_realistic_consumption(meter, current_time)
            readings_batch.append(reading)

            # Insert in batches
            if len(readings_batch) >= batch_size:
                insert_historical_data(conn, readings_batch)
                total_inserted += len(readings_batch)
                print(f"   Inserted {total_inserted:,} readings...", end='\r')
                readings_batch = []

        current_time += timedelta(hours=1)

    # Insert remaining readings
    if readings_batch:
        insert_historical_data(conn, readings_batch)
        total_inserted += len(readings_batch)

    print(f"\n✅ Successfully inserted {total_inserted:,} historical readings")

    # Verify data
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            meter_id,
            COUNT(*) as reading_count,
            MIN(timestamp) as first_reading,
            MAX(timestamp) as last_reading
        FROM energy_readings
        GROUP BY meter_id
        ORDER BY meter_id;
    """)

    print("\n📈 Data Summary:")
    for row in cursor.fetchall():
        meter_id, count, first, last = row
        hours = (last - first).total_seconds() / 3600
        print(f"   {meter_id}: {count:,} readings ({hours:.1f} hours of data)")

    cursor.close()
    conn.close()
    print("\n🎉 Historical data generation complete!")

if __name__ == "__main__":
    main()

