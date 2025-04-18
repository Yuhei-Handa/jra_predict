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
import argparse
from glob import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



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
    
class RaceDB:
    def __init__(self, homepage_url:str):
        self.homepage_url = homepage_url
        self.track_count = 0
        self.race_count = 0
        self.race_df = pd.DataFrame()
        self.track_df = pd.DataFrame()
        self.driver = None
        self.wait_time = 30
        self.first_month_flag = True
        self.max_wait_time = 0
        self.num_wait = 0
        self.save_dir = "jra_race_data"
        self.init_driver()
        self.mkdir()

    def init_driver(self):
        options = Options()
        #options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def mkdir(self):
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)
    
    def check_saved_data(self):
        # save_dir内にデータが存在するか確認
        # save_dir内にフォルダが存在する場合はTrue、存在しない場合はFalse

        year_folder_path = os.path.join(self.save_dir, "*")
        year_folder_pathes = glob(year_folder_path)
        if len(year_folder_pathes) == 0:
            return False
        else:
            return True

    def wait_random_seconds(self, min_range=0.1, max_range=0.2):
        original_time = 0.1
        wait_range = np.random.uniform(min_range, max_range)
        wait_time = original_time + wait_range
        time.sleep(wait_time)

    def _has_tag(self, element:webdriver.remote.webelement.WebElement, tag_name:str):
        try:
            # wait = WebDriverWait(self.driver, self.wait_time)
            # wait.until(EC.presence_of_element_located((By.TAG_NAME, tag_name)))
            element.find_element(By.TAG_NAME, tag_name)
            return True
        except:
            return False
        
    def _has_class(self, element:webdriver.remote.webelement.WebElement, class_name:str):
        try:
            # wait = WebDriverWait(self.driver, self.wait_time)
            # wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
            element.find_element(By.CLASS_NAME, class_name)
            return True
        except:
            return False
    
    def _has_id(self, element:webdriver.remote.webelement.WebElement, id_name:str):
        try:
            # wait = WebDriverWait(self.driver, self.wait_time)
            # wait.until(EC.presence_of_element_located((By.ID, id_name)))
            element.find_element(By.ID, id_name)
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
        
    def _has_alt(self, element:webdriver.remote.webelement.WebElement):
        try:
            element.get_attribute("alt")
            return True
        except:
            return False
        
    def _has_href(self, element:webdriver.remote.webelement.WebElement):
        try:
            element.get_attribute("href")
            return True
        except:
            return False
        
    def _is_numeric(self, text:str):
        try:
            float(text)
            return True
        except:
            return False
    
    def _wait_class_element(self, class_name:str):
        try:
            wait = WebDriverWait(self.driver, self.wait_time)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        except:
            self.driver.quit()
            new_race_db = RaceDB(self.homepage_url)
            new_race_db.init_driver()
            new_race_db.continue_past_db()
    
    def _wait_id_element(self, id_name:str):
        try:
            wait = WebDriverWait(self.driver, self.wait_time)
            wait.until(EC.presence_of_element_located((By.ID, id_name)))
        except:
            self.driver.quit()
            new_race_db = RaceDB(self.homepage_url)
            new_race_db.init_driver()
            new_race_db.continue_past_db()
            

    def _wait_tag_element(self, tag_name:str):
        try:
            wait = WebDriverWait(self.driver, self.wait_time)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, tag_name)))
        except:
            self.driver.quit()
            new_race_db = RaceDB(self.homepage_url)
            new_race_db.init_driver()
            new_race_db.continue_past_db()

    def _wait_click_element(self, element:webdriver.remote.webelement.WebElement, attribute:str):
        try:
            if attribute == "class":
                wait = WebDriverWait(self.driver, self.wait_time)
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, element.class_name)))
            elif attribute == "id":
                wait = WebDriverWait(self.driver, self.wait_time)
                wait.until(EC.element_to_be_clickable((By.ID, element.id)))
            elif attribute == "tag":
                wait = WebDriverWait(self.driver, self.wait_time)
                wait.until(EC.element_to_be_clickable((By.TAG_NAME, element.tag_name)))

        except:
            self.driver.quit()
            new_race_db = RaceDB(self.homepage_url)
            new_race_db.init_driver()
            new_race_db.continue_past_db()

    def _find_element(self, element:webdriver.remote.webelement.WebElement, is_driver:bool, by:str, value:str):
            try:
                if is_driver:
                    if by == "class":
                        self._wait_class_element(value)
                        element = self.driver.find_element(By.CLASS_NAME, value)
                    elif by == "id":
                        self._wait_id_element(value)
                        element = self.driver.find_element(By.ID, value)
                    elif by == "tag":
                        self._wait_tag_element(value)
                        element = self.driver.find_element(By.TAG_NAME, value)
                else:
                    if by == "class":
                        self._wait_class_element(value)
                        element = element.find_element(By.CLASS_NAME, value)
                    elif by == "id":
                        self._wait_id_element(value)
                        element = element.find_element(By.ID, value)
                    elif by == "tag":
                        self._wait_tag_element(value)
                        element = element.find_element(By.TAG_NAME, value)
                return element
            except:
                self.driver.quit()
                new_race_db = RaceDB(self.homepage_url)
                new_race_db.init_driver()
                new_race_db.continue_past_db()

    def _find_elements(self, element:webdriver.remote.webelement.WebElement, is_driver:bool, by:str, value:str):
        try:
            if is_driver:
                if by == "class":
                    self._wait_class_element(value)
                    elements = self.driver.find_elements(By.CLASS_NAME, value)
                elif by == "id":
                    self._wait_id_element(value)
                    elements = self.driver.find_elements(By.ID, value)
                elif by == "tag":
                    self._wait_tag_element(value)
                    elements = self.driver.find_elements(By.TAG_NAME, value)
            else:
                if by == "class":
                    self._wait_class_element(value)
                    elements = element.find_elements(By.CLASS_NAME, value)
                elif by == "id":
                    self._wait_id_element(value)
                    elements = element.find_elements(By.ID, value)
                elif by == "tag":
                    self._wait_tag_element(value)
                    elements = element.find_elements(By.TAG_NAME, value)
            return elements
        except:
            self.driver.quit()
            new_race_db = RaceDB(self.homepage_url)
            new_race_db.init_driver()
            new_race_db.continue_past_db()
    
    def _get_target_date(self):
        # csvファイルのパスは「jra_race_data\\2024\\04\\06\\2024_04_06_土曜_09_50_1回福島1日_3歳未勝利.csv」のような形式で格納
        # 「西暦_月_日_曜日_時_分_開催回数開催場所日数_レース名.csv」のような形式で格納
        year_folder_path = os.path.join(self.save_dir, "*")
        year_folder_pathes = glob(year_folder_path)
        # 最も古い年を取得
        oldest_year_folder_path = sorted(year_folder_pathes)[0]
        tmp_oldest_year = os.path.basename(oldest_year_folder_path)
        oldest_year = int(tmp_oldest_year)
        # 最も古い月を取得
        month_folder_path = os.path.join(oldest_year_folder_path, "*")
        month_folder_pathes = glob(month_folder_path)
        oldest_month_folder_path = sorted(month_folder_pathes)[0]
        tmp_oldest_month = os.path.basename(oldest_month_folder_path)
        oldest_month = int(tmp_oldest_month)
        # 最も大きい日を取得
        day_folder_path = os.path.join(oldest_month_folder_path, "*")
        day_folder_pathes = glob(day_folder_path)
        oldest_day_folder_path = sorted(day_folder_pathes)[-1]
        tmp_oldest_day = os.path.basename(oldest_day_folder_path)
        oldest_day = int(tmp_oldest_day)

        conected_file_pathes = glob(os.path.join(oldest_day_folder_path, "*.csv"))

        return oldest_year, oldest_month, oldest_day
    
    def _open_next_page_until_oldest_date(self, oldest_year:int, oldest_month:int, oldest_day:int):
        # ページネーションの次へボタンをクリックして、最も古い西暦、月のページまで移動する
        prev_month_flag = False
        # self._wait_id_element("contents")
        # prev_month_element = self.driver.find_element(By.ID, "contents")
        prev_month_element = self._find_element(element=None, is_driver=True, by="id", value="contents")
        if self._has_class(prev_month_element, "month"):
            prev_month_flag = True
        else:
            pass
        #print(f"prev_month_flag: {prev_month_flag}")

        # 現在の西暦、月をページから取得
        # self._wait_id_element("contents")
        # contents_element = self.driver.find_element(By.ID, "contents")
        contents_element = self._find_element(element=None, is_driver=True, by="id", value="contents")
        # self._wait_class_element("nav")
        # nav_element = contents_element.find_element(By.CLASS_NAME, "nav")
        nav_element = self._find_element(element=contents_element, is_driver=False, by="class", value="nav")
        # self._wait_class_element("current")
        # current_element = nav_element.find_element(By.CLASS_NAME, "current")
        if self._has_class(nav_element, "current"):
            current_element = self._find_element(element=nav_element, is_driver=False, by="class", value="current")
            current_element = self._find_element(element=nav_element, is_driver=False, by="class", value="current")
            # self._wait_class_element("year")
            # span_element = current_element.find_element(By.TAG_NAME, "span")
            span_element = self._find_element(element=current_element, is_driver=False, by="tag", value="span")
            current_year_month = span_element.text
            # 「2024年4月」のような形式
            tmp_current_year = re.search(r"(\d+)年", current_year_month).group(1)
            tmp_current_month = re.search(r"(\d+)月", current_year_month).group(1)
            current_year = int(tmp_current_year)
            current_month = int(tmp_current_month)
            print(f"current_year: {current_year} current_month: {current_month}")
            print(f"olkdest_year: {oldest_year} oldest_month: {oldest_month}")
            if current_year > oldest_year:
                # 「前年」をクリック、次のページに移動
                if self._has_class(nav_element, "year"):
                    # 「前年」、「翌年」の場合があるが、構造上「前年」が最初に来る
                    # tmp_prev_year_element = nav_element.find_element(By.CLASS_NAME, "year")
                    tmp_prev_year_element = self._find_element(element=nav_element, is_driver=False, by="class", value="year")
                    if self._has_tag(tmp_prev_year_element, "a"):
                        # prev_year_element = tmp_prev_year_element.find_element(By.TAG_NAME, "a")
                        prev_year_element = self._find_element(element=tmp_prev_year_element, is_driver=False, by="tag", value="a")
                        self._wait_click_element(prev_year_element, "tag")
                        prev_year_element.click()
                        self._open_next_page_until_oldest_date(oldest_year, oldest_month, oldest_day)
            elif current_year == oldest_year:
                if current_month > oldest_month:
                    # 「前月」をクリック、次のページに移動
                    # 「前月」、「翌月」の場合があるが、構造上「前月」が最初に来る
                    if self._has_class(nav_element, "month"):
                        # tmp_prev_month_element = nav_element.find_element(By.CLASS_NAME, "month")
                        tmp_prev_month_element = self._find_element(element=nav_element, is_driver=False, by="class", value="month")
                        # prev_month_element = tmp_prev_month_element.find_element(By.TAG_NAME, "a")
                        prev_month_element = self._find_element(element=tmp_prev_month_element, is_driver=False, by="tag", value="a")
                        self._wait_click_element(prev_month_element, "tag")
                        prev_month_element.click()
                        self._open_next_page_until_oldest_date(oldest_year, oldest_month, oldest_day)
                elif current_month < oldest_month:
                    # 「翌月」のボタンをクリック、次のページに移動
                    if self._has_class(nav_element, "month"):
                        # tmp_next_month_element = nav_element.find_element(By.CLASS_NAME, "month")
                        tmp_month_elements = self._find_elements(element=nav_element, is_driver=False, by="class", value="month")
                        tmp_next_month_element = tmp_month_elements[-1]
                        # next_month_element = tmp_next_month_element.find_element(By.TAG_NAME, "a")
                        next_month_element = self._find_element(element=tmp_next_month_element, is_driver=False, by="tag", value="a")
                        self._wait_click_element(next_month_element, "tag")
                        next_month_element.click()
                        self._open_next_page_until_oldest_date(oldest_year, oldest_month, oldest_day)

                elif current_month == oldest_month:
                    # 目的のページに到達した場合は、データ取得を開始する
                    self.continue_month_db(oldest_day)
                else:
                    pass
        else:
            # 「9月1日（日）」のような場合、レースデータが存在しない場合がある
            # この場合、ページにcurrentクラスが存在しない
            # そのため、前月のページに移動する
            if self._has_class(nav_element, "month"):
                # tmp_prev_month_element = nav_element.find_element(By.CLASS_NAME, "month")
                tmp_prev_month_element = self._find_element(element=nav_element, is_driver=False, by="class", value="month")
                # prev_month_element = tmp_prev_month_element.find_element(By.TAG_NAME, "a")
                prev_month_element = self._find_element(element=tmp_prev_month_element, is_driver=False, by="tag", value="a")
                self._wait_click_element(prev_month_element, "tag")
                prev_month_element.click()
                self._open_next_page_until_oldest_date(oldest_year, oldest_month, oldest_day)

    def get_past_db_from_any_date(self, date:str):
        # 任意の日付からスクレイピングを開始する
        # dateは「2024-04-06」のような形式で入力
        year, month, day = date.split("-")
        any_year = int(year)
        any_month = int(month)
        any_day = int(day)
        self.driver.get(self.homepage_url)
        element = self.driver.find_element(By.CSS_SELECTOR, "#quick_menu > div > ul > li:nth-of-type(4)")
        element.click()
        element = self.driver.find_element(By.CSS_SELECTOR, "#past_result > div.layout_grid.mt15 > div.cell.right > a")
        element.click()
        self._open_next_page_until_oldest_date(any_year, any_month, any_day)

    def continue_past_db(self):
        # スクレイピングの偶発的な中断時用の関数
        # データディレクトリ内の最も古い日付のデータから再開する
        self.driver.get(self.homepage_url)
        element = self.driver.find_element(By.CSS_SELECTOR, "#quick_menu > div > ul > li:nth-of-type(4)")
        element.click()
        element = self.driver.find_element(By.CSS_SELECTOR, "#past_result > div.layout_grid.mt15 > div.cell.right > a")
        element.click()
        oldest_year, oldest_month, oldest_day = self._get_target_date()
        self._open_next_page_until_oldest_date(oldest_year, oldest_month, oldest_day)

    def continue_month_db(self, oldest_day:int):
        prev_month_flag = False
        # self._wait_id_element("contents")
        # prev_month_element = self.driver.find_element(By.ID, "contents")
        prev_month_element = self._find_element(element=None, is_driver=True, by="id", value="contents")
        if self._has_class(prev_month_element, "month"):
            prev_month_flag = True
        else:
            pass
        print(f"prev_month_flag: {prev_month_flag}")

        # self._wait_class_element("link_list")
        # monthly_track_elements = self.driver.find_elements(By.CLASS_NAME, "link_list")
        # monthly_track_elements = self._find_elements(element=None, is_driver=True, by="class", value="link_list")
        # track_element_list = []
        # for monthly_track_element in monthly_track_elements:
        #     # daily_track_elements = monthly_track_element.find_elements(By.TAG_NAME, "a")
        #     daily_track_elements = self._find_elements(element=monthly_track_element, is_driver=False, by="tag", value="a")
        #     for daily_track_element in daily_track_elements:
        #         track_element_list.append(daily_track_element)
        # num_track = len(track_element_list)
        # print(f"track_num: {num_track}")

        self.continue_track_db(oldest_day)

        if prev_month_flag:
            # self._wait_id_element("contents")
            # element = self.driver.find_element(By.ID, "contents")
            element = self._find_element(element=None, is_driver=True, by="id", value="contents")
            # tmp_prev_month_element = element.find_element(By.CLASS_NAME, "month")
            tmp_prev_month_element = self._find_element(element=element, is_driver=False, by="class", value="month")
            # prev_month_element = tmp_prev_month_element.find_element(By.TAG_NAME, "a")
            prev_month_element = self._find_element(element=tmp_prev_month_element, is_driver=False, by="tag", value="a")
            self._wait_click_element(prev_month_element, "tag")
            prev_month_element.click()
            self.get_month_db()
        else:
            print("終了")
            self.driver.quit()

    def continue_track_db(self, oldest_day:int):
        # past_result_line_unit_elements = self.driver.find_elements(By.CLASS_NAME, "past_result_line_unit")
        past_result_line_unit_elements = self._find_elements(element=None, is_driver=True, by="class", value="past_result_line_unit")
        num_days = len(past_result_line_unit_elements)
        for n_day in range(num_days):
            # past_result_line_unit_elements = self.driver.find_elements(By.CLASS_NAME, "past_result_line_unit")
            past_result_line_unit_elements = self._find_elements(element=None, is_driver=True, by="class", value="past_result_line_unit")
            past_result_line_element = past_result_line_unit_elements[n_day]
            # head_element = past_result_line_element.find_element(By.CLASS_NAME, "head")
            head_element = self._find_element(element=past_result_line_element, is_driver=False, by="class", value="head")
            sub_header_element = self._find_element(element=head_element, is_driver=False, by="class", value="sub_header")
            sub_header = sub_header_element.text
            tmp_day = re.search(r"(\d+)日", sub_header).group(1)
            day = int(tmp_day)
            if day >= oldest_day:
                target_past_result_line_unit_element = past_result_line_element
                # link_list_element = target_past_result_line_unit_element.find_element(By.CLASS_NAME, "link_list")
                link_list_element = self._find_element(element=target_past_result_line_unit_element, is_driver=False, by="class", value="link_list")
                # div_elements = link_list_element.find_elements(By.TAG_NAME, "div")
                a_elements = self._find_elements(element=link_list_element, is_driver=False, by="tag", value="a")
                num_track = len(a_elements)
                for n_track in range(num_track):
                    print(f"n_track: {n_track + 1} / {num_track}")
                    # past_result_line_unit_elements = self.driver.find_elements(By.CLASS_NAME, "past_result_line_unit")
                    past_result_line_unit_elements = self._find_elements(element=None, is_driver=True, by="class", value="past_result_line_unit")
                    print(1)
                    past_result_line_unit_element = past_result_line_unit_elements[n_day]
                    target_past_result_line_unit_element = past_result_line_unit_element
                    # link_list_element = target_past_result_line_unit_element.find_element(By.CLASS_NAME, "link_list")
                    link_list_element = self._find_element(element=target_past_result_line_unit_element, is_driver=False, by="class", value="link_list")
                    print(2)
                    # div_elements = link_list_element.find_elements(By.TAG_NAME, "div")
                    a_elements = self._find_elements(element=link_list_element, is_driver=False, by="tag", value="a")
                    print(3)
                    a_element = a_elements[n_track]
                    # track_element = div_element.find_element(By.TAG_NAME, "a")
                    track_element = a_element
                    print(4)
                    self._wait_click_element(track_element, "tag")
                    track_element.click()
                    # self._wait_tag_element("tbody")
                    # tbody_element = self.driver.find_element(By.TAG_NAME, "tbody")
                    tbody_element = self._find_element(element=None, is_driver=True, by="tag", value="tbody")
                    print(5)
                    # tmp_race_elements = tbody_element.find_elements(By.CLASS_NAME, "race_num")
                    tmp_race_elements = self._find_elements(element=tbody_element, is_driver=False, by="class", value="race_num")
                    print(6)
                    num_race = len(tmp_race_elements)
                    self.get_race_db(num_race)
                oldest_day = day
            else:
                continue

    def get_past_db(self):
        self.driver.get(self.homepage_url)
        element = self.driver.find_element(By.CSS_SELECTOR, "#quick_menu > div > ul > li:nth-of-type(4)")
        element.click()
        element = self.driver.find_element(By.CSS_SELECTOR, "#past_result > div.layout_grid.mt15 > div.cell.right > a")
        element.click()
        self.get_month_db()

    def get_month_db(self):
        prev_month_flag = False
        # self._wait_id_element("contents")
        # prev_month_element = self.driver.find_element(By.ID, "contents")
        prev_month_element = self._find_element(element=None, is_driver=True, by="id", value="contents")
        if self._has_class(prev_month_element, "month"):
            prev_month_flag = True
        else:
            pass
        print(f"prev_month_flag: {prev_month_flag}")
        # self._wait_class_element("link_list")
        # monthly_track_elements = self.driver.find_elements(By.CLASS_NAME, "link_list")
        monthly_track_elements = self._find_elements(element=None, is_driver=True, by="class", value="link_list")
        track_element_list = []
        for monthly_track_element in monthly_track_elements:
            # daily_track_elements = monthly_track_element.find_elements(By.TAG_NAME, "a")
            daily_track_elements = self._find_elements(element=monthly_track_element, is_driver=False, by="tag", value="a")
            for daily_track_element in daily_track_elements:
                track_element_list.append(daily_track_element)
        num_track = len(track_element_list)
        print(f"track_num: {num_track}")

        self.get_track_db()

        if prev_month_flag:
            # self._wait_id_element("contents")
            # element = self.driver.find_element(By.ID, "contents")
            element = self._find_element(element=None, is_driver=True, by="id", value="contents")
            # tmp_prev_month_element = element.find_element(By.CLASS_NAME, "month")
            tmp_prev_month_element = self._find_element(element=element, is_driver=False, by="class", value="month")
            # prev_month_element = tmp_prev_month_element.find_element(By.TAG_NAME, "a")
            prev_month_element = self._find_element(element=tmp_prev_month_element, is_driver=False, by="tag", value="a")
            self._wait_click_element(prev_month_element, "tag")
            prev_month_element.click()
            self.get_month_db()
        else:
            print("終了")
            self.driver.quit()


    def get_track_db(self):
        # past_result_line_unit_elements = self.driver.find_elements(By.CLASS_NAME, "past_result_line_unit")
        past_result_line_unit_elements = self._find_elements(element=None, is_driver=True, by="class", value="past_result_line_unit")
        num_days = len(past_result_line_unit_elements)
        for n_day in range(num_days):
            # past_result_line_unit_elements = self.driver.find_elements(By.CLASS_NAME, "past_result_line_unit")
            past_result_line_unit_elements = self._find_elements(element=None, is_driver=True, by="class", value="past_result_line_unit")
            past_result_line_element = past_result_line_unit_elements[n_day]
            target_past_result_line_unit_element = past_result_line_element
            # link_list_element = target_past_result_line_unit_element.find_element(By.CLASS_NAME, "link_list")
            link_list_element = self._find_element(element=target_past_result_line_unit_element, is_driver=False, by="class", value="link_list")
            # div_elements = link_list_element.find_elements(By.TAG_NAME, "div")
            a_elements = self._find_elements(element=link_list_element, is_driver=False, by="tag", value="a")
            num_track = len(a_elements)
            for n_track in range(num_track):
                print(f"n_track: {n_track + 1} / {num_track}")
                # past_result_line_unit_elements = self.driver.find_elements(By.CLASS_NAME, "past_result_line_unit")
                past_result_line_unit_elements = self._find_elements(element=None, is_driver=True, by="class", value="past_result_line_unit")
                print(1)
                past_result_line_unit_element = past_result_line_unit_elements[n_day]
                target_past_result_line_unit_element = past_result_line_unit_element
                # link_list_element = target_past_result_line_unit_element.find_element(By.CLASS_NAME, "link_list")
                link_list_element = self._find_element(element=target_past_result_line_unit_element, is_driver=False, by="class", value="link_list")
                print(2)
                # div_elements = link_list_element.find_elements(By.TAG_NAME, "div")
                a_elements = self._find_elements(element=link_list_element, is_driver=False, by="tag", value="a")
                print(3)
                a_element = a_elements[n_track]
                # track_element = div_element.find_element(By.TAG_NAME, "a")
                track_element = a_element
                print(4)
                self._wait_click_element(track_element, "tag")
                track_element.click()
                # self._wait_tag_element("tbody")
                # tbody_element = self.driver.find_element(By.TAG_NAME, "tbody")
                tbody_element = self._find_element(element=None, is_driver=True, by="tag", value="tbody")
                print(5)
                # tmp_race_elements = tbody_element.find_elements(By.CLASS_NAME, "race_num")
                tmp_race_elements = self._find_elements(element=tbody_element, is_driver=False, by="class", value="race_num")
                print(6)
                num_race = len(tmp_race_elements)
                self.get_race_db(num_race)

    def get_race_db(self, num_race:int):
        for n in range(num_race):
            # self._wait_tag_element("tbody")
            # tmp_race_element = self.driver.find_element(By.TAG_NAME, "tbody")
            tmp_race_element = self._find_element(element=None, is_driver=True, by="tag", value="tbody")
            # tmp_race_elements = tmp_race_element.find_elements(By.CLASS_NAME, "race_num")
            tmp_race_elements = self._find_elements(element=tmp_race_element, is_driver=False, by="class", value="race_num")
            print(f"n: {n} tmp_race_elements: {len(tmp_race_elements)}")
            tmp_race_element = tmp_race_elements[n]
            race_element = tmp_race_element.find_element(By.TAG_NAME, "a")
            race_element = self._find_element(element=tmp_race_element, is_driver=False, by="tag", value="a")
            self._wait_click_element(race_element, "tag")
            race_element.click()
            #race_df = self.get_info()
            race_df = self.get_info()

        self.driver.back()

    def get_info(self):
        def _get_odds():
            # self._wait_class_element("narrow-xy")
            # tmp_table_element = self.driver.find_element(By.CLASS_NAME, "narrow-xy")
            tmp_tmp_table_element = self._find_element(element=None, is_driver=True, by="class", value="narrow-xy")
            # table_element = tmp_table_element.find_element(By.TAG_NAME, "tbody")
            tmp_table_element = self._find_element(element=tmp_tmp_table_element, is_driver=False, by="tag", value="tbody")
            odds_tan_elements = self._find_elements(element=tmp_table_element, is_driver=False, by="class", value="odds_tan")
            odds_tan_list = []
            for odds_tan_element in odds_tan_elements:
                tmp_odds_tan = odds_tan_element.text
                if self._is_numeric(tmp_odds_tan):
                    odds_tan = float(tmp_odds_tan)
                    odds_tan_list.append(odds_tan)
                else:
                    odds_tan_list.append(None)
            
            self.driver.back()

            return odds_tan_list

        print("Start get_info")
        # テーブルデータの取得
        self._wait_class_element("narrow-xy")
        # tmp_table_element = self.driver.find_element(By.CLASS_NAME, "narrow-xy")
        tmp_table_element = self._find_element(element=None, is_driver=True, by="class", value="narrow-xy")
        # table_element = tmp_table_element.find_element(By.TAG_NAME, "tbody")
        table_element = self._find_element(element=tmp_table_element, is_driver=False, by="tag", value="tbody")
        # 順位
        # rank_elements = table_element.find_elements(By.CLASS_NAME, "place")
        rank_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="place")
        rank_list = []
        for rank_element in rank_elements:
            if self._has_text(rank_element):
                rank = rank_element.text
                if self._is_numeric(rank):
                    rank = int(rank)
                    rank_list.append(rank)
                else:
                    # 中止や除外の場合はNoneとする
                    rank = None
                    rank_list.append(rank)
            else:
                rank = None
                rank_list.append(rank)
        num_horse = len(rank_list)
        print(f"rank_list: {rank_list} num_horse: {num_horse}")

        # 枠番
        # waku_elements = table_element.find_elements(By.CLASS_NAME, "waku")
        waku_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="waku")
        waku_list = []
        for tmp_waku_element in waku_elements:
            # 「<img src="/JRADB/img/waku/8.png" alt="枠8桃">」のような形式で格納
            # waku = int(tmp_waku_element.find_element(By.TAG_NAME, "img").get_attribute("alt")[1])
            waku_element = self._find_element(element=tmp_waku_element, is_driver=False, by="tag", value="img")
            if self._has_alt(waku_element):
                waku = int(waku_element.get_attribute("alt")[1])
            else:
                waku = None
            waku_list.append(waku)
        print(f"waku_list: {waku_list}") 

        # 馬番
        # horse_number_elements = table_element.find_elements(By.CLASS_NAME, "num")
        horse_number_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="num")
        horse_number_list = []
        for horse_number_element in horse_number_elements:
            if self._has_text(horse_number_element):
                if self._is_numeric(horse_number_element.text):
                    horse_number = int(horse_number_element.text)
                else:
                    horse_number = None
            else:
                horse_number = None
            horse_number_list.append(horse_number)
        print(f"horse_number_list: {horse_number_list}")

        # 馬名
        # tmp_horse_name_elements = table_element.find_elements(By.CLASS_NAME, "horse")
        tmp_horse_name_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="horse")
        horse_name_list = []
        for tmp_horse_name_element in tmp_horse_name_elements:
            if tmp_horse_name_element.tag_name == "div":
                continue
            else:
                # horse_element = tmp_horse_name_element.find_element(By.TAG_NAME, "a")
                horse_element = self._find_element(element=tmp_horse_name_element, is_driver=False, by="tag", value="a")
                if self._has_text(horse_element):
                    horse_name = horse_element.text
                else:
                    horse_name = None
            horse_name_list.append(horse_name)
        print(f"horse_name_list: {horse_name_list}")

        # ブリンカー
        # tmp_horse_blinker_elements = table_element.find_elements(By.CLASS_NAME, "horse")
        tmp_horse_blinker_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="horse")
        horse_blinker_list = []
        for tmp_horse_blinker_element in tmp_horse_blinker_elements:
            if tmp_horse_blinker_element.tag_name == "div":
                if self._has_class(tmp_horse_blinker_element, "blinker"):
                    horse_blinker_list[-1] = 1
                else:
                    pass
            else:
                horse_blinker_list.append(0)
        print(f"horse_blinker_list: {horse_blinker_list}")

        # アイコン
        # tmp_horse_icon_elements = table_element.find_elements(By.CLASS_NAME, "horse")
        tmp_horse_icon_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="horse")
        horse_icon_list = []
        for tmp_horse_icon_element in tmp_horse_icon_elements:
            if tmp_horse_icon_element.tag_name == "div":
                continue
            else:
                if self._has_class(tmp_horse_icon_element, "horse_icon"):
                    # tmp_horse_icon_element = tmp_horse_icon_element.find_element(By.CLASS_NAME, "horse_icon")
                    tmp_horse_icon_element = self._find_element(element=tmp_horse_icon_element, is_driver=False, by="class", value="horse_icon")
                    # horse_icon = tmp_horse_icon_element.find_element(By.TAG_NAME, "img").get_attribute("alt")
                    horse_icom_element = self._find_element(element=tmp_horse_icon_element, is_driver=False, by="tag", value="img")
                    if self._has_alt(horse_icom_element):
                        horse_icon = horse_icom_element.get_attribute("alt")
                    else:
                        horse_icon = None
                else:
                    horse_icon = None

            horse_icon_list.append(horse_icon)

        print(f"horse_icon_list: {horse_icon_list}")

        # 性齢
        # 「牡3」のような形式
        # 性別と年齢を分解
        # sex_age_elements = table_element.find_elements(By.CLASS_NAME, "age")
        sex_age_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="age")
        sex_list = []
        age_list = []
        for sex_age_element in sex_age_elements:
            if self._has_text(sex_age_element):
                sex = re.search(r"(.+)\d+", sex_age_element.text).group(1)
                age = int(re.search(r"\d+", sex_age_element.text).group(0))
            else:
                sex = None
                age = None
            sex_list.append(sex)
            age_list.append(age)
        print(f"sex_list: {sex_list}")
        print(f"age_list: {age_list}")

        # 負担重量（斥量）
        # weight_elements = table_element.find_elements(By.CLASS_NAME, "weight")
        weight_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="weight")
        weight_list = []
        for weight_element in weight_elements:
            if self._has_text(weight_element):
                if self._is_numeric(weight_element.text):
                    weight = float(weight_element.text)
                else:
                    weight = None
            else:
                weight = None
            weight_list.append(weight)
        print(f"weight_list: {weight_list}")

        # 騎手名
        # 注意：「★大江原 比呂」のように★がついている場合がある
        # 騎手マーク
        # 「<span title="3kg減量" class="mark jockey">▲</span>」のようにマークがついている場合がある
        # 「jockey_name_list: ['坂井 瑠星', '★大江原 比呂', '★', '★河原田 菜々', '★']」のような形式で保存される
        # jockey_name_elements = table_element.find_elements(By.CLASS_NAME, "jockey")
        jockey_name_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="jockey")
        remove_index_list = []
        get_index_list = []
        jockey_name_list = []
        jockey_mark_list = []
        for idx, tmp_jockey_name_element in enumerate(jockey_name_elements):
            jockey_name = tmp_jockey_name_element.text
            name_length = len(jockey_name)
            jockey_name_list.append(jockey_name)
            if name_length == 1:
                remove_index_list.append(idx)
            else:
                get_index_list.append(idx)

        tmp1_jockey_name_list = [jockey_name_list[idx] for idx in get_index_list]

        for remove_index in remove_index_list:
            remove_mark = jockey_name_list[remove_index]
            jockey_name_list[remove_index - 1] = jockey_name_list[remove_index - 1].replace(remove_mark, "")

        jockey_name_list = [jockey_name_list[idx] for idx in get_index_list]

        tmp2_jockey_name_list = []
        for jockey_name in jockey_name_list:
            name_length = len(jockey_name)
            if not name_length == 1:
                tmp2_jockey_name_list.append(jockey_name)
        jockey_name_list = tmp2_jockey_name_list

        for jockey_name, marked_jockey_name in zip(jockey_name_list, tmp1_jockey_name_list):
            if jockey_name == marked_jockey_name:
                jockey_mark_list.append(None)
            else:
                mark = marked_jockey_name[0]
                jockey_mark_list.append(mark)
            
        print(f"jockey_name_list: {jockey_name_list}")
        print(f"jockey_mark_list: {jockey_mark_list}")

        # タイム
        # 「1:10.5」（minutes:seconds.milicseconds）の形式
        time_elements = table_element.find_elements(By.CLASS_NAME, "time")
        time_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="time")
        # TODO: find_elementの修正続き
        time_list = []
        for time_element in time_elements:
            if self._has_text(time_element):
                tmp_time = time_element.text
                if not tmp_time == "":
                    minutes = int(tmp_time.split(":")[0])
                    seconds = int(tmp_time.split(":")[1].split(".")[0])
                    miliseconds = int(tmp_time.split(":")[1].split(".")[1])
                    total_seconds = minutes * 60 + seconds + miliseconds * 0.1
                    time_ = total_seconds
                else:
                    # タイムが空欄の場合はNoneとする
                    time_ = None
            else:
                # タイムが空欄の場合はNoneとする
                time_ = None
            time_list.append(time_)

        print(f"time_list: {time_list}")

        # 着差
        # margin_elements = table_element.find_elements(By.CLASS_NAME, "margin")
        margin_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="margin")
        margin_list = []
        for margin_element in margin_elements:
            if self._has_class(margin_element, "record"):
                # record_element = margin_element.find_element(By.CLASS_NAME, "record")
                record_element = self._find_element(element=margin_element, is_driver=False, by="class", value="record")
                if self._has_text(record_element):
                    record = record_element.text
                    margin = record
                else:
                    margin = None
            else:
                margin = margin_element.text
                if not margin == "":
                    pass
                else:
                    margin = None
            margin_list.append(margin)
        # 1着は着差がほとんど存在しない
        # 注意：レコード記録の場合は「レコード」と記載される
        print(f"margin_list: {margin_list}")

        # 推定上がり
        # 「34.5」のような形式
        # 注意：テーブルによっては「推定あがり」と「平均1F」のように指標が異なる場合がある
        # f_time_elements = table_element.find_elements(By.CLASS_NAME, "f_time")
        f_time_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="f_time")
        f_time_list = []
        for f_time_element in f_time_elements:
            if self._has_text(f_time_element):
                tmp_f_time = f_time_element.text
                if not tmp_f_time == "":
                    seconds = int(tmp_f_time.split(".")[0])
                    miliseconds = int(tmp_f_time.split(".")[1])
                    f_time = seconds + miliseconds * 0.1
                else:
                    # 推定上がりが空欄の場合はNoneとする
                    f_time = None
            else:
                # 推定上がりが空欄の場合はNoneとする
                f_time = None
            f_time_list.append(f_time)
        print(f"f_time_list: {f_time_list}")

        # 馬体重
        # 「466(-8)」のような形式
        # ただしh_weightクラスに「468」、直下のspanタグに「-8」のような構造
        # 注意：「508(初出走)」のように初出走の場合、前回差がない
        # 体重と前回比を分解
        # weight_elements = table_element.find_elements(By.CLASS_NAME, "h_weight")
        weight_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="h_weight")
        current_weight_list = []
        previous_weight_diff_list = []
        weight_diff_list = []
        is_first_list = []
        is_first = 0
        for weight_element in weight_elements:
            if self._has_tag(weight_element, "span"):
                # weight_diff_element = weight_element.find_element(By.TAG_NAME, "span")
                weight_diff_element = self._find_element(element=weight_element, is_driver=False, by="tag", value="span")
                tmp_weight_diff = weight_diff_element.text
                tmp_current_weight = weight_element.text
                tmp_current_weight = tmp_current_weight.replace(tmp_weight_diff, "")
                if not self._is_numeric(tmp_current_weight):
                    current_weight = None
                else:
                    current_weight = int(tmp_current_weight)
                tmp_weight_diff = tmp_weight_diff.replace("(", "").replace(")", "")
                if not self._is_numeric(tmp_weight_diff):
                    weight_diff = None
                    previous_weight = None
                    if "初出走" in tmp_weight_diff:
                        is_first = 1
                    else:
                        is_first = 0
                else:
                    weight_diff = int(tmp_weight_diff)
                    previous_weight = current_weight + weight_diff
                current_weight_list.append(current_weight)
                previous_weight_diff_list.append(weight_diff)
                weight_diff_list.append(previous_weight)
                is_first_list.append(is_first)
            else:
                current_weight_list.append(None)
                previous_weight_diff_list.append(None)
                weight_diff_list.append(None)
                is_first_list.append(None)
        print(f"current_weight_list: {current_weight_list}")
        print(f"previous_weight_diff_list: {previous_weight_diff_list}")
        print(f"weight_diff_list: {weight_diff_list}")
        print(f"is_first_list: {is_first_list}")

        # 調教師名
        # trainer_name_elements = table_element.find_elements(By.CLASS_NAME, "trainer")
        trainer_name_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="trainer")
        trainer_name_list = []
        for trainer_name_element in trainer_name_elements:
            if self._has_tag(trainer_name_element, "a"):
                # trainer_name = trainer_name_element.find_element(By.TAG_NAME, "a").text
                tmp_trainer_name_element = self._find_element(element=trainer_name_element, is_driver=False, by="tag", value="a")
                trainer_name = tmp_trainer_name_element.text
            else:
                trainer_name = trainer_name_element.text
            trainer_name_list.append(trainer_name)
        print(f"trainer_name_list: {trainer_name_list}")

        # 人気
        # pop_elements = table_element.find_elements(By.CLASS_NAME, "pop")
        pop_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="pop")
        pop_list = []
        for pop_element in pop_elements:
            tmp_pop = pop_element.text
            if not self._is_numeric(tmp_pop):
                pop = None
            else:
                pop = int(pop_element.text)
            pop_list.append(pop)
        print(f"pop_list: {pop_list}")

        # レース情報の取得
        # self._wait_class_element("race_header")
        # header_element = self.driver.find_element(By.CLASS_NAME, "race_header")
        header_element = self._find_element(element=None, is_driver=True, by="class", value="race_header")

        # 日時
        # 「2024年8月3日（土曜） 2回新潟3日」のような形式
        # date_track_info = header_element.find_element(By.CLASS_NAME, "date").text
        date_track_element = self._find_element(element=header_element, is_driver=False, by="class", value="date")
        date_track_info = date_track_element.text
        date_info = date_track_info.split(" ")[0]
        tmp_year = re.search(r"(\d+)年", date_info).group(1)
        tmp_month = re.search(r"(\d+)月", date_info).group(1)
        tmp_day = re.search(r"(\d+)日", date_info).group(1)
        year = int(tmp_year)
        month = int(tmp_month)
        day = int(tmp_day)
        #datetime形式に変換
        date = datetime.datetime(year=year, month=month, day=day)
        date_list = [date] * num_horse
        print(f"date_list: {date_list}")

        #曜日
        dow = re.search(r"（(.+)）", date_info).group(1)
        dow_list = [dow] * num_horse
        print(f"dow_list: {dow_list}")

        # 会場
        # 「2回新潟3日」のような形式
        # 「回」の後に続き、「3」のような数字の前までが会場名
        track_info = date_track_info.split(" ")[1]
        track = re.search(r"回(.+)\d+日", track_info).group(1)
        track_list = [track] * num_horse
        print(f"track_list: {track_list}")
        # 何日目の開催か
        num_day = int(re.search(r"(\d+)日", track_info).group(1))
        num_day_list = [num_day] * num_horse
        print(f"num_day_list: {num_day_list}")

        # 何回目の開催か
        num_round = int(re.search(r"(\d+)回", track_info).group(1))
        num_round_list = [num_round] * num_horse
        print(f"num_round_list: {num_round_list}")

        # 発走時刻
        # 「発走時刻：9時35分」のような形式
        # start_time = header_element.find_element(By.CLASS_NAME, "time").text
        start_time_element = self._find_element(element=header_element, is_driver=False, by="class", value="time")
        start_time = start_time_element.text
        start_time = re.search(r"：(.+)", start_time).group(1)
        tmp_hour = re.search(r"(\d+)時", start_time).group(1)
        tmp_minute = re.search(r"(\d+)分", start_time).group(1)
        hour = int(tmp_hour)
        minute = int(tmp_minute)
        print(f"hour: {hour} minute: {minute}")
        # 発走時刻をdatetime形式に変換
        start_time = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
        start_time_list = [start_time] * num_horse
        print(f"start_time_list: {start_time_list}")

        # レース名
        # tmp_race_name_element = header_element.find_element(By.CLASS_NAME, "main")
        tmp_race_name_element = self._find_element(element=header_element, is_driver=False, by="class", value="main")
        # race_name_element = tmp_race_name_element.find_element(By.CLASS_NAME, "race_name")
        race_name_element = self._find_element(element=tmp_race_name_element, is_driver=False, by="class", value="race_name")
        race_name = race_name_element.text
        race_name_list = [race_name] * num_horse

        # レースの開催回数
        # 「第60回 札幌記念」のように周期的に開催されるレースの場合
        if self._has_class(tmp_race_name_element, "cap"):
            # cap_element = tmp_race_name_element.find_element(By.CLASS_NAME, "cap")
            cap_element = self._find_element(element=tmp_race_name_element, is_driver=False, by="class", value="cap")
            if self._has_class(cap_element, "num"):
                # num_element = cap_element.find_element(By.CLASS_NAME, "num")
                num_element = self._find_element(element=cap_element, is_driver=False, by="class", value="num")
                num = num_element.text
            else:
                num = None
        else:
            num = None

        num_race_list = [num] * num_horse # 各DBとの結合のため、int型に変換しない
        
        # グレード
        # 「G1」のような形式
        if self._has_class(race_name_element, "grade_icon"):
            # grade_element = race_name_element.find_element(By.CLASS_NAME, "grade_icon")
            tmp_grade_element = self._find_element(element=race_name_element, is_driver=False, by="class", value="grade_icon")
            if self._has_tag(tmp_grade_element, "img"):
                # grade = tmp_grade_element.find_element(By.TAG_NAME, "img").get_attribute("alt")
                grade_element = self._find_element(element=tmp_grade_element, is_driver=False, by="tag", value="img")
                grade = grade_element.get_attribute("alt")
            else:
                grade = None
        else:
            grade = None

        grade_list = [grade] * num_horse
        
        print(f"race_name_list: {race_name_list}")
        print(f"num_race_list: {num_race_list}")
        print(f"grade_list: {grade_list}")

        # コース長
        # course_element = header_element.find_element(By.CLASS_NAME, "course")
        course_element = self._find_element(element=header_element, is_driver=False, by="class", value="course")
        tmp_course_length = course_element.text
        print(f"tmp_course_length: {tmp_course_length}")
        tmp_course_length = re.search(r"：(.+)メートル", tmp_course_length).group(1)
        tmp_course_length = tmp_course_length.replace(",", "")
        course_length = int(tmp_course_length)
        course_length_list = [course_length] * num_horse
        print(f"course_length_list: {course_length_list}")

        # ターフの種類
        # 「（芝・左 外）」または「（ダート・左）」のような形式
        # 注意：「（芝 外内）」のような場合もある
        # 注意：「（芝）」のような場合もある
        # 注意：「（芝→ダート）」のような場合もある
        # course_detail_info = course_element.find_element(By.CLASS_NAME, "detail").text
        course_detail_element = self._find_element(element=course_element, is_driver=False, by="class", value="detail")
        course_detail_info = course_detail_element.text
        # 例：「（芝・左 外）」の場合
        if "・" in course_detail_info and " " in course_detail_info:
            ground = course_detail_info.split("・")[0][1:]
            ground_list = [ground] * num_horse
            # コースの方向
            direction_info = course_detail_info.split("・")[1]
            direction = direction_info.split(" ")[0]
            direction_list = [direction] * num_horse
            # 内外
            change_info = direction_info.split(" ")[1]
            in_out = change_info[:-1]
            in_out_list = [in_out] * num_horse

        # 例：「（ダート・左）」の場合
        elif "・" in course_detail_info and not " " in course_detail_info:
            ground = course_detail_info.split("・")[0][1:]
            ground_list = [ground] * num_horse
            direction = course_detail_info.split("・")[1][:-1]
            direction_list = [direction] * num_horse
            in_out_list = [None] * num_horse

        # 「（芝 外内）」の場合
        elif "・" not in course_detail_info and " " in course_detail_info:
            ground = course_detail_info.split(" ")[0][1:]
            ground_list = [ground] * num_horse
            direction_info = course_detail_info.split(" ")[1][:-1]
            direction = None
            direction_list = [direction] * num_horse
            change_info = direction_info[:-1]
            in_out = change_info
            in_out_list = [in_out] * num_horse

        # 例：「（芝）」の場合
        elif "・" not in course_detail_info and not " " in course_detail_info:
            if "→" in course_detail_info:
                ground1 = course_detail_info.split("→")[0][1:]
                ground2 = course_detail_info.split("→")[1][:-1]
                ground = ground1 + ground2
                ground_list = [ground] * num_horse
                direction = None
                direction_list = [direction] * num_horse
                in_out = None
                in_out_list = [in_out] * num_horse
            else:
                ground = course_detail_info[1:-1]
                ground_list = [ground] * num_horse
                direction = None
                direction_list = [direction] * num_horse
                in_out = None
                in_out_list = [in_out] * num_horse


        print(f"ground_list: {ground_list}")
        print(f"direction_list: {direction_list}")
        print(f"in_out_list: {in_out_list}")

        # 通過
        if not direction == "直":
            # corner_elements = table_element.find_elements(By.CLASS_NAME, "corner_list")
            corner_elements = self._find_elements(element=table_element, is_driver=False, by="class", value="corner_list")
            corner_list = []
            for corner_element in corner_elements:
                corner_list_per_horse = []
                # corner_elements_per_horse = corner_element.find_elements(By.TAG_NAME, "li")
                corner_elements_per_horse = self._find_elements(element=corner_element, is_driver=False, by="tag", value="li")
                for corner_element_per_horse in corner_elements_per_horse:
                    corner = corner_element_per_horse.text
                    if self._is_numeric(corner):
                        corner_list_per_horse.append(corner)
                    else:
                        corner_list_per_horse = None
                        break
                corner_list.append(corner_list_per_horse)
        else:
            corner_list = [None] * num_horse
        print(f"corner_list: {corner_list}")

        # 馬場状態
        # baba_element = header_element.find_element(By.CLASS_NAME, "baba")
        baba_element = self._find_element(element=header_element, is_driver=False, by="class", value="baba")
        # 天候
        # weather_element = baba_element.find_element(By.CLASS_NAME, "weather")
        tmp_weather_element = self._find_element(element=baba_element, is_driver=False, by="class", value="weather")
        weather_element = self._find_element(element=tmp_weather_element, is_driver=False, by="class", value="txt")
        # weather = weather_element.find_element(By.CLASS_NAME, "txt").text
        weather = weather_element.text
        weather_list = [weather] * num_horse
        print(f"weather_list: {weather_list}")

        # ターフ
        if ground == "芝":
            # ground_status_element = baba_element.find_element(By.CLASS_NAME, "turf")
            ground_status_element = self._find_element(element=baba_element, is_driver=False, by="class", value="turf")
            turf_element = self._find_element(element=ground_status_element, is_driver=False, by="class", value="txt")
            turf = turf_element.text
            # turf = ground_status_element.find_element(By.CLASS_NAME, "txt").text
            ground_status_list = [turf] * num_horse
            print(f"turf_list: {ground_status_list}")
        elif ground == "ダート":
            # ground_status_element = baba_element.find_element(By.CLASS_NAME, "durt")
            ground_status_element = self._find_element(element=baba_element, is_driver=False, by="class", value="durt")
            # durt = ground_status_element.find_element(By.CLASS_NAME, "txt").text
            durt_element = self._find_element(element=ground_status_element, is_driver=False, by="class", value="txt")
            durt = durt_element.text
            ground_status_list = [durt] * num_horse
            print(f"ground_status_list: {ground_status_list}")
        elif ground == "芝ダート":
            # ground_status_element = baba_element.find_element(By.CLASS_NAME, "turf")
            ground_status_element = self._find_element(element=baba_element, is_driver=False, by="class", value="turf")
            # turf = ground_status_element.find_element(By.CLASS_NAME, "txt").text
            turf_element = self._find_element(element=ground_status_element, is_driver=False, by="class", value="txt")
            turf = turf_element.text
            # ground_status_element = baba_element.find_element(By.CLASS_NAME, "durt")
            ground_status_element = self._find_element(element=baba_element, is_driver=False, by="class", value="durt")
            durt_element = self._find_element(element=ground_status_element, is_driver=False, by="class", value="txt")
            # durt = ground_status_element.find_element(By.CLASS_NAME, "txt").text
            durt = durt_element.text
            ground = turf + durt
            ground_status_list = [ground] * num_horse
        elif ground == "ダート芝":
            # ground_status_element = baba_element.find_element(By.CLASS_NAME, "turf")
            ground_status_element = self._find_element(element=baba_element, is_driver=False, by="class", value="turf")
            # turf = ground_status_element.find_element(By.CLASS_NAME, "txt").text
            turf_element = self._find_element(element=ground_status_element, is_driver=False, by="class", value="txt")
            turf = turf_element.text
            # ground_status_element = baba_element.find_element(By.CLASS_NAME, "durt")
            ground_status_element = self._find_element(element=baba_element, is_driver=False, by="class", value="durt")
            durt_element = self._find_element(element=ground_status_element, is_driver=False, by="class", value="txt")
            # durt = ground_status_element.find_element(By.CLASS_NAME, "txt").text
            durt = durt_element.text
            ground = durt + turf
            ground_status_list = [ground] * num_horse

        print(f"ground_status_list: {ground_status_list}")

        # 賞金
        # 「1着　800　2着　320	3着　200　4着　120	5着　80」のような形式
        # 注意：賞金が与えられる順位はレースによって異なる（基本的には5着まで）
        # tmp_prize_element = header_element.find_element(By.CLASS_NAME, "prize_unit")
        tmp_prize_element = self._find_element(element=header_element, is_driver=False, by="class", value="prize_unit")
        # prize_elements = tmp_prize_element.find_elements(By.CLASS_NAME, "num")
        prize_elements = self._find_elements(element=tmp_prize_element, is_driver=False, by="class", value="num")
        prize_list = []
        for prize_element in prize_elements:
            tmp_prize = prize_element.text.replace(",", "")
            prize = int(tmp_prize)
            prize_list.append(prize)
        for _ in range(num_horse - len(prize_list)):
            prize_list.append(0)
        print(f"prize_list: {prize_list}")

        # 単勝オッズ
        # レース結果ページの直下にあるリンクから取得
        # tmp_race_releted_element = header_element.find_element(By.CLASS_NAME, "race_related_link")
        tmp_race_related_element = self._find_element(element=header_element, is_driver=False, by="class", value="race_related_link")
        # race_related_elements = tmp_race_related_element.find_elements(By.TAG_NAME, "a")
        race_related_elements = self._find_elements(element=tmp_race_related_element, is_driver=False, by="tag", value="a")
        check_word = "オッズ"
        for race_related_element in race_related_elements:
            text = race_related_element.text
            if check_word in text:
                self._wait_click_element(race_related_element, "tag")
                race_related_element.click()
                odds_tan_list = _get_odds()
                break
            else:
                continue

        print(f"all list length")
        print(f"rank_list: {len(rank_list)}")
        print(f"waku_list: {len(waku_list)}")
        print(f"horse_number_list: {len(horse_number_list)}")
        print(f"horse_name_list: {len(horse_name_list)}")
        print(f"horse_blinker_list: {len(horse_blinker_list)}")
        print(f"horse_icon_list: {len(horse_icon_list)}")
        print(f"sex_list: {len(sex_list)}")
        print(f"age_list: {len(age_list)}")
        print(f"weight_list: {len(weight_list)}")
        print(f"jockey_name_list: {len(jockey_name_list)}")
        print(f"jockey_mark_list: {len(jockey_mark_list)}")
        print(f"time_list: {len(time_list)}")
        print(f"margin_list: {len(margin_list)}")
        print(f"corner_list: {len(corner_list)}")
        print(f"f_time_list: {len(f_time_list)}")
        print(f"current_weight_list: {len(current_weight_list)}")
        print(f"previous_weight_diff_list: {len(previous_weight_diff_list)}")
        print(f"weight_diff_list: {len(weight_diff_list)}")
        print(f"trainer_name_list: {len(trainer_name_list)}")
        print(f"pop_list: {len(pop_list)}")
        print(f"odds_tan_list: {len(odds_tan_list)}")
        print(f"date_list: {len(date_list)}")
        print(f"dow_list: {len(dow_list)}")
        print(f"track_list: {len(track_list)}")
        print(f"num_day_list: {len(num_day_list)}")
        print(f"num_round_list: {len(num_round_list)}")
        print(f"start_time_list: {len(start_time_list)}")
        print(f"weather_list: {len(weather_list)}")
        print(f"ground_status_list: {len(ground_status_list)}")
        print(f"race_name_list: {len(race_name_list)}")
        print(f"num_race_list: {len(num_race_list)}")
        print(f"grade_list: {len(grade_list)}")
        print(f"course_length_list: {len(course_length_list)}")
        print(f"ground_list: {len(ground_list)}")
        print(f"direction_list: {len(direction_list)}")
        print(f"in_out_list: {len(in_out_list)}")
        print(f"prize_list: {len(prize_list)}")
        print(f"odds_tan_list: {len(odds_tan_list)}")

        # データフレームに格納
        race_df = pd.DataFrame({
            "順位": rank_list,
            "枠番": waku_list,
            "馬番": horse_number_list,
            "馬名": horse_name_list,
            "ブリンカー": horse_blinker_list,
            "アイコン": horse_icon_list,
            "性別": sex_list,
            "年齢": age_list,
            "負担重量": weight_list,
            "騎手名": jockey_name_list,
            "騎手マーク": jockey_mark_list,
            "タイム": time_list,
            "着差": margin_list,
            "通過": corner_list,
            "推定上がり": f_time_list,
            "今馬体重": current_weight_list,
            "前馬体重": previous_weight_diff_list,
            "馬体重差": weight_diff_list,
            "初出走": is_first_list,
            "調教師名": trainer_name_list,
            "人気": pop_list,
            "単勝オッズ": odds_tan_list,
            "日付": date_list,
            "曜日": dow_list,
            "会場": track_list,
            "日目": num_day_list,
            "回目": num_round_list,
            "発走時刻": start_time_list,
            "天候状態": weather_list,
            "グラウンド状態": ground_status_list,
            "レース名": race_name_list,
            "コース長": course_length_list,
            "グラウンド種類": ground_list,
            "コース方向": direction_list,
            "内外": in_out_list,
            "賞金": prize_list
        })

        # ファイル名の構成
        # 例：「2024_08_03_15_30_2歳未勝利.csv」のような形式で保存
        # 「西暦_月_日_時_分_レース名.csv」

        year = str(year).zfill(4)
        month = str(month).zfill(2)
        day = str(day).zfill(2)
        hour = str(hour).zfill(2)
        minute = str(minute).zfill(2)

        file_name = f"{year}_{month}_{day}_{dow}_{hour}_{minute}_{num_round}回{track}{num_day}日_{race_name}.csv"

        # フォルダの構成
        # 「jra_race_data/西暦/月/日/」のような形式で保存

        year_dir = os.path.join(self.save_dir, year)
        if not os.path.exists(year_dir):
            os.makedirs(year_dir)

        month_dir = os.path.join(year_dir, month)
        if not os.path.exists(month_dir):
            os.makedirs(month_dir)

        day_dir = os.path.join(month_dir, day)
        if not os.path.exists(day_dir):
            os.makedirs(day_dir)
        

        file_path = os.path.join(day_dir, file_name)
        race_df.to_csv(file_path, index=False)
        print(f"Saved: {file_path}")
        print("*" * 50)
        self.driver.back()

        return race_df



def main():
    #任意の日付からデータを取得したい場合は、引数に日付を入力
    # 例：python jra_race.py 2024-08-03 

    homepage_url = "https://www.jra.go.jp/"
    race_db = RaceDB(homepage_url)

    parser = argparse.ArgumentParser()
    parser.add_argument("arg1", help="Please input the number of date such as '2024-08-03'.")
    args = parser.parse_args()

    if args.arg1:
        any_date = args.arg1
        race_db.get_past_db_from_any_date(any_date)
    else:
        if  not race_db.check_saved_data():
            print("There is no new data.")
            race_db.get_past_db()
        else:
            print("There is continued data.")
            race_db.continue_past_db()

if __name__ == '__main__':
    main()
