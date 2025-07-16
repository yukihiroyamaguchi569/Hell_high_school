import streamlit as st
from openai import OpenAI
from pathlib import Path
import base64
import os
import time
import google.generativeai as genai  # Gemini APIのインポート

# Google Cloud Text-to-Speech APIのインポート
from google.cloud import texttospeech

# OpenAI APIキーを環境変数から取得（Render.com用）
def get_openai_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI APIキーが設定されていません。環境変数OPENAI_API_KEYを設定してください。")
        st.stop()
    return api_key

# Gemini APIキーをファイルから取得
def get_gemini_api_key():
    try:
        with open("src/credentials/gemini-api-key.txt", "r") as f:
            api_key = f.read().strip()
        if not api_key:
            st.error("Gemini APIキーが設定されていません。src/credentials/gemini-api-key.txtを確認してください。")
            return None
        return api_key
    except Exception as e:
        st.error(f"Gemini APIキーの読み込みエラー: {str(e)}")
        return None

# OpenAIクライアントの初期化
client = OpenAI(api_key=get_openai_api_key())

# Gemini APIの初期化
gemini_api_key = get_gemini_api_key()
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

# 画像のパスを設定
AVATAR_PATH = Path("src/images/opening.png")

def load_prompt_from_file(file_path):
    """プロンプトをファイルから読み込む"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            prompt_content = f.read()
        return prompt_content
    except Exception as e:
        st.error(f"プロンプトファイルの読み込みエラー: {str(e)}")
        return None

def init_session_state():
    """Initialize session state variables"""
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'opening'  
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'openai_messages' not in st.session_state:
        # プロンプトをファイルから読み込む
        prompt_content = load_prompt_from_file("prompt.txt")
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
    if 'tts_provider' not in st.session_state:
        st.session_state.tts_provider = 'openai'  # デフォルトはOpenAI TTS
    if 'quiz1_completed' not in st.session_state:
        st.session_state.quiz1_completed = False
    if 'quiz2_completed' not in st.session_state:
        st.session_state.quiz2_completed = False
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    if 'current_quiz' not in st.session_state:
        st.session_state.current_quiz = 'quiz1'
    if 'model_choice' not in st.session_state:
        st.session_state.model_choice = 'gpt-4o'  # デフォルトはGPT-4o

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
        "満々":"まんまん",
        "松下由依":"まつしたゆい",
        "勝連":"かつれん",
        "小林":"こばやし",
        "松雪":"まつゆき",
        "中島":"なかじま",
        "山本":"やまもと",
        "上坂元":"かみさかもと",
        "秋本":"あきもと",
        "松浦":"まつうら",
        "田中":"たなか",
        "吉開":"よしかい",
        "年": "ねん",
        "織田信長":"おだのぶなが",
        "町田": "まちだ",
        "情け": "なさけ",
        "三権分立":"さんけんぶんりつ",
        "県花":"けんか",
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

# 既存のOpenAI TTS関数の下にGoogle TTSの関数を追加
def generate_speech_google(text):
    """Generate speech from text using Google Cloud TTS"""
    try:
        # 読み方ガイドを適用
        modified_text = apply_pronunciation_guides(text)
        
        # 認証情報ファイルへのパスを絶対パスで設定
        # __file__を使わず、明示的に絶対パスを指定
        credentials_path = "/Users/Yukis_MacBook/Python/Hell-high-school/src/credentials/hell-highschool-40eb2d572293.json"
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        # Google Cloud Text-to-Speech クライアントを初期化
        tts_client = texttospeech.TextToSpeechClient()
        
        # 合成する入力テキストを設定
        synthesis_input = texttospeech.SynthesisInput(text=modified_text)
        
        # 音声設定（日本語、女性の声）
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            name="ja-JP-Wavenet-B",  # 女性の声
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        
        # 音声ファイルの設定（MP3形式）
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        # リクエストを送信
        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        # 音声データを返す
        return response.audio_content
    except Exception as e:
        st.error(f"Google音声生成エラー: {str(e)}")
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
    """Get response from OpenAI API or Gemini API based on model choice"""
    try:
        if st.session_state.model_choice == 'gpt-4o':
            # OpenAI APIを使用
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        elif st.session_state.model_choice == 'gemini':
            # Gemini APIを使用
            if not gemini_api_key:
                st.error("Gemini APIキーが設定されていません。")
                return None
            
            # Gemini用にメッセージをフォーマット（最後のメッセージを除く）
            gemini_messages = []
            for msg in messages[:-1]:  # 最後のメッセージを除外
                if msg["role"] == "system":
                    # Geminiはシステムロールをサポートしていないため、ユーザーメッセージとして扱う
                    gemini_messages.append({"role": "user", "parts": [msg["content"]]})
                else:
                    gemini_messages.append({"role": "user" if msg["role"] == "user" else "model", "parts": [msg["content"]]})
            
            # Geminiモデルを設定
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # チャット履歴を作成
            chat = model.start_chat(history=gemini_messages)
            
            # 最後のメッセージを送信
            last_message = messages[-1]
            response = chat.send_message(last_message["content"])
            return response.text
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
            # 選択されたプロバイダーに基づいて音声を生成
            if st.session_state.tts_provider == "openai":
                audio_bytes = generate_speech(speech_text)
            else:  # google
                audio_bytes = generate_speech_google(speech_text)
                
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
            
            # 最後のメッセージが成功メッセージかチェック
            if st.session_state.current_quiz == 'quiz1' and "これでクイズ1は終了だ" in ai_response:
                st.session_state.quiz1_completed = True
                st.session_state.game_state = 'middle_success'
            elif st.session_state.current_quiz == 'quiz2' and "これでクイズ2は終了だ" in ai_response and len(st.session_state.messages) > 3:
                st.session_state.quiz2_completed = True
                st.session_state.game_state = 'final_success'
        
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
    
    # 隠しジャンプボタン（背景と同じ色）
    col1, col2, col3 = st.columns([1, 1, 1])
    with col3:
        st.markdown("""
        <style>
        .hidden-button {
            background-color: #212121;
            color: #212121;
            border: none;
            width: 30px;
            height: 30px;
            cursor: pointer;
            position: absolute;
            right: 10px;
            bottom: 10px;
        }
        .hidden-button:hover {
            background-color: #2a2a2a;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 隠しボタン（HTMLを使用して背景色と同じ色にする）
        st.markdown("""
        <button class="hidden-button" id="quiz2-jump" onclick="
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: true,
                key: 'jump_to_quiz2'
            }, '*');
        "></button>
        """, unsafe_allow_html=True)
        
        # ボタンの状態を受け取るための仕組み
        jump_clicked = st.checkbox("", key="jump_to_quiz2", value=False, label_visibility="collapsed")
        if jump_clicked:
            # クイズ2のプロンプトを読み込む
            prompt_content = load_prompt_from_file("prompt2.txt")
            if prompt_content:
                # メッセージをリセットして新しいプロンプトを設定
                st.session_state.messages = []
                st.session_state.openai_messages = [
                    {"role": "system", "content": prompt_content}
                ]
                st.session_state.current_quiz = 'quiz2'
                st.session_state.game_state = 'quiz2'
                st.session_state.quiz1_completed = True  # クイズ1をクリアした状態にする
                st.rerun()
            else:
                st.error("prompt2.txtファイルが見つからないか、読み込めませんでした。")

    st.markdown("<p style='text-align: center'>Built with <a href='https://streamlit.io'>Streamlit</a></p>", unsafe_allow_html=True)

def display_opening():
    # 2カラムレイアウトを作成（左側に画像、右側にフォーム）
    col1, col2 = st.columns([1, 1])
    
    # 左側のカラムに画像を表示
    with col1:
        st.image("src/images/ruined-door.jpg", use_container_width=True)
    
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

                st.session_state.game_state = 'opening2'
                st.rerun()
            else:
                st.error("暗証番号が間違っているようだ")

def display_opening2():
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image("src/images/ruined-door-opened.png", use_container_width=True)
    
    with col2:
        st.markdown("<div style='margin-top: 30%;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100%;">
                <h2 style="margin-bottom: 20px;">暗証番号を入力せよ</h2>
            </div>
        """, unsafe_allow_html=True)
    
    # 音声再生と画面遷移の処理を分離
    st.markdown("<div style='height: 0px;'></div>", unsafe_allow_html=True)  # 非表示のスペーサー
    
    # ドアが開く音を再生
    try:
        with open("src/audio/door-open.mp3", "rb") as f:
            audio_bytes = f.read()
        
        audio_b64 = base64.b64encode(audio_bytes).decode()
        
        st.markdown(f"""
        <audio autoplay style="display: none;">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("音声ファイルが見つかりません: src/audio/door-open.mp3")
    
    # 音が再生されるまで少し待機
    time.sleep(2)
    st.session_state.game_state = 'quiz_intro'
    st.rerun()


def display_middle_success():
    """quiz1クリア後の中間成功画面を表示"""
    # カラムの比率を変更して中央の列をより大きく
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("src/images/school-gate.png", use_container_width=True)
    
    st.markdown("""
    <div style="text-align: center; margin: 20px 0;">
    「ふん！基本的な学力や知識はあるようやね……だが第二関門が待っとるぞ！」
    </div>
    """, unsafe_allow_html=True)
    
    # 次に進むボタン（中央揃え）
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("次に進む", key="next_quiz_button"):
            # quiz2のプロンプトを読み込む
            prompt_content = load_prompt_from_file("prompt2.txt")
            if prompt_content:
                # メッセージをリセットして新しいプロンプトを設定
                st.session_state.messages = []
                st.session_state.openai_messages = [
                    {"role": "system", "content": prompt_content}
                ]
                st.session_state.current_quiz = 'quiz2'
                st.session_state.game_state = 'quiz2'
                st.rerun()
            else:
                st.error("prompt2.txtファイルが見つからないか、読み込めませんでした。")

def display_final_success():
    """quiz2クリア後の最終成功画面を表示"""
    # カラムの比率を変更して中央の列をより大きく
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
        「ちぃぃっ……まさか全問正解するとは……」
        </div>
        """, unsafe_allow_html=True)

        st.image("src/images/anger-kuromizu.png", use_container_width=True)

    with col3:
        # ボタンの上にマージンを追加
        st.markdown("<div style='margin-top: 100%;'></div>", unsafe_allow_html=True)
        if st.button("次へ", key="next_button"):
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
            
            time.sleep(2.0)
            st.session_state.game_state = 'ending'
            st.rerun()


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
                    <div class="subtitle">黒水校長が現れた！</div>
                </h2>
            </div>
        """, unsafe_allow_html=True)
    
        if st.button("挑戦する", key="quiz_start_button", use_container_width=True):
            st.session_state.game_state = 'quiz'
            st.rerun()

def display_quiz():
    """クイズ画面を表示（quiz1）"""
    st.markdown(f"<h1 style='text-align: center;'>基本問題をクリアせよ！</h1>", unsafe_allow_html=True)
    st.markdown("""
<style>
.center-text {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)
    st.markdown('<p class="center-text">元の高校に戻せ！と入力してスタートせよ</p>', unsafe_allow_html=True)
    
    # モデル選択（サイドバーに移動）
    with st.sidebar:
        st.markdown("### モデル設定")
        model_choice = st.radio(
            "使用するAIモデル",
            ["gpt-4o", "gemini"],
            index=0 if st.session_state.model_choice == "gpt-4o" else 1
        )
        if model_choice != st.session_state.model_choice:
            st.session_state.model_choice = model_choice
            st.rerun()
    
    # チャットメッセージの表示エリア
    chat_area = st.container()
    
    # 過去のメッセージを表示（TTSなし）
    for i, msg in enumerate(st.session_state.messages[:-1] if st.session_state.messages else []):
        format_message(msg['role'], msg['content'], chat_area, is_new_message=False)
    
    # 最新のメッセージのみTTS処理を行う
    if st.session_state.messages:
        latest_msg = st.session_state.messages[-1]
        format_message(latest_msg['role'], latest_msg['content'], chat_area, is_new_message=True)
    
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
    
    # 画面下部に余白を追加して、チャットが上に表示されるようにする
    st.markdown("<div style='height: 300px;'></div>", unsafe_allow_html=True)

def display_quiz2():
    """クイズ画面を表示（quiz2）"""
    st.markdown(f"<h1 style='text-align: center;'>附設に関する質問をクリアせよ！</h1>", unsafe_allow_html=True)
    st.markdown("""
<style>
.center-text {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)
    ## st.markdown('<p class="center-text">なんでも聞いてみろ！と入力してスタートせよ</p>', unsafe_allow_html=True)
    
    # モデル選択（サイドバーに移動）
    with st.sidebar:
        st.markdown("### モデル設定")
        model_choice = st.radio(
            "使用するAIモデル",
            ["gpt-4o", "gemini"],
            index=0 if st.session_state.model_choice == "gpt-4o" else 1
        )
        if model_choice != st.session_state.model_choice:
            st.session_state.model_choice = model_choice
            st.rerun()
    
    # チャットメッセージの表示エリア
    chat_area = st.container()
    
    # 過去のメッセージを表示（TTSなし）
    for i, msg in enumerate(st.session_state.messages[:-1] if st.session_state.messages else []):
        format_message(msg['role'], msg['content'], chat_area, is_new_message=False)
    
    # 最新のメッセージのみTTS処理を行う
    if st.session_state.messages:
        latest_msg = st.session_state.messages[-1]
        format_message(latest_msg['role'], latest_msg['content'], chat_area, is_new_message=True)
    
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
    
    # 画面下部に余白を追加して、チャットが上に表示されるようにする
    st.markdown("<div style='height: 300px;'></div>", unsafe_allow_html=True)

def display_ending():
    """エンディング画面を表示"""
    # カラムの比率を変更して中央の列をより大きく
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("src/images/manager-room-empty.png", use_container_width=True)

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
    if st.session_state.game_state == 'quiz' or st.session_state.game_state == 'quiz2':
        with st.sidebar:
            st.markdown("### 音声設定")
            tts_enabled = st.toggle("音声読み上げ", value=st.session_state.tts_enabled)
            
            # TTSプロバイダー選択を追加
            tts_provider = st.radio(
                "音声プロバイダー",
                options=["openai", "google"],
                index=0 if st.session_state.tts_provider == "openai" else 1
            )
            
            if tts_enabled != st.session_state.tts_enabled or tts_provider != st.session_state.tts_provider:
                st.session_state.tts_enabled = tts_enabled
                st.session_state.tts_provider = tts_provider
                st.rerun()
    
    # ゲーム状態に応じて画面を表示
    if st.session_state.game_state == 'title':
        display_title()
    elif st.session_state.game_state == 'opening':
        display_opening()
    elif st.session_state.game_state == 'opening2':
        display_opening2()
    elif st.session_state.game_state == 'quiz_intro':
        display_quiz_intro()
    elif st.session_state.game_state == 'quiz':
        display_quiz()
    elif st.session_state.game_state == 'middle_success':
        display_middle_success()
    elif st.session_state.game_state == 'quiz2':
        display_quiz2()
    elif st.session_state.game_state == 'final_success':
        display_final_success()
    elif st.session_state.game_state == 'ending':
        display_ending()

if __name__ == "__main__":
    main() 