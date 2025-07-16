# AI-SE-FINAL-PROJECT-W8


# 🌱 **RootPredict: Climate-Resilient Crop Yield & Resource Planner**  
_Cultivating Tomorrow's Harvest with AI-Powered Precision_

Live web address:
`https://ai-se-final-project-w8-msuc4wbwztmsus6nd2zsyw.streamlit.app/#root-predict-climate-resilient-yield-and-resource-planner`.

pITCHDECK LINK:`https://drive.google.com/file/d/199stNy3FkvajeLAVF4AjcGqK3hed4yJY/view?usp=sharing
`

---

## 🚀 **Project Overview**
RootPredict is an intuitive, **AI-driven web application** designed to empower farmers and agricultural stakeholders with **data-driven insights** for optimizing crop yields and managing resources. Leveraging machine learning, the platform provides **predictive analytics** based on environmental and soil conditions, fostering more sustainable and resilient agricultural practices.

This project directly addresses critical global challenges related to food security (**UN SDG 2: Zero Hunger**) and climate change adaptation (**UN SDG 13: Climate Action**) by enabling proactive decision-making in farming.

---

## ✨ **Key Features**
- **AI-Powered Yield Prediction**: Predicts potential crop yield (tons/hectare) based on user-defined and real-world environmental inputs.
- **Comprehensive Input Control**: Allows users to simulate various scenarios by adjusting sliders for:
  - Soil Nutrients: Nitrogen (N), Phosphorus (P), Potassium (K)
  - Soil Health: pH Level
  - Environmental Factors: Temperature, Humidity, Seasonal Rainfall, Average Annual Rainfall
  - Resource Usage: Pesticides (tonnes)
- **Dynamic Climate Data Integration**: Uses the **Meteostat API** to fetch 10-year historical climate averages for any global city.
- **Current Weather Fetch**: Retrieves real-time weather conditions using **OpenWeatherMap API**.
- **Expanded Crop Support** (Coming Soon): Predictions for Potatoes, Wheat, Sorghum, Soybeans, Cassava, Sweet Potatoes, Plantains, and Yams.
- **Yield Comparison**: Compares predicted vs. historical yields for insights.
- **Resource Optimization Estimates**: Estimates nutrient and pesticide needs.
- **User-Friendly Interface**: Built with **Streamlit**, offering a clean, responsive, and themed UI.

---

## 🎯 **UN Sustainable Development Goals (SDGs) Alignment**
- **SDG 2: Zero Hunger** – Maximizes food production & enhances food security.
- **SDG 13: Climate Action** – Supports climate-resilient farming & sustainable land use.

---

## 🛠️ **Technologies Used**
- **Python** (Core programming)
- **Streamlit** (Web UI)
- **Pandas**, **NumPy** (Data handling)
- **Scikit-learn**, **RandomForestRegressor** (ML model)
- **Joblib** (Model persistence)
- **Meteostat API**, **OpenWeatherMap API**
- **Requests** (API communication)

---

## 📂 **Project Structure**
```
RootPredict/
├── app.py                      # Streamlit app
├── crop_yield_model.pkl        # ML model
├── model_features.pkl          # Model features
├── requirements.txt            # Dependencies
├── .streamlit/
│   └── config.toml             # Theme config
├── SDG_2.png                   # SDG 2 icon
├── SDG_13.png                  # SDG 13 icon
├── crop_data.csv               # Training data
└── README.md                   # This file
```

---

## ⚙️ **How to Run Locally**
1. **Clone the Repository:**
```bash
git clone https://github.com/KlaasMatlou/AI-SE-FINAL-PROJECT-W8.git
cd AI-SE-FINAL-PROJECT-W8
```

2. **Create a Virtual Environment:**
```bash
python -m venv venv
# Windows:
.env\Scriptsctivate
# macOS/Linux:
source venv/bin/activate
```

3. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set Up API Key in `app.py`:**
```python
OPENWEATHER_API_KEY = "YOUR_API_KEY_HERE"
```

5. **Run the App:**
```bash
streamlit run app.py
```

---

## 🚀 **Deployment Instructions**
- Push all files to [GitHub Repo](https://github.com/KlaasMatlou/AI-SE-FINAL-PROJECT-W8)
- Use **Streamlit Cloud** to deploy
- Secure your API key via **Streamlit Secrets**
- Your app will be live at:  
  https://ai-se-final-project-w8-msuc4wbwztmsus6nd2zsyw.streamlit.app/

---

## 📊 **Data Sources**
- **crop_data.csv**: Training data (Maize, Rice)
- **Meteostat API**: Historical weather data
- **OpenWeatherMap API**: Current weather data & location geocoding

---

## 🧠 **Model Details**
- **Model**: RandomForestRegressor
- **Features**: N, P, K, temperature, humidity, pH, rainfall, avg_rainfall, avg_temp, pesticides, crop type
- **Target**: `yield_tonnes_per_hectare`
- **Performance**: Accurate on Maize & Rice; generalizes to other crops

---

## ⚖️ **Ethical Considerations**
- **Privacy**: Public data used; future updates will ensure user data security.
- **Fairness**: Limited crop training data; expanding to avoid bias.
- **Accessibility**: Streamlit ensures mobile responsiveness.
- **Sustainability**: Energy-efficient models.
- **Transparency**: Open model and data source communication.

---

## 📈 **Future Enhancements**
- Real-time IoT sensor integration
- Personalized farm recommendations
- ROI and economic modules
- Native mobile apps
- Climate scenario forecasting

---

## 📧 **Contact**
**Klaas Matlou**  
📧 tshupianematlou@gmail.com
[+27720724950]

---

## 📄 **License**
MIT License
