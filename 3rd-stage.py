import streamlit as st
from openai import OpenAI
from pathlib import Path
import base64
import os
import time

# OpenAI APIキーを環境変数から取得（Render.com用）
def get_openai_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI APIキーが設定されていません。環境変数OPENAI_API_KEYを設定してください。")
        st.stop()
    return api_key

client = OpenAI(api_key=get_openai_api_key())

# 画像のパスを設定
AVATAR_PATH = Path("src/images/opening.png")

def load_prompt_from_file():
    """プロンプトをファイルから読み込む"""
    try:
        with open("prompt.txt", "r", encoding="utf-8") as f:
            prompt_content = f.read()
        return prompt_content
    except Exception as e:
        st.error(f"プロンプトファイルの読み込みエラー: {str(e)}")
        return None

def init_session_state():
    """Initialize session state variables"""
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'title'  
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'openai_messages' not in st.session_state:
        # プロンプトをファイルから読み込む
        prompt_content = load_prompt_from_file()
        if prompt_content:
            st.session_state.openai_messages = [
                {"role": "system", "content": prompt_content}
            ]
        else:
            # ファイル読み込みに失敗した場合はエラーメッセージを表示して終了
            st.error("プロンプトファイルが見つからないか、読み込めませんでした。prompt.txtファイルを確認してください。")
            st.stop()
    if 'avatar_image' not in st.session_state:
        if AVATAR_PATH.exists():
            with open(AVATAR_PATH, "rb") as f:
                avatar_data = f.read()
            st.session_state.avatar_image = avatar_data
        else:
            st.session_state.avatar_image = None
    if 'tts_enabled' not in st.session_state:
        st.session_state.tts_enabled = True
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False

def apply_pronunciation_guides(text):
    """読み方が難しい言葉にふりがなや読み方のヒントを付ける"""
    # 読み方マッピング辞書（漢字: 読み方の表記）
    pronunciation_map = {
        "源頼朝": "源頼朝みなもとのよりとも",
        "征夷大将軍": "せいいたいしょうぐん",
        "趣":"おもむき",
        "浪人生":"ろうにんせい",
        "板垣政参": "いたがきまさみつ",
        "瑞宝中綬章": "ずいほうちゅうじゅしょう",
        "裏店": "うらみせ",
        "肉飯": "にくめし",
        "男く祭": "おとこくさい",
        "芙蓉": "ふよう",
        "西鉄": "にしてつ",
        "久留米":"くるめ",
        "チーム1":"チームいち",
        "チーム2":"チームに",
        "チーム3":"チームさん",
        "チーム4":"チームよん",
        "チーム5":"チームご",
        "1192":"せんひゃくきゅうじゅうに",
        "2005":"にせんご",
        "1968":"せんきゅうひゃくろうじゅうはち",
        "吉川敦": "よしかわあつし",
        "黒水": "くろうず",
        "七福神":"しちふくじん", 
        "満々":"まんまん"

    }
    
    # 辞書内の各項目に対して読み方を追加
    for word, reading in pronunciation_map.items():
        if word in text and word != reading:  # 既に読み方が付いていない場合のみ
            text = text.replace(word, reading)
    
    return text

