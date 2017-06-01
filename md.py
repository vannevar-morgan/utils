#! /usr/bin/env python3

# md.py downloads youtube music using convert2mp3.net

import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
import requests
import logging
logging.basicConfig(level=logging.DEBUG, format=" %(asctime)s - %(levelname)s - %(message)s")
logging.disable(logging.CRITICAL)

def save_file(link, filename):
    # save the file at link to the specified format
    print("\ndownloading file from:\n" + link)
    resp = requests.get(link, stream=True)
    total_length = resp.headers.get("content-length")
    try:
        resp.raise_for_status()
    except:
        print("error downloading file...")
        return

    chunk_size = 4096
    with open(filename, "wb") as out_file:
        print("saving to filename:\t" + filename)
        if total_length is None:
            out_file.write(resp.content)
        else:
            print()
            dl = 0
            total_length = int(total_length)
            for data in resp.iter_content(chunk_size):
                dl += len(data)
                out_file.write(data)
                print("\r" + str(int(100 * (dl / total_length))) + "%", end="")
    print("\ndownload complete!")



def download_file(link, file_format):
    # download the video at youtube link, link,
    # using convert2mp3.net, in specified file format
    #    FIREFOX_PATH = "/usr/bin/firefox"
    
    PHANTOMJS_PATH = "/usr/bin/phantomjs"
    CONVERT_URL = "http://convert2mp3.net/en/index.php"
    print("downloading " + file_format + " for video at link:\t" + link)
    #browser = webdriver.Firefox()
    browser = webdriver.PhantomJS(PHANTOMJS_PATH, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=TLSv1'])
    browser.set_window_size(1280, 800)
#    browser.ignoreSynchronization = True
    browser.get(CONVERT_URL)
#    browser.ignoreSynchronization = False
    print("got page:\t" + CONVERT_URL)
    print("finding urlinput...")
    link_input_elem = browser.find_element_by_id("urlinput")
    link_input_elem.send_keys(link)

    print("finding dropdown button...")
    #format_button_elem = browser.find_element_by_class_name("btn.dropdown-toggle.btn-default")
    format_button_elem = browser.find_element_by_css_selector("button[data-toggle='dropdown']")
    #    print(browser.page_source)
    print("clicking dropdown button...")
    format_button_elem.click()
    print("finding file format link text...")
    format_elem = browser.find_element_by_link_text(file_format)
    print("clicking file format link text...")
    format_elem.click()
    print("finding submit button...")
    submit_button_elem = browser.find_element_by_css_selector("button[type='submit']")
    print("clicking submit button...")
    print("waiting for converter service...")
    try:
        submit_button_elem.click()
    except exceptions.WebDriverException as e:
        debug_ss_filename = "md_error_screenshot.png"
        print("\nerror occurred while clicking submit button...")
        print(e)
        print("saved screenshot of error to " + debug_ss_filename)
        browser.save_screenshot(debug_ss_filename)
        browser.quit()
        return
        
    try:
        print("finding download link...")
        #print("waiting for converter service...")
        #download_button = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CLASS_NAME, "btn.btn-success.btn-large")))
        download_button = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn:nth-child(5)")))
        dl_url = download_button.get_attribute("href")
        filename_label = browser.find_element_by_css_selector(".alert > b:nth-child(1)")
        filename = filename_label.text + "." + file_format
        save_file(dl_url, filename)
        browser.quit()
    except exceptions.TimeoutException as e:
        print("\nconverter service timed out, couldn't find the download button...")
        print(e)
        browser.quit()
        return
    


USAGE_MESSAGE = "usage: ./md.py link (format)"

arg_len = len(sys.argv)
if arg_len != 2 and arg_len != 3:
    print(USAGE_MESSAGE)
    sys.exit(0)

link = sys.argv[1]

file_format = "flac"

if arg_len == 3:
    file_format = sys.argv[2]

download_file(link, file_format)

