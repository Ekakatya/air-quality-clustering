import streamlit as st
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit import columns
import base64
import matplotlib.pyplot as plt
import seaborn as sns
from modules.model_logic import (data_preparation, engineer_feature, CausalPolicyModel,
                                 columns_selection, calculate_iptw_weights_rf,
                                 treatment_creation, run_causal_model, validate_policy_robust_with_raw,
                                 generate_path_dependent_report_final_v2)


@st.cache_resource
def get_cached_causal_model(df, features, cats, target_col):
    """
    Эта функция обучит модель один раз и сохранит её в оперативной памяти.
    При переключении кнопок Streamlit просто возьмет готовую модель.
    """
    # Вызываем твою основную функцию обучения
    recs, test_df, model = run_causal_model(df, features, cats, target=target_col)
    return recs, test_df, model


@st.cache_resource
def get_full_causal_analysis(df, target_col):
    """
    Универсальная функция: возвращает данные для карты, валидации,
    важности признаков и финального отчета.
    """
    # 1. Подготовка признаков и весов
    cols = columns_selection(df)
    df_t = treatment_creation(df)
    df_w = calculate_iptw_weights_rf(df_t, cols)

    # 2. Обучение (run_causal_model возвращает recs, test, model)
    cats = ['region', 'income']
    all_f = cols + cats
    recs, test, model = run_causal_model(df_w, all_f, cats, target=target_col)

    # 3. Формируем ПОЛНЫЕ рекомендации (для Tab 5 и точной валидации)
    # Мы соединяем идентификаторы из test и предсказания из recs
    full_recs = pd.concat([
        test[['CountryName', 'year', 'region', 'income']].reset_index(drop=True),
        recs.reset_index(drop=True)
    ], axis=1)

    # 4. Формируем LATEST (только последний год для метрик и карты в Tab 3/4)
    latest = full_recs.sort_values(['CountryName', 'year']).groupby('CountryName').tail(1).copy()

    # Чистим названия для красоты на карте
    strategy_map = {
        0: "Control", 1: "Tax", 2: "Subsidy", 3: "Mix",
        "Control (Do Nothing)": "Control",
        "Uplift_Tax": "Tax", "Uplift_Subsidy": "Subsidy", "Uplift_Mix": "Mix"
    }
    latest['Recommended_Policy'] = latest['Best_Strategy'].map(strategy_map).fillna(latest['Best_Strategy'])
    latest['Recommended_Policy'] = latest['Recommended_Policy'].astype(str).str.split(' ').str[0]

    # ВОЗВРАЩАЕМ 4 ОБЪЕКТА:
    # latest - для карты и метрик
    # test - тот самый исходный df_test для твоей функции валидации
    # model - для Feature Importance
    # full_recs - полные рекомендации для Tab 5
    return latest, test, model, full_recs


