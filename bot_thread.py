from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException
from threading import Thread
from event import EVENT
from dialog_box import DialogBox
from helpers import get_asked_models
from event_queue import threads_event_queue
from re import search
from datetime import datetime
from time import sleep
import logging
from pathlib import Path
from os import listdir

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(filename)s:%(levelname)s:%(message)s')
now = datetime.now()
file_handler = logging.FileHandler(f'./logs/log_d{now.day}m{now.month}h{now.hour}m{now.minute}.txt')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

CHIPSETS = ['nvidia', 'amd']


def init_dialog_box():
    DialogBox()


def bot_thread():
    Thread(target=init_dialog_box).start()

    event = EVENT

    while not event.is_set():
        logger.info('CaseKing bot started')
        try:
            caseking()
            logger.info('CaseKing completed')
        except WebDriverException as err:
            log_error('Caseking', err)
            return

        logger.info('Mindfactory bot started')
        try:
            mindfactory()
            logger.info('Mindfactory completed')
        except WebDriverException as err:
            log_error('Midfactory', err)
            return

        event.wait(180)
    else:
        threads_event_queue.put('bot_stopped')


def caseking():
    driver = get_mozzila_webdriver()

    asked_models = get_asked_models()
    asked_models_available = []
    try:
        # print('CaseKing:')  # For debug
        for chipset in CHIPSETS:
            driver.get(f"https://www.caseking.de/pc-komponenten/grafikkarten/{chipset}")
            sleep(6)
            all_offers = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'listing-1col')))
            offers = all_offers.find_elements_by_class_name("artbox.grid_20.first.last")
            for offer in offers:
                subtitle = offer.find_element_by_class_name("ProductSubTitle").text
                title = offer.find_element_by_class_name("ProductTitle").text
                for model in asked_models[chipset]:
                    pattern = pattern_for_regex(chipset, model)

                    if search(pattern, title):
                        if 'lagernd' in offer.text:
                            asked_models_available.append(f'{subtitle} {title}')

        if asked_models_available:
            logger.info(f"Models available: {asked_models_available}")
            asked_models_available.append('caseking')
            threads_event_queue.put(asked_models_available)

    except Exception as err:
        raise err
    finally:
        driver.quit()

    # print('bot_thread: bot ended')    # For Debug


def mindfactory():
    driver = get_mozzila_webdriver()

    asked_models = get_asked_models()
    asked_models_available = []

    # print('Mindfactory:') # For Debug
    try:
        driver.get(f"https://www.mindfactory.de/Hardware/Grafikkarten+(VGA).html")

        # Accept cookies
        driver.find_element_by_id("checkcookie").click()
        sleep(5)
        # all_offers = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'bProducts')))
        all_offers = driver.find_element_by_id("bProducts")

        offers = all_offers.find_elements_by_class_name("pcontent")
        for chipset in CHIPSETS:
            for offer in offers:
                title = offer.find_element_by_class_name("pname").text
                for model in asked_models[chipset]:
                    pattern = pattern_for_regex(chipset, model)
                    if search(pattern, title):
                        try:
                            status = offer.find_element_by_class_name("shipping1").text
                        except WebDriverException as err:
                            logger.error(f'{err.msg} for model: {title}')
                            continue
                        if status == 'Lagernd':
                            # print(title)
                            asked_models_available.append(f'{title}')

        if asked_models_available:
            logger.info(f"Models available: {asked_models_available}")
            asked_models_available.append('mindfactory')
            threads_event_queue.put(asked_models_available)
    except Exception as err:
        raise err
    finally:
        driver.quit()


def get_mozzila_webdriver():
    profile_dir = get_mozzila_profile_dir()
    profile = get_profile(profile_dir)
    mozzila_options = Options()
    mozzila_options.headless = True
    driver = webdriver.Firefox(executable_path='./bin/geckodriver.exe', options=mozzila_options,
                               firefox_profile=profile)
    return driver


def get_profile(path):
    profile = webdriver.FirefoxProfile(path)
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference('useAutomationExtension', False)
    profile.update_preferences()
    return profile


def get_mozzila_profile_dir():
    home_dir = Path.home()
    profiles_dir = Path.joinpath(home_dir, 'AppData\Roaming\Mozilla\Firefox\Profiles')
    dirs = listdir(profiles_dir)
    default_release_folder = None
    for dir in dirs:
        if '.default-release' in dir:
            default_release_folder = dir
    complete_dir = Path.joinpath(profiles_dir, default_release_folder)
    return complete_dir


def log_error(website, err):
    logger.error(f'{website} process terminated. Error: {err}')
    send_error_in_gui()


def send_error_in_gui():
    threads_event_queue.put('error')


def check_pattern_for_nvidia(model):
    if 'Ti' in model:
        pattern = rf'{model[:-3]}(?=( Ti|Ti))'
    else:
        pattern = rf'{model}(?![^\s]| Ti)'

    return pattern


def check_pattern_for_amd(model):
    if 'XT' in model:
        pattern = rf'{model[:-3]}(?=( XT|XT))'
    else:
        pattern = rf'{model}(?![^\s]| XT)'

    return pattern


def pattern_for_regex(chipset, model):
    if chipset == 'nvidia':
        return check_pattern_for_nvidia(model)
    elif chipset == 'amd':
        return check_pattern_for_amd(model)


if __name__ == '__main__':
    bot_thread()

# def delete_cache(driver):
#     driver.execute_script("window.open('');")
#     sleep(2)
#     driver.switch_to.window(driver.window_handles[-1])
#     sleep(2)
#     driver.get('chrome://settings/clearBrowserData')  # for old chromedriver versions use cleardriverData
#     sleep(2)
#     actions = ActionChains(driver)
#     actions.send_keys(Keys.TAB * 3 + Keys.DOWN * 3)  # send right combination
#     actions.perform()
#     sleep(2)
#     actions = ActionChains(driver)
#     actions.send_keys(Keys.TAB * 4 + Keys.ENTER)  # confirm
#     actions.perform()
#     sleep(5)  # wait some time to finish
#     driver.close()  # close this tab
#     driver.switch_to.window(driver.window_handles[0])
