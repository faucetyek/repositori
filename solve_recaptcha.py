from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import shutil
import requests
import re
from ultralytics import YOLO
import numpy as np
from PIL import Image
import cv2
model = YOLO("yolov8x.pt")


def go_to_recaptcha_iframe1(driver):
    driver.switch_to.default_content()
    recaptcha_iframe1 = WebDriverWait(driver=driver, timeout=10).until(
        EC.presence_of_element_located((By.XPATH, '//iframe[@title="reCAPTCHA"]')))
    driver.switch_to.frame(recaptcha_iframe1)


def go_to_recaptcha_iframe2(driver):
    driver.switch_to.default_content()
    recaptcha_iframe2 = WebDriverWait(driver=driver, timeout=10).until(
        EC.presence_of_element_located((By.XPATH, '//iframe[contains(@title, "challenge")]')))
    driver.switch_to.frame(recaptcha_iframe2)


def get_target_num(driver):
    target = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, '//div[@id="rc-imageselect"]//strong')))

    if re.search(r"bicycle", target.text) != None:
        return 1
    elif re.search(r"bus", target.text) != None:
        return 5
    elif re.search(r"boat", target.text) != None:
        return 8
    elif re.search(r"car", target.text) != None:
        return 2
    elif re.search(r"hydrant", target.text) != None:
        return 10
    elif re.search(r"motorcycle", target.text) != None:
        return 3
    elif re.search(r"traffic", target.text) != None:
        return 9
    else:
        return 1000


def get_answers(target_num):
    image = Image.open("0.png")
    image = np.asarray(image)
    result = model.predict(image)

    target_index = []
    count = 0
    for num in result[0].boxes.cls:
        if num == target_num:
            target_index.append(count)
        count += 1

    answers = []
    boxes = result[0].boxes.data
    count = 0
    for i in target_index:
        target_box = boxes[i]
        p1, p2 = (int(target_box[0]), int(target_box[1])
                  ), (int(target_box[2]), int(target_box[3]))
        x1, y1 = p1
        x2, y2 = p2

        xc = (x1+x2)/2
        yc = (y1+y2)/2

        if xc < 100 and yc < 100:
            answers.append(1)
        if 100 < xc < 200 and yc < 100:
            answers.append(2)
        if 200 < xc < 300 and yc < 100:
            answers.append(3)

        if xc < 100 and 100 < yc < 200:
            answers.append(4)
        if 100 < xc < 200 and 100 < yc < 200:
            answers.append(5)
        if 200 < xc < 300 and 100 < yc < 200:
            answers.append(6)

        if xc < 100 and 200 < yc < 300:
            answers.append(7)
        if 100 < xc < 200 and 200 < yc < 300:
            answers.append(8)
        if 200 < xc < 300 and 200 < yc < 300:
            answers.append(9)

        count += 1

    return list(set(answers))


def get_all_captcha_img_urls(driver):
    images = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
        (By.XPATH, '//div[@id="rc-imageselect-target"]//img')))

    img_urls = []
    for img in images:
        img_urls.append(img.get_attribute("src"))

    return img_urls


def download_img(name, url):
    response = requests.get(url, stream=True)
    with open(f'{name}.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def get_all_new_dynamic_captcha_img_urls(answers, before_img_urls, driver):
    images = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(
        (By.XPATH, '//div[@id="rc-imageselect-target"]//img')))
    img_urls = []

    for img in images:
        try:
            img_urls.append(img.get_attribute("src"))
        except:
            is_new = False
            return is_new, img_urls

    index_common = []
    for answer in answers:
        if img_urls[answer-1] == before_img_urls[answer-1]:
            index_common.append(answer)

    if len(index_common) >= 1:
        is_new = False
        return is_new, img_urls
    else:
        is_new = True
        return is_new, img_urls


def paste_new_img_on_main_img(main, new, loc):
    paste = np.copy(main)
    if loc == 1:
        paste[0:100, 0:100] = new
    elif loc == 2:
        paste[0:100, 100:200] = new
    elif loc == 3:
        paste[0:100, 200:300] = new
    elif loc == 4:
        paste[100:200, 0:100] = new
    elif loc == 5:
        paste[100:200, 100:200] = new
    elif loc == 6:
        paste[100:200, 200:300] = new
    elif loc == 7:
        paste[200:300, 0:100] = new
    elif loc == 8:
        paste[200:300, 100:200] = new
    elif loc == 9:
        paste[200:300, 200:300] = new

    paste = cv2.cvtColor(paste, cv2.COLOR_RGB2BGR)
    cv2.imwrite('0.png', paste)


