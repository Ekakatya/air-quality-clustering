import wbgapi as wb
import pandas as pd
import numpy as np
from catboost import CatBoostRegressor, Pool
import xgboost as xgb
from econml.metalearners import TLearner
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import RandomForestClassifier
from scipy import stats
import warnings
warnings.filterwarnings("ignore")



def data_preparation(df_final, energy_price):
    """
    Merging datasets and calculating regional energy prices based on geographical groups.
    """

    df = df_final.copy()

    # 1. Merging initial dataset with pink sheet with energy prices
    energy_cols = [
        'year', 'Crude oil, average', 'Crude oil, Brent', 'Crude oil, Dubai',
        'Crude oil, WTI', 'Coal, Australian', 'Coal, South African',
        'Natural gas, US', 'Natural gas, Europe',
        'Liquefied natural gas, Japan'
    ]
    df = df.merge(energy_price[energy_cols], on='year', how='left')

    # Calculating local price for Gas
    conditions_gas = [
        df['region'].isin(['Europe and Central Asia', 'Sub-Saharan Africa', 'Middle East and North Africa']),
        df['region'].isin(['Latin America and Caribbean']),
        df['region'].isin(['East Asia and Pacific', 'South Asia'])
    ]
    choices_gas = [
        df['Natural gas, Europe'],
        df['Natural gas, US'],
        df['Liquefied natural gas, Japan']
    ]
    df['Local_Gas_Price'] = np.select(conditions_gas, choices_gas, default=np.nan)

    # 3. Calculating local price for Crude oil
    conditions_oil = [
        df['region'].isin(['Europe and Central Asia', 'Sub-Saharan Africa']),
        df['region'].isin(['Latin America and Caribbean']),
        df['region'].isin(['East Asia and Pacific', 'South Asia', 'Middle East and North Africa'])
    ]
    choices_oil = [
        df['Crude oil, Brent'],
        df['Crude oil, WTI'],
        df['Crude oil, Dubai']
    ]
    df['Local_Oil_Price'] = np.select(conditions_oil, choices_oil, default=np.nan)

    # 4. Calculating local price for coal
    conditions_coal = [
        df['region'].isin(['Europe and Central Asia', 'Sub-Saharan Africa', 'Middle East and North Africa',
                           'Latin America and Caribbean']),
        df['region'].isin(['East Asia and Pacific', 'South Asia'])
    ]
    choices_coal = [
        df['Coal, South African'],
        df['Coal, Australian']
    ]
    df['Local_Coal_Price'] = np.select(conditions_coal, choices_coal, default=np.nan)

    # 5. Merit Order indication
    df['Coal_Gas_Ratio'] = df['Local_Coal_Price'] / df['Local_Gas_Price']

    # 6. Removing unnecessary columns
    cols_to_drop = energy_cols[1:]
    df.drop(columns=cols_to_drop, inplace=True, errors='ignore')

    # Changing datatype for newly created columns
    target_cols = ['Local_Gas_Price', 'Local_Oil_Price', 'Local_Coal_Price', 'Coal_Gas_Ratio']
    df[target_cols] = df[target_cols].apply(pd.to_numeric, errors='coerce')

    df['Treatment'] = df['TAX'] + (df['SUB'] * 2)

    return df


