# pip3 install Flask
# pip3 install selenium
# pip3 install webdriver_manager
# pip3 install beautifulsoup4
import re

from flask import Flask, request, jsonify, render_template
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

app = Flask(__name__)
# 메인 페이지 라우팅
@app.route('/')
def index():
    return render_template('/index.html')


def getPlaceCode(marker_elements):
    marker_dict = {}
    for marker in marker_elements:
        marker_id = marker.get('id')
        if marker_id:
            marker_number = marker_id.split('-')[-1]
            # Find the marker_title element under this marker element
            marker_title_element = marker.find_next(class_='marker_title')
            if marker_title_element:
                marker_title_text = marker_title_element.get_text(strip=True)
                if marker_title_text:
                    marker_dict[marker_number] = marker_title_text
    return marker_dict

def getContents(driver, scroll_container):
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
        if stars_score == "":
            stars_score = "-"
        item_dict['stars_score'] = stars_score

        review_text = ""
        for span in li.find_all('span'):
            # span의 contents를 확인하여 '리뷰'를 포함하는지 검사
            span_text = ''.join([str(content) for content in span.contents])
            if '리뷰 ' in span_text:
                review_text = span.get_text(strip=True)
                break
                # print(span.get_text(strip=True))
        # review_target = li.find('span', string=lambda text: text and text.strip().startswith('리뷰 '))
        # review_text = review_target.text.strip() if review_target else ""
        # review_count = ''.join(filter(str.isdigit, review_text))
        # 정규 표현식을 사용하여 숫자와 그 뒤의 '+'를 추출
        match = re.search(r'\d+\+?', review_text)
        review_count = "-"
        if match:
            review_count = match.group()
        print(review_count)
        # if review_count == "":
        #     review_count = "-"
        item_dict['review_number'] = review_count

        # 결과 딕셔너리를 결과 리스트에 추가
        results.append(item_dict)

    return results

# 네이버 지도에서 음식점을 검색하고 리뷰를 스크래핑하는 함수
@app.route('/scrapeNaverPlace', methods=['POST'])
def scrapeNaverPlace(search_query):
    # search_query = request.json.get('searchText')
    # Selenium 웹드라이버 설정
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 네이버 지도 페이지 열기
    driver.get("https://map.naver.com/p/search/" + search_query)

    try:
        # salt-search-marker 요소가 나타날 때까지 기다림 (최대 3초)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[id^="salt-search-marker"]'))
        )
    except TimeoutException:
        return "Timeout"
        # 에러 발생 시 대응할 코드
    except NoSuchElementException:
        return "NoSuchElementException"
    finally:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        marker_elements = soup.select('[id^="salt-search-marker"]')
        if not marker_elements:
            # 드라이버 종료
            driver.quit()
            return {}
        # 음식점 코드와 이름 수집
        marker_dict = getPlaceCode(marker_elements)

        try:
            search_iframe = driver.find_element(By.ID, 'searchIframe')
            driver.switch_to.frame(search_iframe)

            # id가 '_pcmap_list_scroll_container'인 div 태그 찾기
            scroll_container = driver.find_element(By.ID, '_pcmap_list_scroll_container')

            # 음식점 리뷰와 별점 수집
            placeContents = getContents(driver, scroll_container)

        finally:
            # 드라이버 종료
            driver.quit()

        merged_list = []
        for item in placeContents:
            for marker_key, marker_value in marker_dict.items():
                if item['name'] == marker_value:
                    # 일치하는 항목을 찾으면 병합
                    merged_item = {'id': marker_key}
                    merged_item.update(item)
                    merged_list.append(merged_item)
                    break

        # 결과를 JSON 형태로 반환
        return merged_list

# 버튼 클릭 시 실행되는 라우트
@app.route('/run-python', methods=['POST'])
def run_python():
    if request.headers['Content-Type'] == 'application/json':
        search_text = request.json.get('searchText')
        result = scrapeNaverPlace(search_text)
        # JSON 데이터를 사용하여 원하는 작업을 수행
        return jsonify(result=result)
    else:
        return jsonify(error='Did not attempt to load JSON data because the request Content-Type was not application/json.'), 400

if __name__ == '__main__':
    app.run(debug=True)