def get_occupied_cells(vertices):
    occupied_cells = set()
    rows, cols = zip(*[((v-1)//4, (v-1) % 4) for v in vertices])

    for i in range(min(rows), max(rows)+1):
        for j in range(min(cols), max(cols)+1):
            occupied_cells.add(4*i + j + 1)

    return sorted(list(occupied_cells))


def get_answers_4(target_num):
    image = Image.open("0.png")
    image = np.asarray(image)
    result = model.predict(image)
    boxes = result[0].boxes.data

    target_index = []
    count = 0
    for num in result[0].boxes.cls:
        if num == target_num:
            target_index.append(count)
        count += 1

    for i in target_index:
        target_box = boxes[i]
        p1, p2 = (int(target_box[0]), int(target_box[1])
                  ), (int(target_box[2]), int(target_box[3]))
        x1, y1 = p1
        x2, y2 = p2

    answers = []
    count = 0
    for i in target_index:
        target_box = boxes[i]
        p1, p2 = (int(target_box[0]), int(target_box[1])
                  ), (int(target_box[2]), int(target_box[3]))
        x1, y1 = p1
        x4, y4 = p2
        x2 = x4
        y2 = y1
        x3 = x1
        y3 = y4
        xys = [x1, y1, x2, y2, x3, y3, x4, y4]

        four_cells = []
        for i in range(4):
            x = xys[i*2]
            y = xys[(i*2)+1]

            if x < 112.5 and y < 112.5:
                four_cells.append(1)
            if 112.5 < x < 225 and y < 112.5:
                four_cells.append(2)
            if 225 < x < 337.5 and y < 112.5:
                four_cells.append(3)
            if 337.5 < x <= 450 and y < 112.5:
                four_cells.append(4)

            if x < 112.5 and 112.5 < y < 225:
                four_cells.append(5)
            if 112.5 < x < 225 and 112.5 < y < 225:
                four_cells.append(6)
            if 225 < x < 337.5 and 112.5 < y < 225:
                four_cells.append(7)
            if 337.5 < x <= 450 and 112.5 < y < 225:
                four_cells.append(8)

            if x < 112.5 and 225 < y < 337.5:
                four_cells.append(9)
            if 112.5 < x < 225 and 225 < y < 337.5:
                four_cells.append(10)
            if 225 < x < 337.5 and 225 < y < 337.5:
                four_cells.append(11)
            if 337.5 < x <= 450 and 225 < y < 337.5:
                four_cells.append(12)

            if x < 112.5 and 337.5 < y <= 450:
                four_cells.append(13)
            if 112.5 < x < 225 and 337.5 < y <= 450:
                four_cells.append(14)
            if 225 < x < 337.5 and 337.5 < y <= 450:
                four_cells.append(15)
            if 337.5 < x <= 450 and 337.5 < y <= 450:
                four_cells.append(16)
        answer = get_occupied_cells(four_cells)
        count += 1
        for ans in answer:
            answers.append(ans)
    answers = sorted(list(answers))
    return list(set(answers))


def solve_recaptcha(driver):
    go_to_recaptcha_iframe1(driver)

    # کلیک روی چک باکس کپچا
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, '//div[@class="recaptcha-checkbox-border"]'))).click()

    go_to_recaptcha_iframe2(driver)

    count_solve = 0
    while True:
        try:
            # Skipping if it is a 4x4 captcha...will be implementing it later on .
            while True:
                reload = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'recaptcha-reload-button')))
                title_wrapper = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'rc-imageselect')))

                target_num = get_target_num(driver)

                if target_num == 1000:
                    print("skipping")
                    reload.click()
                elif "squares" in title_wrapper.text:
                    print("Square captcha found....")
                    img_urls = get_all_captcha_img_urls(driver)
                    download_img(0, img_urls[0])
                    answers = get_answers_4(target_num)
                    if len(answers) >= 1 and len(answers) < 16:
                        captcha = "squares"
                        break
                    else:
                        reload.click()
                elif "none" in title_wrapper.text:
                    print("found a 3x3 dynamic captcha")
                    img_urls = get_all_captcha_img_urls(driver)
                    download_img(0, img_urls[0])
                    answers = get_answers(target_num)
                    if len(answers) > 2:
                        captcha = "dynamic"
                        break
                    else:
                        reload.click()
                else:
                    print("found a 3x3 one time selection captcha")
                    img_urls = get_all_captcha_img_urls(driver)
                    download_img(0, img_urls[0])
                    answers = get_answers(target_num)
                    if len(answers) > 2:
                        captcha = "selection"
                        break
                    else:
                        reload.click()
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                    (By.XPATH, '(//div[@id="rc-imageselect-target"]//td)[1]')))

            if captcha == "dynamic":
                for answer in answers:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                        (By.XPATH, f'(//div[@id="rc-imageselect-target"]//td)[{answer}]'))).click()
                while True:
                    before_img_urls = img_urls
                    while True:
                        is_new, img_urls = get_all_new_dynamic_captcha_img_urls(
                            answers, before_img_urls, driver)
                        if is_new:
                            break

                    new_img_index_urls = []
                    for answer in answers:
                        new_img_index_urls.append(answer-1)
                    new_img_index_urls

                    for index in new_img_index_urls:
                        download_img(index+1, img_urls[index])
                    while True:
                        try:
                            for answer in answers:
                                main_img = Image.open("0.png")
                                new_img = Image.open(f"{answer}.png")
                                location = answer
                                paste_new_img_on_main_img(
                                    main_img, new_img, location)
                            break
                        except:
                            while True:
                                is_new, img_urls = get_all_new_dynamic_captcha_img_urls(
                                    answers, before_img_urls, driver)
                                if is_new:
                                    break
                            new_img_index_urls = []
                            for answer in answers:
                                new_img_index_urls.append(answer-1)

                            for index in new_img_index_urls:
                                download_img(index+1, img_urls[index])

                    answers = get_answers(target_num)

                    if len(answers) >= 1:
                        for answer in answers:
                            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                                (By.XPATH, f'(//div[@id="rc-imageselect-target"]//td)[{answer}]'))).click()
                    else:
                        break
            elif captcha == "selection" or captcha == "squares":
                for answer in answers:
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                        (By.XPATH, f'(//div[@id="rc-imageselect-target"]//td)[{answer}]'))).click()

            verify = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
                (By.ID, "recaptcha-verify-button")))
            verify.click()

            # check solve
            try:
                go_to_recaptcha_iframe1(driver)
                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//span[contains(@class, "recaptcha-checkbox-checked")]')))
                print("solved")
                driver.switch_to.default_content()
                break
            except:
                go_to_recaptcha_iframe2(driver)
        except Exception as e:
            print(e)
