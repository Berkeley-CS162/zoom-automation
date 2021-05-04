### Zoom Meeting Generation Script
###   INPUT: CSV of one column: Email
###   OUTPUT: CSV of two columns: Email, Meeting
###   Options:
###     --help
###     -t, --topic TEXT                Name (Topic) of meeting (@ symbol replaced by email)
###     -c, --cohost                    Add each email as a co-host for its meeting
###     -w, --when INTEGER              Date/time of meeting, as timestamp (seconds)
###     -d, --duration INTEGER          Duration of meeting, in minutes
###     -b, --browser [chrome|firefox]  Selenium WebDriver
###
### Requirements:
###  - Python 3
###  - Selenium (pip install selenium)
###  - Selenium driver for your browser (a separately downloadable executable in your path)
###       Chrome drivers:  https://chromedriver.storage.googleapis.com/index.html
###       Firefox drivers: https://github.com/mozilla/geckodriver/releases

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import click
from datetime import datetime

MAX_WAIT = 10
RETRIES = 3

def retry(func):
    def wrapper_retry(*args):
        success = False
        attempts = RETRIES
        while not success and attempts:
            success = True
            try:
                func(*args)
            except Exception:
                success = False
                attempts -= 1
    return wrapper_retry

def id_click(driver, id):
    elem = driver.find_element_by_id(id)
    ActionChains(driver).move_to_element(elem).perform()
    WebDriverWait(driver, MAX_WAIT).until(EC.element_to_be_clickable((By.ID, id)))
    elem.click()

@retry
def css_click(driver, q):
    if q[0] == "#" and " " not in q:
        return id_click(driver, q[1:])
    elem = driver.find_element_by_css_selector(q)
    ActionChains(driver).move_to_element(elem).perform()
    WebDriverWait(driver, MAX_WAIT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, q)))
    elem.click()

@retry
def css_fill(driver, q, text):
    WebDriverWait(driver, MAX_WAIT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, q)))
    elem = driver.find_element_by_css_selector(q)
    elem.clear()
    elem.send_keys(text)

@retry
def css_checkbox(driver, q, check):
    elem = driver.find_element_by_css_selector(q)
    ActionChains(driver).move_to_element(elem).perform()
    WebDriverWait(driver, MAX_WAIT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, q)))
    if (check and not elem.is_selected()) or (not check and elem.is_selected()):
        elem.click()

def create_meeting(driver, email, topic, cohost, when, duration):
    driver.get("https://berkeley.zoom.us/meeting/schedule")

    # Wait for sign-in
    WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.ID, "meetings")))

    # Topic
    css_fill(driver, "#topic", topic)

    # Recurring / When+Duration
    if when == 0 or duration == 0:
        css_checkbox(driver, "#option_rm", True)
        css_click(driver, "#recurrenceType")
        css_click(driver, "#select-item-recurrenceType-3") # No Fixed Time
    else:
        datetime_obj = datetime.fromtimestamp(when)
        date_str = datetime_obj.strftime("%B ") + str(datetime_obj.day) + " " + str(datetime_obj.year)
        time_str = str(datetime_obj.hour % 12) + datetime_obj.strftime(":%M")
        css_click(driver, ".ui-datepicker-trigger")
        css_click(driver, "a[aria-label^='" + date_str + "']")
        css_click(driver, "[name='start_time']")
        css_click(driver, "dd[aria-label='" + time_str + "']")
        css_click(driver, "[name='start_time_2']")
        if datetime_obj.hour < 12:
            css_click(driver, "#select-item-start_time_2-0") # AM
        else:
            css_click(driver, "#select-item-start_time_2-1") # PM
        css_click(driver, "#duration_hr")
        css_click(driver, "#select-item-duration_hr-" + str(duration // 60))
        css_click(driver, "#duration_min")
        css_click(driver, "#select-item-duration_min-" + str((duration % 60) // 15))

    # Registration
    css_checkbox(driver, "#option_registration", False)

    # Meeting ID
    css_click(driver, "#optionOneTimeId")

    # Security
    css_checkbox(driver, "#option_password", True)
    css_checkbox(driver, "#option_waiting_room", False)

    # Video, Audio
    css_click(driver, "#option_video_host_on")
    css_click(driver, "#option_video_participant_on")
    css_click(driver, "#option_audio_both")
    css_click(driver, "#optionOneTimeId")

    # Meeting Options
    css_checkbox(driver, "#option_jbh", True)
    css_checkbox(driver, "#option_mute_upon_entry", False)
    css_click(driver, "#auth_select")
    css_click(driver, "#select-item-auth_select-1")
    css_checkbox(driver, "#breout-room", False)
    css_checkbox(driver, "#option_autorec", True)
    css_click(driver, "#option_autorec_cloud")

    # Alternative Hosts
    if cohost:
        css_fill(driver, "#mtg_alternative_host input", email)
        try:
            WebDriverWait(driver, MAX_WAIT).until(EC.element_to_be_clickable((By.ID, "select-item-select-0-0")))
            css_click(driver, "#select-item-select-0-0")
            WebDriverWait(driver, MAX_WAIT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#schedule_form > div.meeting-options-section > div:nth-child(10) > div > label')))
            css_click(driver, "#schedule_form > div.meeting-options-section > div:nth-child(10) > div > label")
        except Exception:
            print("COHOST ERR: " + email)
            # return "ERROR"

    # Wait for save
    css_click(driver, ".submit")
    link_q = ".controls a[href^='https://berkeley.zoom.us/j/']"
    try:
        WebDriverWait(driver, MAX_WAIT).until(EC.presence_of_element_located((By.CSS_SELECTOR, link_q)))
        print("successful: " + email)
        return driver.find_element_by_css_selector(link_q).text
    except Exception:
        print("SAVE ERROR: " + email)
        return "ERROR"


@click.command()
@click.argument('input', type=click.File('r'))
@click.argument('output', type=click.File('w'))

@click.option('-t', '--topic', default="Meeting (@)", help="Name of meeting")
@click.option('-c', '--cohost', default=False, is_flag=True, help='Add emails as cohosts')

# If when/duration are not specified, then the meeting will be scheduled as recurring
@click.option('-w', '--when', default=0, type=int, help="Date/time of meeting, as timestamp")
@click.option('-d', '--duration', default=0, type=int, help="Duration of meeting, in minutes")

@click.option('-b', '--browser', default="chrome", type=click.Choice(['chrome', 'firefox'], case_sensitive=False), help="Selenium WebDriver")

def run(input, output, topic, cohost, when, duration, browser):
    email_reader = csv.reader(input)
    next(email_reader) # skip header row
    zoom_writer = csv.writer(output, lineterminator='\n')
    zoom_writer.writerow(["Email", "Link"])

    if browser == "chrome":
        driver = webdriver.Chrome()
    if browser == "firefox":
        driver = webdriver.Firefox()

    for row in email_reader:
        if row:
            email = row[0]
            link = create_meeting(driver, email, topic.replace("@", email), cohost, when, duration)
            zoom_writer.writerow([email, link])

if __name__ == '__main__':
    run()
