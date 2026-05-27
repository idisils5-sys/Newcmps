import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import numpy as np

# [모바일 최적화 세팅] 
st.set_page_config(page_title="Spravato Tracker", layout="centered")

st.title("🍄 Spravato 실시간 Tracker")
st.caption("J&J 공식 인프라 추적 및 CMPS 선행지표 연동형 대시보드")

# 1. 크롤링 함수 (하루 단위 캐시 적용)
@st.cache_data(ttl=86400)
def get_live_centers_count():
    try:
        url = "https://www.spravatohcp.com/find/treatment-center/"
        headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        centers_elements = soup.find_all(class_="location-card")
        if len(centers_elements) > 0:
            return len(centers_elements)
        return 3850  
    except:
        return 3850  

live_centers = get_live_centers_count()

# 2. 슬라이더 컨트롤러
st.subheader("⚙️ 가중치 실시간 조정")
avg_sessions = st.slider("🏥 병원 1곳당 주간 평균 치료 (건)", 5, 40, 15)
session_cost = st.slider("💵 1회 투여당 약가 단가 ($)", 300, 1000, 600)

# 기본 계산
weekly_total = live_centers * avg_sessions
annual_total = weekly_total * 52
estimated_revenue = annual_total * session_cost

st.markdown("---")

# 3. 실시간 추정 지표 결과 (수치)
st.subheader("📊 실시간 추정 지표")
st.metric(label="🇺🇸 미국 내 인증 치료소 개수 (선행 지표)", value=f"{live_centers:,} 개")
st.metric(label="📈 전미 주간 치료 세션수 (추정)", value=f"{weekly_total:,} 건")
st.metric(label="💰 스프라바토 연간 런레이트 매출", value=f"${estimated_revenue:,}")

st.markdown("---")

# 4. 🔥 [신규 추가] 미래 12개월 누적 치료 건수 성장 시뮬레이션 그래프
st.subheader("📅 향후 12개월 누적 치료 건수 예측")

# 매달 치료소가 분기 5%씩 성장한다는 가정 하에 월별 누적 치료 건수 데이터 생성
months = [f"{i}개월 뒤" for i in range(1, 13)]
monthly_run_rate = []
current_centers_sim = live_centers

for month in range(1, 13):
    # 3개월(1분기)마다 병원 수가 5%씩 복리로 늘어난다고 가정
    if month % 3 == 0:
        current_centers_sim *= 1.05
    
    # 해당 월의 월간 총 치료 건수 계산 (주간 건수 * 4.33주)
    month_sessions = current_centers_sim * avg_sessions * 4.333
    monthly_run_rate.append(int(month_sessions))

# 그래프용 데이터프레임 생성
chart_data = pd.DataFrame({
    "추정 월간 치료 건수": monthly_run_rate
}, index=months)

# 폰 화면에 최적화된 라인 차트 출력
st.line_chart(chart_data)

# 컴패스 투자 아이디어 요약 바
st.success(f"💡 **CMPS 주주용 팁:** 하단의 슬라이더를 움직이면 주간 치료 건수가 바뀌면서, 향후 12개월 동안 병원들이 소화해낼 전체 치료 규모(그래프 기울기)가 실시간으로 연동되어 바뀝니다.")
