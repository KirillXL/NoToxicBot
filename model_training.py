
#В этом файле изучается создание классификационной модели
# Подключим все необходимые библиотеки
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Библиотеки из обучающего видео

import nltk #анализ текста
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
nltk.download('punkt')
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import precision_score, recall_score, precision_recall_curve
from matplotlib import pyplot as plt
import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import PrecisionRecallDisplay

nltk.download('stopwords') #Загрузка стоп-слов

#Загрузим датасет с размеченными данными
#В датасете информация о негативных комментариях


data_path = 'Dataframe/labeled.csv'

df = pd.read_csv(data_path)
df.head(10)

#Возьму код из своей прошлой практики для разделения данных на тестовые и обучающие
train_df, test_df = train_test_split(df, test_size = 0.2)

sentence_example = df.iloc[1]["comment"]
tokens = word_tokenize(sentence_example, language="russian")
tokens_without_punctuation = [i for i in tokens if i not in string.punctuation]
russian_stop_words = stopwords.words("russian")
tokens_without_stop_words_and_punctuation = [i for i in tokens_without_punctuation if i not in russian_stop_words]
snowball = SnowballStemmer(language="russian")
stemmed_tokens = [snowball.stem(i) for i in tokens_without_stop_words_and_punctuation]

"""#Функция обработки"""

snowball = SnowballStemmer(language="russian")
russian_stop_words = stopwords.words("russian")

def tokenize_sentence(sentence: str, remove_stop_words: bool = True):
    tokens = word_tokenize(sentence, language="russian")
    tokens = [i for i in tokens if i not in string.punctuation]
    if remove_stop_words:
        tokens = [i for i in tokens if i not in russian_stop_words]
    tokens = [snowball.stem(i) for i in tokens]
    return tokens

tokenize_sentence(sentence_example)

"""#Обучение модели"""

vectorizer = TfidfVectorizer(tokenizer=tokenize_sentence)

#Делим все слова как признаки предложений
features = vectorizer.fit_transform(train_df["comment"])

#Обучаем модель определять по словам токсичность комментария
model = LogisticRegression(random_state=0)
model.fit(features, train_df["toxic"])

# Проверим первый коммент
model.predict(features[0])

#Прочитаем его
train_df["comment"].iloc[0]

"""# Создание пайплайна модели(делаем модель рабочей у пользователя)"""

#Мы объединяем векторайзер и модель, тем самым мы создаем модель, которая работает с цельными предложениями
model_pipeline = Pipeline([
    ("vectorizer", TfidfVectorizer(tokenizer = tokenize_sentence)),
    ("model", LogisticRegression(random_state=0))
]
)
#Все из-за того, что мы до этого дробили предложения

model_pipeline.fit(train_df["comment"], train_df["toxic"])

"""#Измерим метрики модели"""

precision_score(y_true=test_df["toxic"], y_pred=model_pipeline.predict(test_df["comment"]))

recall_score(y_true=test_df["toxic"], y_pred=model_pipeline.predict(test_df["comment"]))

print('Обучение завершено')

import cloudpickle

with open('model.pkl', 'wb') as f:
    cloudpickle.dump(model_pipeline, f)