import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
import ssl

def get_diet():
    url = "https://www.kongju.ac.kr/KNU/16865/subview.do"
    context = ssl._create_unverified_context()
    context.set_ciphers('DEFAULT@SECLEVEL=1:ALL')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=context, timeout=15) as response:
            html = response.read().decode('utf-8')
        
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        
        # 1. 평일 이름표 (5일)
        headers_list = ['월요일', '화요일', '수요일', '목요일', '금요일']
        rows = []
        for tr in table.find('tbody').find_all('tr'):
            cells = []
            for td in tr.find_all('td'):
                raw_text = td.get_text(separator='|', strip=True).replace('\r', '')
                menu_items = [item.strip() for item in raw_text.split('|') if item.strip()]
                formatted_menu = "".join(['<div style="white-space: nowrap; margin-bottom: 5px;">' + m + '</div>' for m in menu_items])
                cells.append(formatted_menu)
            
            # 2. 데이터 개수에 따라 평일(5일치)만 잘라내기
            if len(cells) == 7: # [월~일]
                rows.append(cells[:5])
            elif len(cells) == 8: # [구분, 월~일]
                rows.append(cells[1:6])

        return pd.DataFrame(rows, columns=headers_list)

    except Exception as e:
        print("🚨 에러 발생:", e)
        return None

def save_to_html(df):
    if df is None or df.empty:
        print("❌ 저장할 데이터가 없습니다.")
        return
    
    # CSS 스타일을 한 줄씩 안전하게 합칩니다. (SyntaxError 방지)
    style = "<style>"
    style += "body { font-family: 'Malgun Gothic', sans-serif; padding: 40px; background-color: #f4f7f6; }"
    style += ".container { width: 98%; max-width: 1200px; margin: auto; background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); overflow-x: auto; }"
    style += "h1 { color: #004ea2; text-align: center; margin-bottom: 20px; }"
    style += "table { width: 100%; border-collapse: collapse; }"
    style += "th, td { border: 1px solid #eee; padding: 15px; text-align: center; vertical-align: top; }"
    style += "th { background-color: #004ea2; color: white; width: 20%; }" # 5일이라 20%씩
    style += "td { color: #444; font-size: 0.95em; }"
    style += "tr:hover { background-color: #f9f9f9; }"
    style += "</style>"
    
    # HTML 구성 요소 준비
    table_html = df.to_html(index=False, escape=False)
    now_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')
    
    # 전체 HTML 조립 (문자열 더하기 방식)
    html = '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">' + style + '</head>'
    html += '<body><div class="container"><h1>🏫 주간 평일 식단표</h1>' + table_html
    html += '<p style="text-align:right; color:#888;">업데이트: ' + now_time + '</p></div></body></html>'
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✨ 미션 성공! 토/일 제외하고 평일만 아주 깔끔하게 나옵니다.")

# 실행
df = get_diet()
save_to_html(df)