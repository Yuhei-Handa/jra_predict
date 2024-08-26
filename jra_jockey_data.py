from bs4 import BeautifulSoup
import requests
import urllib.robotparser
import pandas as pd
import numpy as np
import re
import datetime
import time
import os
import sys
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def check_robot_txt(homepage_url:str):
    """robots.txtの内容を取得し、クローリング許可かどうかを判定する

    Args:
        homepage_url (str): robots.txt取得先のホームページURL

    Returns:
        bool: クローリング許可の場合はTrue, 禁止の場合はFalse
    """

    robots_url = os.path.join(homepage_url, 'robots.txt')

    #　robots.txtの内容をrequestsで取得
    response = requests.get(robots_url)
    response.encoding = response.apparent_encoding
    robot_txt = response.text

    # robots.txtの内容を表示
    #print(robot_txt)

    user_agent = robot_txt.split("\n")[0].split(":")[1].strip()
    disallow = robot_txt.split("\n")[1].split(":")[1].strip()

    if user_agent == "*" and disallow == "":
        print("クローリング許可")
        return True
    else:
        print("クローリング禁止")
        return False
    
class JockeyDB:
    def __init__(self, homepage_url:str):
        self.homepage_url = homepage_url
        self.driver = None

    def init_driver(self):
        options = Options()
        #options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def wait_random_seconds(self, min_range=0.1, max_range=0.2):
        original_time = 0.1
        wait_range = np.random.uniform(min_range, max_range)
        wait_time = original_time + wait_range
        time.sleep(wait_time)

    def _has_tag(self, element:webdriver.remote.webelement.WebElement, tag_name:str):
        try:
            element.find_element(By.TAG_NAME, tag_name)
            return True
        except:
            return False
        
    def _has_class(self, element:webdriver.remote.webelement.WebElement, class_name:str):
        try:
            element.find_element(By.CLASS_NAME, class_name)
            return True
        except:
            return False
    
    def _has_text(self, element:webdriver.remote.webelement.WebElement):
        try:
            txt = element.text
            if txt == "":
                return False
            else:
                return True
        except:
            return False
    
    def _has_attribute(self, element:webdriver.remote.webelement.WebElement, attribute:str):
        try:
            element.get_attribute(attribute)
            return True
        except:
            return
        
    def _is_numeric(self, text:str):
        try:
            float(text)
            return True
        except:
            return False
        
    def _get_all_page_db(self):
        day_element_list = []
        track_element_list = []
        race_name_element_list = []
        horse_name_element_list = []
        ground_element_list = []
        distance_element_list = []
        ground_state_element_list = []
        num_horse_element_list = []
        popularity_element_list = []
        rank_element_list = []
        trainer_element_list = []
        weight_element_list = []
        horse_weight_element_list = []
        time_element_list = []

        tbody_element = self.driver.find_element(By.TAG_NAME, "tbody")
        tr_elements = tbody_element.find_elements(By.TAG_NAME, "tr")

        for tr_element in tr_elements:
            td_elements = tr_element.find_elements(By.TAG_NAME, "td")
            for n, td_element in enumerate(td_elements):
                if n == 0:
                    day_element_list.append(td_element)
                elif n == 1:
                    track_element_list.append(td_element)
                elif n == 2:
                    race_name_element_list.append(td_element)
                elif n == 3:
                    horse_name_element_list.append(td_element)
                elif n == 4:
                    ground_element_list.append(td_element)
                elif n == 5:
                    distance_element_list.append(td_element)
                elif n == 6:
                    ground_state_element_list.append(td_element)
                elif n == 7:
                    num_horse_element_list.append(td_element)
                elif n == 8:
                    popularity_element_list.append(td_element)
                elif n == 9:
                    rank_element_list.append(td_element)
                elif n == 10:
                    trainer_element_list.append(td_element)
                elif n == 11:
                    weight_element_list.append(td_element)
                elif n == 12:
                    horse_weight_element_list.append(td_element)
                elif n == 13:
                    time_element_list.append(td_element)

        # 年月日
        # 「2024年12月31日」のような形式で格納
        # datetime型に変換
        day_list = []
        for day_element in day_element_list:
            if self._has_text(day_element):
                day = day_element.text
                tmp_year = re.search(r"(\d+)年", day).group(1)
                tmp_month = re.search(r"年(\d+)月", day).group(1)
                tmp_day = re.search(r"月(\d+)日", day).group(1)
                year = int(tmp_year)
                month = int(tmp_month)
                day = int(tmp_day)
                day = datetime.datetime(year, month, day)
                day_list.append(day)
            else:
                day_list.append(None)

        # 場
        track_list = []
        for track_element in track_element_list:
            if self._has_text(track_element):
                track = track_element.text
                track_list.append(track)
            else:
                track_list.append(None)

        # レース名
        # アイコン
        race_name_list = []
        icon_list = []
        for race_name_element in race_name_element_list:
            if self._has_text(race_name_element):
                race_name = race_name_element.text
                icon_element = race_name_element.find_element(By.TAG_NAME, "img")
                icon = icon_element.get_attribute("alt")
                race_name_list.append(race_name)
                icon_list.append(icon)
            else:
                race_name_list.append(None)
                icon_list.append(None)

        # 馬名
        horse_name_list = []
        for horse_name_element in horse_name_element_list:
            if self._has_text(horse_name_element):
                horse_name = horse_name_element.text
                horse_name_list.append(horse_name)
            else:
                horse_name_list.append(None)

        # 地面
        # 本来「ダ1400」のような形式で格納
        # このうち、地面のみを抽出
        ground_list = []
        distance_list = []
        for ground_element in ground_element_list:
            if self._has_text(ground_element):
                ground_distance = ground_element.text
                distance = re.search(r"\d+", ground_distance).group()
                ground = ground_distance.replace(distance, "")
                ground_list.append(ground)
                distance_list.append(distance)
            else:
                ground_list.append(None)
                distance_list.append(None)

        # 馬場状態
        ground_state_list = []
        for ground_state_element in ground_state_element_list:
            if self._has_text(ground_state_element):
                ground_state = ground_state_element.text
                ground_state_list.append(ground_state)
            else:
                ground_state_list.append(None)

        # 頭数
        num_horse_list = []
        for num_horse_element in num_horse_element_list:
            if self._has_text(num_horse_element):
                num_horse = num_horse_element.text
                num_horse_list.append(num_horse)
            else:
                num_horse_list.append(None)

        # 人気
        popularity_list = []
        for popularity_element in popularity_element_list:
            if self._has_text(popularity_element):
                popularity = popularity_element.text
                popularity_list.append(popularity)
            else:
                popularity_list.append(None)

        # 着順
        rank_list = []
        for rank_element in rank_element_list:
            if self._has_text(rank_element):
                rank = rank_element.text
                if self._is_numeric(rank):
                    rank_list.append(rank)
                else:
                    rank_list.append(None)
            else:
                rank_list.append(None)

        # 調教師名
        trainer_list = []
        for trainer_element in trainer_element_list:
            if self._has_text(trainer_element):
                trainer = trainer_element.text
                trainer_list.append(trainer)
            else:
                trainer_list.append(None)

        # 負担重量
        weight_list = []
        for weight_element in weight_element_list:
            if self._has_text(weight_element):
                weight = weight_element.text
                weight_list.append(weight)
            else:
                weight_list.append(None)

        # 馬体重
        horse_weight_list = []
        for horse_weight_element in horse_weight_element_list:
            if self._has_text(horse_weight_element):
                if self._is_numeric(horse_weight_element.text):
                    horse_weight = horse_weight_element.text
                    horse_weight_list.append(horse_weight)
                else:
                    horse_weight_list.append(None)
            else:
                horse_weight_list.append(None)

        # タイム
        # 「2:00.1」のような形式で格納
        # 秒単位に変換後、float型に変換
        time_list = []
        for time_element in time_element_list:
            if self._has_text(time_element):
                time = time_element.text
                if self._is_numeric(time):
                    tmp_minute = re.search(r"(\d+):", time).group(1)
                    tmp_second = re.search(r":(\d+).", time).group(1)
                    tmp_decimal = re.search(r".(\d+)", time).group(1)
                    minute = int(tmp_minute)
                    second = int(tmp_second)
                    decimal = int(tmp_decimal)
                    time = minute * 60 + second + decimal / 10
                    time_list.append(time)
                else:
                    time_list.append(None)
            else:
                time_list.append(None)

        current_page_df = pd.DataFrame({
                                    "年月日": day_list,
                                    "場": track_list,
                                    "レース名": race_name_list,
                                    "アイコン": icon_list,
                                    "馬名": horse_name_list,
                                    "地面": ground_list,
                                    "距離": distance_list,
                                    "馬場状態": ground_state_list,
                                    "頭数": num_horse_list,
                                    "人気": popularity_list,
                                    "着順": rank_list,
                                    "調教師名": trainer_list,
                                    "負担重量": weight_list,
                                    "馬体重" : horse_weight_list,
                                    "タイム": time_list
                                    })

        # 次のページに遷移
        # 次のページが存在するかどうかを判定
        # li要素の数が7個の場合は必ず次のページが存在する
        # li要素の数が6個の場合は次のページが存在しない場合がある
        # li要素の数が6個の場合「前の20件」と「次の20件」が存在する場合は次のページが存在する
        # 「次の20件」が存在しない場合は次のページが存在しないと判定
        # 「前の20件」が存在する場合は、最初のli要素のclass属性が「current」の場合は次のページが存在しない
        paper_block_element = self.driver.find_element(By.CLASS_NAME, "pager_block")
        pager_element = paper_block_element.find_element(By.CLASS_NAME, "pager")
        ul_element = pager_element.find_element(By.TAG_NAME, "ul")
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")
        num_li_elements = len(li_elements)
        if num_li_elements == 7:
            tmp_next_page_element = li_elements[-1]
            next_page_element = tmp_next_page_element.find_element(By.TAG_NAME, "a")
            next_page_element.click()
            all_next_page_df = self._get_all_page_db()
            self.wait_random_seconds()
        elif num_li_elements == 6:
            current_page_element = li_elements[0]
            if self._has_attribute(current_page_element, "class"):
                if current_page_element.get_attribute("class") == "current":
                    tmp_next_page_element = li_elements[-1]
                    next_page_element = tmp_next_page_element.find_element(By.TAG_NAME, "a")
                    next_page_element.click()
                    all_next_page_df = self._get_all_page_db()
                else: # エラー処理
                    pass
            else: # 「次の20件」が存在しない場合
                self.driver.back()

        # 現在のページのdataframeと次ページ以降のdataframeを結合
        all_next_page_df = pd.concat([all_next_page_df, current_page_df], axis=0)

        return all_next_page_df

    def get_past_db(self):
        self.driver.get(self.homepage_url)
        element = self.driver.find_element(By.CSS_SELECTOR, "#quick_menu > div > ul > li:nth-of-type(6)")
        element.click()
        self.wait_random_seconds()
        element = self.driver.find_element(By.ID, "jockey")
        element = element.find_element(By.CLASS_NAME, "link_list")
        tmp_meikan_element = element.find_elements(By.TAG_NAME, "li")[0]
        meikan_element = tmp_meikan_element.find_element(By.TAG_NAME, "a")
        meikan_element.click()
        self.wait_random_seconds()
        self.get_japanese_order_db()
        self.driver.quit()

    def get_japanese_order_db(self):
        initial_list_element = self.driver.find_element(By.CLASS_NAME, "initial_list")
        link_list_element = initial_list_element.find_elements(By.CLASS_NAME, "link_list")
        li_elements = link_list_element.find_elements(By.TAG_NAME, "li")
        num_japanese_order = len(li_elements)

        for n in range(num_japanese_order):
            initial_list_element = self.driver.find_element(By.CLASS_NAME, "initial_list")
            link_list_element = initial_list_element.find_elements(By.CLASS_NAME, "link_list")
            li_elements = link_list_element.find_elements(By.TAG_NAME, "li")
            tmp_li_elements = li_elements[n]
            li_element = tmp_li_elements.find_element(By.TAG_NAME, "a")
            li_element.click()
            self.wait_random_seconds()
            self.get_one_japanese_order_db()
        self.driver.back()


    def get_one_japanese_order_db(self):
        name_list_element = self.driver.find_element(By.CLASS_NAME, "name_list")
        inner_elements = name_list_element.find_elements(By.CLASS_NAME, "inner")
        num_jockey = len(inner_elements)
        for n in range(num_jockey):
            name_list_element = self.driver.find_element(By.CLASS_NAME, "name_list")
            inner_elements = name_list_element.find_elements(By.CLASS_NAME, "inner")
            inner_element = inner_elements[n]
            inner_element.click()
            self.wait_random_seconds()
            self.get_jockey_db()
        self.driver.back()

    def get_jockey_db(self):

        data_element = self.driver.find_element(By.CLASS_NAME, "data")
        li_elements = data_element.find_elements(By.TAG_NAME, "li")

        # 今年度成績のdataframeを取得
        this_year_df = self.get_this_year_db()

        # 過去成績のdataframeを取得
        past_year_df = self.get_past_year_db()

        # 今年度成績と過去成績を結合
        jockey_df = pd.concat([this_year_df, past_year_df], axis=0)
        # レース数
        len_df = len(jockey_df)
        
        # 生年月日
        # 「2001年9月12日」のような形式で格納
        # datetime型に変換
        tmp_birthday_element = li_elements[0]
        birthday_element = tmp_birthday_element.find_element(By.TAG_NAME, "dd")
        birthday = birthday_element.text
        tmp_year = re.search(r"(\d+)年", birthday).group(1)
        tmp_month = re.search(r"年(\d+)月", birthday).group(1)
        tmp_day = re.search(r"月(\d+)日", birthday).group(1)
        year = int(tmp_year)
        month = int(tmp_month)
        day = int(tmp_day)
        birthday = datetime.datetime(year, month, day)
        birthday_list = [birthday] * len_df

        # 身長
        tmp_height_element = li_elements[1]
        height_element = tmp_height_element.find_element(By.TAG_NAME, "dd")
        tmp_height = height_element.text
        height = float(tmp_height)
        height_list = [height] * len_df

        # 体重
        tmp_weight_element = li_elements[2]
        weight_element = tmp_weight_element.find_element(By.TAG_NAME, "dd")
        tmp_weight = weight_element.text
        weight = float(tmp_weight)
        weight_list = [weight] * len_df

        # 所属
        tmp_belong_element = li_elements[9]
        belong_element = tmp_belong_element.find_element(By.TAG_NAME, "dd")
        belong = belong_element.text
        belong_list = [belong] * len_df

        # data frameに新たな列を追加
        jockey_df["生年月日"] = birthday_list
        jockey_df["身長"] = height_list
        jockey_df["体重"] = weight_list
        jockey_df["所属"] = belong_list

    def get_this_year_db(self):
        jockey_menu_element = self.driver.find_element(By.CLASS_NAME, "jockey_menu")
        link_list_element = jockey_menu_element.find_element(By.CLASS_NAME, "link_list")
        li_elements = link_list_element.find_elements(By.TAG_NAME, "li")
        tmp_this_year_element = li_elements[1]
        this_year_element = tmp_this_year_element.find_element(By.TAG_NAME, "a")
        this_year_element.click()
        self.wait_random_seconds()
        this_year_df = self._get_all_page_db()
        self.driver.back()
    
    def get_past_year_db(self):
        jockey_menu_element = self.driver.find_element(By.CLASS_NAME, "jockey_menu")
        link_list_element = jockey_menu_element.find_element(By.CLASS_NAME, "link_list")
        li_elements = link_list_element.find_elements(By.TAG_NAME, "li")
        tmp_past_year_element = li_elements[2]
        past_year_element = tmp_past_year_element.find_element(By.TAG_NAME, "a")
        past_year_element.click()
        self.wait_random_seconds()
        past_year_df = self._get_all_page_db()
        self.driver.back()





    