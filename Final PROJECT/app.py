import streamlit as st
import pandas as pd
import requests
import joblib # To load your trained model
from datetime import datetime, timedelta 

# --- Configuration ---
# IMPORTANT: Your actual OpenWeather API KEY
OPENWEATHER_API_KEY = st.secrets["OPENWEATHER_API_KEY"] 

# Load the trained model and feature columns
try:
    model = joblib.load('crop_yield_model.pkl')
    model_features = joblib.load('model_features.pkl')
except FileNotFoundError:
    st.error("❌ Model files (crop_yield_model.pkl or model_features.pkl) not found. Please ensure they are in the same directory as this app.py.")
    st.stop() # Stop the app if model files are missing

# Hardcoded Historical Average Yields (calculated from your crop_data.csv)
HISTORICAL_AVG_YIELDS = {
    'maize': 363.10, # Average yield for maize in your dataset (tonnes/hectare)
    'rice': 407.30 # Average yield for rice in your dataset (tonnes/hectare)
}

# Hardcoded Average Nutrient and Pesticide Requirements per Hectare (calculated from your crop_data.csv)
AVG_NUTRIENT_PESTICIDE_PER_HA = {
    'maize': {'N': 77.76, 'P': 48.44, 'K': 19.79, 'pesticides_tonnes_per_ha_base': 327.66}, 
    'rice': {'N': 79.89, 'P': 47.58, 'K': 39.87, 'pesticides_tonnes_per_ha_base': 369.42}  
}

# Initialize session state for dynamic slider defaults
if 'avg_temp_from_api' not in st.session_state:
    st.session_state['avg_temp_from_api'] = 25.0 # Default fallback
if 'avg_annual_rainfall_from_api' not in st.session_state:
    st.session_state['avg_annual_rainfall_from_api'] = 1500.0 # Default fallback

# Updated page_title and main title to "RootPredict"
st.set_page_config(page_title="RootPredict: Climate-Resilient Yield & Resource Planner", page_icon="📈", layout="centered")

# --- Custom CSS for enhanced aesthetics ---
st.markdown("""
<style>
/* General body font and spacing */
.stApp {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Make headers slightly more impactful */
h1 {
    color: #2E8B57; /* A deeper green */
    text-align: center;
    font-size: 2.8em; /* Slightly larger */
    padding-bottom: 10px;
    margin-bottom: 20px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.05); /* Subtle shadow for depth */
}
h2 {
    color: #3CB371; /* A medium green */
    font-size: 2.0em; /* Slightly larger */
    border-bottom: 2px solid #A5D6A7; /* Light green underline */
    padding-bottom: 5px;
    margin-top: 35px; /* More spacing above */
    margin-bottom: 20px; /* More spacing below */
}
h3 {
    color: #4CAF50; /* Primary green */
    font-size: 1.5em;
    margin-top: 25px;
    margin-bottom: 10px;
}

/* Custom styling for containers/sections */
.stContainer {
    background-color: #FAFAFA; /* Slightly off-white for internal containers */
    padding: 25px; /* More padding */
    border-radius: 12px; /* More rounded corners */
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08); /* Soft shadow for lift */
    margin-bottom: 25px; /* More spacing between containers */
    border: 1px solid #E0F2E0; /* Subtle border */
}

/* Input fields and sliders */
.stSlider > div > div {
    background-color: #E6F6E6; /* Secondary background color */
    border-radius: 8px; /* More rounded */
}
.stNumberInput, .stSelectbox, .stTextInput {
    border-radius: 8px; /* More rounded */
    border: 1px solid #A5D6A7;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.08); /* More noticeable inset shadow */
    padding: 8px; /* More padding inside inputs */
}

/* Buttons */
.stButton>button {
    background-color: #4CAF50;
    color: white;
    border-radius: 10px; /* More rounded */
    padding: 12px 25px; /* Larger padding */
    font-size: 1.1em; /* Slightly larger font */
    border: none;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25); /* Stronger shadow */
    transition: background-color 0.3s ease, transform 0.2s ease; /* Add transform for subtle hover effect */
    margin-top: 15px; /* Space above buttons */
    margin-bottom: 10px; /* Space below buttons */
}
.stButton>button:hover {
    background-color: #388E3C; /* Darker green on hover */
    transform: translateY(-2px); /* Lift effect on hover */
}

/* Expander styling */
.streamlit-expanderHeader {
    background-color: #E6F6E6; /* Match secondary background */
    border-radius: 10px; /* More rounded */
    padding: 15px 20px; /* More padding */
    color: #1E421E; /* Dark green text */
    font-weight: bold;
    font-size: 1.1em; /* Slightly larger font */
    box-shadow: 0 2px 5px rgba(0,0,0,0.1); /* Subtle shadow for expander */
    margin-bottom: 15px;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: #E6F6E6;
    border-left: 6px solid #4CAF50; /* Thicker border */
    padding: 20px; /* More padding */
    border-radius: 10px; /* More rounded */
    margin-bottom: 15px;
    box-shadow: 0 3px 6px rgba(0,0,0,0.08);
}
[data-testid="stMetricLabel"] {
    font-weight: bold;
    color: #388E3C;
    font-size: 1.1em;
}
[data-testid="stMetricValue"] {
    color: #2E8B57;
    font-size: 2.2em !important; /* Significantly larger */
    font-weight: bold;
}
[data-testid="stMetricDelta"] {
    color: #2E8B57; /* Ensure delta color is also green-themed */
}

/* Info/Success/Warning boxes */
.stAlert {
    border-radius: 8px;
    padding: 15px;
}
.stSuccess {
    background-color: #E8F5E9; /* Very light green */
    color: #2E7D32; /* Dark green */
    border-left: 6px solid #4CAF50;
}
.stWarning {
    background-color: #FFFDE7; /* Very light yellow */
    color: #FFB300; /* Orange-yellow */
    border-left: 6px solid #FFC107;
}
.stInfo {
    background-color: #E1F5FE; /* Very light blue */
    color: #1976D2; /* Dark blue */
    border-left: 6px solid #2196F3;
}
</style>
""", unsafe_allow_html=True)


