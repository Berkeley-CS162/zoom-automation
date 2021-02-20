from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import click

MAX_WAIT = 10

def parse(data):
    try:
        lines = data.strip().split("\n")
        email = lines[0].split(":")[-1].strip()
        timestamp = lines[1].split(" :")[-1].strip()
        link = lines[-1].strip()
        return "\"{}\",\"{}\",\"{}\"\n".format(email, timestamp, link)
    except Exception:
        return data

def id_click(driver, id):
    WebDriverWait(driver, MAX_WAIT).until(EC.element_to_be_clickable((By.ID, id)))
    elem = driver.find_element_by_id(id)
    ActionChains(driver).move_to_element(elem).perform()
    elem.click()

def css_click(driver, q):
    if q[0] == "#" and " " not in q:
        return id_click(driver, q[1:])
    WebDriverWait(driver, MAX_WAIT).until(EC.element_to_be_clickable((By.CSS_SELECTOR, q)))
    elem = driver.find_element_by_css_selector(q)
    ActionChains(driver).move_to_element(elem).perform()
    elem.click()

def saveRecordingsPage(driver):
    lst = []
    WebDriverWait(driver, MAX_WAIT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".sharemeet_from_myrecordinglist")))
    elems = driver.find_elements_by_css_selector(".sharemeet_from_myrecordinglist")
    for elem in elems:
        ActionChains(driver).move_to_element(elem).perform()
        elem.click()
        WebDriverWait(driver, MAX_WAIT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".zm-switch")))

        # turn off passcode protection
        switch = driver.find_elements_by_css_selector(".zm-switch")[-1]
        if "is-checked" in switch.get_attribute("class"):
            switch.click()
        
        # get sharing info
        css_click(driver, ".share-info-div")
        textarea = driver.find_element_by_id("r_share_meet_content")
        value = textarea.get_attribute("value")
        while "Access Passcode" in value:
            value = textarea.get_attribute("value")
        lst.append(value)

        css_click(driver, ".copy-to-clipboard + button")
    return lst

@click.command()
@click.argument('output', type=click.File('w', encoding="utf-8"))
def run(output):
    driver = webdriver.Chrome()
    driver.get("https://berkeley.zoom.us/recording")
    WebDriverWait(driver, 120).until(EC.presence_of_element_located((By.ID, "recordings")))
    while True:
        datalist = saveRecordingsPage(driver)
        for data in datalist:
            output.write(parse(data))
        try:
            driver.find_element_by_css_selector(".next.disabled")
            break
        except Exception:
            css_click(driver, ".next a")

if __name__ == '__main__':
    run()
