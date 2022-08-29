import json, string
import pandas as pd
import pymorphy2 as morph
import warnings


warnings.filterwarnings("ignore") # Отключим сообщения о предупреждениях


df = pd.read_csv('test_data.csv') # Прочитаем наши данные


'''
Создадим словарь вхождений приветствий и ниаменований компаний
'''
dict = {
    'introduce':
    ['меня зовут', 'мое имя'],
    'company':
    ['компания', 'фирма', 'ооо']
}


def greetings(dialog):
    '''
    Функция обрабатывающая реплики с приветствиями
    Принимает на вход ссылку на отфильтрованные данные
    Возвращает текс диалога с приветствием менеджера и флаг о том, что менеджер поздоровался
    '''
    print('Реплики с приветствием – где менеджер поздоровался:')
    for message in df.index[df['dlg_id'] == dialog]:
        '''
        Сравниваем наш текст с текстом приветствия из файла с собранными вариантами приветствий
        '''
        if {i.lower().translate (str.maketrans('', '', string.punctuation))\
            for i in df['text'][message].split(' ')}\
            .intersection (set (json.load(open ('greetings.json')))) != set(): # Если встречаем пересечение
            if df['role'][message] == 'manager': # Проверяем, принадлежит ли фраза менеджеру
                print(df['text'][message])
                return True
    return False


def intriduce(dialog):
    '''
    Функция обрабатывающая реплики, где менеджер представился
    Принимает на вход ссылку на отфильтрованные данные
    Возвращает текс диалога с представлением менеджера
    '''
    print('Реплики, где менеджер представил себя:')
    for message in df.index[df['dlg_id'] == dialog]:
        for i in dict['introduce']: # Берем все варианты представления из словаря
            if i in df['text'][message]: # Если совпадает
                if df['role'][message] == 'manager': # Если фраза пренадлежит менеджеру
                    print(df['text'][message])
                    manager_name(df['text'][message]) # Выделяем имя менеджера


def manager_name(dailog):
    '''
    Функция обрабатывающая реплики, где менеджер представился
    Принимает на вход ссылку на отфильтрованные данные
    Возвращает имя менеджера
    '''
    tresh = 0.6
    words = dailog.split(' ') # Разбиваем тект диалога на отдельные слова
    for name in words: # И циклом пробегаемся по ним
        name = morph.MorphAnalyzer().parse(name) # Анализируем слова морфологически
        if 'Name' in name[0].tag and name[0].score >= tresh: # Смотрим по его тегам и сравниваем со скором
            print('Имя менеджера: ', name[0].normal_form) # Выводим его нормальную форму


def company_name(text):
    '''
    Функция обрабатывающая реплики, где втречаются наименования компаний
    Принимает на вход ссылку на отфильтрованные данные
    Возвращает наименование компании
    '''
    result = []
    words = text.split(' ') # Разбиваем тект диалога на отдельные слова
    for word_index, word in enumerate(text.split(' ')): # И циклом пробегаемся по ним
        if word in dict['company']: # Если слово-вхождение совпадает со словом из словаря
            if word_index != len(text.split()) - 1: # Если индекс вхождения не совпадает с конечной фразой
                i = 1
                company_name = morph.MorphAnalyzer().parse(words[word_index + i]) # Запоминаем в переменной
                while 'NOUN' in company_name[0].tag or 'ADJF' in company_name[0].tag: # Пока есть что еще смотреть
                    result.append(words[word_index + i]) # Добавляем в переменную
                    i += 1
                    company_name = morph.MorphAnalyzer().parse(words[word_index + i])
    return ' '.join(result) # Возвращем результат


def parting(dialog):
    '''
    Функция обрабатывающая реплики, где менеджер попрощался
    Принимает на вход ссылку на отфильтрованные данные
    Возвращает реплику с прощанием и флаг о том, что менеджер попрощался
    '''
    print('Реплики с прощанием, где менеджер попрощался:')
    for message in df.index[df['dlg_id'] == dialog]:
        if {i.lower().translate (str.maketrans('', '', string.punctuation))\
            for i in df['text'][message].split(' ')}\
            .intersection (set (json.load(open ('parting.json')))) != set(): # Если встречаем пересечение
            if df['role'][message] == 'manager': # Проверяем, принадлежит ли фраза менеджеру
                print(df['text'][message])
                return True
    return False


def names(dialog):
    '''
    Функция обрабатывает тект диалога и ищет в нем имена
    Получает на вход ссылку на отфильтрованные данные
    Возвращает встречающиеся в тесте диалога имена
    '''
    print('Но в диалоге упоминаются имена:')
    for message in df.index[df['dlg_id'] == dialog]:
        if {i.lower ().translate (str.maketrans ('', '', string.punctuation))\
            for i in df['text'][message].split (' ')}\
            .intersection (set (json.load (open ('names.json')))) != set (): # Если встречаем пересечение
            print({i.lower ().translate (str.maketrans ('', '', string.punctuation))\
                   for i in df['text'][message].split (' ')}\
            .intersection (set (json.load (open ('names.json'))))) # Выводим встречающиеся имена


def main():
    '''
    Собственно, управляющая функция
    '''
    for i in df['dlg_id'].unique():
        print('Диалог', i)
        print('\n')
        status_greetings = greetings(i)
        print('\n')
        intriduce(i)
        print('\n')
        names(i)
        print('\n')
        for dialog in df.index[df['dlg_id'] == i]:
            if (company_name(df['text'][dialog]) != '') & (company_name(df['text'][dialog]) != 'которая'):
                print('В диалоге упоминается компания:', company_name(df['text'][dialog]))
        print('\n')
        status_parting = parting(i)
        print('\n')
        if status_greetings & status_parting:
            print('Все требования менеджер выполнил')
        else:
            print('Не все требования были выполнены менеджером')
        print('\n')


'''
Проверяем, собственно вызванная функция или мы используем парсер как отдельный объект
'''
if __name__ == '__main__':
    main()