def generate_speech(text):
    """Generate speech from text using OpenAI TTS"""
    try:
        # 読み方ガイドを適用
        modified_text = apply_pronunciation_guides(text)
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="ash",
            input=modified_text,
            speed=1.0
        )
        
        return response.content
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
        
        /* st.chat_messageのスタイル調整 */
        .stChatMessage {
            background-color: #212121 !important;
        }
        
        /* ユーザーメッセージのスタイル */
        .stChatMessage[data-testid="chatMessage"] {
            background-color: #212121 !important;
        }
        
        /* アシスタントメッセージのスタイル */
        .stChatMessage[data-testid="chatMessage"] .stChatMessageContent {
            background-color: #383838 !important;
            color: white !important;
        }
        
        /* ユーザーメッセージのスタイル */
        .stChatMessage[data-testid="chatMessage"] .stChatMessageContent[data-testid="user"] {
            background-color: #2F2F2F !important;
            color: white !important;
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

        /* Streamlitデフォルトの余白を調整 */
        .stMarkdown {
            margin: 0 !important;
            padding: 0 !important;
            background-color: #212121 !important;
        }

        /* タイトル画面用のスタイル */
        .title-container {
            text-align: center;
            padding: 2rem;
        }
        .stButton > button {
            display: block;
            margin: 0 auto;
            padding: 0.5rem 2rem;
            font-size: 1.2rem;
            width: 200px;
        }
        /* 画像コンテナのスタイル */
        .block-container {
            max-width: 1800px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .center-text {
            text-align: center;
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

def convert_to_hiragana(text):
    """難しい漢字や固有名詞をひらがなに変換"""
    # 変換マッピング
    conversion_map = {
        "源頼朝": "みなもとのよりとも",
        "征夷大将軍": "せいいたいしょうぐん",
        "鎌倉幕府": "かまくらばくふ",
        "裏店": "うらみせ",
        "男く祭": "おとこくさい",
        "芙蓉": "ふよう"
    }
    
    # 表示用テキストと音声用テキストを分ける
    display_text = text
    speech_text = text
    
    for word, reading in conversion_map.items():
        if word in speech_text:
            speech_text = speech_text.replace(word, reading)
    
    return display_text, speech_text

def format_message(role, content, container, is_new_message=False):
    """Format message with Streamlit components"""
    if role == "user":
        with container.chat_message("user"):
            st.write(content)
    else:
        # 表示用テキストと音声用テキストを分ける
        display_text, speech_text = convert_to_hiragana(content)
        
        # TTSが有効で、新しいメッセージの場合のみ音声を先に生成・再生
        if st.session_state.tts_enabled and is_new_message:
            audio_bytes = generate_speech(speech_text)  # ひらがな変換したテキストを使用
            if audio_bytes:
                # Base64エンコードしてHTMLに埋め込み
                audio_b64 = base64.b64encode(audio_bytes).decode()
                
                # 音声を先に再生
                container.markdown(f"""
                <audio autoplay style="display: none;">
                    <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                </audio>
                """, unsafe_allow_html=True)
        
        # 音声再生後に元のテキストを表示
        with container.chat_message("assistant", avatar=st.session_state.avatar_image):
            st.write(display_text)  # 元のテキストを表示

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
        
        # スピナーを削除して画面が暗くならないようにする
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

def display_title():
    """タイトル画面を表示"""
    # カラムの比率を変更して中央の列をより大きく
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("src/images/title.png", use_container_width=True)
    
    # ゲームスタートボタン（中央揃え）
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("ゲームスタート", key="game_start_button"):
            st.session_state.game_state = 'opening'
            st.rerun()
    
    col1, col2, col3 = st.columns([1, 1, 1])

    st.markdown("<p style='text-align: center'>Built with <a href='https://streamlit.io'>Streamlit</a></p>", unsafe_allow_html=True)

def display_opening():
    # 2カラムレイアウトを作成（左側に画像、右側にフォーム）
    col1, col2 = st.columns([1, 1])
    
    # 左側のカラムに画像を表示
    with col1:
        st.image("src/images/manager-room-door.png", use_container_width=True)
    
    # 右側のカラムに暗証番号入力フォームを表示（垂直方向の中央に配置）
    with col2:
        
        # 空白を入れて上部に余白を作成
        st.markdown("<div style='margin-top: 30%;'></div>", unsafe_allow_html=True)

        # 垂直方向の中央揃えのためのCSSとHTMLを使用
        st.markdown("""
            <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
                <h2 style="margin-bottom: 20px;">暗証番号を入力せよ</h2>
            </div>
        """, unsafe_allow_html=True)


        pin_code = st.text_input("暗証番号", type="password", placeholder="６桁の数字", max_chars=6, key="pin_input", label_visibility="collapsed")
        
        # 入力値が6桁になったら自動チェック
        if pin_code and len(pin_code) == 6:
            if pin_code == "442222":
                # ドアが開く音を再生
                try:
                    with open("src/audio/door-open.mp3", "rb") as f:
                        audio_bytes = f.read()
                    
                    # Base64エンコードしてHTMLに埋め込み
                    audio_b64 = base64.b64encode(audio_bytes).decode()
                    
                    st.markdown(f"""
                    <audio autoplay style="display: none;">
                        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                    </audio>
                    <script>
                        // 音声再生を確実にするためのJavaScript
                        document.addEventListener('DOMContentLoaded', function() {{
                            const audio = document.querySelector('audio[autoplay]');
                            if (audio) {{
                                audio.play().catch(function(error) {{
                                    console.log('音声再生に失敗しました:', error);
                                }});
                            }}
                        }});
                    </script>
                    """, unsafe_allow_html=True)
                except FileNotFoundError:
                    st.warning("音声ファイルが見つかりません: src/audio/door-open.mp3")
                
                st.success("鍵が開いた・・")
                # 音が再生されるまで少し待機
                time.sleep(2)
                st.session_state.game_state = 'quiz_intro'
                st.rerun()
            else:
                st.error("暗証番号が間違っているようだ")

    st.markdown("<p style='text-align: center'>Built with <a href='https://streamlit.io'>Streamlit</a></p>", unsafe_allow_html=True)

def display_success():
    # カラムの比率を変更して中央の列をより大きく
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("src/images/anger-kuromizu.png", use_container_width=True)
    
    st.markdown("""
    
    「ちぃぃっ……まさか全問正解するとは……

    """)
    

def display_quiz_intro():
    """クイズ開始前のイントロ画面を表示"""
    
    # より均等な配置のためのcolumns設定
    col1, col2 = st.columns([1, 1])  # 比率を[1, 2, 1]に変更してより中央に寄せる
    with col1:
        st.image("src/images/principals-office.png", use_container_width=True)
    
    with col2:
        # 空白を入れて上部に余白を作成し、垂直方向の中央に配置
        st.markdown("<div style='margin-top: 30%;'></div>", unsafe_allow_html=True)
        
        # 垂直方向の中央揃えのためのCSSとHTMLを使用
        st.markdown("""
            <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
                <h2 class="title-container" style="font-size: 1.5rem; margin: 0; padding: 0;">
                    <div class="subtitle">なんね、あんたら？元の附設にもどしたい？<br>そんならおいの質問に答えてみんね？<br>卒業生なら、簡単に答えられるやろう</div>
                </h2>
            </div>
        """, unsafe_allow_html=True)
    
        if st.button("挑戦する", key="quiz_start_button", use_container_width=True):
            st.session_state.game_state = 'quiz'
            st.rerun()

def display_quiz():
    st.markdown("<h1 style='text-align: center;'>黒水校長の質問をクリアせよ！</h1>", unsafe_allow_html=True)
    st.markdown("""
<style>
.center-text {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)
    st.markdown('<p class="center-text">元の附設に戻せ！と入力してスタートせよ</p>', unsafe_allow_html=True)
    
    # チャットメッセージの表示エリア
    chat_area = st.container()
    
    # 過去のメッセージを表示（TTSなし）
    for i, msg in enumerate(st.session_state.messages[:-1] if st.session_state.messages else []):
        format_message(msg['role'], msg['content'], chat_area, is_new_message=False)
    
    # 最新のメッセージのみTTS処理を行う
    if st.session_state.messages:
        latest_msg = st.session_state.messages[-1]
        format_message(latest_msg['role'], latest_msg['content'], chat_area, is_new_message=True)
        
        # 最後のメッセージが成功メッセージかチェック
        if "全問正解かい" in latest_msg['content'] and not st.session_state.quiz_completed:
            st.session_state.quiz_completed = True
            st.session_state.game_state = 'success'
            st.rerun()
    
    # 入力フィールド（固定位置）
    st.markdown("""
        <div class="input-container">
            <div style="max-width: 1000px; margin: 0 auto;">
    """, unsafe_allow_html=True)
    
    st.text_input(
        "あなたの回答を入力してください",
        key="user_input_field",
        on_change=handle_submit,
        label_visibility="collapsed"
    )
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="漆黒の遥藍地",
        page_icon="🏫",
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
    
    # TTS設定のトグルボタン（クイズ画面でのみ表示）
    if st.session_state.game_state == 'quiz':
        with st.sidebar:
            st.markdown("### 音声設定")
            tts_enabled = st.toggle("音声読み上げ", value=st.session_state.tts_enabled)
            if tts_enabled != st.session_state.tts_enabled:
                st.session_state.tts_enabled = tts_enabled
                st.rerun()
    
    
    # ゲーム状態に応じて画面を表示
    if st.session_state.game_state == 'title':
        display_title()
    elif st.session_state.game_state == 'opening':
        display_opening()
    elif st.session_state.game_state == 'quiz_intro':
        display_quiz_intro()
    elif st.session_state.game_state == 'quiz':
        display_quiz()
    elif st.session_state.game_state == 'success':
        display_success()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 