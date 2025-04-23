import pandas as pd
import numpy as np

# Emission factors (kg CO2)
EMISSION_FACTORS = {
    "car_petrol": 0.21,  # per km (average small petrol car)
    "car_diesel": 0.18,  # per km (average small diesel car)
    "car_electric": 0.05,  # per km (electric vehicle using grid electricity)
    "public_transport": 0.08,  # per km (average bus)
    "motorcycle": 0.11,  # per km (average motorcycle)
    "flight_short": 0.24,  # per km (short haul flight)
    "flight_long": 0.18,  # per km (long haul flight - more efficient per km)
    "electricity": 0.233,  # per kWh (UK average)
    "natural_gas": 0.184,  # per kWh (natural gas heating)
    "meat_beef": 6.0,  # per meal (beef)
    "meat_pork": 1.7,  # per meal (pork)
    "meat_chicken": 0.9,  # per meal (chicken)
    "vegetarian": 0.5,  # per meal (vegetarian)
    "vegan": 0.4,  # per meal (vegan)
}

# National averages (kg CO2 per year)
NATIONAL_AVERAGES = {
    "UK": 5200,
    "USA": 16000,
    "EU": 6800,
    "World": 4800,
    "China": 7000,
    "India": 1900,
    "Australia": 15000,
    "Canada": 14000,
}

def calculate_transportation_emissions(transport_type, distance):
    """Calculate weekly emissions from transportation."""
    return distance * EMISSION_FACTORS.get(transport_type, 0)

def calculate_household_emissions(electricity_kwh, gas_kwh=0):
    """Calculate weekly emissions from household energy use."""
    electricity_emissions = electricity_kwh * EMISSION_FACTORS["electricity"]
    gas_emissions = gas_kwh * EMISSION_FACTORS["natural_gas"]
    return electricity_emissions + gas_emissions

def calculate_food_emissions(diet_type, meals_per_week):
    """Calculate weekly emissions from food choices."""
    return meals_per_week * EMISSION_FACTORS.get(diet_type, 0)

def get_footprint_comparison(annual_footprint, country="UK"):
    """Compare the user's footprint to the national average for a country."""
    national_avg = NATIONAL_AVERAGES.get(country, NATIONAL_AVERAGES["World"])
    percentage = (annual_footprint / national_avg) * 100
    
    if percentage > 120:
        message = f"Your carbon footprint is significantly higher than the {country} average."
        status = "high"
    elif percentage > 100:
        message = f"Your carbon footprint is above the {country} average."
        status = "above_avg"
    elif percentage > 80:
        message = f"Your carbon footprint is close to the {country} average."
        status = "average"
    elif percentage > 50:
        message = f"Your carbon footprint is below the {country} average. Good job!"
        status = "below_avg"
    else:
        message = f"Your carbon footprint is significantly lower than the {country} average. Excellent!"
        status = "low"
    
    return {
        "country": country,
        "national_avg": national_avg,
        "percentage": percentage,
        "message": message,
        "status": status
    }

def get_recommendations(emissions_data):
    """Generate personalized recommendations based on emissions data."""
    recommendations = []
    
    # Transportation recommendations
    if emissions_data.get("car_petrol", 0) > 30 or emissions_data.get("car_diesel", 0) > 30:
        recommendations.append("Consider carpooling, using public transport, or cycling for short journeys to reduce your driving emissions.")
    
    if emissions_data.get("flight_short", 0) > 50 or emissions_data.get("flight_long", 0) > 100:
        recommendations.append("Reduce the number of flights you take. Consider trains for shorter journeys or virtual meetings instead of business travel.")
    
    # Household recommendations
    if emissions_data.get("electricity", 0) > 40:
        recommendations.append("Reduce your electricity consumption by using energy-efficient appliances, LED bulbs, and being mindful of standby power.")
    
    if emissions_data.get("natural_gas", 0) > 30:
        recommendations.append("Improve your home insulation and consider lowering your heating thermostat by 1-2°C to save energy.")
    
    # Diet recommendations
    if emissions_data.get("meat_beef", 0) > 15:
        recommendations.append("Consider reducing beef consumption. Beef has one of the highest carbon footprints among food items.")
    
    if (emissions_data.get("meat_beef", 0) + emissions_data.get("meat_pork", 0) + 
            emissions_data.get("meat_chicken", 0)) > 20:
        recommendations.append("Try introducing 1-2 meat-free days per week to reduce your food-related carbon footprint.")
    
    # General recommendations if specific areas don't trigger recommendations
    if not recommendations:
        recommendations = [
            "Consider using renewable energy sources for your home.",
            "Look into carbon offsetting programs for emissions you can't reduce.",
            "Reduce, reuse, and recycle to minimize waste-related emissions.",
            "Support local businesses to reduce transportation emissions from goods."
        ]
    
    return recommendations

def format_emissions_for_download(data):
    """Format emissions data for download as CSV."""
    rows = []
    
    # Add weekly emissions
    for category, value in data["weekly_breakdown"].items():
        rows.append({"Category": category, "Timeframe": "Weekly", "Emissions (kg CO2)": value})
    
    # Add totals
    rows.append({"Category": "Total", "Timeframe": "Weekly", "Emissions (kg CO2)": data["weekly_total"]})
    rows.append({"Category": "Total", "Timeframe": "Annual", "Emissions (kg CO2)": data["annual_total"]})
    
    # Add comparison
    rows.append({"Category": "National Average", "Timeframe": "Annual", 
                 "Emissions (kg CO2)": data["comparison"]["national_avg"]})
    
    return pd.DataFrame(rows)