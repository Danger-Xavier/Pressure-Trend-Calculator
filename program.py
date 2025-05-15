import os

def clear_console():
    """Clear the console screen (uses 'cls' for Windows)."""
    os.system('cls')

def determine_trend(pressure1, pressure2, threshold=0.01):
    """
    Determine the trend between two pressure readings (in inHg).
    Returns 'Rising', 'Falling', or 'Steady' based on the difference.
    Threshold avoids minor fluctuations being counted as a change.
    """
    diff = pressure2 - pressure1
    if diff > threshold:
        return "Rising"
    elif diff < -threshold:
        return "Falling"
    else:
        return "Steady"

def calculate_pressure_trend(current_pressure, past_pressures, unit="inHg"):
    """
    Calculate the pressure trend for a station model, including intermediate trends.
    
    Parameters:
    current_pressure (float): Current pressure in chosen unit (inHg, hPa, kPa, or custom)
    past_pressures (list): List of pressures [1 hour ago, 2 hours ago, 3 hours ago] in chosen unit
    unit (str): Unit of input pressure ('inHg', 'hPa', 'kPa', or 'custom')
    
    Returns:
    dict: Dictionary containing current pressure (mb and station model format),
          pressure change (mb), trend value (tenths of mb), overall trend direction,
          and detailed tendency description.
    """
    # Conversion factors
    INHG_TO_MB = 33.8639   # 1 inHg = 33.8639 mb
    HPA_TO_INHG = 0.02953   # 1 hPa = 0.02953 inHg
    KPA_TO_INHG = 0.2953    # 1 kPa = 10 hPa = 0.2953 inHg
    
    # Convert input pressures to inHg for internal consistency
    if unit == "hPa":
        current_pressure_inhg = current_pressure * HPA_TO_INHG
        past_pressures_inhg = [p * HPA_TO_INHG for p in past_pressures]
    elif unit == "kPa":
        current_pressure_inhg = current_pressure * KPA_TO_INHG
        past_pressures_inhg = [p * KPA_TO_INHG for p in past_pressures]
    elif unit == "custom":
        current_pressure_inhg = current_pressure  # Current pressure in inHg
        past_pressures_inhg = [p * HPA_TO_INHG for p in past_pressures]  # Past pressures in hPa to inHg
    else:  # inHg
        current_pressure_inhg = current_pressure
        past_pressures_inhg = past_pressures
    
    # Convert pressures to millibars for station model
    current_pressure_mb = current_pressure_inhg * INHG_TO_MB
    pressure_1h_ago_mb = past_pressures_inhg[0] * INHG_TO_MB
    pressure_2h_ago_mb = past_pressures_inhg[1] * INHG_TO_MB
    pressure_3h_ago_mb = past_pressures_inhg[2] * INHG_TO_MB
    
    # Calculate pressure change over 3 hours (current - 3h ago)
    pressure_change_mb = current_pressure_mb - pressure_3h_ago_mb
    
    # Round pressure change to nearest 0.1 mb for station model
    pressure_change_mb = round(pressure_change_mb, 1)
    
    # Determine overall trend direction
    if pressure_change_mb > 0:
        overall_trend = "Rising"
    elif pressure_change_mb < 0:
        overall_trend = "Falling"
    else:
        overall_trend = "Steady"
    
    # Calculate trend value in tenths of millibars (absolute value)
    trend_value = int(abs(pressure_change_mb) * 10)
    
    # Format current pressure for station model (last 3 digits of mb, e.g., 1013.2 -> 132)
    current_pressure_mb_rounded = round(current_pressure_mb, 1)
    station_model_pressure = int(current_pressure_mb_rounded * 10) % 1000
    
    # Convert current pressure and change back to chosen unit for display
    if unit == "hPa":
        display_current_pressure = current_pressure_mb_rounded  # Already in mb (hPa)
        display_pressure_change = pressure_change_mb  # Already in mb (hPa)
        unit_label = "hPa"
    elif unit == "kPa":
        display_current_pressure = current_pressure_mb_rounded / 10  # Convert mb to kPa
        display_pressure_change = pressure_change_mb / 10  # Convert mb to kPa
        unit_label = "kPa"
    elif unit == "custom":
        display_current_pressure = current_pressure_inhg  # Current in inHg
        display_pressure_change = pressure_change_mb  # Change in hPa (mb)
        unit_label = "hPa (change), inHg (current)"
    else:  # inHg
        display_current_pressure = current_pressure_inhg
        display_pressure_change = pressure_change_mb / INHG_TO_MB  # Convert mb to inHg
        unit_label = "inHg"
    
    # Calculate intermediate trends (using inHg values)
    trend_3h_to_2h = determine_trend(past_pressures_inhg[2], past_pressures_inhg[1])
    trend_2h_to_1h = determine_trend(past_pressures_inhg[1], past_pressures_inhg[0])
    trend_1h_to_now = determine_trend(past_pressures_inhg[0], current_pressure_inhg)
    
    # Simplify to two periods: first two hours (3h to 1h), last hour (1h to now)
    if trend_3h_to_2h == trend_2h_to_1h:
        first_period_trend = trend_3h_to_2h
    elif trend_3h_to_2h == "Steady" and trend_2h_to_1h != "Steady":
        first_period_trend = trend_2h_to_1h
    elif trend_2h_to_1h == "Steady" and trend_3h_to_2h != "Steady":
        first_period_trend = trend_3h_to_2h
    else:
        pressure_change_first_period = past_pressures_inhg[0] - past_pressures_inhg[2]
        first_period_trend = determine_trend(past_pressures_inhg[2], past_pressures_inhg[0])
    
    second_period_trend = trend_1h_to_now
    
    # Determine the tendency description
    tendency_description = f"{first_period_trend} then {second_period_trend}"
    
    # Station model tendency symbol
    tendency_symbol = ""
    if first_period_trend == "Rising" and second_period_trend == "Falling":
        tendency_symbol = "+/"
    elif first_period_trend == "Falling" and second_period_trend == "Rising":
        tendency_symbol = "-+"
    elif first_period_trend == "Rising" and second_period_trend == "Steady":
        tendency_symbol = "+="
    elif first_period_trend == "Falling" and second_period_trend == "Steady":
        tendency_symbol = "-="
    elif first_period_trend == "Rising" and second_period_trend == "Rising":
        tendency_symbol = "+"
    elif first_period_trend == "Falling" and second_period_trend == "Falling":
        tendency_symbol = "-"
    elif first_period_trend == "Steady" and second_period_trend == "Rising":
        tendency_symbol = "=+"
    elif first_period_trend == "Steady" and second_period_trend == "Falling":
        tendency_symbol = "=-"
    elif first_period_trend == "Steady" and second_period_trend == "Steady":
        tendency_symbol = "="
    
    return {
        "current_pressure_display": display_current_pressure,
        "current_pressure_mb": current_pressure_mb_rounded,
        "station_model_pressure": station_model_pressure,
        "pressure_change_display": display_pressure_change,
        "pressure_change_mb": pressure_change_mb,
        "trend_value": trend_value,
        "overall_trend": overall_trend,
        "tendency_description": tendency_description,
        "tendency_symbol": tendency_symbol,
        "unit": unit,
        "unit_label": unit_label
    }

