import pypdfium2 as pdf
from glob import glob
import pandas as pd
import os
import datetime
import json
import argparse
from glob import glob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BabaDB:
    def __init__(self, homepage_url:str):
        self.homepage_url = homepage_url
        self.track_count = 0
        self.race_count = 0
        self.race_df = pd.DataFrame()
        self.track_df = pd.DataFrame()
        self.driver = None
        self.first_month_flag = True
        self.save_dir = "baba_data"
        self.init_driver()
        self.mkdir()

    def init_driver(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {
            f"download.default_directory": f"~/{self.save_dir}/pdf",
            "plugins.always_open_pdf_externally": True
        })
        options.add_argument('--kiosk-printing')
        #options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def mkdir(self):
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)

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
        header_element = self.driver.find_element(By.TAG_NAME, "header")
        if self._has_class(header_element, "content"):
            content_element = header_element.find_element(By.CLASS_NAME, "content")
            line_elements = self._find_elements(content_element, False, "class", "line")
            for line_element in line_elements:
                if not self._has_id(line_element, "global_nav"):
                    continue
                else:
                    global_nav_element = self._find_element(line_element, False, "id", "global_nav")
                    if self._has_class(global_nav_element, "nav"):
                        nav_element = self._find_element(global_nav_element, False, "class", "nav")
                        li_elements = self._find_elements(nav_element, False, "tag", "li")
                        # 各li要素を取得
                        # 最も左にある競馬メニューを選択
                        for li_element in li_elements:
                            if self._has_id(li_element, "gnav_keiba"):
                                keiba_element = self._find_element(li_element, False, "id", "gnav_keiba")
                                a_element = self._find_element(keiba_element, False, "tag", "a")
                                self._wait_click_element(a_element, "tag")
                                a_element.click()
                            else:
                                continue
                    else:
                        continue
        else:
            self.driver.quit()
    
    def open_baba_page(self):
        # 馬場情報が記載されたページに遷移
        search_word = "馬場情報"
        contents_body_element = self._find_element(self.driver, True, "id", "contentsBody")
        category_unit_elements = self._find_elements(contents_body_element, False, "class", "categoryUnit")
        for category_unit_element in category_unit_elements:
            if self._has_id(category_unit_element, "kaisai"):
                kaisai_element = self._find_element(category_unit_element, False, "id", "kaisai")
                link_list_element = self._find_element(kaisai_element, False, "class", "link_list")
                li_elemets = self._find_elements(link_list_element, False, "tag", "li")
                for li_element in li_elemets:
                    if self._has_tag(li_element, "a"):
                        a_element = self._find_element(li_element, False, "tag", "a")
                        if self._has_text(a_element):
                            target_text = a_element.text
                            if target_text == search_word:
                                self._wait_click_element(a_element, "tag")
                                a_element.click()
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
        contents_body_element = self._find_element(self.driver, True, "id", "contentsBody")
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
                                    self.download_pdf(is_current=True)
                                    self.download_past_pdfs()
                                    break
                                else:
                                    continue
                            else:
                                continue
                        else:
                            continue
                else:
                    self.driver.quit()
            else:
                self.driver.quit()
        else:
            self.driver.quit()

    def download_pdf(self, is_current:bool):
        # 今年の馬場情報をダウンロード
        # 今年の馬場情報ページの場合、ページは戻らない
        if is_current:
            contents_body_element = self._find_element(self.driver, True, "id", "contentsBody")
            if self._has_class(contents_body_element, "data_line_list"):
                data_line_list_element = self._find_element(contents_body_element, False, "class", "data_line_list")
                li1_elements = self._find_elements(data_line_list_element, False, "tag", "li")
                num_track = len(li1_elements)
                for n_track in range(num_track):
                    li1_element = li1_elements[n_track]
                    if self._has_class(li1_element, "content"):
                        content_element = self._find_element(li1_element, False, "class", "content")
                        li2_elements = self._find_elements(content_element, False, "tag", "li")
                        num_times = len(li2_elements)
                        for n_time in range(num_times):
                            contents_body_element = self._find_element(self.driver, True, "id", "contentsBody")
                            data_line_list_element = self._find_element(contents_body_element, False, "class", "data_line_list")
                            li1_elements = self._find_elements(data_line_list_element, False, "tag", "li")
                            li1_element = li1_elements[n_track]
                            content_element = self._find_element(li1_element, False, "class", "content")
                            li2_elements = self._find_elements(content_element, False, "tag", "li")
                            li2_element = li2_elements[n_time]
                            if self._has_tag(li2_element, "a"):
                                a_element = self._find_element(li2_element, False, "tag", "a")
                                self._wait_click_element(a_element, "tag")
                                a_element.click()
                            else:
                                continue
                    else:
                        continue
                #self.driver.back()
            else:
                self.driver.quit()
        # 過去の馬場情報ページの場合、ページを戻る
        else:
            contents_body_element = self._find_element(self.driver, True, "id", "contentsBody")
            if self._has_class(contents_body_element, "data_line_list"):
                data_line_list_element = self._find_element(contents_body_element, False, "class", "data_line_list")
                li1_elements = self._find_elements(data_line_list_element, False, "tag", "li")
                num_track = len(li1_elements)
                for n_track in range(num_track):
                    li1_element = li1_elements[n_track]
                    if self._has_class(li1_element, "content"):
                        content_element = self._find_element(li1_element, False, "class", "content")
                        li2_elements = self._find_elements(content_element, False, "tag", "li")
                        num_times = len(li2_elements)
                        for n_time in range(num_times):
                            contents_body_element = self._find_element(self.driver, True, "id", "contentsBody")
                            data_line_list_element = self._find_element(contents_body_element, False, "class", "data_line_list")
                            li1_elements = self._find_elements(data_line_list_element, False, "tag", "li")
                            li1_element = li1_elements[n_track]
                            content_element = self._find_element(li1_element, False, "class", "content")
                            li2_elements = self._find_elements(content_element, False, "tag", "li")
                            li2_element = li2_elements[n_time]
                            if self._has_tag(li2_element, "a"):
                                a_element = self._find_element(li2_element, False, "tag", "a")
                                self._wait_click_element(a_element, "tag")
                                a_element.click()
                            else:
                                continue
                    else:
                        continue
                #self.driver.back()
            else:
                self.driver.quit()
            self.driver.back()

    def download_past_pdfs(self):
        # 過去の馬場情報をダウンロード
        contents_body_element = self._find_element(self.driver, True, "id", "contentsBody")
        if self._has_class(contents_body_element, "bn-area"):
            bn_area_element = self._find_element(contents_body_element, False, "class", "bn-area")
            if self._has_class(bn_area_element, "link_list"):
                link_list_element = self._find_element(bn_area_element, False, "class", "link_list")
                div_elements = self._find_elements(link_list_element, False, "tag", "div")
                num_years = len(div_elements)
                for n_year in range(num_years):
                    contents_body_element = self._find_element(self.driver, True, "id", "contentsBody")
                    bn_area_element = self._find_element(contents_body_element, False, "class", "bn-area")
                    link_list_element = self._find_element(bn_area_element, False, "class", "link_list")
                    div_elements = self._find_elements(link_list_element, False, "tag", "div")
                    div_element = div_elements[n_year]
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

def main():
    # 同ディレクトリにあるPDFファイルを取得
    pdf_files = glob('*.pdf')
    print(pdf_files)
    for pdf_file in pdf_files:
        # PDFファイルを開く
        doc = pdf.PdfDocument(pdf_file)
        # ページ数を取得
        for page in doc:
            textpage = page.get_textpage()
            text = textpage.get_text_range()
            print(text)
            print('---------------------------')

    

if __name__ == '__main__':
    main()