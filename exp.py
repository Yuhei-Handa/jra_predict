import pandas as pd
import numpy as np
import re
from glob import glob
import os
from playwright.sync_api import Playwright, sync_playwright, expect
import time

from playwright.sync_api import Playwright, sync_playwright, expect


# def run(playwright: Playwright) -> None:
#     homepage_url = "https://www.jra.go.jp/"
#     browser = playwright.chromium.launch(headless=False)
#     context = browser.new_context()

#     # Open new page
#     page = context.new_page()

#     # Go to https://www.google.com/
#     page.goto(homepage_url)
#     elements = page.query_selector_all('.content')





# with sync_playwright() as playwright:
#     run(playwright)


a = [1, 2, 3, 4, 5]
b = [1, 2, 3, 4, 5]
print(a + b)

print(str(1 + 0))

csv_file = "C:\Users\yuhei\Downloads\2024_第1回札幌(Sheet1) (1).csv"

df = pd.read_csv(csv_file)

print(df)