# --- Header Section ---
st.container()
st.title("🌱 RootPredict: Climate-Resilient Yield & Resource Planner")
st.markdown("""
    _Empowering sustainable agriculture through predictive intelligence for **Zero Hunger (SDG 2)**
    and proactive **Climate Action (SDG 13)**._
""")
st.markdown("---")

# --- Investment Rationale Section (now in an expander) ---
with st.expander("🎯 **Why Invest in RootPredict? Unlock Sustainable Growth!**"):
    st.markdown("""
        Our AI-powered platform delivers **actionable intelligence** for the agricultural sector, offering compelling value for investors by:
        * **🛡️ Mitigating Climate Risks**: Strategically planning for future climate scenarios to protect agricultural assets and ensure long-term viability.
        * **💰 Optimizing Resource Allocation**: Precisely calculating input needs (fertilizers, pesticides) to reduce waste, enhance efficiency, and boost profitability.
        * **🌍 Enhancing Food Security**: Driving sustainable practices that ensure stable and increasing crop yields, vital for a growing global population.
        * **✅ Achieving ESG Goals**: Directly aligning with UN Sustainable Development Goals, demonstrating a commitment to responsible and impactful investment.
    """)
st.markdown("---")


# --- User Inputs Section ---
with st.container():
    st.header("📊 1. Configure Your Farming Scenario")
    st.markdown("Set the stage for your crop yield prediction and resource planning.")

    col1, col2 = st.columns(2)
    with col1:
        crop_options = ["maize", "rice"] # Keep current crop options
        selected_crop = st.selectbox("🌿 Select Crop Type:", crop_options, help="Choose the crop for which you want to predict yield and plan resources.")
    with col2:
        land_area_ha = st.number_input("🚜 Enter Land Area (hectares):", min_value=1.0, max_value=10000.0, value=10.0, step=1.0, help="Specify the total land area for your agricultural operation.")

    st.subheader("📍 Global Weather & Location Details:")
    city_name_input = st.text_input("🌍 Enter City Name (e.g., Paris, Mumbai, Lebowakgomo):", "Lebowakgomo", help="Type the name of any city worldwide to get its current weather.")

    # --- Fetch Current Weather Data (for demonstration of API integration) ---
    if st.button(f"🌤️ Fetch Current Weather for {city_name_input}"):
        with st.spinner(f"Fetching current weather data for {city_name_input}..."):
            # Step 1: Geocoding - Convert city name to lat/lon using OpenWeather
            geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name_input}&limit=1&appid={OPENWEATHER_API_KEY}"
            try:
                geo_response = requests.get(geocode_url)
                geo_data = geo_response.json()

                if geo_response.status_code == 200 and geo_data:
                    lat = geo_data[0]['lat']
                    lon = geo_data[0]['lon']
                    actual_city_name = geo_data[0]['name'] # Use the name returned by API for accuracy

                    # Step 2: Fetch Current Weather
                    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
                    weather_response = requests.get(weather_url)
                    weather_data = weather_response.json()

                    if weather_response.status_code == 200:
                        temp = weather_data['main']['temp']
                        humidity = weather_data['main']['humidity']
                        weather_desc = weather_data['weather'][0]['description']
                        st.success(f"Current Weather for {actual_city_name}:")
                        st.markdown(f"- **Temperature:** **{temp}°C**")
                        st.markdown(f"- **Humidity:** **{humidity}%**")
                        st.markdown(f"- **Conditions:** **{weather_desc.capitalize()}**")
                        st.info("💡 Note: This is current weather. For yield prediction, the model relies on simulated *seasonal averages* below.")
                    else:
                        st.error(f"❌ Could not fetch weather data for {actual_city_name} from OpenWeather: {weather_data.get('message', 'Unknown error')}. Please check your API key and try again.")
                else:
                    st.error(f"❌ Could not find geographic coordinates for '{city_name_input}'. Please check the city name for typos and try again.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Network error: Could not connect to OpenWeatherMap API. Please check your internet connection.")
            except Exception as e:
                st.error(f"❌ An unexpected error occurred during weather fetching: {e}")
    
    # New section for fetching historical averages using Meteostat
    st.subheader("🗓️ Fetch Historical Climate Averages (Meteostat)")
    st.info("💡 Click below to automatically fetch 10-year average temperature and rainfall for your chosen city. This will update the simulation sliders for a realistic baseline.")
    if st.button(f"Fetch Climate Averages for {city_name_input}", key="fetch_climate_averages_btn"):
        with st.spinner(f"Fetching 10-year climate averages for {city_name_input} from Meteostat..."):
            try:
                # Step 1: Geocoding (reuse existing logic from current weather fetch with OpenWeather)
                geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name_input}&limit=1&appid={OPENWEATHER_API_KEY}"
                geo_response = requests.get(geocode_url)
                geo_data = geo_response.json()

                if geo_response.status_code == 200 and geo_data:
                    lat = geo_data[0]['lat']
                    lon = geo_data[0]['lon']
                    actual_city_name_for_avg = geo_data[0]['name']

                    st.write(f"DEBUG: Geocoded {city_name_input} to Lat: {lat}, Lon: {lon}")
                    
                    # Step 2: Fetch historical data using Meteostat
                    try:
                        from meteostat import Point, Daily # Import Meteostat classes here

                        # Define the 10-year period (from 2015-01-01 to 2024-12-31)
                        start_date_meteostat = datetime(2015, 1, 1) 
                        end_date_meteostat = datetime(2024, 12, 31)

                        # Create a Point for the location
                        location_point = Point(lat, lon) 

                        # Get daily data for the 10-year period
                        data = Daily(location_point, start_date_meteostat, end_date_meteostat)
                        data = data.fetch() # Fetch data into a Pandas DataFrame

                        if data is not None and not data.empty:
                            # Meteostat columns: 'tavg' for average temperature, 'prcp' for precipitation sum
                            avg_temp_over_period = data['tavg'].mean()
                            total_precipitation_over_period = data['prcp'].sum()

                            # Calculate annual average precipitation from total
                            num_full_years = (end_date_meteostat.year - start_date_meteostat.year) + 1
                            if num_full_years == 0: num_full_years = 1 # Avoid division by zero for periods less than a year
                            avg_annual_precipitation = total_precipitation_over_period / num_full_years

                            st.success(f"Climate Averages for {actual_city_name_for_avg} ({start_date_meteostat.year}-{end_date_meteostat.year}):")
                            st.markdown(f"- **Average Annual Temperature:** **{avg_temp_over_period:.2f}°C**")
                            st.markdown(f"- **Average Annual Rainfall:** **{avg_annual_precipitation:.2f} mm/year**")
                            
                            # Store these values in Streamlit's session state to update sliders
                            st.session_state['avg_temp_from_api'] = avg_temp_over_period
                            st.session_state['avg_annual_rainfall_from_api'] = avg_annual_precipitation
                            st.rerun() # Using st.rerun()
                            
                        else:
                            st.error(f"❌ No climate data available for {actual_city_name_for_avg} from Meteostat for the period {start_date_meteostat.year}-{end_date_meteostat.year}. This might happen for very remote locations or if all nearby stations lack data.")
                    except ImportError:
                        st.error("❌ The 'meteostat' library is not installed. Please install it using: `pip install meteostat`")
                    except Exception as e:
                        st.error(f"❌ An error occurred while fetching climate data from Meteostat: {e}. Please ensure coordinates are valid and try again.")
                else:
                    st.error(f"❌ Could not find geographic coordinates for '{city_name_input}'. Please check the city name for typos.")
            except requests.exceptions.ConnectionError:
                st.error("❌ Network error: Could not connect to OpenWeatherMap/Meteostat API. Please check your internet connection.")
            except Exception as e:
                st.error(f"❌ An unexpected error occurred during climate data fetching: {e}")
    st.markdown("---")

