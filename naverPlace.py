from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# 네이버 지도에서 음식점을 검색하고 리뷰를 스크래핑하는 함수
def scrape_naver_reviews(search_query):
    # Selenium 웹드라이버 설정
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 네이버 지도 페이지 열기
    driver.get("https://map.naver.com/p/search/" + search_query)
    time.sleep(2)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[id^="salt-search-marker"]'))
    )
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    canvas_container = soup.find('div', class_='mapboxgl-canvas-container')

    print(canvas_container)
    marker_elements = soup.select('[id^="salt-search-marker"]')
    cnt = 0
    for marker in marker_elements:
        cnt = cnt + 1
        marker_id = marker.get('id')
        if marker_id:
            marker_number = marker_id.split('-')[-1]
            print(f"Marker{cnt} ID Number: {marker_number}")

            # Find the marker_title element under this marker element
            marker_title_element = marker.find_next(class_='marker_title')
            if marker_title_element:
                marker_title_text = marker_title_element.get_text(strip=True)
                print(f"Marker{cnt} Title: {marker_title_text}")
    search_iframe = driver.find_element(By.ID, 'searchIframe')
    driver.switch_to.frame(search_iframe)

    # id가 '_pcmap_list_scroll_container'인 div 태그 찾기
    scroll_container = driver.find_element(By.ID, '_pcmap_list_scroll_container')
    # 스크롤을 내리는 함수
    def scroll_down_little_by_little():
        current_scroll_position = driver.execute_script("return arguments[0].scrollTop", scroll_container)
        scroll_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
        new_scroll_position = current_scroll_position + 1000  # 1000 픽셀씩 내립니다.
        if new_scroll_position > scroll_height:
            return False  # 스크롤이 이미 끝까지 내려간 경우
        driver.execute_script("arguments[0].scrollTop = arguments[1]", scroll_container, new_scroll_position)
        return True

    # 스크롤을 여러 번 반복해서 조금씩 내리기
    while scroll_down_little_by_little():
        time.sleep(0.1)  # 각 스크롤 조작 사이에 충분한 시간을 줍니다.

    # 페이지 소스 가져오기
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    li_list = soup.find('ul').find_all("li")
    results = []

    for li in li_list:
        item_dict = {}
        # 가게명
        name_target = li.find("span", class_="place_bluelink")
        name = name_target.text if name_target else ""
        item_dict['name'] = name.strip()

        # 별점
        stars_score_target = li.find('span', class_='place_blind', string='별점')
        stars_score = stars_score_target.find_next_sibling(string=True).strip() if stars_score_target else ""
        item_dict['stars_score'] = stars_score

        # 리뷰 숫자를 포함하는 span 요소 찾기
        review_target = li.find('span', string=lambda text: text and text.strip().startswith('리뷰'))
        # print(f"{name}: {review_target}")
        review_text = review_target.text.strip() if review_target else ""
        review_count = ''.join(filter(str.isdigit, review_text))
        item_dict['review_number'] = review_count

        # 결과 딕셔너리를 결과 리스트에 추가
        results.append(item_dict)

    # 드라이버 종료
    driver.quit()

    return results

# 측정 시작 시간 기록
start_time = time.time()
# 함수 사용 예제
search_query = "용산맛집"
results = scrape_naver_reviews(search_query)
print(results)
# 측정 종료 시간 기록
end_time = time.time()
# 실행 시간 계산
execution_time = end_time - start_time
print(f"실행 시간: {execution_time}초")