def engineer_feature(df, threshold=0.95):
    # Работаем с копией, чтобы не испортить исходные данные
    df = df.copy()
    df.columns = df.columns.str.strip()

    # 1. Список колонок для создания лагов (как в твоем исходном коде)
    cols_to_lag = [
        'hdi', 'Ih', 'Ie', 'Ig', 'EVI', 'AE', 'Eint', 'Eimp', 'RE', 'NE',
        'FFE', 'El', 'Fexp', 'Rel', 'Oil_Rents', 'Gas_Rents', 'Urbanization',
        'Internet_Usage', 'WA', 'Unemployment_Rate', 'GNI_per_capita', 'OE',
        'GNS', 'FD', 'Inflation', 'Tax_revenue', 'Industry_Value_Added',
        'GEH', 'GEE', 'Control_of_Corruption', 'Gov_Effectiveness',
        'Political_Stability', 'Rule_of_Law', 'Local_Gas_Price',
        'Local_Oil_Price', 'Local_Coal_Price', 'Coal_Gas_Ratio'
    ]

    # Создаем лаги и тренды
    existing_cols = [c for c in cols_to_lag if c in df.columns]
    for col in existing_cols:
        df[f'Lag1_{col}'] = df.groupby('CountryCode')[col].shift(1)
        df[f'Trend3yr_{col}'] = df.groupby('CountryCode')[col].transform(
            lambda x: x.shift(1).rolling(window=3).mean())
        # Добавляем Growth, если он был в твоей версии
        df[f'Growth_{col}'] = df.groupby('CountryCode')[col].transform(
            lambda x: x.pct_change().shift(1))

    # --- ШАГ ИЗ ЮПИТЕРА №1: Фильтрация колонок ПЕРЕД корреляцией ---
    cols_to_keep = [col for col in df.columns if col.startswith('Lag1') or col.startswith('Trend3yr')]

    # Собираем df_filtered точно как в Юпитере
    base_cols = ['CountryName', 'year', 'CountryCode', 'region', 'income', 'hdi', 'EVI']
    policy_cols = ['TAX', 'SUB', 'NON']

    # Проверяем наличие колонок (на случай разных версий файлов)
    valid_base = [c for c in base_cols if c in df.columns]
    valid_policy = [c for c in policy_cols if c in df.columns]

    df_filtered = df[valid_base + cols_to_keep + valid_policy]

    # --- ШАГ ИЗ ЮПИТЕРА №2: Поиск коллинеарности на отфильтрованном наборе ---
    df_num = df_filtered.select_dtypes(include=[np.number])

    # Считаем матрицу корреляций (удаляем NaN для точности)
    corr_matrix = df_num.dropna().corr().abs()

    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

    # Находим колонки на удаление
    to_drop = [column for column in upper.columns if any(upper[column] > threshold)]

    # Защищаем hdi, EVI и политики от случайного удаления
    protected = ['hdi', 'EVI', 'TAX', 'SUB', 'NON']
    to_drop = [c for c in to_drop if c not in protected]

    dropped_count = len(to_drop)

    # Итоговый результат
    df_final = df_filtered.drop(columns=to_drop)

    return df_final, dropped_count

def treatment_creation(df):
    df['Treatment'] = df['TAX'] + (df['SUB'] * 2)
    return df