# --- Simulate Climate & Soil Inputs for Prediction ---
with st.container():
    st.header("📈 2. Simulate Seasonal & Soil Conditions")
    st.markdown(
        "Adjust these parameters to model potential future climate conditions and "
        "customize soil nutrient and pesticide levels for your crop. These values are used by the AI model for yield prediction."
    )

    st.subheader("☀️ Climate Change Scenario:")
    # Scenario options - now with dynamic defaults if API values are loaded
    scenario_options = {
        "Baseline (Current Climate)": {"temp_offset": 0.0, "rainfall_factor": 1.0},
        "Moderate Warming (+1.5°C)": {"temp_offset": 1.5, "rainfall_factor": 0.9}, # 10% less rain
        "Severe Warming (+3.0°C)": {"temp_offset": 3.0, "rainfall_factor": 0.75} # 25% less rain
    }
    selected_scenario_name = st.selectbox("Select Climate Scenario:", list(scenario_options.keys()), help="Choose a scenario to see its potential impact on yield and resource needs.")
    temp_offset = scenario_options[selected_scenario_name]["temp_offset"]
    rainfall_factor = scenario_options[selected_scenario_name]["rainfall_factor"]
    
    # Use session state values if available, otherwise fall back to original defaults
    base_temp_for_sliders = st.session_state['avg_temp_from_api']
    base_rainfall_for_sliders = st.session_state['avg_annual_rainfall_from_api']

    # Default values for sliders, adjusted by scenario and (now) fetched API data
    sim_avg_temp_default = base_temp_for_sliders + temp_offset
    sim_avg_rainfall_default = base_rainfall_for_sliders * rainfall_factor

    col_clim1, col_clim2 = st.columns(2)
    with col_clim1:
        # Temperature slider value updated from API
        sim_temp = st.slider("🌡️ Average Seasonal Temperature (°C):", min_value=15.0, max_value=35.0, 
                             value=sim_avg_temp_default, # Use calculated default including API data
                             step=0.1, help="Average temperature over the growing season.")
        sim_humidity = st.slider("💧 Average Seasonal Humidity (%):", min_value=30.0, max_value=95.0, value=75.0, step=0.1, help="Average humidity over the growing season.")
        sim_ph = st.slider("🧪 Soil pH Level:", min_value=4.0, max_value=9.0, value=6.5, step=0.1, help="The acidity or alkalinity of the soil.")
    with col_clim2:
        sim_rainfall_current = st.slider("🌧️ Total Seasonal Rainfall (mm):", min_value=50.0, max_value=300.0, value=150.0, step=1.0, help="Total rainfall expected during the growing season.")
        # Average annual rainfall slider value updated from API
        sim_avg_rain_fall = st.slider("☔ Average Annual Rainfall (mm/year):", min_value=500.0, max_value=3000.0, 
                                       value=sim_avg_rainfall_default, # Use calculated default including API data
                                       step=10.0, help="Long-term average annual rainfall for the region.")

    st.subheader("🔬 Soil Nutrients & Pesticide Levels (per hectare baseline):")
    st.markdown("Adjust the baseline nutrient and pesticide levels. These are scaled by your land area.")
    col_nut1, col_nut2, col_nut3, col_nut4 = st.columns(4)
    with col_nut1:
        sim_N = st.slider("🌱 Nitrogen (N) (kg/ha):", min_value=0, max_value=140, value=int(AVG_NUTRIENT_PESTICIDE_PER_HA[selected_crop]['N']), help="Nitrogen is crucial for leaf growth and overall plant vigor.")
    with col_nut2:
        sim_P = st.slider("🪨 Phosphorus (P) (kg/ha):", min_value=0, max_value=140, value=int(AVG_NUTRIENT_PESTICIDE_PER_HA[selected_crop]['P']), help="Phosphorus supports root development, flowering, and fruiting.")
    with col_nut3:
        sim_K = st.slider("✨ Potassium (K) (kg/ha):", min_value=0, max_value=140, value=int(AVG_NUTRIENT_PESTICIDE_PER_HA[selected_crop]['K']), help="Potassium aids in water regulation, nutrient transport, and disease resistance.")
    with col_nut4:
        sim_pesticides_tonnes_input = st.slider("🐛 Pesticides (tonnes/ha base):", min_value=0.0, max_value=500.0, value=AVG_NUTRIENT_PESTICIDE_PER_HA[selected_crop]['pesticides_tonnes_per_ha_base'], step=1.0, help="Simulated pesticide usage baseline per hectare.")

    st.markdown("---")

