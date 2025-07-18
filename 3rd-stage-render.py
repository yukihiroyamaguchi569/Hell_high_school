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
        # 既存のプロンプトのみを使用
        st.session_state.openai_messages = [
            {"role": "system", "content": """
            GPTは黒水校長になりきってユーザーに問題を出します
            福岡の筑後弁で、ユーモラスかつ挑発的な態度でしゃべってください。
            参加者のことは「あんたら」とか「お前ら」と呼びます
            参加者が間違ったら、馬鹿にして、ヒントをだします。
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
            - 「しゃあない」（仕方ない）
        

            ### 質問
            下記の質問を順番に質問してください。
            間違えたらヒントを出します。しかし正解自体は教えません。
            参加者が２回間違えたら、正解を教えて次の問題にいきます。

            質問：ムハンマドが創始した宗教は何や？
            答え：イスラム教
            
            質問：次の文の空欄にはいる最も適切な単語はなんや  If I ___ more time, I would travel around the world.
            答え：had
            
            質問：細胞の中で、エネルギーを作り出す働きを持つ細胞小器官は何や？
            答え：ミトコンドリア
            
            質問：「いとをかし」の現代語訳として正しいものは何や？
            答え：趣がある もしくは　面白い
            
            質問：福岡市の交通系ICカードとかけて、ウサイン・ボルトが尊敬される理由と解く、その心は？
            答え：はやかけん

            
            #### ここからは附設に関する質問やけんな
                 
            質問：高校の文化祭の名前は何やった？
            答え：男く祭（おとこくさい）
            
            質問：附設の裏にあった商店の通称はなんや？
            答え：裏店（うらみせ）
            ヒント：高校のすぐ裏にあった

            質問：附設高校が共学になった年はわかるや？
            答え：2005年
            
            質問：附設の近くにあった美味しいお好み焼きのお店は何や？
            答え：弁天
            ヒント：七福神の一人の名前
                     
            質問：附設高校が現在の場所に移転したのはいつや？
            答え：1968年
             
            ### 正誤の判定方法
            厳密に答えとあっていなくても正解とします
            「わからない」「分からない」「知らない」などの回答は不正解とします
            
            ### 予備知識 回答の参考にしてください
            
            #####歴代校長
                初代 1950-1959 板垣政参
                二代 1959-1961 楢崎広之助
                三代 1961-1965 大内覚之助
                四代 1965-1979 原巳冬
                五代 1979-1990 世良忠彦
                六代 1990-1993 緒方道彦
                七代 1993-1998 鹿毛勲臣
                八代 1998-2007 樋口忠治
                九代 2007-2008 古田智信
                十代 2008-2017 吉川敦
                十一代 2017- 町田健

            ### 最後の会話
            参加者がすべての問題を終了したら、「これでゲーム終了だ」というコメントをしてください。

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
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False

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

def format_message(role, content, container, is_new_message=False):
    """Format message with Streamlit components"""
    if role == "user":
        with container.chat_message("user"):
            st.write(content)
    else:
        # メッセージを表示
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
        # デバッグ用ボタン
        if st.button("デバッグ: 成功画面へ", key="debug_success_button"):
            st.session_state.game_state = 'success'
            st.rerun()
    
    col1, col2, col3 = st.columns([1, 1, 1])

    st.markdown("<p style='text-align: center'>Built with <a href='https://streamlit.io'>Streamlit</a></p>", unsafe_allow_html=True)

def display_opening():
    # カラムの比率を変更して中央の列をより大きく
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("src/images/manager-room-door.png", use_container_width=True)
    
    # 次へボタン（中央揃え）
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("扉を開く", key="open_door_button", use_container_width=True):

            st.session_state.game_state = 'quiz_intro'
            st.rerun()
    
    col1, col2, col3 = st.columns([1, 1, 1])

    st.markdown("<p style='text-align: center'>Built with <a href='https://streamlit.io'>Streamlit</a></p>", unsafe_allow_html=True)

def display_success():
    # カラムの比率を変更して中央の列をより大きく
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("src/images/anger-kuromizu.png", use_container_width=True)
    
    st.markdown("""
    
    「ちぃぃっ……この俺様が負けるとは……
                
    俺様が間違っていたということか…………
                
    仕方がない……　元の附設に戻して、これからは附設の未来のために尽くすとするか
                
    """)
    # 「次へ」ボタン（中央揃え）
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("次へ", key="to_form_button", use_container_width=True):
            st.session_state.game_state = 'form'
            st.rerun()


def display_form():
    st.markdown("<h1 style='text-align: center;'>ゲーム終了！</h1>", unsafe_allow_html=True)
    
    # Google FormsのURL
    form_url = "https://forms.gle/rb4sn5wxWBDssZGy6"
    
    st.markdown(f"""
    
    皆さまの力で、附設高校は黒水校長の支配から開放されました！
                
    ありがとうございました！！
                
    同窓会ゲーム「漆黒の遥藍地」お楽しみ頂けましたでしょうか？
        
    AIとの会話を楽しんでいただけなら幸いです。
                
    さて、ゲームはここで終了となりますが、ぜひ皆さまのご感想をお聞かせください。
                
    今後の企画の参考とさせていただきますので、以下のアンケートにご協力をお願いいたします。
                
    """)

    # フォームの埋め込み表示
    st.components.v1.iframe(form_url, height=1200)
    

def display_quiz_intro():
    """クイズ開始前のイントロ画面を表示"""
    st.markdown("<h1 style='text-align: center;'>黒水校長の試練</h1>", unsafe_allow_html=True)
    
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
    
    # 「はい」ボタンを中央に配置
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("はい", key="quiz_start_button", use_container_width=True):
            st.session_state.game_state = 'quiz'
            st.rerun()

def display_quiz():
    st.markdown("<h1 style='text-align: center;'>黒水校長の試練</h1>", unsafe_allow_html=True)
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
    
    # メッセージを表示
    for msg in st.session_state.messages:
        format_message(msg['role'], msg['content'], chat_area, is_new_message=False)
        
        # 最後のメッセージが成功メッセージかチェック
        if msg == st.session_state.messages[-1] and "ゲーム終了" in msg['content'] and not st.session_state.quiz_completed:
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
    
    # メインコンテンツエリア
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
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
    elif st.session_state.game_state == 'form':
        display_form()
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 