class CausalPolicyModel:
    def __init__(self, feature_names, cat_features=None):
        """
        feature_names: Список колонок, которые модель будет использовать для обучения.
        cat_features: Список категориальных признаков (для CatBoost).
        """
        self.models = {}
        # 0: Control, 1: Tax, 2: Subsidy, 3: Mix
        self.treatments = [0, 1, 2, 3]

        self.feature_names = feature_names
        self.cat_features = cat_features if cat_features else []

    def prepare_data(self, df):
        """Создает колонку Treatment"""
        df = df.copy()

        def get_group(row):
            t, s = row.get('TAX', 0), row.get('SUB', 0)
            if t == 1 and s == 1: return 3  # Mix
            if t == 1: return 1  # Tax
            if s == 1: return 2  # Subsidy
            return 0  # Control

        if 'Treatment' not in df.columns:
            df['Treatment'] = df.apply(get_group, axis=1)

        return df

    def get_feature_importance(self, group=1):
        """
        group: 0=Control, 1=Tax, 2=Subsidy, 3=Mix
        """
        if group not in self.models or self.models[group] is None:
            # Если выбранная модель не обучена, берем первую доступную
            available = [k for k, v in self.models.items() if v is not None]
            if not available: raise ValueError("No trained models found.")
            group = available[0]

        target_model = self.models[group]
        importance = target_model.get_feature_importance()

        return pd.DataFrame({
            'Feature': self.feature_names,
            'Importance': importance
        }).sort_values(by='Importance', ascending=False)

    def fit(self, df_train, target_col='hdi', weight_col=None):
        """Обучает 4 взвешенные модели (T-Learner с IPTW)"""

        X = df_train[self.feature_names]
        y = df_train[target_col]
        t = df_train['Treatment']

        # Извлекаем веса. Если их нет, создаем массив из единиц (равный вес)
        if weight_col and weight_col in df_train.columns:
            weights = df_train[weight_col].values
            print(f"✅ Используются IPTW веса из колонки: {weight_col}")
        else:
            weights = np.ones(len(df_train))
            print("⚠️ Веса не переданы, используется обычное обучение (веса = 1)")

        for group in self.treatments:
            mask = (t == group)
            X_grp = X[mask]
            y_grp = y[mask]
            w_grp = weights[mask]  # <-- Фильтруем веса только для текущей группы!

            n_samples = len(X_grp)
            print(f"Группа {group}: {n_samples} наблюдений.")

            if n_samples < 10:
                print(f"⚠️ ПРОПУСК ГРУППЫ {group}: слишком мало данных.")
                self.models[group] = None
                continue

            # --- МАГИЯ IPTW: Создаем CatBoost Pool с весами ---
            train_pool = Pool(
                data=X_grp,
                label=y_grp,
                cat_features=self.cat_features,
                weight=w_grp  # Передаем веса модели
            )

            # Обучаем CatBoost
            model = CatBoostRegressor(
                iterations=500,
                depth=5,
                learning_rate=0.05,
                loss_function='RMSE',
                verbose=0,
                allow_writing_files=False,
                random_state=42
            )

            # Обучаем на пуле данных (в нем уже есть признаки, таргет и ВЕСА)
            model.fit(train_pool)
            self.models[group] = model

    def predict_uplift(self, df_test, direction='maximize'):
        """
        direction: 'maximize' (для HDI) или 'minimize' (для EVI)
        """
        X_new = df_test[self.feature_names]
        results = pd.DataFrame(index=X_new.index)

        # 1. Базовый прогноз (Control)
        if self.models.get(0) is None:
            print("Внимание: Модель Control не обучена.")
            base_pred = np.zeros(len(X_new))
        else:
            base_pred = self.models[0].predict(X_new)

        results['Pred_Control'] = base_pred

        # 2. Считаем Uplift
        uplift_cols = []
        names = {1: 'Uplift_Tax', 2: 'Uplift_Subsidy', 3: 'Uplift_Mix'}

        for grp in [1, 2, 3]:
            col_name = names[grp]
            if self.models.get(grp):
                pred = self.models[grp].predict(X_new)
                results[col_name] = pred - base_pred
                uplift_cols.append(col_name)
            else:
                results[col_name] = 0

        # 3. Рекомендация с учетом НАПРАВЛЕНИЯ
        if uplift_cols:
            if direction == 'maximize':
                results['Best_Strategy'] = results[uplift_cols].idxmax(axis=1)
                results['Max_Gain'] = results[uplift_cols].max(axis=1)
                mask_bad = results['Max_Gain'] <= 0
                results.loc[mask_bad, 'Best_Strategy'] = 'Control (Do Nothing)'

            elif direction == 'minimize':
                results['Best_Strategy'] = results[uplift_cols].idxmin(axis=1)
                results['Max_Gain'] = results[uplift_cols].min(axis=1)
                mask_bad = results['Max_Gain'] >= 0
                results.loc[mask_bad, 'Best_Strategy'] = 'Control (Do Nothing)'
        else:
            results['Best_Strategy'] = 'Control (Do Nothing)'
            results['Max_Gain'] = 0

        return results

