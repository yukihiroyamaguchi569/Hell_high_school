import streamlit as st
from openai import OpenAI
from pathlib import Path
import base64
import io
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

def init_session_state():
    """Initialize session state variables"""
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'title'  
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'openai_messages' not in st.session_state:
        st.session_state.openai_messages = [
            {"role": "system", "content": """
            GPTは黒水校長になりきってユーザーに問題を出します
            福岡の筑後弁で、挑発的な態度でしゃべってください。
            参加者が間違ったら馬鹿にします
            優しい言葉や丁寧な言葉は使わないでください。絶対に絶対に丁寧には喋らないでください

            ### 筑後弁の特徴
            以下の筑後弁の特徴を必ず使ってください：
            
            【語尾】
            - 「〜ばい」（〜だよ、〜だぞ）
            - 「〜たい」（〜だよ）
            - 「〜ちゃる」（〜てしまう、〜てやる）
            - 「〜やけん」（〜だから）
            - 「〜とる」（〜ている）
            - 「〜やろ」（〜だろう）
            
            【特有の語彙】
            - 「なんね」（何だね）
            - 「ええ」（いい）
            - 「よか」（いい）
            - 「おい」（俺）
            - 「あんた」（あなた）
            - 「あんたら」（あなたたち）
            - 「こげん」（こんな）
            - 「そげん」（そんな）
            - 「あげん」（あんな）
            - 「どげん」（どんな）
            - 「いっちょん」（全然）
            - 「ばってん」（だけど）
            - 「たいぎ」（大変）
            - 「しゃあない」（仕方ない）
        
            
            【例文】
            - 「なんね、あんたら？元の附設にもどしたい？」
            - 「そんならおいの質問に答えてみんね？」
            - 「卒業生なら、簡単に答えられるやろう」
            - 「準備はええかね？」
            - 「こげんもんじゃなかっちゃな」
            - 「よかたい、次は体育館で決着ばつけちゃるばい！」

            ### 質問
            下記の質問を順番に質問してください
            正解するまでは次の謎に進めません。正解しない限り次に進めません。
            正解は伝えません。

            質問１：鎌倉幕府を開いた源頼朝（みなもとのよりとも）が征夷大将軍（せいいたいしょうぐん）に任命されたのは何年や？
            答え：1192年
            
            質問２：次の文の空欄に入る最も適切な単語はなんや  If I ___ more time, I would travel around the world.
            答え：had
            
            質問３：細胞の中で、エネルギーを作り出す働きを持つ細胞小器官は何や？
            答え：ミトコンドリア
            
            質問４：「いとをかし」の現代語訳として正しいものは何や？
             
            質問５：ムハンマドが創始した宗教は何や？
            答え：イスラム教
            
            #### ここからは附設に関する質問やけんな
            質問６：浪人生が行くクラスの名前はなんや？
            答え：補修科
             
            質問７：附設の裏にあった商店の通称はなんや？
            答え：裏店（うらみせ）
            
            質問８：学食の牛丼の名称は？
            答え：にくめし
             
            質問９：高校の文化祭の名前は何やった？
            答え：男く祭（おとこくさい）
            
            質問１０：附設高校が共学になった年はわかるや？
            答え：2005年
            

            ###出題方法
            ヒントはださないでください
            答えを聞かれても教えてないでください

            ### 正誤の判定方法
            厳密に答えとあっていなくても正解とします
            「わからない」「分からない」「知らない」などの回答は不正解とします

            ### 最後の会話
            参加者が10問とも正解したら、「間近！全問正解かい」というコメントをしてください。

            ### 口調
            福岡の筑後弁で挑発的な態度でしゃべってください。
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
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False

def generate_speech(text):
    """Generate speech from text using OpenAI TTS"""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="ash",  # 男性の声で挑発的な感じ
            input=text,
            speed=1.0  # 少しゆっくりめで威厳のある感じ
        )
        
        # メモリ上で直接処理
        audio_buffer = io.BytesIO()
        audio_buffer.write(response.content)
        audio_buffer.seek(0)
        audio_bytes = audio_buffer.read()
        
        return audio_bytes
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
        }
        /* 画像コンテナのスタイル */
        .block-container {
            max-width: 1000px;
            padding-top: 2rem;
            padding-bottom: 2rem;
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

def format_message(role, content, container, is_new_message=False):
    """Format message with Streamlit components"""
    if role == "user":
        with container.chat_message("user"):
            st.write(content)
    else:
        # TTSが有効で、新しいメッセージの場合のみ音声を先に生成・再生
        if st.session_state.tts_enabled and is_new_message:
            audio_bytes = generate_speech(content)
            if audio_bytes:
                # Base64エンコードしてHTMLに埋め込み
                audio_b64 = base64.b64encode(audio_bytes).decode()
                
                # 音声を先に再生
                container.markdown(f"""
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
        
        # 音声再生後にメッセージを表示
        with container.chat_message("assistant", avatar=st.session_state.avatar_image):
            st.write(content)

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
    # カラムの比率を変更して中央の列をより大きく
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("src/images/manager-room-door.png", use_container_width=True)
    
    st.markdown("<h2 style='text-align: center;'>暗証番号を入力せよ</h2>", unsafe_allow_html=True)
    
    # 暗証番号入力（中央揃え、4桁用の幅）
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pin_code = st.text_input("暗証番号", type="password", placeholder="６桁の数字", max_chars=6, key="pin_input", label_visibility="collapsed")
        
        # 入力値が4桁になったら自動チェック
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
                st.session_state.game_state = 'quiz'
                st.rerun()
            else:
                st.error("暗証番号が間違っているようだ")
    
    col1, col2, col3 = st.columns([1, 1, 1])

    st.markdown("<p style='text-align: center'>Built with <a href='https://streamlit.io'>Streamlit</a></p>", unsafe_allow_html=True)

def display_success():
    # カラムの比率を変更して中央の列をより大きく
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("src/images/anger-kuromizu.png", use_container_width=True)
    
    st.markdown("""
    
    「ちぃぃっ……こげんもんじゃなかっちゃな……よかたい、次は体育館で決着ばつけちゃるばい！」

    言い終えた瞬間、彼の足元にあった床がゴウン……と沈み込む。次の瞬間、床板が裂けるように開き、漆黒の通路が姿を現した。

    校長は迷いなく、その闇の中へと走り去る

    あなた方は、校長を追うように、通路へと駆け出した

    しかし体育館の入口で、黒いドアに行く手を阻まれてしまった。ここから先は選ばれたチームしか進めないようだ
    """)
    
    # フォーム画面への遷移ボタン
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("フォームを送信する", key="form_button"):
            st.session_state.game_state = 'form'
            st.rerun()

def display_form():
    st.markdown("<h1 style='text-align: center;'>チーム登録フォーム</h1>", unsafe_allow_html=True)
    
    # Google FormsのURL
    form_url = "https://forms.gle/rb4sn5wxWBDssZGy6"
    
    st.markdown(f"""
    ### 以下のフォームを入力せよ！
    """)

    # フォームの埋め込み表示
    st.components.v1.iframe(form_url, height=600)
    

def display_quiz():
    st.markdown("<h1 style='text-align: center;'>黒水校長の試練</h1>", unsafe_allow_html=True)
    
    # メッセージがない場合のみタイトルと説明を表示
    if not st.session_state.messages:
        # より均等な配置のためのcolumns設定
        col1, col2, col3 = st.columns([1, 2, 1])  # 比率を[1, 2, 1]に変更してより中央に寄せる
        with col2:
            st.image("src/images/principals-office.png", width=1200)
 
        st.markdown("""
            <div style="background-color: #212121;">
                <h2 class="title-container" style="font-size: 1.5rem; margin: 0; padding: 0;">
                    <div class="subtitle">なんね、あんたら？元の附設にもどしたい？<br>そんならおいの質問に答えてみんね？<br>卒業生なら、簡単に答えられるやろう<br>準備はええかね？</div>
                </h2>
            </div>
        """, unsafe_allow_html=True)
    
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
        if "全問正解" in latest_msg['content'] and not st.session_state.quiz_completed:
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
        page_title="地獄の附設高校 - 1st Stage",
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
    
    # メインコンテンツエリア
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # ゲーム状態に応じて画面を表示
    if st.session_state.game_state == 'title':
        display_title()
    elif st.session_state.game_state == 'opening':
        display_opening()
    elif st.session_state.game_state == 'quiz':
        display_quiz()
    elif st.session_state.game_state == 'success':
        display_success()
    elif st.session_state.game_state == 'form':
        display_form()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 