def main():
    while True:
        # Clear console at the start of each calculation
        clear_console()
        
        print("Pressure Trend Calculator")
        print("------------------------")
        
        # Ask for unit preference
        print("Select pressure unit:")
        print("1. inHg (inches of mercury)")
        print("2. hPa (hectopascals)")
        print("3. kPa (kilopascals)")
        print("4. Custom (current in inHg, past in hPa)")
        unit_choice = input("Enter 1, 2, 3, or 4: ").strip()
        
        if unit_choice == "1":
            unit = "inHg"
            unit_label = "inHg"
        elif unit_choice == "2":
            unit = "hPa"
            unit_label = "hPa"
        elif unit_choice == "3":
            unit = "kPa"
            unit_label = "kPa"
        elif unit_choice == "4":
            unit = "custom"
            unit_label = "hPa (change), inHg (current)"
        else:
            print("\nInvalid choice. Defaulting to inHg.")
            unit = "inHg"
            unit_label = "inHg"
        
        # Input pressures
        try:
            if unit == "custom":
                print("\nEnter current pressure in inHg and past pressures in hPa:")
                current_pressure = float(input("Enter current pressure (inHg): "))
                pressure_1h = float(input("Enter pressure 1 hour ago (hPa): "))
                pressure_2h = float(input("Enter pressure 2 hours ago (hPa): "))
                pressure_3h = float(input("Enter pressure 3 hours ago (hPa): "))
            else:
                print(f"\nEnter pressures in {unit_label}:")
                current_pressure = float(input(f"Enter current pressure ({unit_label}): "))
                pressure_1h = float(input(f"Enter pressure 1 hour ago ({unit_label}): "))
                pressure_2h = float(input(f"Enter pressure 2 hours ago ({unit_label}): "))
                pressure_3h = float(input(f"Enter pressure 3 hours ago ({unit_label}): "))
            
            past_pressures = [pressure_1h, pressure_2h, pressure_3h]
            
            # Calculate pressure trend
            result = calculate_pressure_trend(current_pressure, past_pressures, unit)
            
            # Display results
            print("\nPressure Trend Results:")
            print(f"Current Pressure: {result['current_pressure_display']:.2f} {result['unit_label'].split(' ')[0]} "
                  f"({result['current_pressure_mb']:.1f} mb)")
            print(f"Station Model Pressure: {result['station_model_pressure']:03d}")
            print(f"Pressure Change (3 hours): {result['pressure_change_display']:+.1f} {result['unit_label'].split(' ')[0]} "
                  f"({result['pressure_change_mb']:+.1f} mb)")
            print(f"Pressure Trend: {result['trend_value']} tenths of mb "
                  f"({result['overall_trend']})")
            print(f"Pressure Tendency: {result['tendency_description']} "
                  f"(Symbol: {result['tendency_symbol']})")
        
        except ValueError:
            print("\nError: Please enter valid numeric values for pressures.")
        
        # Ask if user wants to continue
        print("\nWould you like to calculate another trend? (y/n)")
        choice = input().strip().lower()
        if choice != 'y':
            clear_console()
            print("Thank you for using the Pressure Trend Calculator!")
            break

if __name__ == "__main__":
    main()