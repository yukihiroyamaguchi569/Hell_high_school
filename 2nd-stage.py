import streamlit as st
from openai import OpenAI
from datetime import datetime
from pathlib import Path
import base64
import io
import tempfile
import os

# OpenAI APIキーをsecretsから取得
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 画像のパスを設定
AVATAR_PATH = Path("src/images/opening.png")

def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'openai_messages' not in st.session_state:
        st.session_state.openai_messages = [
            {"role": "system", "content": """
             GPTは黒水校長になりきってユーザーに問題を出します

            ### 質問
            下記の質問を順番に質問してください
            正解するまでは次の謎に進めません。正解しない限り次に進めません。
            正解は伝えません。

            質問：附設高校初代校長の名前は何や？
            答え：板垣政参（いたがきまさみつ）
            
            質問：附設高校の校章の花は何や？
            答え：芙蓉
             
            質問：2023年に瑞宝中綬章を受けた元校長は誰や？
            答え：吉川敦
            
            質問：町田校長は第何代校長や？
            答え：第11代校長
             
            質問：75周年事業の寄付金は6月19日現在いくら集まっとるか知っとるや？
            答え：75,368,404円
            注：この問題のみ参加者の答えが、正解より高いか低いかを教える
             
            質問：現在の場所に移転したのはいつや？
            答え：1968年
             
            質問：西鉄久留米から附設高校前に停まる西鉄バスの行き先番号は何番や？
            答え：２番と７番
            
            質問：附設の近くにあった生姜焼きの美味しいお店は何や？
            答え：一茶
             

            ###出題方法
            ヒントはださないでください
            答えを聞かれても教えてないでください

            ### 正誤の判定方法
            厳密に答えとあっていなくても正解とします

            ### 最後の会話
            参加者が全問正解したら、「ぐはぁぁ、まさか...まさか俺が...敗れるとは...！」<br><br>   
            というコメントをしてください。

            ### 口調
            久留米弁で挑発的な態度でしゃべってください。
            優しい言葉や丁寧な言葉は使わないでください。絶対に絶対に丁寧には喋らないでください
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
    if 'tts_enabled' not in st.session_state:
        st.session_state.tts_enabled = True

def generate_speech(text):
    """Generate speech from text using OpenAI TTS"""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",  # 男性の声で挑発的な感じ
            input=text,
            speed=0.9  # 少しゆっくりめで威厳のある感じ
        )
        
        # 音声データを一時ファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    except Exception as e:
        st.error(f"音声生成エラー: {str(e)}")
        return None

def load_css():
    """Return CSS for the chat interface"""
    return """
    <style>
        /* ベース背景色の設定 */
        .stApp {
            background-color: #212121 !important;
        }

        /* すべてのStreamlitコンテナに背景色を強制適用 */
        .stApp > header {
            background-color: #212121 !important;
        }

        .stApp > div:first-child {
            background-color: #212121 !important;
        }

        .stApp > div:nth-of-type(2) {
            background-color: #212121 !important;
        }

        .element-container {
            background-color: #212121 !important;
        }

        div[data-testid="stToolbar"] {
            background-color: #212121 !important;
        }
        
        /* ヘッダーを非表示にする */
        header {
            display: none !important;
        }

        .stDeployButton {
            display: none !important;
        }
        
        /* Streamlitのデフォルト背景色を上書き */
        .main .block-container {
            background-color: #212121 !important;
        }

        section[data-testid="stSidebar"] {
            background-color: #212121 !important;
        }
        
        /* タイトルコンテナのスタイル */
        .title-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 200px;
            text-align: center;
            margin-bottom: 2rem;
            background-color: #212121 !important;
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
        
        /* メッセージコンテナのスタイル */
        .message-container {
            display: flex;
            margin: 0 auto;
            padding: 18px 0.75rem;
            width: 100%;
            font-size: 1rem;
            background-color: #212121 !important;
        }

        /* レスポンシブパディング設定 */
        @media (min-width: 768px) {
            .message-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }

        @media (min-width: 1024px) {
            .message-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }

        @media (min-width: 1280px) {
            .message-container {
                padding-left: 1.25rem;
                padding-right: 1.25rem;
            }
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
        .stTextInput {
            position: relative;
            background-color: #212121;
        }

        /* 入力フィールドの背景を完全に設定 */
        .stTextInput > div {
            background-color: #212121 !important;
        }

        .stTextInput > div > div {
            background-color: #212121 !important;
        }

        /* 入力フィールドの基本スタイル */
        .stTextInput > div > div > input {
            background-color: #2F2F2F !important;
            color: white !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 15px 20px !important;
            font-size: 16px;
            box-shadow: none !important;
            outline: none !important;
        }

        /* 入力フィールドのホバー時とフォーカス時のスタイル */
        .stTextInput > div > div > input:hover,
        .stTextInput > div > div > input:focus {
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            background-color: #2F2F2F !important;
        }

        /* フォーカス時の赤い枠を削除 */
        .stTextInput div[data-focus="true"] {
            border-color: transparent !important;
            box-shadow: none !important;
            outline: none !important;
        }

        .stTextInput div[data-focus="true"] > input {
            border-color: transparent !important;
            box-shadow: none !important;
            outline: none !important;
        }

        /* Streamlitのデフォルトフォーカススタイルを上書き */
        :focus-visible {
            outline: none !important;
            box-shadow: none !important;
            border: none !important;
        }

        *:focus {
            outline: none !important;
            box-shadow: none !important;
            border: none !important;
        }

        /* チャットコンテナのスタイル */
        .chat-container {
            margin-bottom: 100px;
            padding-bottom: 20px;
            background-color: #212121 !important;
        }
        
        /* Streamlitのimage要素のスタイル */
        .avatar-image {
            width: 40px !important;
            height: 40px !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .avatar-image > div {
            margin: 0 !important;
        }
        
        /* スピナーの色を設定 */
        .stSpinner > div {
            border-color: white !important;
        }
        
        /* プレースホルダーテキストの色 */
        .stTextInput > div > div > input::placeholder {
            color: #888 !important;
        }
        
        /* フォーカス時のアウトラインを完全に削除 */
        div:focus, div:focus-visible {
            outline: none !important;
            border: none !important;
            box-shadow: none !important;
        }
        
        /* メインコンテンツエリアのパディング調整 */
        .main-content {
            padding-bottom: 80px;
            background-color: #212121 !important;
        }

        /* Streamlitデフォルトの余白を調整 */
        .stMarkdown {
            margin: 0 !important;
            padding: 0 !important;
            background-color: #212121 !important;
        }

        .row-widget {
            margin: 0 !important;
            padding: 0 !important;
            background-color: #212121 !important;
        }

    </style>
    """

def get_chat_response(messages):
    """Get response from OpenAI API"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
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
            
            # TTSが有効な場合、音声を生成して自動再生
            if st.session_state.tts_enabled and role == "assistant":
                audio_file = generate_speech(content)
                if audio_file:
                    with open(audio_file, "rb") as f:
                        audio_bytes = f.read()
                    
                    # Base64エンコードしてHTMLに埋め込み
                    audio_b64 = base64.b64encode(audio_bytes).decode()
                    
                    # 自動再生用のHTML
                    st.markdown(f"""
                    <audio autoplay style="display: none;">
                        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                    </audio>
                    <script>
                        // 自動再生を確実にするためのJavaScript
                        document.addEventListener('DOMContentLoaded', function() {{
                            const audio = document.querySelector('audio[autoplay]');
                            if (audio) {{
                                audio.play().catch(function(error) {{
                                    console.log('自動再生に失敗しました:', error);
                                }});
                            }}
                        }});
                    </script>
                    """, unsafe_allow_html=True)
                    
                    # 一時ファイルを削除
                    os.unlink(audio_file)

def handle_submit():
    """Handle message submission"""
    current_input = st.session_state["user_input_field"]
    
    if current_input.strip():
        user_message = {
            "role": "user",
            "content": current_input
        }
        st.session_state.messages.append(user_message)
        st.session_state.openai_messages.append({
            "role": "user",
            "content": current_input
        })
        
        with st.spinner("応答を生成中..."):
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
        
        st.session_state["user_input_field"] = ""

def main():
    st.set_page_config(
        page_title="問鬼",
        page_icon="🤖",
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
    
    # TTS設定のトグルボタン
    with st.sidebar:
        st.markdown("### 音声設定")
        tts_enabled = st.toggle("音声読み上げ", value=st.session_state.tts_enabled)
        if tts_enabled != st.session_state.tts_enabled:
            st.session_state.tts_enabled = tts_enabled
            st.rerun()
    
    # メインコンテンツエリア
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # メッセージがない場合のみタイトルと説明を表示
    if not st.session_state.messages:
            # より均等な配置のためのcolumns設定
        col1, col2, col3 = st.columns([2, 1, 2])  # 比率を[1, 2, 1]に変更してより中央に寄せる
        with col2:
            st.image("src/images/kurouzu-gate.jpg", width=400)
 
        st.markdown("""
            <div style="background-color: #212121;">
                <div class="title-container">
                    <div class="main-title">お前たちに私が倒せるかな？？</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # チャットメッセージの表示エリア
    chat_area = st.container()
    for msg in st.session_state.messages:
        format_message(msg['role'], msg['content'], chat_area)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 入力フィールド（固定位置）
    st.markdown("""
        <div class="input-container">
            <div style="max-width: 1000px; margin: 0 auto;">
    """, unsafe_allow_html=True)
    
    st.text_input(
        "メッセージを入力してください",
        key="user_input_field",
        on_change=handle_submit,
        label_visibility="collapsed"
    )
    
    st.markdown('</div></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()