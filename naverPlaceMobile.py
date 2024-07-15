from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# 네이버 지도에서 음식점을 검색하고 리뷰를 스크래핑하는 함수
def scrapeNaverRestrantId(search_query):
    # Selenium 웹드라이버 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 네이버 지도 페이지 열기
    driver.get("https://m.map.naver.com/search2/search.naver?query=" + search_query)
    time.sleep(1)
    # 페이지 소스 가져오기
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    elements = soup.find_all('li', class_='_lazyImgContainer', attrs={'data-id': True})

    data_ids = [li['data-id'] for li in elements]
    print(data_ids)
    print(len(data_ids))
    # 웹 드라이버 종료
    driver.quit()

    return data_ids, len(data_ids)

def scrapeNaver(id):
    # Selenium 웹드라이버 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 브라우저 창을 띄우지 않음
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 네이버 지도 페이지 열기
    # driver.get("https://pcmap.place.naver.com/restaurant/1221548859/home")
    driver.get("https://pcmap.place.naver.com/restaurant/" + id + "/home")
    # 페이지 소스 가져오기
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    # 별점
    starsScore = ""
    target_span = soup.find('span', class_='place_blind', string='별점')
    if target_span:
        # 다음 sibling 태그인 문자열 추출
        starsScore = target_span.find_next_sibling(string=True)
        print(starsScore)
    else:
        print("해당 조건을 만족하는 요소를 찾을 수 없습니다.")

    # 방문자 리뷰
    visitor_review = ""
    visitor_element = soup.find('a', string=lambda text: text and '방문자 리뷰' in text)

    if visitor_element:
        # 텍스트에서 숫자만 추출하기
        visitor_text = visitor_element.text.strip()
        visitor_review = ''.join(filter(str.isdigit, visitor_text))
        print(f"방문자 리뷰 숫자: {visitor_review}")
    else:
        print("방문자 리뷰를 포함한 요소를 찾을 수 없습니다.")

    # 블로그 리뷰
    blog_review = ""
    blog_element = soup.find('a', string=lambda text: text and '블로그 리뷰' in text)

    if blog_element:
        # 텍스트에서 숫자만 추출하기
        blog_text = blog_element.text.strip()
        blog_review = ''.join(filter(str.isdigit, blog_text))
        print(f"블로그 리뷰 숫자: {blog_review}")
    else:
        print("블로그 리뷰를 포함한 요소를 찾을 수 없습니다.")

    return starsScore, visitor_review, blog_review

# 측정 시작 시간 기록
start_time = time.time()
# 검색어 입력
search_query = "용산맛집"
ids, idCount = scrapeNaverRestrantId(search_query)
# time.sleep(5)
dic = {}
for id in ids:
    stars, visitor_review, blog_review = scrapeNaver(id)
    dic[id] = stars, visitor_review, blog_review
    print(dic)
# 측정 종료 시간 기록
end_time = time.time()
# 실행 시간 계산
execution_time = end_time - start_time
print(f"실행 시간: {execution_time}초")
# scrapeNaver("id")
