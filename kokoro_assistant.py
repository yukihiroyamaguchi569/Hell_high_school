import streamlit as st
from openai import OpenAI
from pathlib import Path

# OpenAI APIキーをsecretsから取得
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 画像のパスを設定
AVATAR_PATH = Path("images/src/kokoro_icon.png")

def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'openai_messages' not in st.session_state:
        st.session_state.openai_messages = [
            {"role": "assistant", "content": """
            こんにちは！看護師のこころです。
            何か質問があればお気軽にどうぞ♪

            """
            }
        ]
    if 'avatar_image' not in st.session_state:
        if AVATAR_PATH.exists():
            with open(AVATAR_PATH, "rb") as f:
                avatar_data = f.read()
            st.session_state.avatar_image = avatar_data
        else:
            st.session_state.avatar_image = None

def load_css():
    """Return CSS for the chat interface"""
    return """
    <style>
        /* ベース背景色の設定 */
        .stApp {
            background-color: #212121 !important;
        }

        /* すべてのStreamlitコンテナに背景色を強制適用 */
        .stApp > header,
        .stApp > div:first-child,
        .stApp > div:nth-of-type(2),
        .element-container,
        div[data-testid="stToolbar"],
        .main .block-container,
        section[data-testid="stSidebar"],
        .title-container,
        .message-container,
        .chat-container,
        .stMarkdown,
        .row-widget {
            background-color: #212121 !important;
        }

        /* ヘッダーとデプロイボタンを非表示 */
        header, .stDeployButton {
            display: none !important;
        }
        
        /* メッセージコンテナのスタイル */
        .message-container {
            display: flex;
            margin: 0 auto;
            padding: 18px 0.75rem;
            width: 100%;
            font-size: 1rem;
        }

        /* ユーザーメッセージのスタイル */
        .user-message-container {
            justify-content: flex-end !important;
            margin-left: auto;
            width: 100%;
        }
        
        .user-message {
            background-color: #2F2F2F;
            padding: 1rem;
            border-radius: 10px;
            color: white;
            max-width: 70%;
            margin-left: auto;
        }
        
        /* アシスタントメッセージのスタイル */
        .assistant-message-container {
            justify-content: flex-start;
            width: 100%;
        }
        
        .assistant-message {
            background-color: #383838;
            padding: 1rem;
            border-radius: 10px;
            color: white;
            max-width: 70%;
            margin-right: auto;
        }

        .message-text {
            margin: 0;
            padding: 0;
        }

        /* 入力フィールドのスタイル */
        .stTextArea > div > div > textarea {
            background-color: #2F2F2F !important;
            color: white !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 15px 20px !important;
            font-size: 16px;
            resize: none !important;  /* リサイズハンドルを非表示 */
        }

        /* プレースホルダーテキストの色 */
        .stTextArea > div > div > textarea::placeholder {
            color: #888 !important;
        }

        /* フォーカス関連のスタイル */
        .stTextArea div[data-focus="true"],
        .stTextArea div[data-focus="true"] > textarea,
        textarea:focus-visible,
        textarea:focus {
            outline: none !important;
            box-shadow: none !important;
            border: none !important;
        }

        /* タイトルコンテナのスタイル */
        .title-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 150px;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .main-title {
            color: white;
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .subtitle {
            color: #888;
            font-size: 1rem;
            max-width: 600px;
            text-align: center;
        }

        /* その他の必要なスタイル */
        .chat-container {
            margin-bottom: 150px;
            padding-bottom: 20px;
            overflow-y: auto;
        }
        
        .avatar-image {
            width: 40px !important;
            height: 40px !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* 入力フィールドのコンテナの調整 */
        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #212121;
            padding: 1rem;
            z-index: 1000;
            border-top: 1px solid #383838;
        }

        /* スピナーコンテナのスタイル */
        .spinner-container {
            position: fixed;
            bottom: 120px;
            left: 20px;
            transform: none;
            z-index: 1000;
            background-color: #212121;
            padding: 10px 15px;
            border-radius: 5px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        /* スピナーのアニメーション */
        .spinner {
            width: 16px;
            height: 16px;
            border: 3px solid #ff69b4;
            border-top: 3px solid transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .spinner-text {
            color: #ff69b4;
            font-size: 14px;
        }

        /* メッセージエリアのスタイルを追加 */
        .messages-area {
            padding-bottom: 120px;
        }
    </style>
    """

