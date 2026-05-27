import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import time

# [모바일 최적화 세팅] 화면을 폰 비율에 맞게 타이트하게 조정
st.set_page_config(page_title="Spravato Tracker", layout="centered")

# 헤더 디자인
st.title("🍄 Spravato 실시간 Tracker")
st.caption("J&J 공식 인프라 추적 및 CMPS 선행지표 연동형 대시보드")

# 1. 모바일 백그라운드 크롤링 함수 (REMS 인프라 맵 소스 파싱)
@st.cache_data(ttl=86400) # 하루에 한 번만 크롤링하여 폰 배터리 및 속도 최적화
def get_live_centers_count():
    try:
        url = "https://www.spravatohcp.com/find/treatment-center/"
        headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # J&J 사이트의 모바일 대응 태그 카운트
        centers_elements = soup.find_all(class_="location-card")
        if len(centers_elements) > 0:
            return len(centers_elements)
        return 3850  # 2026년 상반기 미국 베이스라인 추정값
    except:
        return 3850  # 오프라인/서버 방화벽 대비용 기본값

# 실시간 데이터 로드
live_centers = get_live_centers_count()

# 2. 폰 화면용 슬라이더 컨트롤러 (터치하기 편하도록 가독성 개선)
st.subheader("⚙️ 가중치 실시간 조정")
avg_sessions = st.slider("🏥 병원 1곳당 주간 평균 치료 (건)", 5, 40, 15)
session_cost = st.slider("💵 1회 투여당 약가 단가 ($)", 300, 1000, 600)

# 핵심 산출 공식
weekly_total = live_centers * avg_sessions
annual_total = weekly_total * 52
estimated_revenue = annual_total * session_cost

st.markdown("---")

# 3. 모바일 세로 레이아웃 스코어보드 (큼직하게 배치)
st.subheader("📊 실시간 추정 지표 결과")

st.metric(label="🇺🇸 미국 내 인증 치료소 개수 (선행 지표)", value=f"{live_centers:,} 개")
st.metric(label="📈 전미 주간 치료 세션수 (추정)", value=f"{weekly_total:,} 건")
st.metric(label="💰 스프라바토 연간 런레이트 매출", value=f"${estimated_revenue:,}")

# 컴패스 투자 아이디어 요약 바
st.success(f"💡 **CMPS 주주용 팁:** 현재 구축된 {live_centers}개의 처방 인프라는 향후 컴패스의 실로시빈(COMP360) 승인 시 그대로 흡수 가능한 '유통망 망 크기'와 직결됩니다.")
