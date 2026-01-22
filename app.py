import streamlit as st
import google.generativeai as genai
import time
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 1. 페이지 설정 (최우선 실행)
st.set_page_config(
    page_title="🌟 AI 학습 친구",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 커스텀 CSS (접근성: 큰 글씨, 가독성 향상)
st.markdown("""
    <style>
    /* 메인 타이틀 크기 */
    .main h1 {
        font-size: 3rem !important;
        color: #2E5A88;
    }
    /* 대화창 텍스트 크기 */
    .stMarkdown p {
        font-size: 1.4rem !important;
        line-height: 1.6;
    }
    /* 버튼 크기 및 강조 */
    .stButton button {
        font-size: 1.2rem !important;
        padding: 0.5rem 1rem !important;
        border-radius: 10px !important;
    }
    /* 사이드바 텍스트 */
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 세션 상태 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'api_key' not in st.session_state:
    # .env 파일이나 환경 변수에서 기본값 가져오기
    st.session_state.api_key = os.getenv("GOOGLE_API_KEY", "")

# 4. 사이드바 구성
with st.sidebar:
    st.title("⚙️ 설정")
    
    # API 키 입력
    api_key_input = st.text_input(
        "🔑 Gemini API 키를 입력하세요",
        value=st.session_state.api_key,
        type="password",
        help="https://aistudio.google.com/app/apikey 에서 발급받을 수 있습니다."
    )
    
    if api_key_input:
        st.session_state.api_key = api_key_input
        st.success("✅ API 키가 설정되었습니다!")
    else:
        st.warning("⚠️ 서비스를 이용하려면 API 키가 필요합니다.")
        st.markdown("[여기서 API 키 발급받기](https://aistudio.google.com/app/apikey)")

    st.divider()

    # 학습 모드 선택
    st.subheader("📚 학습 모드")
    learning_mode = st.selectbox(
        "어떤 공부를 할까요?",
        ["자유 대화 💬", "읽기 연습 📖", "수학 연습 ➕", "생활 기술 🧼"]
    )

    # 대화 초기화 버튼
    if st.button("🔄 처음부터 다시 하기", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    
    # 성취도 표시 (칭찬 시스템)
    if len(st.session_state.messages) > 0:
        count = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.success(f"🎉 오늘 벌써 {count}번이나 공부했어요! 대단해요!")

# 5. 메인 화면 구성
st.title("🌟 AI 학습 친구")
st.markdown("### 안녕! 무엇을 도와줄까? 😊")

# 6. Gemini API 설정 및 시스템 프롬프트 정의
SYSTEM_INSTRUCTION = """
당신은 지적장애 학생을 돕는 'AI 학습 친구'라는 이름의 친절한 선생님입니다.

학습 모드 상황: {mode}

규칙:
1. 항상 아주 쉽고 짧은 문장을 사용하세요. (예: "이것은 사과예요." "잘했어요!")
2. 한 번에 하나씩만 물어보거나 설명하세요.
3. 긍정적이고 격려하는 표현을 많이 사용하세요. (이모지 적극 활용: 👏, 👍, ✨)
4. 어려운 단어는 쉬운 말로 풀어서 설명해 주세요.
5. 학생이 이해했는지 "알겠나요?" 또는 "한번 해볼까요?"라고 부드럽게 확인해 주세요.
6. 만약 위험하거나 나쁜 말을 들으면 부드럽게 화제를 돌려주세요.
"""

def get_system_prompt(mode):
    mode_desc = {
        "자유 대화 💬": "학생과 즐겁게 대화하며 친구가 되어주세요.",
        "읽기 연습 📖": "쉬운 문장이나 단어를 보여주고 함께 읽어보는 연습을 하세요. 짧은 동화 이야기를 들려주어도 좋습니다.",
        "수학 연습 ➕": "1부터 10 사이의 아주 쉬운 숫자 더하기나 빼기 문제를 내고 칭찬해 주세요.",
        "생활 기술 🧼": "손 씻기, 양치질하기, 옷 입기 등 생활 속에서 필요한 행동들을 순서대로 쉽게 알려주세요."
    }
    return SYSTEM_INSTRUCTION.format(mode=mode_desc.get(mode, "즐겁게 대화하세요."))

# 7. 대화 인터페이스 구현
# 이전 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("여기에 궁금한 것을 적어보세요!"):
    if not st.session_state.api_key:
        st.error("사이드바에 API 키를 먼저 입력해 주세요! 🔑")
    else:
        # 사용자 메시지 표시 및 저장
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Gemini 모델 호출
        try:
            genai.configure(api_key=st.session_state.api_key)
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=get_system_prompt(learning_mode)
            )
            
            # 안전 설정
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                # 대화 이력을 포함하여 요청 (간단하게 최근 요청만 전달하거나 전체 이력을 context로 활용 가능)
                # 여기서는 Streamlit의 chat 형식을 위해 간단히 처리
                response = model.generate_content(
                    prompt, 
                    safety_settings=safety_settings
                )
                
                # 타이핑 효과 (지적장애 학생을 위한 시각적 배려)
                for chunk in response.text.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            
            # AI 메시지 저장
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"아이쿠, 잠시 문제가 생겼어요: {str(e)}")
            st.info("💡 API 키가 올바른지 확인하거나 잠시 후 다시 시도해 보세요.")