def columns_selection(df):
    all_columns = df.columns.tolist()

    filtered_cols = [
        'Lag1_Eint', 'Lag1_Eimp', 'Lag1_RE', 'Lag1_NE', 'Lag1_FFE', 'Lag1_El',
        'Lag1_Fexp', 'Lag1_Rel', 'Lag1_Oil_Rents', 'Lag1_Gas_Rents',
        'Lag1_Urbanization', 'Lag1_Internet_Usage', 'Lag1_WA',
        'Lag1_Unemployment_Rate', 'Lag1_GNI_per_capita', 'Lag1_OE', 'Lag1_GNS',
        'Trend3yr_GNS', 'Lag1_FD', 'Trend3yr_FD', 'Lag1_Inflation',
        'Trend3yr_Inflation', 'Lag1_Tax_revenue', 'Lag1_Industry_Value_Added',
        'Lag1_GEH', 'Trend3yr_GEH', 'Lag1_GEE', 'Trend3yr_GEE',
        'Lag1_Control_of_Corruption', 'Lag1_Gov_Effectiveness',
        'Lag1_Political_Stability', 'Lag1_Rule_of_Law', 'Lag1_Local_Gas_Price',
        'Trend3yr_Local_Gas_Price', 'Lag1_Local_Oil_Price',
        'Trend3yr_Local_Oil_Price', 'Lag1_Local_Coal_Price',
        'Trend3yr_Local_Coal_Price', 'Lag1_Coal_Gas_Ratio', 'Trend3yr_Coal_Gas_Ratio'
    ]

    # 2. Оставляем только те, что начинаются на Lag или Trend,
    # НО НЕ содержат внутри Ih, Ie или Ig
    # filtered_cols = [
    #     col for col in all_columns
    #     if (col.startswith('Lag') or col.startswith('Trend'))  # Условие на приставку
    #        and not any(x in col for x in ['Ih', 'Ie', 'Ig', 'hdi', 'EVI'])  # Исключаем ненужные
    # ]
    return filtered_cols

def calculate_iptw_weights_rf(df, feature_cols, target_col='Treatment'):
    """
    Рассчитывает веса IPTW с использованием Random Forest для обхода нелинейностей.
    """
    X = df[feature_cols].copy()
    y = df[target_col].copy()

    # 1. Обучаем Случайный Лес
    # Параметры max_depth и min_samples_leaf критически важны для PSM,
    # чтобы деревья не переобучились и не выдавали уверенность 100%
    rf = RandomForestClassifier(
        n_estimators=500,
        max_depth=5,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1  # используем все ядра процессора для скорости
    )
    rf.fit(X, y)

    # Получаем вероятности (Propensity Scores)
    ps_matrix = rf.predict_proba(X)
    weights = np.zeros(len(y))
    classes = sorted(y.unique())

    print("=== Результаты IPTW (Random Forest) ===")

    for policy_code in classes:
        mask = (y == policy_code)

        # Числитель: базовая историческая вероятность
        p_marginal = mask.mean()

        # Знаменатель: предсказанная вероятность (с защитой от деления на 0)
        class_idx = list(rf.classes_).index(policy_code)
        p_conditional = np.clip(ps_matrix[mask, class_idx], 0.01, 0.99)

        # Расчет стабилизированного веса
        w = p_marginal / p_conditional

        # Тримминг (срезаем 1% самых экстремальных значений)
        w = np.clip(w, a_min=None, a_max=np.percentile(w, 99))
        weights[mask] = w

        print(f"Политика {policy_code}: Средний вес = {w.mean():.3f} | Макс = {w.max():.3f}")

    # Создаем копию датасета и добавляем колонку с весами
    df_weighted = df.copy()
    df_weighted['IPTW_Weight'] = weights

    return df_weighted


def run_full_pipeline(df_weighted: pd.DataFrame, features: list, cat_cols: list, target: str = 'hdi'):
    """
    Полный цикл: инициализация, подготовка, обучение и прогноз.
    """
    # 1. Инициализация модели
    model = CausalPolicyModel(feature_names=features, cat_features=cat_cols)

    # 2. Подготовка (добавление колонки Treatment)
    df_processed = model.prepare_data(df_weighted)

    # 3. Разбиение на Train/Test (Out-of-Time)
    train_cutoff = 2019
    train_df = df_processed[df_processed['year'] < train_cutoff]
    test_df = df_processed[df_processed['year'] >= train_cutoff]

    # 4. Обучение (используем веса IPTW, если они есть)
    weight_column = 'IPTW_Weight' if 'IPTW_Weight' in train_df.columns else None
    model.fit(train_df, target_col=target, weight_col=weight_column)

    # 5. Прогноз на тестовых данных
    results = model.predict_uplift(test_df)

    return results, test_df, model