def get_chat_response(messages):
    """Get response from OpenAI API"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"エラーが発生しました: {str(e)}")
        return None

def format_message(role, content, container):
    """Format message with Streamlit components"""
    if role == "user":
        container.markdown(f"""
        <div class="message-container user-message-container">
            <div class="user-message">
                <p class="message-text">{content}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        cols = container.columns([1, 15])
        
        with cols[0]:
            if st.session_state.avatar_image:
                st.image(st.session_state.avatar_image, width=40)
        
        with cols[1]:
            st.markdown(f"""
            <div class="message-container assistant-message-container">
                <div class="assistant-message">
                    <p class="message-text">{content}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

def handle_submit():
    current_input = st.session_state["user_input_field"]
    
    if current_input.strip():
        # スピナーを表示するためのプレースホルダー
        spinner_container = st.empty()
        
        with spinner_container.container():
            st.markdown("""
                <div class="spinner-container">
                    <div class="spinner"></div>
                    <div class="spinner-text">こころが入力中...</div>
                </div>
            """, unsafe_allow_html=True)
            
            user_message = {
                "role": "user",
                "content": current_input
            }
            st.session_state.messages.append(user_message)
            st.session_state.openai_messages.append({
                "role": "user",
                "content": current_input
            })
            
            # AIの応答を取得
            ai_response = get_chat_response(st.session_state.openai_messages)
            
            if ai_response:
                assistant_message = {
                    "role": "assistant",
                    "content": ai_response
                }
                st.session_state.messages.append(assistant_message)
                st.session_state.openai_messages.append({
                    "role": "assistant",
                    "content": ai_response
                })
        
        # スピナーを非表示にする
        spinner_container.empty()
        
        # 入力フィールドをクリア
        st.session_state["user_input_field"] = ""

def main():
    st.set_page_config(
        page_title="看護師こころ",
        page_icon="👩‍⚕️",
        layout="wide",
        menu_items={},
        initial_sidebar_state="collapsed"
    )
    
    # 即座に背景色を設定
    st.markdown("""
        <style>
        body {
            background-color: #212121 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    init_session_state()
    st.markdown(load_css(), unsafe_allow_html=True)
    
    # メインコンテンツエリア
    # st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # メッセージがない場合のみタイトルと説明を表示
    if not st.session_state.messages:
        # より均等な配置のためのcolumns設定
        col1, col2, col3 = st.columns([2, 1, 2])  # 比率を調整
        with col2:
            # 画像のサイズを小さくして上部の空白を減らす
            st.image("src/images/kokoro.webp", width=200)  # 300から200に変更
       
        st.markdown("""
            <div style="background-color: #212121;">
                <div class="title-container" style="height: 150px;"> 
                    <div class="main-title">看護師 こころ</div>
                    <div class="subtitle">
                        強力な助っ人を得た！<BR>
                        分からないことは何でも尋ねてみよう<BR>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # チャットメッセージの表示エリア
    chat_container = st.container()
    
    # メッセージの表示
    for msg in st.session_state.messages:
        format_message(msg['role'], msg['content'], chat_container)
    
    # 入力フィールド
    user_input = st.chat_input(
        placeholder="ここに入力",
    )
    
    if user_input:
        # まずUIにユーザーメッセージを表示
        format_message("user", user_input, chat_container)
        
        with st.spinner("こころが考え中..."):
            # 次にセッションステートを更新
            user_message = {
                "role": "user",
                "content": user_input
            }
            st.session_state.messages.append(user_message)
            st.session_state.openai_messages.append(user_message)
            
            # AIの応答を取得して表示
            ai_response = get_chat_response(st.session_state.openai_messages)
            if ai_response:
                assistant_message = {
                    "role": "assistant",
                    "content": ai_response
                }
                st.session_state.messages.append(assistant_message)
                st.session_state.openai_messages.append(assistant_message)
                format_message("assistant", ai_response, chat_container)

if __name__ == "__main__":
    main()
