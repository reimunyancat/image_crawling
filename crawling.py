import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from Scripts.fun import create_save_folder, image_limit_check, file_extention_f, image_download, error

pause = 0.5
click_pause = 0.4
scroll_pause_time = 1.7
success_count = 0

# HTTP 헤더 설정
opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')]
urllib.request.install_opener(opener)

while True:
    query = input("검색어 입력: ")

    create_save_folder(query)

    # 이미지 개수 입력
    num_images = int(input("수집할 이미지 개수 입력: "))

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://www.google.com/imghp")

    # 검색어 입력 및 검색 수행
    search_bar = driver.find_element(By.NAME, "q")
    search_bar.send_keys(query)
    search_bar.submit()
    time.sleep(pause)

    def scroll_and_load():
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                try:
                    driver.find_element(By.CSS_SELECTOR, ".RVQdVd").click()
                except:
                    try:
                        driver.find_element(By.CSS_SELECTOR, ".mye4qd").click()
                    except:
                        break
            last_height = new_height

    scroll_and_load()
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(1)

    # 이미지 요소 탐색
    images = driver.find_elements(By.CSS_SELECTOR, ".YQ4gaf")
    print(f"총 {len(images)}개의 이미지를 찾았습니다.")

    # 이미지 다운로드
    for i in range(0, num_images):
        if image_limit_check(i, num_images, images):
            break

        try:
            # 이미지를 클릭하여 큰 이미지가 표시되도록 함
            img_element = driver.find_elements(By.CSS_SELECTOR, ".mNsIhb")[i]
            driver.execute_script("arguments[0].click();", img_element)
            time.sleep(click_pause)

            # 큰 이미지 URL 가져오기
            original_img_element = driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div/div[3]/div[1]/a/img[1]')
            original_img_src = original_img_element.get_attribute('src')

            # 파일명 설정
            filename = file_extention_f(original_img_src, query, i)

            # 이미지 다운로드
            image_download(original_img_src, filename, query, i, num_images)
            success_count += 1

        except NoSuchElementException:
            try:
                print(f"{i+1}번째 이미지 처리 중 오류 발생: NoSuchElementException\n다시 시도합니다.")
                original_img_element = driver.find_element(By.XPATH, '/html/body/div[2]/c-wiz/div[3]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/c-wiz/div/div/div/div/div[3]/div[1]/a/img[1]')
                original_img_src = original_img_element.get_attribute('src')

                filename = file_extention_f(original_img_src, query, i)

                image_download(original_img_src, filename, query, i, num_images)
                success_count += 1
            except Exception as e:
                error(filename, query, i, num_images, e)

        except Exception as e:
            error(filename, query, i, num_images, e)

    driver.quit()
    print(f"{query} 검색어 이미지 수집 완료. 성공한 이미지 수: {success_count}")
    print("작업 완료 'exit' 입력시 종료 아니면 다시 반복합니다.")
    wa = input()
    if wa == 'exit':
        print("종료중...")
        break