def run_causal_model(df_weighted, features, cat_cols, target, train_cutoff=2019):
    """
    Функция для инициализации, обучения и прогноза CausalPolicyModel
    """
    # Инициализация
    model = CausalPolicyModel(feature_names=features, cat_features=cat_cols)

    # Подготовка данных
    df_processed = model.prepare_data(df_weighted)

    # Разбиение
    train_df = df_processed[df_processed['year'] < train_cutoff]
    test_df = df_processed[df_processed['year'] >= train_cutoff]

    # Обучение
    model.fit(train_df, target_col=target, weight_col='IPTW_Weight')

    # Прогноз
    if target == 'hdi':
        recommendations = model.predict_uplift(test_df)
    elif target == 'EVI':
        recommendations = model.predict_uplift(test_df, "minimize")

    # Можно также вернуть саму модель, если захочешь вытащить важность признаков
    return recommendations, test_df, model


def validate_policy_robust_with_raw(df_test, recommendations, target):
    # 1. Подготовка данных
    val_df = df_test[[target, 'Treatment', 'CountryName']].copy()
    val_df = val_df.join(recommendations[['Best_Strategy', 'Pred_Control']])

    strategy_map = {
        'Control (Do Nothing)': 0, 'Uplift_Tax': 1,
        'Uplift_Subsidy': 2, 'Uplift_Mix': 3
    }
    val_df['Rec_Code'] = val_df['Best_Strategy'].map(strategy_map)

    # 2. Определяем совпадение (Match)
    val_df['Is_Match'] = val_df['Treatment'] == val_df['Rec_Code']

    # 3. Считаем Value Added
    val_df['Value_Added'] = val_df[target] - val_df['Pred_Control']

    # Динамические названия для печати
    target_name = "HDI" if target == 'hdi' else "EVI"
    desc = "Развитие" if target == 'hdi' else "Уязвимость"

    # Рассчитываем средние значения
    raw_match = val_df[val_df['Is_Match']][target].mean()
    raw_mismatch = val_df[~val_df['Is_Match']][target].mean()

    score_match = val_df[val_df['Is_Match']]['Value_Added'].mean()
    score_mismatch = val_df[~val_df['Is_Match']]['Value_Added'].mean()

    print(f"=== РЕЗУЛЬТАТЫ ВАЛИДАЦИИ ({target_name}) ===")
    print(f"1. СЫРОЙ {target_name} ({desc}):")
    print(f"   - Страны, следовавшие совету: {raw_match:.4f}")
    print(f"   - Страны, нарушившие совет:   {raw_mismatch:.4f}")

    # Логика выигрыша
    diff = score_match - score_mismatch
    # Для EVI выигрыш — это когда разница отрицательная (снизили уязвимость больше)
    is_success = diff > 0 if target == 'hdi' else diff < 0
    result_text = "УСПЕХ" if is_success else "ВНИМАНИЕ: Проверьте модель"

    print(f"\n2. VALUE ADDED (Эффект относительно контроля):")
    print(f"   - У 'послушных':   {score_match:.5f}")
    print(f"   - У 'непослушных': {score_mismatch:.5f}")
    print(f"   --> Чистый эффект модели: {diff:.5f} ({result_text})")

    return val_df