# --- Prediction & Results Section ---
with st.container():
    st.header("📈 3. Prediction & Impact Analysis")
    st.markdown("Run the AI model to predict crop yield and calculate necessary resources based on your chosen scenario.")
    
    # Predict button at the bottom of inputs, before results
    if st.button("🚀 Predict Yield & Calculate Resources", type="primary"):
        with st.spinner("Calculating predictions and resource estimates..."):
            try:
                # Prepare input data for the model
                input_data = {
                    'N': sim_N,
                    'P': sim_P,
                    'K': sim_K,
                    'temperature': sim_temp, 
                    'humidity': sim_humidity,
                    'ph': sim_ph,
                    'rainfall': sim_rainfall_current, 
                    'average_rain_fall_mm_per_year': sim_avg_rain_fall,
                    'pesticides_tonnes': sim_pesticides_tonnes_input, 
                    'avg_temp': sim_temp,
                    'label_maize': 1 if selected_crop == 'maize' else 0,
                    'label_rice': 1 if selected_crop == 'rice' else 0
                }

                input_df = pd.DataFrame([input_data])
                input_df = input_df[model_features] # Ensure column order

                # Make prediction
                predicted_yield_per_ha = model.predict(input_df)[0]
                total_predicted_yield = predicted_yield_per_ha * land_area_ha

                historical_avg_yield_per_ha = HISTORICAL_AVG_YIELDS.get(selected_crop, 0)
                
                st.subheader("💡 Your Prediction Results:")
                col_pred1, col_pred2 = st.columns(2)
                with col_pred1:
                    st.metric(label=f"Predicted {selected_crop.capitalize()} Yield (per hectare)", value=f"{predicted_yield_per_ha:.2f} tonnes/ha 🌾")
                with col_pred2:
                    st.metric(label=f"Total Predicted Yield for {land_area_ha:.0f} ha", value=f"{total_predicted_yield:.2f} tonnes 🚚")
                
                st.markdown("---")

                st.subheader("📈 Yield Comparison & Scenario Insights:")
                st.write(f"The historical average yield for {selected_crop.capitalize()} is: **{historical_avg_yield_per_ha:.2f} tonnes/hectare**.")

                if predicted_yield_per_ha > historical_avg_yield_per_ha:
                    st.success(f"🎉 **Strong Performance!** Under these simulated conditions, the predicted yield is **{((predicted_yield_per_ha - historical_avg_yield_per_ha)/historical_avg_yield_per_ha * 100):.2f}% higher** than the historical average. This indicates highly favorable conditions or optimized inputs, highlighting potential for **significant ROI**.")
                elif predicted_yield_per_ha < historical_avg_yield_per_ha:
                    st.warning(f"⚠️ **Potential Challenges!** Under these simulated conditions, the predicted yield is **{((historical_avg_yield_per_ha - predicted_yield_per_ha)/historical_avg_yield_per_ha * 100):.2f}% lower** than the historical average. This signals potential climate challenges or suboptimal inputs, emphasizing the need for **adaptive strategies and targeted investments** to mitigate risks.")
                else:
                    st.info("The predicted yield is aligned with the historical average, suggesting stable conditions.")
                
                st.markdown("---")

                # --- Nutrient and Pesticide Calculation for Land Area ---
                st.subheader(f"🌱 Resource Optimization for {land_area_ha:.0f} Hectares:")
                st.markdown("These are the estimated resource needs for your specified land area, based on historical averages.")
                
                avg_n_per_ha = AVG_NUTRIENT_PESTICIDE_PER_HA[selected_crop]['N']
                avg_p_per_ha = AVG_NUTRIENT_PESTICIDE_PER_HA[selected_crop]['P']
                avg_k_per_ha = AVG_NUTRIENT_PESTICIDE_PER_HA[selected_crop]['K']
                avg_pesticides_per_ha_base = AVG_NUTRIENT_PESTICIDE_PER_HA[selected_crop]['pesticides_tonnes_per_ha_base'] 

                col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                with col_res1:
                    st.metric("Nitrogen (N) Needed", f"{avg_n_per_ha * land_area_ha:.2f} kg")
                with col_res2:
                    st.metric("Phosphorus (P) Needed", f"{avg_p_per_ha * land_area_ha:.2f} kg")
                with col_res3:
                    st.metric("Potassium (K) Needed", f"{avg_k_per_ha * land_area_ha:.2f} kg")
                with col_res4:
                    st.metric("Pesticides Needed", f"{avg_pesticides_per_ha_base * land_area_ha:.2f} tonnes")
                
                st.info("💡 Note: These estimations are based on average historical usage from the training data, scaled by your input land area. Actual requirements may vary based on specific soil tests, crop varietals, and local agricultural practices.")
                
                st.markdown("---")

            except Exception as e:
                st.error(f"❌ Error during prediction: {e}. Please check your inputs and ensure the model is loaded correctly.")

