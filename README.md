
<img width="1280" height="640" alt="TV - 1" src="https://github.com/user-attachments/assets/89525059-7ea7-4147-bb30-d8d9da390af1" />


# Multidimensional Air Quality Analysis of India: From Data to Policy

## Project Overview
This project transforms raw environmental data into an actionable policy roadmap for India. By integrating **time-series forecasting**, **causal clustering**, and **spatial optimization**, we developed a framework to identify not only current pollution levels but also the underlying drivers and geographic "blind spots" in the national monitoring network.

---

## Key Features & Skills Applied

### 1. Advanced Data Engineering & Preprocessing
* **Cascading Imputation Strategy:** Engineered a sophisticated four-layer imputation pipeline to handle systemic data gaps (crucial for time-series integrity):
    * **Layer 1:** Linear & Time Interpolation for short-term missingness.
    * **Layer 2 (Historical Rhythm):** Filling gaps using identical hour/day historical lags (Daily/Weekly cycles).
    * **Layer 3 (Spatial Context):** Imputing based on neighboring stations within the same city or state.
    * **Layer 4:** Global Median for baseline continuity.
* **Data Quality Analysis:** Utilized the `missingno` library to identify systemic station failures, leading to the strategic removal of high-noise variables (e.g., Xylene with $>80\%$ missingness).

### 2. Temporal Analysis: Forecasting (The "Warning" Phase)
* **Hybrid Modeling:** Developed and compared multiple forecasting architectures - **SARIMA**, **LightGBM**, and **Deep Learning (LSTM)** - to predict AQI trends.
* **Key Finding:** Identified a synchronous pollution surge forecasted for the November–January peak season, providing statistical evidence for the necessity of seasonal mitigation efforts.

### 3. Causal Analysis: Interpretative Clustering (The "Diagnosis" Phase)
* **K-Means & Explainable AI:** Segmented monitoring stations based on chemical "fingerprints" (ratios of $SO_{2}, NO_{2}, CO, PM_{2.5}$) to identify specific root causes of pollution.
* **Decision Tree Surrogate:** Implemented a Decision Tree model as a surrogate to the clustering results. This converted high-dimensional clusters into clear, human-readable classification rules (e.g., distinguishing "Traffic-Dominated" from "Industrial-Thermal" zones).

### 4. Spatial Analysis: Network Optimization
* **Ordinary Kriging:** Interpolated AQI data across the national network to generate a **Kriging Variance/Uncertainty Map**.
* **Strategic Optimization:** Pinpointed "Information Deserts" (areas with low statistical reliability) and proposed scientifically optimized coordinates for expanding the national sensor network.

---

## Technical Stack
* **Languages:** Python
* **Data Wrangling:** `pandas`, `numpy`, `missingno`
* **Machine Learning:** `scikit-learn` (K-Means, Decision Trees), `lightgbm`
* **Time-Series:** `statsmodels` (SARIMAX), `tensorflow/keras` (LSTM)
* **Geo-Spatial:** `pykrige`, `folium`, `geopandas`

---

## Key Findings & Policy Impact
* **Industrial Hotspots:** Identified Ahmedabad as a persistent hotspot due to stagnant emissions in the food and beverage sector, while noting improvements in Delhi and Jaipur due to industrial relocation.
* **Data Coverage:** Quantified India's **Area Coverage Index at 0.73**, highlighting significant uncertainty in remote, non-urbanized regions.
* **Policy Recommendation:** Proposed targeted seasonal output restrictions on the chemical sector (specifically identifying the Adani Wilmar facility in Ahmedabad) during peak months to mitigate predictable localized surges.

---

## Portfolio Recommendations for GitHub

To make this repository look professional, I recommend the following setup:

1.  **Visuals:** Add a folder named `visuals/` and export your key plots (Kriging Map, LSTM Forecast, and Decision Tree) as PNG files. Embed them in this README using `![Alt Text](visuals/filename.png)`.
2.  **File Structure:**
    * `/data`: [(Link to the Kaggle dataset)](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india?select=station_hour.csv).
    * `/notebooks`: `Final_Project_Air_Quality_India.ipynb`.
    * `/presentation`: `Project_Presentation.pdf`.
3.  **Requirements:** Include a `requirements.txt` file so others can install your dependencies easily:
    ```bash
    pip install pandas numpy scikit-learn lightgbm statsmodels tensorflow pykrige folium geopandas missingno
    ```