def generate_path_dependent_report_final_v2(df_meta, recs_hdi, recs_evi, max_evi_risk=0.0):
    """
    Генерирует отчет реформ с учетом Base 2019 и баланса HDI/EVI.
    """
    # 1. Подготовка данных
    df_safe = df_meta.loc[df_meta['year'] >= 2019].copy()

    # Используем твою функцию из этого же файла
    if 'Treatment' not in df_safe.columns:
        df_safe = treatment_creation(df_safe)

    report = df_safe[['CountryName', 'year', 'region', 'Treatment']].copy().reset_index(drop=True)

    # 2. Сбор всех прогнозов (Uplifts)
    report['Tax_HDI'] = recs_hdi['Uplift_Tax']
    report['Tax_EVI'] = recs_evi['Uplift_Tax']
    report['Sub_HDI'] = recs_hdi['Uplift_Subsidy']
    report['Sub_EVI'] = recs_evi['Uplift_Subsidy']
    report['Mix_HDI'] = recs_hdi['Uplift_Mix']
    report['Mix_EVI'] = recs_evi['Uplift_Mix']
    report['Control_HDI'] = 0.0
    report['Control_EVI'] = 0.0

    # 3. Якорь 2019 (Baseline)
    df_2019 = df_safe[df_safe['year'] == 2019]
    baseline_map = df_2019.set_index('CountryName')['Treatment'].to_dict()

    # 4. Логика выбора
    final_strategies, marginal_gains, reasons = [], [], []
    final_abs_hdi, final_abs_evi = [], []

    code_to_name = {0: 'Control', 1: 'Tax', 2: 'Subsidy', 3: 'Mix'}

    for idx, row in report.iterrows():
        country = row['CountryName']
        base_code = baseline_map.get(country, 0)

        # Параметры текущего курса (Benchmark)
        mapping = {
            1: ('Uplift_Tax', row['Tax_HDI'], row['Tax_EVI']),
            2: ('Uplift_Subsidy', row['Sub_HDI'], row['Sub_EVI']),
            3: ('Uplift_Mix', row['Mix_HDI'], row['Mix_EVI']),
            0: ('Control (Do Nothing)', 0.0, 0.0)
        }
        current_policy_name, bench_hdi, bench_evi = mapping.get(base_code, ('Control (Do Nothing)', 0.0, 0.0))

        candidates = {
            'Tax': (row['Tax_HDI'], row['Tax_EVI']),
            'Subsidy': (row['Sub_HDI'], row['Sub_EVI']),
            'Mix': (row['Mix_HDI'], row['Mix_EVI']),
            'Control': (0.0, 0.0)
        }

        best_strat = current_policy_name.replace('Uplift_', '')
        best_marginal_gain = 0.0
        rejection_log = []

        for cand_name, (cand_hdi, cand_evi) in candidates.items():
            if cand_name in current_policy_name: continue

            gain_hdi = cand_hdi - bench_hdi
            change_evi = cand_evi - bench_evi  # Изменение уязвимости

            # Условие: не увеличивать EVI больше чем на порог и дать прирост HDI
            is_safe = change_evi <= max_evi_risk
            is_better = gain_hdi > 0.0001

            if is_safe and is_better:
                if gain_hdi > best_marginal_gain:
                    best_strat = cand_name
                    best_marginal_gain = gain_hdi
            else:
                if not is_safe:
                    rejection_log.append(f"{cand_name} Riskier")
                elif not is_better:
                    rejection_log.append(f"{cand_name} No Gain")

        reason = f"SWITCH: -> {best_strat}" if best_strat not in current_policy_name else f"KEEP {best_strat}"

        final_strategies.append(best_strat)
        marginal_gains.append(best_marginal_gain)
        reasons.append(reason)

        chosen_hdi, chosen_evi = candidates.get(best_strat, (0.0, 0.0))
        final_abs_hdi.append(chosen_hdi)
        final_abs_evi.append(chosen_evi)

    report['Baseline_2019'] = report['CountryName'].map(baseline_map).map(code_to_name)
    report['Final_Strategy'] = final_strategies
    report['Marginal_HDI_Gain'] = marginal_gains
    report['Final_Projected_HDI_Gain'] = final_abs_hdi
    report['Final_Projected_EVI_Change'] = final_abs_evi
    report['Reason'] = reasons

    return report