def get_base64_img(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# Укажи имя твоей последней картинки
img_name = "earth_background.jpg"


def get_base64_img(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# Твоя последняя картинка
img_name = "earth_background.jpg"

try:
    if os.path.exists(img_name):
        img_b64 = get_base64_img(img_name)

        st.markdown(f"""
        <style>
        /* 1. КОНТЕЙНЕР-ОСТРОВ (Увеличили высоту, чтобы влезли вкладки) */
        .hero-island {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                              url("data:image/jpg;base64,{img_b64}");
            background-size: cover;
            background-position: center;


            height: 280px; /* Увеличили с 330px, чтобы внизу было место для вкладок */
            border-radius: 30px;
            overflow: hidden;
            
            width: 96% !important;        /* Установи нужный % (например, 80%, 90% или 100%) */
            margin-left: auto !important; /* Эти две строки центрируют остров, */
            margin-right: auto !important;/* если ширина меньше 100% */

            display: flex;
            flex-direction: column;
            justify-content: flex-start; /* Текст начинаем сверху */
            padding: 60px 60px 0 60px;
            color: white;
            text-align: left;
            margin-bottom: 0px; 
        }}

        .hero-title {{
            font-size: 3.8rem;
            font-weight: 800;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}

        .hero-challenge {{
            font-size: 1.2rem !important;
            white-space: nowrap;
            margin-bottom: 10px;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        }}

        /* 2. МАГИЯ: ПЕРЕМЕЩАЕМ ВКЛАДКИ ВНУТРЬ ОСТРОВА */
        [data-testid="stTabs"] {{
            position: relative;
            top: -50px; /* Поднимаем вкладки на картинку */
            z-index: 10;
            padding: 0 60px; /* Выравниваем по левому краю с текстом */
            background: transparent !important;
        }}

        /* Делаем текст вкладок белым */
        .stTabs [data-baseweb="tab-list"] button p {{
            color: white !important;
            font-weight: 600 !important;
            font-size: 20px !important;
        }}

        /* Линия под активной вкладкой */
        .stTabs [data-baseweb="tab-highlight"] {{
            background-color: white !important;
        }}

        /* Убираем серую разделительную линию */
        .stTabs [data-baseweb="tab-list"] {{
            border-bottom: 1px solid rgba(255,255,255,0.3) !important;
        }}

        /* Исправляем цвет контента вкладок (чтобы он был на белом фоне ниже) */
        [data-testid="stTabPanel"] {{
            background-color: white;
            margin-top: -100px; /* Компенсируем подъем вкладок */
            padding-top: 20px;
        }}
        </style>

        <div class="hero-island">
            <h1 class="hero-title">Smart Energy Policy ⚡</h1>
            <p class="hero-challenge">
                Using Uplift Modeling to optimize energy policy impacts on human development.
            </p>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error(f"Image {img_name} not found.")

except Exception as e:
    st.error(f"Error: {e}")

st.set_page_config(page_title="Smart Energy Policy", layout="wide")

# --- DATA LOADING ---
path_main = os.path.join('data', 'df_final_updated.xlsx')
path_pink = os.path.join('data', 'pink_sheet.xlsx')

try:
    df_final_updated = pd.read_excel(path_main)

    try:
        energy_price = pd.read_excel(path_pink, sheet_name='Annual Prices (Real)', header=0)
    except:
        energy_price = pd.read_csv(path_pink)

    # --- DATA PREPROCESSING ---
    processed_data = data_preparation(df_final_updated, energy_price)



    # --- ИНТЕРФЕЙС STREAMLIT (ВКЛАДКИ) ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["About", "How it works?", "Uplift Model HDI", "Mitigation Model EVI", "Final Model"])

    with tab1:
        col_desc_1, col_desc_2 = st.columns([2, 2], gap="large")

        with col_desc_1:
            st.markdown("""
                #### 🗺️ Interactive Policy Brief Structure
                This platform is organized as a step-by-step analytical journey to ensure transparency of the decision-making process:
                
                1.  **Exploratory Data Analysis (Current Page):** Understanding the socio-economic and energy landscape of 70 developing nations.
                2.  **Methodological Framework:** Deep dive into Causal AI, stabilized IPTW weights, and the double-optimization logic.
                3.  **Model Insights:** Performance analysis of the HDI-maximization and EVI-minimization engines.
                4.  **Policy Recommendation Engine:** The final synthesis tool that provides data-driven fiscal strategies for specific country profiles.
            """)
            st.markdown(f"""
                    #### 🎯 Mission: Strategic Policy Alignment
                    This **Decision Support System (DSS)** is designed to navigate the complex trade-off between **Human Development (HDI)** and **Energy Vulnerability (EVI)**. 

                    Using Causal AI, we identify the optimal fiscal strategy for a specific country based on its unique **socio-economic, political, institutional, and energy profile**. The model evaluates four strategic paths to determine which intervention—**Taxation, Subsidies, a Mixed approach, or Non-intervention**—will most effectively foster development without compromising energy security.

                    #### ⚖️ The Core Challenge: Resilience in Crisis
                    In an era of recurring global crises and heightened geopolitical tension, energy vulnerability is rapidly increasing, directly threatening human well-being and long-term development. 

                    The challenge lies in breaking the negative feedback loop where energy instability erodes HDI. Our model serves as a precision tool: it analyzes a country's characteristics to select a policy that **stabilizes energy vulnerability** while **maximizing human development gains**, ensuring that fiscal choices are both socially progressive and energy-secure.

                    #### 🛠 Technical Stack
                    * **Causal AI Engine:** T-Learner for Conditional Average Treatment Effect (CATE) estimation.
                    * **Bias Correction:** Inverse Probability Treatment Weighting (IPTW) via Random Forest to ensure balanced comparison.
                    * **Core Estimator:** CatBoost Regressor, optimized for complex non-linear relationships in panel data.

                    #### 🌍 Scope & Impact
                    * **Temporal Coverage:** Longitudinal analysis from **2000 to 2022**.
                    * **Geographic Reach:** Focused on **70 developing economies** across Latin America, Sub-Saharan Africa, South and East Asia, and Eastern Europe.
                    * **Human Impact:** The model provides policy insights affecting the welfare of approximately **5.2 billion people*** living in these regions.

                """, unsafe_allow_html=True)


        with col_desc_2:
            st.write("### Initial data for modeling")
            st.dataframe(processed_data,
                         height=650,  # Увеличили высоту, чтобы она совпадала с текстом миссии
                         use_container_width=True,
                         hide_index=True
                         )
            st.info(f"There are {processed_data.shape[0]} observation in the dataset.")

        st.divider()
        st.subheader("Global Landscape: The Conflict & The Status Quo")

        # Создаем две колонки с большим отступом
        col_left, col_right = st.columns(2, gap="large")

        with col_left:
            st.markdown("#### ⚖️ The Development-Vulnerability Nexus")
            st.write("""
            This visualization illustrates the critical nexus between energy vulnerability (EVI) and human development (HDI) 
            for each developing country included in the research. By mapping these dimensions, we observe a clear structural paradox: 
            lower levels of social well-being are consistently coupled with higher sensitivity to energy shocks.
            """)

            # 1. Твой Scatter Plot (с небольшими правками под Streamlit)
            # Фильтруем данные за последний год для наглядности (как в твоем отчете)
            df_chart = processed_data[processed_data['year'] == processed_data['year'].max()].copy()

            # Создаем метки только для ключевых стран, чтобы не перегружать график
            important_countries = ['Niger', 'Ethiopia', 'Angola', 'Argentina', 'Chile', 'Colombia', 'India', 'China', 'Mongolia']
            df_chart['Label_Text'] = df_chart.apply(
                lambda x: x['CountryName'] if x['CountryName'] in important_countries else "", axis=1
            )

            fig_nexus = px.scatter(
                df_chart,
                x="hdi",
                y="EVI",
                color="region",
                size="EVI",
                text="Label_Text",
                hover_name="CountryName",
                labels={"hdi": "Human Development Index", "EVI": "Energy Vulnerability Index"},
                template="plotly_white",
                color_discrete_sequence=px.colors.qualitative.Safe
            )

            fig_nexus.update_traces(
                textposition='top center',
                textfont=dict(size=10, color='#333333'),
                marker=dict(opacity=0.7, line=dict(width=0.5, color='DarkSlateGrey'))
            )

            fig_nexus.update_layout(
                legend_title_text='',
                legend=dict(
                    orientation="h",
                    yanchor="top",  # Привязка к верху легенды
                    y=-0.15,  # Дистанция от оси (отрегулируй, если будет накладываться)
                    xanchor="center",
                    x=0.5,

                    # ГЛАВНОЕ ИЗМЕНЕНИЕ ТУТ:
                    entrywidthmode="fraction",
                    entrywidth=0.3,  # Даем чуть меньше 33%, чтобы был запас на промежутки

                    font=dict(size=12),  # Твой шрифт остается прежним
                    valign="middle"
                ),

                # Увеличиваем нижний отступ, чтобы легенда не обрезалась снизу
                margin=dict(l=10, r=10, t=50, b=160),
                height=650
            )

            # Добавляем линии средних значений для сегментации
            hdi_mean = df_chart['hdi'].mean()
            evi_mean = df_chart['EVI'].mean()
            fig_nexus.add_vline(x=hdi_mean, line_width=1, line_dash="dash", line_color="grey")
            fig_nexus.add_hline(y=evi_mean, line_width=1, line_dash="dash", line_color="grey")

            # Аннотации зон (Sustainable Leaders vs High Risk)
            fig_nexus.add_annotation(x=0.9, y=0.1, text="<b>Sustainable Leaders</b>", showarrow=False,
                                     font=dict(color="green", size=12), opacity=0.7)
            fig_nexus.add_annotation(x=0.4, y=0.8, text="<b>High Risk Zone</b>", showarrow=False,
                                     font=dict(color="red", size=12), opacity=0.7)

            fig_nexus.update_layout(height=500, margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_nexus, use_container_width=True)

            st.write("""
            **Key Findings**
            * **The Progress Paradox:** There is a distinct negative correlation where countries strive to move from the top-left "High Risk Zone" toward the bottom-right "Sustainable Leaders" quadrant.
            * **Regional Vulnerability:** Nations in Sub-Saharan Africa are predominantly situated in the High Risk Zone. These countries face a double burden of low HDI and extreme energy insecurity, making them the most critical candidates for optimized fiscal policy interventions.
            * **The Trade-off:** The data confirms that economic growth alone does not guarantee safety; without a "Smart Energy Policy," progress can be hindered by rising energy risks.
            """

            )

        with col_right:
            st.markdown("#### 🗺️ Global Policy Landscape")
            st.write("""
            This map illustrates the distribution of fossil fuel fiscal instruments across the 70 developing nations included 
            in this research. Each country is categorized by its specific energy policy regime: Fossil Fuel Tax, Energy Subsidies, 
            a Mix of both instruments, or None (Control), where no significant fiscal regulation is implemented.
            """)

            # 1. Подготовка данных
            df_map = processed_data[processed_data['year'] == processed_data['year'].max()].copy()

            # Считаем количество стран для каждой политики
            counts = df_map['Treatment'].value_counts()

            # Маппинг цветов и названий с динамическим подсчетом
            policy_info = {
                0: {"name": "None (Control)", "color": "#95A5A6"},
                1: {"name": "Tax", "color": "#E67E22"},
                2: {"name": "Subsidy", "color": "#2980B9"},
                3: {"name": "Mix", "color": "#8E44AD"}
            }

            df_map = processed_data[processed_data['year'] == processed_data['year'].max()].copy()

            # Считаем количество стран для каждой политики
            counts = df_map['Treatment'].value_counts()

            policy_info = {
                0: {"name": "None (Control)", "color": "#95A5A6"},
                1: {"name": "Tax", "color": "#E67E22"},
                2: {"name": "Subsidy", "color": "#2980B9"},
                3: {"name": "Mix", "color": "#8E44AD"}
            }

            fig_static = go.Figure()

            # 2. Добавляем слои ПО ОДНОМУ для каждого режима
            for val, info in policy_info.items():
                temp_df = df_map[df_map['Treatment'] == val]
                count = counts.get(val, 0)

                fig_static.add_trace(go.Choropleth(
                    locations=temp_df['CountryCode'],
                    z=[1] * len(temp_df),  # Фиктивное значение для закраски
                    colorscale=[[0, info['color']], [1, info['color']]],  # Однотонная заливка
                    showscale=False,  # Убираем вертикальную шкалу

                    # --- ВОТ ЭТО ВЕРНЕТ ЛЕГЕНДУ ---
                    name=f"{info['name']} ({count})",
                    showlegend=True,

                    marker_line_color='white',
                    marker_line_width=0.5,
                    hovertemplate="<b>%{text}</b><br>Policy: " + info['name'] + "<extra></extra>",
                    text=temp_df['CountryName']
                ))

            # 3. Настройка Layout
            fig_static.update_layout(
                height=500,
                template='plotly_white',

                # 2. Уменьшаем нижний отступ (было 150, ставим 50-80)
                margin={"r": 10, "t": 30, "l": 10, "b": 50},

                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    # 3. Немного корректируем положение легенды под картой
                    y=-0.02,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12),
                    bgcolor='rgba(0,0,0,0)'
                ),

                geo=dict(
                    showframe=False,
                    showcoastlines=True,
                    coastlinecolor="Grey",
                    projection_type='natural earth',
                    bgcolor='rgba(0,0,0,0)',
                    showland=True,
                    landcolor="#f4f4f4",
                    showocean=True,
                    oceancolor="White"
                )
            )

            st.plotly_chart(fig_static, use_container_width=True)

            st.write(
                """
                **Key Insights:**
                * **The "Control" Gap in Africa:** The highest concentration of countries without any fiscal instruments (None) is found in Sub-Saharan Africa. This lack of regulation directly correlates with the region's extreme energy vulnerability and the lowest levels of Human Development (HDI) observed in the dataset.
                * **Resource-Rich Subsidizers:** The Subsidy regime (Blue) is predominantly adopted by countries abundant in energy resources. In these economies, subsidies are often used as a tool for social protection or industrial support, though they frequently lead to higher energy intensity.
                * **Institutional Strength & Taxation:** Countries implementing a Fossil Fuel Tax (Orange) typically demonstrate stronger institutional frameworks and better governance. These nations use carbon-related pricing not only for revenue but as a lever to manage energy transition and fiscal stability.
                * **The Hybrid Approach:** Countries in the Mix group (Purple) attempt to balance the trade-off by taxing certain fuels while subsidizing others, representing a complex transitional state in energy policy.
                """
            )
        # 1. Подготовка данных для анимации
        # Нам нужно убедиться, что для каждого года есть данные
        years = sorted(processed_data['year'].unique())

        # Создаем базовую фигуру
        st.divider()

        col_map, col_text = st.columns([1.5, 1], gap="medium")
        with col_map:
            st.header("🌍 Global Evolution (2000-2022)")
            st.markdown("""
                        This interactive map tracks the long-term relationship between growth and vulnerability. 
                        **Background colors** represent the Human Development Index (HDI), while **bubble sizes** reflect Energy Vulnerability (EVI). 

                        *Press **Play** to see how emerging economies have navigated these trade-offs over three decades.*
                        """)
            fig = go.Figure()

            def create_traces(data_frame, year):
                year_df = data_frame[data_frame['year'] == year]

                # Слой Choropleth (HDI)
                trace_hdi = go.Choropleth(
                    locations=year_df['CountryCode'],
                    z=year_df['hdi'],
                    text=year_df['CountryName'],
                    customdata=year_df['EVI'],
                    colorscale='Viridis',
                    marker_line_color='white',
                    marker_line_width=0.5,
                    hovertemplate="<b>%{text}</b><br>HDI: %{z:.3f}<br>EVI: %{customdata:.3f}<extra></extra>",
                    colorbar=dict(
                        # Иправлено на 'top'
                        title={'text': ""},
                        orientation='v',
                        x=-0.08,  # Смещение влево
                        xanchor='right',
                        y=0.75,  # Верхняя шкала
                        len=0.35,  # Немного уменьшил длину для компактности
                        thickness=15
                    ),
                    name='HDI'
                )

                # Слой Scattergeo (EVI пузырьки)
                trace_evi = go.Scattergeo(
                    locations=year_df['CountryCode'],
                    text=year_df['CountryName'],
                    customdata=year_df['hdi'],
                    marker=dict(
                        size=year_df['EVI'] * 400,
                        color=year_df['EVI'],
                        colorscale='Plasma',
                        line_color='rgba(0,0,0,0.3)',
                        line_width=1,
                        sizemode='area',
                        colorbar=dict(
                            # Исправлено на 'top'
                            title={'text': ""},
                            orientation='v',
                            x=-0.08,
                            xanchor='right',
                            y=0.25,  # Нижняя шкала
                            len=0.35,
                            thickness=15
                        )
                    ),
                    hovertemplate="<b>%{text}</b><br>EVI: %{marker.color:.3f}<br>HDI: %{customdata:.3f}<extra></extra>",
                    name='EVI'
                )
                return trace_hdi, trace_evi


            # 2. Добавляем начальные слои (для самого первого года)
            start_year = years[0]
            trace_hdi_start, trace_evi_start = create_traces(processed_data, start_year)
            fig.add_trace(trace_hdi_start)
            fig.add_trace(trace_evi_start)

            # 3. Создаем кадры (Frames) для анимации по годам
            frames = []
            for year in years:
                trace_hdi, trace_evi = create_traces(processed_data, year)
                frames.append(go.Frame(data=[trace_hdi, trace_evi], name=str(year)))

            fig.frames = frames

            # 4. Настройка кнопок управления анимацией (Play/Pause)
            updatemenus = [dict(
                type="buttons",
                buttons=[
                    dict(label="Play",
                         method="animate",
                         args=[None, {"frame": {"duration": 500, "redraw": True},
                                      "fromcurrent": True, "transition": {"duration": 300}}]),
                    dict(label="Pause",
                         method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": True},
                                        "mode": "immediate", "transition": {"duration": 0}}])
                ],
                direction="left",
                pad={"r": 10, "t": 10},
                showactive=False,
                x=0.1,
                xanchor="right",
                y=0,
                yanchor="top"
            )]

            # 5. Настройка слайдера времени
            sliders = [dict(
                active=0,
                currentvalue={"prefix": "Year: ", "font": {"size": 18}, "visible": True, "xanchor": "right"},
                pad={"t": 50, "b": 10},
                len=0.7,  # Укоротили слайдер (70% от ширины)
                x=0.15,  # Немного сдвинули вправо для центровки
                y=0,
                steps=[dict(label=str(year), method="animate", args=[[str(year)],
                                                                     {"frame": {"duration": 300, "redraw": True},
                                                                      "mode": "immediate",
                                                                      "transition": {"duration": 100}}]) for year in
                       years]
            )]

            # 6. Финальная настройка Layout
            fig.update_layout(

                updatemenus=updatemenus,
                sliders=sliders,

                height=850,
                geo=dict(
                    showframe=False,
                    showcoastlines=True,
                    coastlinecolor="#d1d1d1",
                    projection_type='natural earth',
                    bgcolor='rgba(0,0,0,0)',
                    showland=True,
                    landcolor="#f4f4f4",
                    showocean=True,
                    oceancolor="#e0f3ff"
                ),
                template='plotly_white',
                # Уменьшили нижний отступ, так как шкалы ушли направо
                margin={"r": 20, "t": 80, "l": 100, "b": 80},
                annotations=[
                    # Подпись для HDI
                    dict(
                        text="Human Development Index",
                        textangle=-90,
                        x=-0.15,  # Смещение влево от шкалы (подбери под свой экран)
                        y=0.75,  # ИДЕАЛЬНЫЙ ЦЕНТР ВЕРХНЕЙ ШКАЛЫ
                        yanchor="middle",  # Выравнивание по центру текста
                        xref="paper", yref="paper",
                        showarrow=False,
                        font=dict(size=13, color="#4F4F4F")
                    ),
                    # Подпись для EVI
                    dict(
                        text="Energy Vulnerability",
                        textangle=-90,
                        x=-0.15,  # Смещение влево
                        y=0.25,  # ИДЕАЛЬНЫЙ ЦЕНТР НИЖНЕЙ ШКАЛЫ
                        yanchor="middle",  # Выравнивание по центру текста
                        xref="paper", yref="paper",
                        showarrow=False,
                        font=dict(size=13, color="#4F4F4F")
                    )
                ]
            )

            st.plotly_chart(fig, use_container_width=True)

        with col_text:
            st.markdown("### 📊 Data Description")

            # Сжатый HTML-код без лишних переносов, которые путают Streamlit
            full_html_table = """<style>.custom-table {font-size: 13px; width: 100%; border-collapse: collapse; font-family: sans-serif; color: #31333F;} .custom-table th, .custom-table td {border: 1px solid #e6e9ef; padding: 8px; vertical-align: middle;} .group-header {background-color: #f0f2f6; text-align: center !important; font-weight: bold; text-transform: uppercase;} .subgroup-header {background-color: #ffffff; text-align: center !important; font-style: italic; font-weight: bold;}</style><table class="custom-table"><thead><tr><th style="width: 25%;">Variable</th><th style="width: 55%;">Description</th><th style="width: 20%;">Units</th></tr></thead><tbody><tr><td colspan="3" class="group-header">Dependent Variables</td></tr><tr><td>Energy policy choice</td><td>A categorical variable combining four statuses: 0. None, 1. Tax, 2. Subsidy, 3. Mix.</td><td>Class (0, 1, 2, 3)</td></tr><tr><td colspan="3" class="group-header">Independent Variables</td></tr><tr><td colspan="3" class="subgroup-header">Social Features</td></tr><tr><td>Urbanisation</td><td>Share of population living in urban areas.</td><td>%</td></tr><tr><td>Internet Use</td><td>Population who used the Internet in the last 3 months.</td><td>%</td></tr><tr><td>Water Access</td><td>Share of population with no access to clean water.</td><td>%</td></tr><tr><td colspan="3" class="subgroup-header">Economic Features</td></tr><tr><td>Unemployment Rate</td><td>—</td><td>% of labor force</td></tr><tr><td>GNIPC</td><td>Logarithmic transformation of GNI (PPP).</td><td>2015 PPP $</td></tr><tr><td>Trade openness</td><td>Sum of export and import divided by GDP.</td><td>%</td></tr><tr><td>Gross National Savings</td><td>GNI and net transfers excluding consumption.</td><td>% of GDP</td></tr><tr><td>Private Sector Credit</td><td>Financial resources provided to the private sector.</td><td>% of GDP</td></tr><tr><td>Inflation</td><td>Consumer price index (Annual %).</td><td>Annual %</td></tr><tr><td>Industry Value Added</td><td>Net output of the industrial sector.</td><td>% of GDP</td></tr><tr><td colspan="3" class="subgroup-header">Fiscal Features</td></tr><tr><td>Gov. Exp. Health</td><td>Spending on social health insurance and systems.</td><td>% of GDP</td></tr><tr><td>Gov. Exp. Education</td><td>Current and capital expenditures on education.</td><td>% of GDP</td></tr><tr><td>Tax Revenue</td><td>Total income from production of goods and services.</td><td>% of GDP</td></tr><tr><td colspan="3" class="subgroup-header">Political & Institutional</td></tr><tr><td>Control of Corruption</td><td>Perception of public power used for private gain.</td><td>Index</td></tr><tr><td>Gov. Effectiveness</td><td>Quality of policy implementation and services.</td><td>Index</td></tr><tr><td>Rule of Law</td><td>Confidence in rules of society and courts.</td><td>Index</td></tr><tr><td colspan="3" class="subgroup-header">Energy Features</td></tr><tr><td>Access to electricity</td><td>—</td><td>% of population</td></tr><tr><td>Energy intensity</td><td>—</td><td>kWh/$</td></tr><tr><td>Oil / Gas Rents</td><td>Rents from nonrenewable resources.</td><td>% of GDP</td></tr><tr><td>Coal-Gas Ratio</td><td>Proxy for Merit Order effect.</td><td>Calculated</td></tr></tbody></table>"""

            scrollable_table = f"""
                <div style="height: 900px; overflow-y: auto; border: 1px solid #e6e9ef; border-radius: 5px;">
                    {full_html_table}
                </div>
                """

            st.markdown(scrollable_table, unsafe_allow_html=True)

    with tab2:

        col_pipe, col_info = st.columns([1, 1], gap="large")

        with col_pipe:
            st.markdown("### ⚙️ Research Pipeline")
            st.write("""
            To ensure the reliability of our causal estimates, the modeling process follows a rigorous 4-step pipeline:
            """)

            st.markdown("""
                1. **Feature Engineering & Time-Dynamics:** To capture the evolution of country profiles, we generate **Lagged variables** ($X_{t-1}$) and **3-year Trends** for all indicators. This ensures the model accounts for historical trajectories rather than static snapshots.

                2. **Multicollinearity Filtering:** High correlation between predictors can bias causal estimates. We perform pairwise correlation analysis and remove variables where $|r| > 0.95$, retaining only the most representative features to reduce model variance.

                3. **Propensity Scoring & IPTW (The Balancing Act):** In observational data, policy choices are not random. For instance, wealthy nations with strong institutions are naturally more likely to implement Carbon Taxes. To avoid "selection bias," we calculate **Inverse Probability Treatment Weights (IPTW)**.  
                   * **Why?** This "pseudo-randomizes" the sample by assigning higher weights to **non-typical cases** (e.g., a low-income country choosing a tax). This forces the model to learn from these unique scenarios, ensuring that the estimated effect is driven by the policy itself, not just the country's inherent wealth.

                4. **Dual-Model Causal Estimation:** We employ a **T-Learner** framework using **CatBoost Regressors** to estimate potential outcomes across four fiscal scenarios. Our final decision engine balances two distinct objectives:
                   * **Model A (HDI Maximization):** Predicts which policy yields the highest growth in human development.
                   * **Model B (EVI Minimization):** Identifies the strategy that best mitigates energy vulnerability.

                   **The Consensus Logic:** The system selects the final strategy that **maximizes HDI** while strictly ensuring that **Energy Vulnerability (EVI) does not increase**, creating a sustainable policy recommendation.
                """)


        with col_info:
            st.markdown("### 📋 Processed Feature Schema")
            st.write("Summary of the final dataset after engineering and cleaning:")

            data_with_features, dropped_count = engineer_feature(processed_data)

            info_df = pd.DataFrame({
                "Column": data_with_features.columns,
                "Type": data_with_features.dtypes.values,
                "Non-Null": data_with_features.notnull().sum().values
            })
            st.write("Structure of the dataset with new features:")
            st.dataframe(info_df, use_container_width=True)

            # 3. Расширенная информация об успехах
            new_features_total = len(data_with_features.columns) - len(processed_data.columns)

            # Красивый вывод с двумя показателями
            st.info(f"""
                        ✨ **Feature Engineering Summary:**
                        * Generated: **{new_features_total + dropped_count}** new lags & trends.
                        * Removed due to multicollinearity (threshold=0.95): **{dropped_count}** columns.
                    """)

        st.divider()
        st.subheader("Preview of Engineered Data")

        columns = columns_selection(data_with_features)

        data_with_features = treatment_creation(data_with_features)

        data_with_weights = calculate_iptw_weights_rf(data_with_features, columns)

        st.dataframe(data_with_weights)

        st.divider()

        # 2. Таблица структуры (как была)


        # 1. Создаем две колонки (соотношение 1:1)
        col_graph, col_empty = st.columns(2)

        # 2. Помещаем график в первую колонку
        with col_graph:
            # Уменьшаем figsize, так как теперь места меньше
            fig_box, ax_box = plt.subplots(figsize=(8, 5))

            sns.boxplot(
                data=data_with_weights,
                x='Treatment',
                y='IPTW_Weight',
                palette='Set2',
                ax=ax_box
            )

            ax_box.set_title('IPTW Distribution', fontsize=14)
            ax_box.set_xlabel('Treatment (0=Control, 1=Tax, 2=Subsidy, 3=Mix)', fontsize=10)
            ax_box.set_ylabel('IPTW Weight', fontsize=10)
            ax_box.grid(axis='y', linestyle='--', alpha=0.7)

            # Выводим график в колонку
            st.pyplot(fig_box)

        # 3. Во вторую колонку можно добавить описание (опционально)
        with col_empty:
            st.subheader("IPTW Distribution by Policy Instruments")
            st.write("""
                To neutralize **selection bias**, we use **Inverse Probability of Treatment Weighting (IPTW)**. In our observational data, countries aren't randomly assigned to policies; rich countries tend to tax, while resource-rich ones tend to subsidize. IPTW constructs a **balanced pseudo-population** where these historical correlations are broken.
                """)

            # Вставляем формулу стабилизированных весов
            st.latex(r"SW_i = \frac{P(T_i = t)}{P(T_i = t | X_i)}")

            st.markdown("""
                **How it transforms the Modeling:**

                * **Mathematically Reshaping Importance:** The formula assigns greater weight to **atypical observations**—countries that implemented a policy they were statistically unlikely to choose. 
                * **Modified Loss Function:** During the training of our CatBoost models, these weights are integrated directly into the **Loss Function**. Instead of treating every country equally, the algorithm incurs a **substantially higher mathematical penalty** for mispredicting outcomes of these high-weight "atypical" countries.
                * **Breaking Superficial Correlations:** This mechanism forces the model to move beyond simple historical coincidences (e.g., "taxes work only for the wealthy") and focus on the **underlying structural factors** that actually drive policy effectiveness.
                """)
            st.write("""
                As shown in the boxplots, every treatment group contains **atypical countries represented as outliers** above the whiskers. 

                In our Causal AI framework, these outliers are the most valuable data points. Because the model's error is weighted by the IPTW value, **the algorithm assigns special significance to these countries during training.** This approach ensures that the model "studies" the experiences of countries that made non-traditional choices more intensely. By amplifying their voice, we extract a causal effect that is robust and independent of a country's initial economic or institutional starting point.
                """)

    with tab3:
        st.subheader("Uplift Model & Policy Recommendations")

        # ВЫЗОВ ВСЕГО БЛОКА СРАЗУ
        try:
            recs_hdi, test_df, trained_model, full_recs_hdi = get_full_causal_analysis(data_with_features, "hdi")
            st.success("Analysis ready! ✨")

            # --- РЯД 1: МЕТРИКИ И ТАБЛИЦА ---
            col_metrics, col_table = st.columns([1, 2])

            with col_metrics:
                st.write("### Strategy Summary")
                counts = recs_hdi['Recommended_Policy'].value_counts()

                # ИСПРАВЛЕНО: ищем чистые имена (Tax, Subsidy...)
                m1, m2 = st.columns(2)
                m1.metric("Tax", f"{counts.get('Tax', 0)}")
                m1.metric("Subsidy", f"{counts.get('Subsidy', 0)}")
                m2.metric("Mix Strategy", f"{counts.get('Mix', 0)}")
                m2.metric("No Intervention", f"{counts.get('Control', 0)}")

                st.divider()
                st.metric("Avg. Predicted HDI Gain", f"+{recs_hdi['Max_Gain'].mean():.4f}")

            with col_table:
                st.write("### Policy Report (Latest Data)")
                st.dataframe(full_recs_hdi)


        except Exception as e:
            st.error(f"Error in HDI Tab: {e}")


        # Создаем две колонки: для графика и для пояснения
        st.divider()
        st.header("Model Validation & Strategic Comparison 📊")

        # Создаем две колонки для графиков (равные по ширине)
        col_viz_scatter, col_viz_validation = st.columns([1, 1])

        # --- КОЛОНКА 1: СРАВНЕНИЕ ЭФФЕКТОВ (ТВОЙ ПРЕДЫДУЩИЙ ГРАФИК) ---
        with col_viz_scatter:
            st.subheader("1. Effects Comparison: Tax vs Subsidy")

            # 1. ОЧИСТКА ДАННЫХ ПЕРЕД ГРАФИКОМ (Самое важное!)
            # Мы убираем 'Uplift_' и всё, что в скобках, чтобы остались только: Tax, Subsidy, Mix, Control
            plot_df = recs_hdi.copy()
            plot_df['Recommended_Policy'] = plot_df['Recommended_Policy'].astype(str).str.replace('Uplift_', '', regex=False)
            plot_df['Recommended_Policy'] = plot_df['Recommended_Policy'].str.split(' ').str[0]

            # 2. ПАЛИТРА (под чистые названия)
            custom_palette = {
                "Tax": "#D35400",
                "Subsidy": "#2980B9",
                "Control": "#BDC3C7",
                "Mix": "#8E44AD"
            }

            fig_scatter, ax_scatter = plt.subplots(figsize=(8, 6))

            sns.scatterplot(
                data=plot_df,
                x="Uplift_Tax",
                y="Uplift_Subsidy",
                hue="Recommended_Policy",
                palette=custom_palette,
                alpha=0.7,
                s=80,
                ax=ax_scatter
            )

            # Линия равенства (диагональ)
            all_vals = pd.concat([plot_df['Uplift_Tax'], plot_df['Uplift_Subsidy']])
            min_val, max_val = all_vals.min(), all_vals.max()
            ax_scatter.plot([min_val, max_val], [min_val, max_val], color='black', linestyle='--', alpha=0.5)

            ax_scatter.set_title("Predicted Gains Comparison", fontsize=12)
            ax_scatter.set_xlabel("HDI Gain from Tax", fontsize=10)
            ax_scatter.set_ylabel("HDI Gain from Subsidy", fontsize=10)
            ax_scatter.legend(title="Strategy", fontsize=9)
            ax_scatter.grid(True, linestyle=':', alpha=0.6)

            st.pyplot(fig_scatter)


        # --- КОЛОНКА 2: ВАЛИДАЦИЯ (ТВОЙ НОВЫЙ ГРАФИК MATCH VS MISMATCH) ---
        with col_viz_validation:
            st.subheader("2. Model Validation: Actual vs Predicted")
            try:
                val_results_hdi = validate_policy_robust_with_raw(test_df, full_recs_hdi, "hdi")
                fig_box, ax_box = plt.subplots(figsize=(8, 6))
                sns.boxplot(
                    data=val_results_hdi, x='Is_Match', y='Value_Added',
                    palette={"True": "#d1f2eb", "False": "#f9ebea"}, ax=ax_box
                )
                ax_box.set_title("HDI Delta Comparison: \nFollowed Recommendation (True) vs Violated (False)",
                                 fontsize=12)
                ax_box.set_ylabel("Value Added", fontsize=10)
                ax_box.set_xticklabels(['False (Mismatch)', 'True (Match)'], fontsize=10)
                ax_box.grid(axis='y', linestyle='--', alpha=0.7)
                st.pyplot(fig_box)
                st.success(
                    "**Validation Result:** Countries that followed recommendations show a higher average HDI improvement.")
            except Exception as e:
                st.error(f"Ошибка при валидации модели: {e}")
                st.info("Убедитесь, что в trained_model есть метод validate() и он возвращает нужные данные.")

        st.divider()
        st.header("Global Policy View & Decision Drivers 🌐")

        col_map, col_factors = st.columns([1, 1])

            # --- КОЛОНКА 1: КАРТА (ПЕРЕНЕСЛИ СЮДА) ---
        with col_map:
            st.write("### Policy Recommendations Map (Latest Year)")
            nice_palette_map = {
                    "Tax": "#D35400",  # Терракотовый
                    "Subsidy": "#2980B9",  # Спокойный синий
                    "Control": "#BDC3C7",  # Серый
                    "Mix": "#8E44AD"  # Фиолетовый
                }

            fig_map = px.choropleth(
                    recs_hdi,
                    locations="CountryName",
                    locationmode="country names",
                    color="Recommended_Policy",
                    # Данные при наведении
                    hover_name="CountryName",
                    labels={
                        "Recommended_Policy": "Recommended Policy",
                        "Max_Gain": "Expected HDI Gain",
                        "Uplift_Tax": "Tax Effect",
                        "Uplift_Subsidy": "Subsidy Effect"
                    },
                    hover_data={
                        "Recommended_Policy": True,
                        "Max_Gain": ":.4f",
                        "Uplift_Tax": ":.4f",
                        "Uplift_Subsidy": ":.4f"
                    },
                    color_discrete_map=nice_palette_map,
                    projection="natural earth",
                    template="plotly_white"
                )

                # Настройка оформления легенды и Geo
            fig_map.update_layout(
                    height=800,
                    legend=dict(title="Energy Policy Instrument:", orientation="h", yanchor="bottom", y=-0.15,
                                xanchor="center", x=0.5, font=dict(size=12)),
                    margin={"r": 0, "t": 10, "l": 0, "b": 80},
                    geo=dict(showframe=False, showcoastlines=True, coastlinecolor="white", showland=True,
                             landcolor="#f0f0f0", bgcolor='rgba(0,0,0,0)')
                )

            st.plotly_chart(fig_map, use_container_width=True)
            st.caption(
                    "Grey areas indicate countries with insufficient data or where the model suggests no specific fiscal intervention.")

            # --- КОЛОНКА 2: ЗНАЧИМОСТЬ ПРИЗНАКОВ (НОВОЕ!) ---
        with col_factors:
            st.write("### Key Factors by Policy Type")

            # 1. Словарь для выбора (названия : ID группы)
            policy_options = {
                "Carbon/Energy Tax": 1,
                "Energy Subsidies": 2,
                "Mix Strategy (Tax + Sub)": 3,
                "Control (Baseline/Status Quo)": 0
            }

            # 2. Выпадающий список для выбора модели
            selected_policy_name = st.selectbox(
                "Select policy to see its drivers:",
                options=list(policy_options.keys()),
                key="hdi_policy_select"  # <-- УНИКАЛЬНЫЙ КЛЮЧ
            )

            selected_group_id = policy_options[selected_policy_name]

            try:
                # 3. Вызываем метод, передавая ID выбранной группы
                # (Убедитесь, что в model_logic.py метод принимает аргумент group)
                feat_imp = trained_model.get_feature_importance(group=selected_group_id)

                if feat_imp is not None and not feat_imp.empty:
                    # 4. Рисуем график
                    fig_factors, ax_factors = plt.subplots(figsize=(7, 6.2))

                    sns.barplot(
                        data=feat_imp.head(15),
                        x='Importance',
                        y='Feature',
                        palette='viridis',
                        ax=ax_factors
                    )

                    ax_factors.set_title(f"Drivers for: {selected_policy_name}", fontsize=12)
                    ax_factors.set_xlabel("Feature Importance Score", fontsize=10)
                    ax_factors.set_ylabel("")
                    sns.despine(left=True, bottom=True)

                    st.pyplot(fig_factors)

                    st.caption(
                        f"This chart shows which variables the model uses to predict outcomes specifically for the **{selected_policy_name}** instrument.")
                else:
                    st.info(
                        f"No importance data for {selected_policy_name}. Model might not be trained for this group.")

            except Exception as e:
                st.warning(f"Could not visualize drivers for {selected_policy_name}.")
                with st.expander("Show Error Details"):
                    st.write(f"Error: {e}")

    with tab4:
        st.subheader("Mitigation Model EVI")

        try:
            recs_evi, test_df, trained_model, full_recs_evi = get_full_causal_analysis(data_with_features, "EVI")
            st.success("Analysis ready! ✨")

            # --- РЯД 1: МЕТРИКИ И ТАБЛИЦА ---
            col_metrics, col_table = st.columns([1, 2])

            with col_metrics:
                st.write("### Strategy Summary")
                counts = recs_evi['Recommended_Policy'].value_counts()

                # ИСПРАВЛЕНО: ищем чистые имена (Tax, Subsidy...)
                m1, m2 = st.columns(2)
                m1.metric("Tax Strategy", f"{counts.get('Tax', 0)}")
                m1.metric("Subsidy Strategy", f"{counts.get('Subsidy', 0)}")
                m2.metric("Mix Strategy", f"{counts.get('Mix', 0)}")
                m2.metric("No Intervention", f"{counts.get('Control', 0)}")

                st.divider()
                st.metric("Avg. Predicted EVI Reduction", f"{recs_evi['Max_Gain'].mean():.4f}")

            with col_table:
                st.write("### Policy Report (Latest Data)")
                st.dataframe(full_recs_evi)

        except Exception as e:
            st.error(f"Error in HDI Tab: {e}")

            # Создаем две колонки: для графика и для пояснения
        st.divider()
        st.header("Model Validation & Strategic Comparison 📊")

        # Создаем две колонки для графиков (равные по ширине)
        col_viz_scatter, col_viz_validation = st.columns([1, 1])

        # --- КОЛОНКА 1: СРАВНЕНИЕ ЭФФЕКТОВ (ТВОЙ ПРЕДЫДУЩИЙ ГРАФИК) ---
        with col_viz_scatter:
            st.subheader("1. Effects Comparison: Tax vs Subsidy")

            # 1. ОЧИСТКА ДАННЫХ ПЕРЕД ГРАФИКОМ (Самое важное!)
            # Мы убираем 'Uplift_' и всё, что в скобках, чтобы остались только: Tax, Subsidy, Mix, Control
            plot_df = recs_evi.copy()
            plot_df['Recommended_Policy'] = plot_df['Recommended_Policy'].astype(str).str.replace('Uplift_', '', regex=False)
            plot_df['Recommended_Policy'] = plot_df['Recommended_Policy'].str.split(' ').str[0]

            # 2. ПАЛИТРА (под чистые названия)
            custom_palette = {
                "Tax": "#D35400",
                "Subsidy": "#2980B9",
                "Control": "#BDC3C7",
                "Mix": "#8E44AD"
            }

            fig_scatter, ax_scatter = plt.subplots(figsize=(8, 6))

            sns.scatterplot(
                data=plot_df,
                x="Uplift_Tax",
                y="Uplift_Subsidy",
                hue="Recommended_Policy",
                palette=custom_palette,
                alpha=0.7,
                s=80,
                ax=ax_scatter
            )

            # Линия равенства (диагональ)
            all_vals = pd.concat([plot_df['Uplift_Tax'], plot_df['Uplift_Subsidy']])
            min_val, max_val = all_vals.min(), all_vals.max()
            ax_scatter.plot([min_val, max_val], [min_val, max_val], color='black', linestyle='--', alpha=0.5)

            ax_scatter.set_title("Expected EVI Reduction", fontsize=12)
            ax_scatter.set_xlabel("HDI Gain from Tax", fontsize=10)
            ax_scatter.set_ylabel("HDI Gain from Subsidy", fontsize=10)
            ax_scatter.legend(title="Strategy", fontsize=9)
            ax_scatter.grid(True, linestyle=':', alpha=0.6)

            st.pyplot(fig_scatter)

        # --- КОЛОНКА 2: ВАЛИДАЦИЯ (ТВОЙ НОВЫЙ ГРАФИК MATCH VS MISMATCH) ---
        with col_viz_validation:
            st.subheader("2. Model Validation: Actual vs Predicted")
            try:
                val_results_evi = validate_policy_robust_with_raw(test_df, full_recs_evi, "EVI")
                fig_box, ax_box = plt.subplots(figsize=(8, 6))
                sns.boxplot(
                    data=val_results_evi, x='Is_Match', y='Value_Added',
                    palette={"True": "#d1f2eb", "False": "#f9ebea"}, ax=ax_box
                )
                ax_box.set_title("HDI Delta Comparison: \nFollowed Recommendation (True) vs Violated (False)",
                                 fontsize=12)
                ax_box.set_ylabel("Value Added", fontsize=10)
                ax_box.set_xticklabels(['False (Mismatch)', 'True (Match)'], fontsize=10)
                ax_box.grid(axis='y', linestyle='--', alpha=0.7)
                st.pyplot(fig_box)
                st.success(
                    "**Validation Result:** Countries that followed recommendations show a higher average HDI improvement.")
            except Exception as e:
                st.error(f"Ошибка при валидации модели: {e}")
                st.info("Убедитесь, что в trained_model есть метод validate() и он возвращает нужные данные.")

        st.divider()
        st.header("Global Policy View & Decision Drivers 🌐")

        col_map, col_factors = st.columns([1, 1])

        # --- КОЛОНКА 1: КАРТА (ПЕРЕНЕСЛИ СЮДА) ---
        with col_map:
            st.write("### Policy Recommendations Map (Latest Year)")
            nice_palette_map = {
                "Tax": "#D35400",  # Терракотовый
                "Subsidy": "#2980B9",  # Спокойный синий
                "Control": "#BDC3C7",  # Серый
                "Mix": "#8E44AD"  # Фиолетовый
            }

            fig_map = px.choropleth(
                recs_evi,
                locations="CountryName",
                locationmode="country names",
                color="Recommended_Policy",
                # Данные при наведении
                hover_name="CountryName",
                labels={
                    "Recommended_Policy": "Recommended Policy",
                    "Max_Gain": "EVI Reduction",
                    "Uplift_Tax": "Tax Effect",
                    "Uplift_Subsidy": "Subsidy Effect"
                },
                hover_data={
                    "Recommended_Policy": True,
                    "Max_Gain": ":.4f",
                    "Uplift_Tax": ":.4f",
                    "Uplift_Subsidy": ":.4f"
                },
                color_discrete_map=nice_palette_map,
                projection="natural earth",
                template="plotly_white"
            )

            # Настройка оформления легенды и Geo
            fig_map.update_layout(
                height=800,
                legend=dict(title="Energy Policy Instrument:", orientation="h", yanchor="bottom", y=-0.15,
                            xanchor="center", x=0.5, font=dict(size=12)),
                margin={"r": 0, "t": 10, "l": 0, "b": 80},
                geo=dict(showframe=False, showcoastlines=True, coastlinecolor="white", showland=True,
                         landcolor="#f0f0f0", bgcolor='rgba(0,0,0,0)')
            )

            st.plotly_chart(fig_map, use_container_width=True)
            st.caption(
                "Grey areas indicate countries with insufficient data or where the model suggests no specific fiscal intervention.")

            # --- КОЛОНКА 2: ЗНАЧИМОСТЬ ПРИЗНАКОВ (НОВОЕ!) ---
        with col_factors:
            st.write("### Key Factors by Policy Type")

            # 1. Словарь для выбора (названия : ID группы)
            policy_options = {
                "Carbon/Energy Tax": 1,
                "Energy Subsidies": 2,
                "Mix Strategy (Tax + Sub)": 3,
                "Control (Baseline/Status Quo)": 0
            }

            # 2. Выпадающий список для выбора модели
            selected_policy_name = st.selectbox(
                "Select policy to see its drivers:",
                options=list(policy_options.keys())
            )
            selected_group_id = policy_options[selected_policy_name]

            try:
                # 3. Вызываем метод, передавая ID выбранной группы
                # (Убедитесь, что в model_logic.py метод принимает аргумент group)
                feat_imp = trained_model.get_feature_importance(group=selected_group_id)

                if feat_imp is not None and not feat_imp.empty:
                    # 4. Рисуем график
                    fig_factors, ax_factors = plt.subplots(figsize=(7, 6.2))

                    sns.barplot(
                        data=feat_imp.head(15),
                        x='Importance',
                        y='Feature',
                        palette='viridis',
                        ax=ax_factors
                    )

                    ax_factors.set_title(f"Drivers for: {selected_policy_name}", fontsize=12)
                    ax_factors.set_xlabel("Feature Importance Score", fontsize=10)
                    ax_factors.set_ylabel("")
                    sns.despine(left=True, bottom=True)

                    st.pyplot(fig_factors)

                    st.caption(
                        f"This chart shows which variables the model uses to predict outcomes specifically for the **{selected_policy_name}** instrument.")
                else:
                    st.info(
                        f"No importance data for {selected_policy_name}. Model might not be trained for this group.")

            except Exception as e:
                st.warning(f"Could not visualize drivers for {selected_policy_name}.")
                with st.expander("Show Error Details"):
                    st.write(f"Error: {e}")

    with tab5:
        st.header("Final Balancing: Path-Dependent Policy Brief 🎯")
        st.write("""
            This final model identifies optimal reform paths. It suggests switching policies only if 
            the change improves human development (HDI) **without increasing** energy vulnerability (EVI).
        """)

        # 1. Загружаем полные данные из кэша (принимаем 4 объекта!)
        # Мы игнорируем первые три (latest, test, model), нам нужен только полный отчет (full_recs)
        _, _, _, full_hdi = get_full_causal_analysis(data_with_features, "hdi")
        _, _, _, full_evi = get_full_causal_analysis(data_with_features, "EVI")

        # 2. Фиксированный риск (теперь без слайдера)
        fixed_max_risk = 0.0

        # 3. Запуск балансирующей модели
        final_report = generate_path_dependent_report_final_v2(
            data_with_features, full_hdi, full_evi, max_evi_risk=fixed_max_risk
        )

        # Берем только последний год для визуализации
        latest_final = final_report.sort_values(['CountryName', 'year'])

        latest_final_viz = final_report.sort_values(['CountryName', 'year']).sort_values(by=["CountryName", "year"], ascending=[True, True]).groupby('CountryName').tail(1)

        # --- ВИЗУАЛИЗАЦИЯ МЕТРИК ---
        col_m1, col_m2, col_m3 = st.columns(3)
        switches = latest_final_viz[latest_final['Reason'].str.contains("SWITCH")].shape[0]

        col_m1.metric("Reform Switches", f"{switches} countries")
        col_m2.metric("Avg. Marginal HDI Gain", f"+{latest_final_viz['Marginal_HDI_Gain'].mean():.4f}")
        col_m3.metric("Avg. EVI Impact", f"{latest_final_viz['Final_Projected_EVI_Change'].mean():.4f}")

        st.divider()

        # --- КАРТА И ГРАФИК TRADE-OFF ---
        c1, c2 = st.columns([1, 1])

        with c1:
            st.write("### Recommended Policy Path")
            fig_final_map = px.choropleth(
                latest_final_viz, locations="CountryName", locationmode="country names",
                color="Final_Strategy",
                hover_data=['Baseline_2019', 'Marginal_HDI_Gain', 'Reason'],
                color_discrete_map={"Tax": "#D35400", "Subsidy": "#2980B9", "Control": "#BDC3C7", "Mix": "#8E44AD"},
                projection="natural earth", template="plotly_white"
            )
            fig_final_map.update_layout(height=550, margin={"r": 0, "t": 0, "l": 0, "b": 0})
            st.plotly_chart(fig_final_map, use_container_width=True)

        with c2:
            st.write("### Trade-off Analysis")
            # Показываем, где лежат страны относительно нулевого риска
            fig_tradeoff = px.scatter(
                latest_final_viz, x="Final_Projected_HDI_Gain", y="Final_Projected_EVI_Change",
                color="Final_Strategy",
                size=np.abs(latest_final_viz['Marginal_HDI_Gain']) + 0.05,
                hover_name="CountryName",
                labels={"Final_Projected_HDI_Gain": "HDI Gain", "Final_Projected_EVI_Change": "EVI Change (Risk)"},
                color_discrete_map={"Tax": "#D35400", "Subsidy": "#2980B9", "Control": "#BDC3C7", "Mix": "#8E44AD"}
            )
            # Линия "Zero Risk"
            fig_tradeoff.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Zero Risk Line")
            fig_tradeoff.update_layout(height=550)
            st.plotly_chart(fig_tradeoff, use_container_width=True)

        st.write("### Detailed Reform Path Report")
        st.dataframe(
            latest_final
            .sort_values(by=["CountryName", "year"], ascending=[True, True]),
            use_container_width=True, hide_index=True
        )

except FileNotFoundError as e:
    st.error(f"Не удалось найти файл: {e.filename}. Проверьте наличие папки 'data'.")
except Exception as e:
    st.error(f"Произошла ошибка при выполнении кода: {e}")