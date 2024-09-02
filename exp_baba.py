import pypdfium2 as pdf
from glob import glob
import pandas as pd
import os
import datetime
import json
import argparse
import time
import numpy as np
import re
from glob import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BabaDB:
    def __init__(self, homepage_url:str):
        self.homepage_url = homepage_url
        self.driver = None
        self.first_month_flag = True
        self.save_baba_dir = "baba_data"
        self.continue_year = None
        self.continue_track_name = None
        self.continue_num_time = None
        self.continue_flag = False
        self.mkdir()
        self.init_driver()


    def init_driver(self):
        save_pdf_abs_dir = os.path.abspath(self.save_pdf_dir)
        print(f"save_pdf_abs_dir: {save_pdf_abs_dir}")
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            "download.default_directory": save_pdf_abs_dir,
            "plugins.always_open_pdf_externally": True
        })
        options.add_argument('--kiosk-printing')
        #options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def mkdir(self):
        if not os.path.exists(self.save_baba_dir):
            os.mkdir(self.save_baba_dir)
        
        self.save_csv_dir = f"{self.save_baba_dir}/csv"
        if not os.path.exists(self.save_csv_dir):
            os.mkdir(self.save_csv_dir)

        self.save_pdf_dir = f"{self.save_baba_dir}/pdf"
        if not os.path.exists(self.save_pdf_dir):
            os.mkdir(self.save_pdf_dir)

    def _wait_random_seconds(self, min_range=0, max_range=0.1):
        original_time = 1
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
            pass
    
    def _wait_id_element(self, id_name:str):
        try:
            wait = WebDriverWait(self.driver, self.wait_time)
            wait.until(EC.presence_of_element_located((By.ID, id_name)))
        except:
            pass
            

    def _wait_tag_element(self, tag_name:str):
        try:
            wait = WebDriverWait(self.driver, self.wait_time)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, tag_name)))
        except:
            pass

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
            pass

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
                pass

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
            pass

    def get_pdf(self):
        # 馬場情報が記載されたページに遷移
        self.driver.get(self.homepage_url)
        footer_element = self._find_element(self.driver, True, "id", "footer")
        contents_block_element = self._find_element(footer_element, False, "class", "contents_block")
        grid_element = self._find_element(contents_block_element, False, "class", "grid")
        cell_elements = self._find_elements(grid_element, False, "class", "cell")
        # cell_elementsの最後に馬場情報が記載されたページへのリンクがある
        baba_element = cell_elements[-1]
        ul_element = self._find_element(baba_element, False, "tag", "ul")
        li_elements = self._find_elements(ul_element, False, "tag", "li")
        # li_elementsの最初に馬場情報が記載されたページへのリンクがある
        baba_link_element = li_elements[0]
        a_element = self._find_element(baba_link_element, False, "tag", "a")
        self._wait_click_element(a_element, "tag")
        a_element.click()
        self.open_baba_page()
    
    def open_baba_page(self):
        # 馬場情報が記載されたページに遷移
        search_unit_word = "今週の開催情報"
        search_list_word = "馬場情報"
        contents_body_element = self._find_element(None, True, "id", "contentsBody")
        category_kaiba_element = self._find_element(contents_body_element, False, "id", "category_keiba")
        panel_element = self._find_element(category_kaiba_element, False, "class", "panel")
        content_element = self._find_element(panel_element, False, "class", "content")
        category_unit_elements = self._find_elements(content_element, False, "class", "category_unit")
        for category_unit_element in category_unit_elements:
            lv6_element = self._find_element(category_unit_element, False, "class", "lv6")
            if self._has_text(lv6_element):
                target_unit_text = lv6_element.text
                if target_unit_text == search_unit_word:
                    link_list_element = self._find_element(category_unit_element, False, "class", "link_list")
                    div_elements = self._find_elements(link_list_element, False, "tag", "div")
                    for div_element in div_elements:
                        inner_element = self._find_element(div_element, False, "class", "inner")
                        txt_element = self._find_element(inner_element, False, "class", "txt")
                        if self._has_text(txt_element):
                            target_list_text = txt_element.text
                            if target_list_text == search_list_word:
                                a_element = self._find_element(div_element, False, "tag", "a")
                                self._wait_click_element(a_element, "tag")
                                a_element.click()
                                self.open_past_baba_page()
                                break
                            else:
                                continue
                        else:
                            continue
                else:
                    continue
            else:
                continue

    def open_past_baba_page(self):
        # 過去の馬場情報が記載されたページに遷移
        search_word = "過去の含水率・クッション値"
        contents_body_element = self._find_element(None, True, "id", "contentsBody")
        if self._has_id(contents_body_element, "related_link"):
            related_link_element = self._find_element(contents_body_element, False, "id", "related_link")
            if self._has_class(related_link_element, "content"):
                content_element = self._find_element(related_link_element, False, "class", "content")
                if self._has_class(content_element, "link_list"):
                    link_list_element = self._find_element(content_element, False, "class", "link_list")
                    div_elements = self._find_elements(link_list_element, False, "tag", "div")
                    for div_element in div_elements:
                        if self._has_tag(div_element, "a"):
                            a_element = self._find_element(div_element, False, "tag", "a")
                            if self._has_text(a_element):
                                target_text = a_element.text
                                if target_text == search_word:
                                    self._wait_click_element(a_element, "tag")
                                    a_element.click()
                                    break
                                else:
                                    continue
                            else:
                                self.driver.quit()
                        else:
                            self.driver.quit()
                else:
                    self.driver.quit()
            else:
                self.driver.quit()
        else:
            self.driver.quit()

        self.download_pdf(is_current=True)
        self.download_past_pdfs()

    def download_pdf(self, is_current:bool):
        # 今年の馬場情報をダウンロード
        # 今年の馬場情報ページの場合、ページは戻らない
        year = None
        track_name = None
        num_time = None
        try:
            if is_current:
                contents_body_element = self._find_element(None, True, "id", "contentsBody")
                archive_main_element = self._find_element(contents_body_element, False, "id", "archive_main")
                unit_element = self._find_element(archive_main_element, False, "class", "unit")
                contents_header_element = self._find_element(unit_element, False, "class", "contents_header")
                h1_element = self._find_element(contents_header_element, False, "tag", "h1")
                tmp_header = h1_element.text
                year = int(re.search(r"(\d+)年", tmp_header).group(1))
                if self.continue_year is None or year == self.continue_year or self.continue_flag:
                    if self._has_class(unit_element, "data_line_list"):
                        data_line_list_element = self._find_element(unit_element, False, "class", "data_line_list")
                        data_list_unit_elements = self._find_elements(data_line_list_element, False, "class", "data_list_unit")
                        num_track = len(data_list_unit_elements)
                        for n_track in range(num_track):
                            data_list_unit_element = data_list_unit_elements[n_track]
                            head_element = self._find_element(data_list_unit_element, False, "class", "head")
                            track_name = head_element.text # 「函館競馬場」のような形式
                            if self.continue_track_name is None or track_name == self.continue_track_name or self.continue_flag:
                                if self._has_class(data_list_unit_element, "content"):
                                    content_element = self._find_element(data_list_unit_element, False, "class", "content")
                                    li2_elements = self._find_elements(content_element, False, "tag", "li")
                                    num_times = len(li2_elements)
                                    for n_time in range(num_times):
                                        contents_body_element = self._find_element(None, True, "id", "contentsBody")
                                        data_line_list_element = self._find_element(contents_body_element, False, "class", "data_line_list")
                                        data_list_unit_elements = self._find_elements(data_line_list_element, False, "class", "data_list_unit")
                                        data_list_unit_element = data_list_unit_elements[n_track]
                                        content_element = self._find_element(data_list_unit_element, False, "class", "content")
                                        li2_elements = self._find_elements(content_element, False, "tag", "li")
                                        li2_element = li2_elements[n_time]
                                        if self._has_tag(li2_element, "a"):
                                            a_element = self._find_element(li2_element, False, "tag", "a")
                                            tmp_num_time = a_element.text
                                            num_time = int(re.search(r"第(\d+)回", tmp_num_time).group(1))
                                            print(f"year: {year} track_name: {track_name} num_time: {num_time}")
                                            if self.continue_num_time is None or num_time == self.continue_num_time or self.continue_flag:
                                                self.continue_flag = True
                                                self._wait_click_element(a_element, "tag")
                                                a_element.click()
                                                self._wait_random_seconds()
                                            else:
                                                continue
                                        else:
                                            self.driver.quit()
                                else:
                                    self.driver.quit()
                            else:
                                continue
                    else:
                        self.driver.quit()
                else:
                    pass
            # 過去の馬場情報ページの場合、ページを戻る
            else:
                contents_body_element = self._find_element(None, True, "id", "contentsBody")
                archive_main_element = self._find_element(contents_body_element, False, "id", "archive_main")
                unit_element = self._find_element(archive_main_element, False, "class", "unit")
                contents_header_element = self._find_element(unit_element, False, "class", "contents_header")
                h1_element = self._find_element(contents_header_element, False, "tag", "h1")
                tmp_header = h1_element.text
                year = int(re.search(r"(\d+)年", tmp_header).group(1))
                if self.continue_year is None or year == self.continue_year or self.continue_flag:
                    if self._has_class(unit_element, "data_line_list"):
                        data_line_list_element = self._find_element(unit_element, False, "class", "data_line_list")
                        data_list_unit_elements = self._find_elements(data_line_list_element, False, "class", "data_list_unit")
                        num_track = len(data_list_unit_elements)
                        for n_track in range(num_track):
                            data_list_unit_element = data_list_unit_elements[n_track]
                            head_element = self._find_element(data_list_unit_element, False, "class", "head")
                            track_name = head_element.text # 「函館競馬場」のような形式
                            if self.continue_track_name is None or track_name == self.continue_track_name or self.continue_flag:
                                if self._has_class(data_list_unit_element, "content"):
                                    content_element = self._find_element(data_list_unit_element, False, "class", "content")
                                    li2_elements = self._find_elements(content_element, False, "tag", "li")
                                    num_times = len(li2_elements)
                                    for n_time in range(num_times):
                                        contents_body_element = self._find_element(None, True, "id", "contentsBody")
                                        data_line_list_element = self._find_element(contents_body_element, False, "class", "data_line_list")
                                        data_list_unit_elements = self._find_elements(data_line_list_element, False, "class", "data_list_unit")
                                        data_list_unit_element = data_list_unit_elements[n_track]
                                        content_element = self._find_element(data_list_unit_element, False, "class", "content")
                                        li2_elements = self._find_elements(content_element, False, "tag", "li")
                                        li2_element = li2_elements[n_time]
                                        if self._has_tag(li2_element, "a"):
                                            a_element = self._find_element(li2_element, False, "tag", "a")
                                            tmp_num_time = a_element.text
                                            num_time = int(re.search(r"第(\d+)回", tmp_num_time).group(1))
                                            print(f"year: {year} track_name: {track_name} num_time: {num_time}")
                                            if self.continue_num_time is None or num_time == self.continue_num_time or self.continue_flag:
                                                self.continue_flag = True
                                                self._wait_click_element(a_element, "tag")
                                                a_element.click()
                                                self._wait_random_seconds()
                                            else:
                                                continue
                                        else:
                                            self.driver.quit()
                                else:
                                    self.driver.quit()
                            else:
                                continue
                    else:
                        self.driver.quit()
                else:
                    pass
                self.driver.back()
        except Exception as e:
            print(f"Exception occurred: {e}")
            # ダウンロードが中断した際の年と競馬場名、回数を記録
            if year is not None:
                self.continue_year = year
            else:
                self.continue_year = None

            if track_name is not None:
                self.continue_track_name = track_name
            else:
                self.continue_track_name = None

            if num_time is not None:
                self.continue_num_time = num_time
            else:
                self.continue_num_time = None

            print(f"continue_year: {self.continue_year}")
            print(f"continue_track_name: {self.continue_track_name}")
            print(f"num_time: {self.continue_num_time}")

            self.continue_flag = False
            new_baba_db = BabaDB(self.homepage_url)
            new_baba_db.continue_year = self.continue_year
            new_baba_db.continue_track_name = self.continue_track_name
            new_baba_db.continue_num_time = self.continue_num_time
            new_baba_db.continue_flag = self.continue_flag
            new_baba_db.get_pdf()

    def download_past_pdfs(self):
        # 過去の馬場情報をダウンロード
        if self.continue_year is None:
            contents_body_element = self._find_element(None, True, "id", "contentsBody")
            archive_main_element = self._find_element(contents_body_element, False, "id", "archive_main")
            if self._has_class(contents_body_element, "bn-area"):
                bn_area_element = self._find_element(archive_main_element, False, "class", "bn-area")
                if self._has_class(bn_area_element, "link_list"):
                    link_list_element = self._find_element(bn_area_element, False, "class", "link_list")
                    div_elements = self._find_elements(link_list_element, False, "tag", "div")
                    num_years = len(div_elements)
                    for n_year in range(num_years):
                        contents_body_element = self._find_element(None, True, "id", "contentsBody")
                        archive_main_element = self._find_element(contents_body_element, False, "id", "archive_main")
                        bn_area_element = self._find_element(archive_main_element, False, "class", "bn-area")
                        link_list_element = self._find_element(bn_area_element, False, "class", "link_list")
                        div_elements = self._find_elements(link_list_element, False, "tag", "div")
                        div_element = div_elements[n_year]
                        year_element = self._find_element(div_element, False, "tag", "a")
                        tmp_year = year_element.text
                        year = int(re.search(r"(\d+)年", tmp_year).group(1))
                        if self._has_tag(div_element, "a"):
                            a_element = self._find_element(div_element, False, "tag", "a")
                            self._wait_click_element(a_element, "tag")
                            a_element.click()
                            self.download_pdf(is_current=False)
                        else:
                            continue
                else:
                    self.driver.quit()
            else:
                self.driver.quit()
        else:
            contents_body_element = self._find_element(None, True, "id", "contentsBody")
            archive_main_element = self._find_element(contents_body_element, False, "id", "archive_main")
            if self._has_class(contents_body_element, "bn-area"):
                bn_area_element = self._find_element(archive_main_element, False, "class", "bn-area")
                if self._has_class(bn_area_element, "link_list"):
                    link_list_element = self._find_element(bn_area_element, False, "class", "link_list")
                    div_elements = self._find_elements(link_list_element, False, "tag", "div")
                    num_years = len(div_elements)
                    for n_year in range(num_years):
                        contents_body_element = self._find_element(None, True, "id", "contentsBody")
                        archive_main_element = self._find_element(contents_body_element, False, "id", "archive_main")
                        bn_area_element = self._find_element(archive_main_element, False, "class", "bn-area")
                        link_list_element = self._find_element(bn_area_element, False, "class", "link_list")
                        div_elements = self._find_elements(link_list_element, False, "tag", "div")
                        div_element = div_elements[n_year]
                        year_element = self._find_element(div_element, False, "tag", "a")
                        tmp_year = year_element.text
                        year = int(re.search(r"(\d+)年", tmp_year).group(1))
                        if self.continue_year is None or year == self.continue_year or self.continue_flag:
                            if self._has_tag(div_element, "a"):
                                a_element = self._find_element(div_element, False, "tag", "a")
                                self._wait_click_element(a_element, "tag")
                                a_element.click()
                                self.download_pdf(is_current=False)
                            else:
                                self.driver.quit()
                        else:
                            continue
                else:
                    self.driver.quit()
            else:
                self.driver.quit()

def main():
    # 同ディレクトリにあるPDFファイルを取得
    pdf_files = glob('*.pdf')
    # print(pdf_files)
    # for pdf_file in pdf_files:
    #     # PDFファイルを開く
    #     doc = pdf.PdfDocument(pdf_file)
    #     # ページ数を取得
    #     for page in doc:
    #         textpage = page.get_textpage()
    #         text = textpage.get_text_range()
    #         print(text)
    #         print('---------------------------')

    homepage_url = "https://www.jra.go.jp/"
    baba_db = BabaDB(homepage_url)
    baba_db.get_pdf()

if __name__ == '__main__':
    main()