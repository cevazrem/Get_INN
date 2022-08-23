'''

Created on 6 июл. 2020 г.

 

@author: hz

'''

#Подключаем библиотеки

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
import time
import datetime
import warnings
from time import sleep
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from os import rename
import linecache

def last_line_pos(path):
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        file.close()
    pos = 0
    for line in lines:
        if line.count(';') != 7:
            return pos
        pos += 1
    return -1

   

def add_val(path, num_line, value):
    #print('add_val' + str(num_line))
    pos = 0
    with open(path, 'r+', encoding='utf-8') as file:
        lines = file.readlines()
        lines[num_line] = lines[num_line].replace('\n', '') + ';' + str(value) + '\n'
        file.seek(0)
        text = ''.join(lines)
        file.write(text)
        #with open(outpath, 'w', encoding='utf-8') as file:
        file.close()
    return lines

 

def main_fun():
    allowed_characters=['а','б','в','г','д','е','ё','ж','з','и','й','к','л','м','н','о','п','р','с','т','у','ф','х','ц','ч','ш','щ','ъ','ы','ь','э','ю','я',
                        'А','Б','В','Г','Д','Е','Ё','Ж','З','И','Й','К','Л','М','Н','О','П','Р','С','Т','У','Ф','Х','Ц','Ч','Ш','Щ','Ъ','Ы','Ь','Э','Ю','Я','\'', ' ', ',', '.', 'I', 'V', '(', ')', '-']

    #Задаем константы
    profile = 'C:\\Users\\AUsovich\\Documents\\Papka\\pyscript\\risk2\\User Data'
    engine = r'C:\\Users\\AUsovich\\Documents\\Papka\\pyscript\\risk2\\chromedriver.exe'
    income_file = 'C:\\Users\\AUsovich\\Documents\\Papka\\pyscript\\risk2\\customers.csv'
    #outcome_file = 'C:\\Users\\AUsovich\\Desktop\\pyscript\\risk2\\results.csv'
    inn_url_addr = 'https://service.nalog.ru/static/personal-data.html?svc=inn&from=%2Finn.do'

    cur_pos = 0
    start_pos = 0
    WINDOW_SIZE = "1920,1080"  
 
    options = webdriver.ChromeOptions()
    options.add_argument('user-data-dir='+ profile)
    #options.add_argument("--headless")
    options.add_argument("--window-size=%s" % WINDOW_SIZE)
    #driver = webdriver.Chrome(executable_path=engine,chrome_options=options)
    #driver.get(inn_url_addr)

    #Читаем входной файл
    driver = webdriver.Chrome(executable_path=engine,chrome_options=options)
    #driver = webdriver.Chrome(chrome_options=options, executable_path=engine)
    driver.implicitly_wait(20)
    #driver.get(inn_url_addr)

    with open(income_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    print(lines)
    start_pos = last_line_pos(income_file)
    if start_pos == -1:
        print('Файл уже обработан')
        return 'WRONG_FILE'
    cur_pos = start_pos - 1
    counter = 0
    try:
        while cur_pos < len(lines):
            counter += 1
            if counter > 1000:
                driver.close()
                driver.quit()
                return 'PLAN_RESTART'
            #print(cur_pos)
            it = 0
            while True:
                cur_pos += 1
                if cur_pos >= len(lines):
                    break
                print('Текущая строка->' + str(cur_pos))
                driver.get(inn_url_addr)
                current = lines[cur_pos]
                data_list = current.strip('\n').split(';')

                #Проверим формат даты рождения
                if len(data_list[3]) != 8:
                    inn_val = '<Неверный формат даты рождения>'
                    add_val(income_file, cur_pos, inn_val)
                    print('Неверный формат даты рождения')
                    break

                #Проверим формат серии номера паспорта
		if len(data_list[4]) != 10:
                    inn_val = '<Неверный формат серии номера документа>'
                    add_val(income_file, cur_pos, inn_val)
                    print('Неверный формат серии номера документа')
                    break

                #Проверим формат даты выдачи паспорта
                if len(data_list[5]) != 8:
                    inn_val = '<Неверный формат даты выдачи документа>'
                    add_val(income_file, cur_pos, inn_val)
                    print('Неверный формат даты выдачи документа')
                    break

                if len(data_list) == 7:
                    check = driver.find_element_by_xpath("//a[@class='checkbox checkbox-off']") #driver.find_element_by_xpath("//input[@type='checkbox' and @id='personalData']")
                    if check != None:
                        check.send_keys(Keys.ENTER)#check.click()
                        #sleep(1)
                        cont_btn = driver.find_element_by_xpath("//button[@type='submit' and @id='btnContinue']")
                        if cont_btn != None:
                            cont_btn.send_keys(Keys.ENTER)#cont_btn.click() 

                            #Введем фамилию
                            fem = driver.find_element_by_xpath("//input[@id = 'fam' and @class='txt-wide txt-ru-name-ex uni-hint-linked']")
                            for i in data_list[0]:
                                #sleep(0.1)
                                if i in allowed_characters:
                                    fem.send_keys(i)
                            #Введем имя
                            name = driver.find_element_by_xpath("//input[@id = 'nam' and @class='txt-wide txt-ru-name-ex uni-hint-linked']")
                            for i in data_list[1]:
                                #sleep(0.1)
                                name.send_keys(i)
                            #Введем отчество
                            otch = driver.find_element_by_xpath("//input[@id = 'otch' and @class='txt-wide txt-ru-name-ex uni-hint-linked']")
                            #=====================
                            if (not data_list[2]) or (data_list[2] == "-"):
                                check_otch = driver.find_element_by_xpath("//a[@class='checkbox checkbox-off' and @id='unichk_0']")
                                check_otch.send_keys(Keys.ENTER)
                            else:
                                for i in data_list[2]:
                                    #sleep(0.1)
                                    otch.send_keys(i)
                            #=====================

                            #Введем дату рождения
                            bdate = driver.find_element_by_xpath("//input[@id = 'bdate' and @class='txt-date uni-hint-linked']")
                            for i in data_list[3]:
                                #sleep(0.1)
                                bdate.send_keys(i)
                            #Введем номер документа
                            docno = driver.find_element_by_xpath("//input[@id = 'docno' and @class='txt-wide uni-hint-linked']")
                            for i in data_list[4]:
                                #sleep(0.1)
                                docno.send_keys(i)
                            #Вводим дату выдачи документа
                            docdt = driver.find_element_by_xpath("//input[@id = 'docdt' and @class='txt-date uni-hint-linked']")
                            for i in data_list[5]:
                                #sleep(0.1)
                                docdt.send_keys(i)
                            #Отправить запрос
                                submit_btn = None
                            submit_btn = driver.find_element_by_xpath("//button[@type='submit' and @id='btn_send']")
                            if submit_btn != None:
                                submit_btn.send_keys(Keys.ENTER)
                            #sleep(1)
                            itnum = 0
                            while True:
                                try:
                                    element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "result-inn")))
                                    if element.text != '' or len(data_list[2]) == 0:
                                        break
                                    else:
                                        element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "result_err_message")))
                                        if element.text != '':
                                            print(element.text)
                                            submit_btn.send_keys(Keys.ENTER)
                                            #break
                                        sleep(2)
                                finally:
                                    try:
                                        service_mess = driver.find_element_by_xpath("//div[@class='block result' and @style='display: block;']")
                                        if service_mess != None:
                                            if service_mess.get_attribute("id") == 'result_0' or service_mess.get_attribute("id") == 'result_3':
                                                print('Try1->INN not found')
                                                break
                                    except NoSuchElementException:
                                        pass
                                if itnum != 0:
                                    print('Waiting for a response('+str(itnum)+')...')
                                #print(itnum)
                                itnum = itnum + 1
                                if itnum > 3:
                                    raise NoSuchElementException
                            #Читаем ИНН
                            inn = driver.find_element_by_xpath("//p[@class='result-inn']")
                            if inn != None and inn.text != '':
                                inn_val = driver.find_element_by_xpath("//strong[@id='resultInn']").text
                                add_val(income_file, cur_pos, inn_val)
                            else:
                                print('Давай по новой Миша!')
                                #Try 1 more time
                                driver.get(inn_url_addr)
                                #===============   
                                data_list = current.strip('\n').split(';')
                                if len(data_list) == 7:
                                    check = driver.find_element_by_xpath("//a[@class='checkbox checkbox-off']") #driver.find_element_by_xpath("//input[@type='checkbox' and @id='personalData']")
                                    if check != None:
                                        check.send_keys(Keys.ENTER)#check.click()
                                        #sleep(1)
                                        cont_btn = driver.find_element_by_xpath("//button[@type='submit' and @id='btnContinue']")
                                        if cont_btn != None:
                                            cont_btn.send_keys(Keys.ENTER)#cont_btn.click()
                                            #Введем фамилию
                                            fem = driver.find_element_by_xpath("//input[@id = 'fam' and @class='txt-wide txt-ru-name-ex uni-hint-linked']")
                                            for i in data_list[0]:
                                                #sleep(0.1)
                                                if i in allowed_characters:
                                                    fem.send_keys(i)
                                            #Введем имя
                                            name = driver.find_element_by_xpath("//input[@id = 'nam' and @class='txt-wide txt-ru-name-ex uni-hint-linked']")
                                            for i in data_list[1]:
                                                #sleep(0.1)
                                                name.send_keys(i)
                                            #Введем отчество
                                            otch = driver.find_element_by_xpath("//input[@id = 'otch' and @class='txt-wide txt-ru-name-ex uni-hint-linked']")
                                            #=====================
                                            if not data_list[2]:
                                                check_otch = driver.find_element_by_xpath("//a[@class='checkbox checkbox-off' and @id='unichk_0']")
                                                check_otch.send_keys(Keys.ENTER)
                                            else:
                                                for i in data_list[2]:
                                                    #sleep(0.1)
                                                    otch.send_keys(i)
                                            #=====================
                                            #Введем дату рождения
                                            bdate = driver.find_element_by_xpath("//input[@id = 'bdate' and @class='txt-date uni-hint-linked']")
                                            for i in data_list[3]:
                                                #sleep(0.1)
                                                bdate.send_keys(i)
                                            #Введем номер документа
                                            docno = driver.find_element_by_xpath("//input[@id = 'docno' and @class='txt-wide uni-hint-linked']")
                                            for i in data_list[4]:
                                                #sleep(0.1)
                                                docno.send_keys(i)
                                            #Вводим дату выдачи документа
                                            docdt = driver.find_element_by_xpath("//input[@id = 'docdt' and @class='txt-date uni-hint-linked']")
                                            for i in data_list[5]:
                                                #sleep(0.1)
                                                docdt.send_keys(i)
                                            #Отправить запрос
                                            submit_btn = None
                                            submit_btn = driver.find_element_by_xpath("//button[@type='submit' and @id='btn_send']")
                                            if submit_btn != None:
                                                submit_btn.send_keys(Keys.ENTER)
                                            sleep(1)
                                            itnum = 0
                                            while True:
                                                try:
                                                    element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "result-inn")))
                                                    if element.text != '' or len(data_list[2]) == 0:
                                                        break
                                                    else:
                                                        element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, "result_err_message")))
                                                        if element.text != '':
                                                            print(element.text)
                                                            submit_btn.send_keys(Keys.ENTER)
                                                            #break
                                                        sleep(3)
                                                finally:
                                                    try:
                                                        service_mess = driver.find_element_by_xpath("//div[@class='block result' and @style='display: block;']")
                                                        if service_mess != None:
                                                            if service_mess.get_attribute("id") == 'result_0' or service_mess.get_attribute("id") == 'result_3':
                                                                print('ИНН не найден')
                                                                break
                                                    except NoSuchElementException:
                                                        pass
                                                #print(itnum)
                                                itnum = itnum + 1
                                                print('Waiting for a response('+str(itnum)+')...')
                                                if itnum > 3:
                                                    raise NoSuchElementException
                                            #Читаем ИНН
                                            inn = driver.find_element_by_xpath("//p[@class='result-inn']")
                                            if inn != None and inn.text != '':
                                                inn_val = driver.find_element_by_xpath("//strong[@id='resultInn']").text
                                            else:
                                                #last try
                                                inn_val = '<ИНН не найден>'
                                            add_val(income_file, cur_pos, inn_val)

                                #===============
    except NoSuchElementException:
        driver.close()
        driver.quit()
        return ('WRONG_SYMBOLS' + str(cur_pos))
    return 'FINISHED_SUCCESFULLY'           
 

if __name__ == '__main__':
    warnings.filterwarnings("ignore");
   
    income_file = 'C:\\Users\\AUsovich\\Documents\\Papka\\pyscript\\risk2\\customers.csv'
    #==========add sort===========  
    with open(income_file, "r+", encoding='utf-8') as file:
        lines = file.readlines()
        it = 0
        for line in lines:
            line = line.replace('\n', '')
            lines[it] = line
            it +=1
        lines.sort()
        file.seek(0)
        text = '\n'.join(lines)
        print(text)
        file.write(text)
    #==========add sort===========
    print('Input file sorted')
    print(len(lines))
    state = 'start'
    while state != 'FINISHED_SUCCESFULLY' and state != 'WRONG_FILE':
        state = main_fun()
        print(state)
        sleep(5)
    print('Finished 1 iter' + str(datetime.datetime.now()))
