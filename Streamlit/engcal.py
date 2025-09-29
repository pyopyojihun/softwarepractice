import streamlit as st
import re, math

# --- 상태 관리 초기화 ---
if "expr" not in st.session_state:
    st.session_state["expr"] = "0"

# --- 유틸 함수 (코드 그대로 재활용) ---
def preprocess(expr: str) -> str:
    expr = expr.replace("π", "pi")
    expr = expr.replace("^", "**")
    expr = expr.replace("ln(", "log(")
    expr = expr.replace(" ", "")

    expr = re.sub(r'(\d)\(', r'\1*(', expr)
    expr = re.sub(r'\)(\d)', r')*\1', expr)
    expr = re.sub(r'\)\(', r')*(', expr)
    expr = re.sub(r'(\d)(?=(sin|cos|tan|sqrt|log|abs)\()', r'\1*', expr)
    return expr

def safe_eval(expr: str):
    safe_env = {"__builtins__": None}
    allowed = {
        "sin": lambda x: math.sin(math.radians(x)),
        "cos": lambda x: math.cos(math.radians(x)),
        "tan": lambda x: math.tan(math.radians(x)),
        "sqrt": math.sqrt,
        "log": math.log,
        "abs": abs,
        "pi": math.pi,
        "e": math.e,
    }

    # 허용된 이름 외 금지
    temp = expr
    for name in allowed.keys():
        temp = re.sub(rf'\b{name}\b', '', temp)
    if re.search(r'[A-Za-z_]', temp):
        return "Error"

    try:
        val = eval(expr, safe_env, allowed)
        if isinstance(val, (int, float)) and math.isfinite(val):
            return str(val)
        else:
            return "Error"
    except ZeroDivisionError:
        return "Error: div by 0"
    except:
        return "Error"

# --- UI 구성 ---
st.title("📐 Streamlit 계산기")

# 현재 수식/결과창
st.text_input("수식 입력", value=st.session_state["expr"], key="expr_input")

# 버튼 패드
# 버튼 배열 (빈칸은 "")
button_grid = [
    ["7","8","9","/"],
    ["4","5","6","*"],
    ["1","2","3","-"],
    ["0",".","(",")"],
    ["sin(","cos(","tan(","sqrt("],
    ["log(","abs(","π","^"],
    ["Clear","Del","Run",""],
]


for row in button_grid:
    cols = st.columns(4)
    for i, label in enumerate(row):
        if label:  # 빈칸이 아닐 때만 버튼 생성
            if cols[i].button(label):
                if label == "Clear":
                    st.session_state["expr"] = "0"
                elif label == "Del":
                    txt = st.session_state["expr"][:-1]
                    st.session_state["expr"] = txt if txt else "0"
                elif label == "Run":
                    expr = preprocess(st.session_state["expr"])
                    st.session_state["expr"] = safe_eval(expr)
                elif label == "π":
                    st.session_state["expr"] += "pi" if st.session_state["expr"] != "0" else "pi"
                elif label == "^":
                    st.session_state["expr"] += "**"
                else:
                    if st.session_state["expr"] == "0":
                        st.session_state["expr"] = label
                    else:
                        st.session_state["expr"] += label


# 함수 버튼
funcs = ["sin(","cos(","tan(","sqrt(","log(","abs("]
cols = st.columns(len(funcs))
for i, f in enumerate(funcs):
    if cols[i].button(f):
        if st.session_state["expr"] == "0":
            st.session_state["expr"] = f
        else:
            st.session_state["expr"] += f

# 특수 버튼
if st.button("π"):
    if st.session_state["expr"] == "0":
        st.session_state["expr"] = "pi"
    else:
        st.session_state["expr"] += "pi"

if st.button("Clear"):
    st.session_state["expr"] = "0"

if st.button("Del"):
    txt = st.session_state["expr"][:-1]
    st.session_state["expr"] = txt if txt else "0"

if st.button("Run"):
    expr = preprocess(st.session_state["expr"])
    st.session_state["expr"] = safe_eval(expr)

# 결과 출력
st.subheader("결과")
st.write(st.session_state["expr"])
