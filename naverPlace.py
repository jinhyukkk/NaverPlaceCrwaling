from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
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
    driver.get("https://map.naver.com/p/search/%EC%9A%A9%EC%82%B0%EB%A7%9B%EC%A7%91")
    # 페이지 소스 가져오기
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    next_iframe = driver.find_element(By.ID, 'searchIframe')

    # 해당 프레임으로 전환
    driver.switch_to.frame(next_iframe)
    # 여기서 프레임 내의 작업을 수행할 수 있습니다.
    # 예: 프레임 내부의 요소 찾기
    frame_element = driver.find_element(By.ID, '_pcmap_list_scroll_container')
    print(frame_element.text)


    element = soup.find('iframe', id='searchIframe')
    print(element)
    # 방문자 리뷰 추출
    visitor_reviews = soup.select("div.review_txt > p")
    visitor_review_texts = [review.get_text().strip() for review in visitor_reviews]

    # 블로그 리뷰 제목 추출
    blog_reviews = soup.select("div.blog_inner > a")
    blog_review_titles = [blog.get_text().strip() for blog in blog_reviews]

    # 드라이버 종료
    driver.quit()

    return visitor_review_texts, blog_review_titles

# 함수 사용 예제
search_query = "쌤쌤쌤"
visitor_reviews, blog_reviews = scrape_naver_reviews(search_query)

print("방문자 리뷰:")
for review in visitor_reviews:
    print("-", review)

print("\n블로그 리뷰 제목:")
for title in blog_reviews:
    print("-", title)
