import unittest
import pandas as pd
import pandas.testing as tm


def calculate_moving_average(df):
    # Создаем копию, чтобы не менять оригинал
    result = df.copy()
    # Считаем скользящую среднюю по окну в 3 дня
    result['ma_3d'] = result['price'].rolling(window=3).mean()
    # Заполняем NaN нулями (для простоты)
    result['ma_3d'] = result['ma_3d'].fillna(0)
    return result

class TestFinancialRegression(unittest.TestCase):

    def setUp(self):
        # 1. Создаем "Золотой Эталон" (То, что мы считаем правильным ответом)
        self.golden_data = pd.DataFrame({
            'price': [10, 20, 30, 40],
            'ma_3d': [0.0, 0.0, 20.0, 30.0]
        })

    def test_ma_consistency(self):
        # 2. Готовим входные данные (только цены)
        input_df = pd.DataFrame({
            'price': [10, 20, 30, 40]
        })

        # 3. Запускаем тестируемую функцию
        actual_result = calculate_moving_average(input_df)

        # 4. СРАВНЕНИЕ (Ваш код здесь)
        tm.assert_frame_equal(actual_result, self.golden_data)
        pass


if __name__ == '__main__':
    unittest.main()



import scipy.stats as stats

def check_drift(train, prod):
    num = prod.shape[0]
    train = train.sample(n=num)
    stat, p_value = stats.ttest_ind(train, prod, equal_var=False)

    if p_value < 0.05:
        return ('There os the drift in the data')
    else:
        return('There is no drift, data from prod is similar to train')


def remove_outliers_iqr(df, column):
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5*iqr
    upper = q3 + 1.5*iqr

    df = df.loc[(df[column]<= upper)&(f[column]>= lower) ]
    return df