# --- SDG Alignment Section ---
with st.container():
    st.header("🌍 UN Sustainable Development Goals (SDGs) Impact")
    st.markdown("RootPredict is a powerful instrument for advancing **sustainable development** in agriculture:")

    col_sdg1, col_sdg2 = st.columns(2)
    with col_sdg1:
        # Changed to local image path
        st.image("SDG_2.png", width=100) 
        st.subheader("SDG 2: Zero Hunger")
        st.write(
            "By offering precise yield forecasts and **resource optimization recommendations**, "
            "RootPredict directly aids in **maximizing food production efficiency** and **minimizing input waste**. "
            "This empowers farmers to boost productivity, reduces food insecurity, and builds more resilient food systems, "
            "leading to **stable and increasing returns** for investments in agriculture."
        )
    with col_sdg2:
        # Changed to local image path
        st.image("SDG_13.png", width=100) 
        st.subheader("SDG 13: Climate Action")
        st.write(
            "The ability to simulate yield under different **climate change scenarios** "
            "provides invaluable **risk assessment and adaptation planning capabilities**. "
            "This promotes climate-resilient farming, helps predict impacts from extreme weather, "
            "and informs sustainable land management. Investors can support ventures that are inherently "
            "climate-resilient, securing **long-term viability and sustainability of agricultural investments**."
        )

st.markdown("---")
st.caption("Developed as an AI Solution for the UN SDGs by Your Name/Team Name")