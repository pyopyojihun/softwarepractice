import streamlit as st

st.title(" 단위 변환기 (km/h ↔ mpg)")

# 입력값 (기본값 0.0)
value = st.number_input("값을 입력하세요", value=0.0, step=1.0)

# 결과 초기화
result = None

# 버튼
col1, col2 = st.columns(2)

with col1:
    if st.button("km/h → mpg"):
        result = value * 2.352

with col2:
    if st.button("mpg → km/h"):
        result = value / 2.352

# 결과 출력
if result is not None:
    st.success(f"결과: {result:.4f}")
