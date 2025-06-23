import streamlit as st
import time
from datetime import datetime
import openai
from openai import OpenAI
import json
from typing import Dict, List
from PIL import Image
import random
import threading
import tempfile
import os
import requests
import soundfile as sf
import numpy as np
from io import BytesIO

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# COEIROINKの設定
COEIROINK_URL = "http://localhost:50031"  # COEIROINKのデフォルトURL
SPEAKER_ID = "metan"  # メタンのID

def init_session_state():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'opening'
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'quiz_count' not in st.session_state:
        st.session_state.quiz_count = 0
    if 'correct_answers' not in st.session_state:
        st.session_state.correct_answers = 0
    if 'is_quiz_finished' not in st.session_state:
        st.session_state.is_quiz_finished = False
    if 'quizzes' not in st.session_state:
        st.session_state.quizzes = generate_quizzes()
    if 'current_conversation' not in st.session_state:
        st.session_state.current_conversation = []

def generate_quizzes():
    """2つの問題（歴史と英語）と正解を固定で返す"""
    quizzes = [
        {
            "subject": "社会",
            "quiz_number": 1,
            "question": "鎌倉幕府を開いた源頼朝が征夷大将軍に任命されたのは何年ですか？",
            "correct_answer": "1192年",
            "acceptable_answers": ["1192年", "1192"],
            "keywords": ["1192"]
        },
        {
            "subject": "英語",
            "quiz_number": 2,
            "question": "次の英文を和訳してください：The rapid development of artificial intelligence has raised both hopes and concerns about the future of work.",
            "correct_answer": "人工知能の急速な発展は、仕事の未来に対して期待と懸念の両方を引き起こしています。",
            "acceptable_answers": ["人工知能の急速な発展は仕事の未来に対して期待と懸念の両方を引き起こしています", "AIの急速な発展は仕事の未来について期待と懸念を生んでいます"],
            "keywords": ["人工知能", "AI", "発展", "仕事", "未来", "期待", "懸念"]
        }
    ]
    
    return quizzes

def speak_text(text):
    """テキストを音声で読み上げる（非同期）"""
    def speak():
        try:
            # 音声合成のリクエストを作成
            synthesis_request = {
                "text": text,
                "speaker": SPEAKER_ID,
                "speed": 1.0,
                "pitch": 0.0,
                "intonation": 1.0,
                "volume": 1.0
            }
            
            # 音声合成を実行
            synthesis_response = requests.post(
                f"{COEIROINK_URL}/synthesis",
                json=synthesis_request
            )
            synthesis_response.raise_for_status()
            
            # 音声データを一時ファイルに保存
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(synthesis_response.content)
                temp_filename = temp_file.name
            
            # 音声ファイルを再生
            st.audio(temp_filename)
            
            # 一時ファイルを削除
            os.unlink(temp_filename)
            
        except Exception as e:
            st.error(f"音声合成中にエラーが発生しました: {str(e)}")
    
    # 別スレッドで音声を再生
    thread = threading.Thread(target=speak)
    thread.start()

def get_bot_response(user_message=None):
    """黒水校長の返答を生成する"""
    current_quiz_idx = st.session_state.quiz_count
    
    # 初期メッセージまたは現在の問題
    if user_message is None:
        if current_quiz_idx == 0:
            # 初回メッセージ
            system_content = """
## 役割
GPTは会話を通して問題を出すゲームの校長役を演じて問題をだします。
喋るのは久留米弁です。

## 設定
久留米大学附設高校は悪の校長黒水校長の支配する、地獄の高校と成り果てていた。この状況を救うべく立ち上がった卒業生たちは、黒水校長と対決する

訪れた卒業生に対して、黒水校長は本当に附設の卒業生か試すために問題を出します。

##最初の会話
なんね？附設の卒業生やと？？この高校を元に戻したい？？
何を言うとるのかわからんが、それなら附設を卒業したっちゅうことば証明してみみんね！覚悟はよかとや！？

今からお前らに問題を出す。2問連続で正解せんと、卒業生とは認めんけん覚悟しとけ！！
            """
            
            # 1問目を出題
            current_quiz = st.session_state.quizzes[0]
            quiz_instruction = f"""
            まずは1問目、{current_quiz['subject']}の問題ばい！
            
            【問題1】
            「{current_quiz['question']}」
            
            答えてみみんね！
            """
            
            # 音声で読み上げ
            speak_text(quiz_instruction)
            return quiz_instruction
            
        else:
            # 次の問題を出題
            current_quiz = st.session_state.quizzes[current_quiz_idx]
            
            # 2問目以降は問題文を直接設定する
            quiz_instruction = f"""
            次は{current_quiz_idx + 1}問目、{current_quiz['subject']}の問題ばい！
            
            【問題{current_quiz_idx + 1}】
            「{current_quiz['question']}」
            
            答えてみみんね！
            """
            
            # 音声で読み上げ
            speak_text(quiz_instruction)
            return quiz_instruction
            
    else:
        # ユーザーの回答に対するフィードバック
        current_quiz = st.session_state.quizzes[current_quiz_idx]
        is_correct = check_answer(user_message, current_quiz)
        
        if is_correct:
            st.session_state.correct_answers += 1
            response = f"""
            おお！正解ばい！「{user_message}」は正解じゃった！
            
            さすがは附設の卒業生じゃのう。頭の回転が速かばい！
            """
            
            # 全問題終了後の処理
            if current_quiz_idx + 1 >= len(st.session_state.quizzes):
                if st.session_state.correct_answers == len(st.session_state.quizzes):
                    response += """
                    全問正解！さすがじゃ！お前が本当の附設の卒業生じゃと認めよう。
                    素晴らしい実力を見せてくれたばい。
                    """
                else:
                    response += f"""
                    {st.session_state.correct_answers}問正解/{len(st.session_state.quizzes)}問中じゃった。
                    残念ながら、まだまだじゃのう。もう一度挑戦してくれんか？
                    """
            else:
                response += """
                次の問題もあるけん、気合い入れていくばい！
                """
        else:
            response = f"""
            おっと、残念じゃったね！「{user_message}」は不正解じゃった。
            正解は「{current_quiz['correct_answer']}」じゃった。
            """
            
            # 全問題終了後の処理
            if current_quiz_idx + 1 >= len(st.session_state.quizzes):
                if st.session_state.correct_answers == len(st.session_state.quizzes):
                    response += """
                    全問正解！さすがじゃ！お前が本当の附設の卒業生じゃと認めよう。
                    素晴らしい実力を見せてくれたばい。
                    """
                else:
                    response += f"""
                    {st.session_state.correct_answers}問正解/{len(st.session_state.quizzes)}問中じゃった。
                    残念ながら、まだまだじゃのう。もう一度挑戦してくれんか？
                    """
            else:
                response += """
                まだチャンスはあるけん、次の問題も頑張るんばい！
                """
        
        # 音声で読み上げ
        speak_text(response)
                
        # 会話履歴を更新
        st.session_state.current_conversation.append({"role": "user", "content": user_message})
        st.session_state.current_conversation.append({"role": "assistant", "content": response})
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        return response

def check_answer(user_answer, quiz):
    """ユーザーの回答が正解かどうかをAPIを使ってチェックする"""
    # 「わからない」などの回答は不正解
    if "わからない" in user_answer or "分からない" in user_answer or "知らない" in user_answer:
        return False
    
    # 空白や短すぎる回答は不正解
    if len(user_answer.strip()) < 2:
        return False
    
    try:
        # 正解情報をまとめる
        correct_info = {
            "question": quiz["question"],
            "correct_answer": quiz["correct_answer"],
            "acceptable_answers": quiz["acceptable_answers"],
            "keywords": quiz["keywords"]
        }
        
        # APIリクエスト用のプロンプト
        prompt = f"""
        以下の回答が正解かどうか判定してください：
        
        【問題】
        {quiz["question"]}
        
        【模範解答】
        {quiz["correct_answer"]}
        
        【許容される別解答】
        {', '.join(quiz["acceptable_answers"])}
        
        【キーワード】
        {', '.join(quiz["keywords"])}
        
        【ユーザーの回答】
        {user_answer}
        
        意味が通じていれば、厳密な表現の一致でなくても正解と判定してください。
        「はい」か「いいえ」だけで答えてください。
        """
        
        # OpenAI APIを使用して判定
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "あなたは問題の採点者です。ユーザーの回答が正解かどうかを判定してください。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().lower()
        return "はい" in result or "yes" in result
        
    except Exception as e:
        st.error(f"回答チェック中にエラーが発生しました: {str(e)}")
        # エラー時はフォールバックとして従来の判定方法を使用
        
        # 完全一致の場合
        if user_answer.strip() == quiz["correct_answer"].strip():
            return True
        
        # 許容される解答の一覧と比較
        for acceptable in quiz["acceptable_answers"]:
            if user_answer.strip() == acceptable.strip():
                return True
        
        # キーワードベースの判定
        user_answer_lower = user_answer.lower()
        keyword_matches = 0
        for keyword in quiz["keywords"]:
            if keyword.lower() in user_answer_lower:
                keyword_matches += 1
        
        # キーワードの半分以上が含まれていれば正解とみなす
        if keyword_matches >= len(quiz["keywords"]) / 2 and len(quiz["keywords"]) > 0:
            return True
        
        return False

def display_opening():
    st.markdown(
        """
        <style>
        .title-container {
            text-align: center;
            padding: 2rem;
        }
        .start-button {
            text-align: center;
            margin-top: 2rem;
        }
        .centered-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: bold;
            margin: 2rem 0;
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
        """,
        unsafe_allow_html=True
    )
    
    # カラムの比率を変更して中央の列をより大きく
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image("src/images/opening.png", use_container_width=True)
    
    st.markdown("<h1 class='centered-title'>地獄の附設高校</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("ゲームを始める"):
            st.session_state.game_state = 'clinic'
            st.rerun()

    st.markdown("<p style='text-align: center'>Built with <a href='https://streamlit.io'>Streamlit</a></p>", unsafe_allow_html=True)
    

def display_clinic():
    st.markdown(
        """
        <style>
        .centered-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: bold;
            margin: 2rem 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title("附設高校")

    st.image("src/images/school-gate.png", use_container_width=True)
    
    st.markdown("""
    あなた方は、今年も附設の同窓会にやってきた。
    
    ところがふとした拍子に「もうひとつの附設高校」に迷い込む。

    そこは、かつての思い出がねじ曲げられた、悪の校長、黒水先生が支配する世界。

    鬼のような教師たちが、生徒に容赦ない"試練"を課している。

    附設を取り戻すには、あのときの自分＝原点を思い出しながら、

    鬼教師たちが出す謎と難題を乗り越えねばならない——
                
    """)
    
    if st.button("校長室へ向かう"):
        st.session_state.game_state = 'intro'
        st.rerun()

def display_intro():
    st.title("黒水校長")

    st.image("src/images/principals-office.png", use_container_width=True)
    
    st.markdown("""
    部屋の奥、荘厳な書棚を背にして、黒水校長がどっしりとした椅子に腰かけている。
                
    その場の空気はまるで時間が止まったかのように重く、冷たさすら感じさせる。

    この校長室は、ただの部屋ではない。ここに足を踏み入れた者は、必ず何か試されるのだ――黒水校長の鋭いまなざしがそう語っているようだった。
                
    　
              
    「なんね？附設の卒業生やと？？この高校を元に戻せ？？」
                
    「何を言うとるのかわからんが、それなら附設を卒業したっちゅうことば証明してみんね！」
    

    「今からお前らに問題を出す。2問連続で正解せんと、卒業生とは認めんけん覚悟しとけ！！」

    """)
    
    if st.button("試練を受ける"):
        init_session_state()
        st.session_state.game_state = 'quiz'
        st.rerun()

def display_quiz():
    st.title("黒水校長の試練")
    
    # クイズが終了していない場合
    if not st.session_state.is_quiz_finished:
        # 最初のメッセージがない場合は初期メッセージを取得
        if len(st.session_state.messages) == 0:
            bot_response = get_bot_response()
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            st.rerun()  # 初回の問題表示後に再読み込みして表示を更新
    
    # メッセージの表示
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
    
    # クイズが終了していない場合のユーザー入力処理
    if not st.session_state.is_quiz_finished:
        # ユーザー入力欄
        user_input = st.chat_input("あなたの回答を入力してください")
        
        if user_input:
            # ユーザーの回答を表示
            st.chat_message("user").write(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # 回答に対するフィードバックを取得
            bot_response = get_bot_response(user_input)
            
            # 次の問題へ進む
            st.session_state.quiz_count += 1
            
            # 全ての問題が終わったかチェック
            if st.session_state.quiz_count >= len(st.session_state.quizzes):
                st.session_state.is_quiz_finished = True
                
                # 全問正解したらsuccess、そうでなければfailure
                if st.session_state.correct_answers == len(st.session_state.quizzes):
                    st.success(f"おめでとうございます！{len(st.session_state.quizzes)}問全て正解しました！")
                    st.session_state.game_state = 'success'
                else:
                    st.error(f"残念...{st.session_state.correct_answers}問正解でした。")
                    st.session_state.game_state = 'failure'
                
                if st.button("結果を見る"):
                    st.rerun()
            else:
                # まだ問題が残っている場合、次の問題を表示
                next_question = get_bot_response()
                st.session_state.messages.append({"role": "assistant", "content": next_question})
                st.rerun()  # 入力後に画面を更新

def display_success():
    st.title("試練クリア！")
    st.image("src/images/principals-office.png", use_container_width=True)
    
    st.markdown("""
    黒水校長は不満げな表情を浮かべながらも、あなたの実力を認めざるを得ない様子だ。
    
    「さすがは附設の卒業生じゃ。見事、すべての問題に答えたな」
    
    「まあ良かろう。今回は認めてやる。だが、これで終わりと思うなよ」
    
    「まだまだ試練は続くぞ。次回も覚悟しておけ！」
    
    黒水校長の言葉を背に、あなたは校長室を後にした。
    
    この学校を元の姿に戻すには、まだまだ長い道のりがありそうだ...
    """)
    
    if st.button("最初からやり直す"):
        # セッション状態をリセット
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def display_failure():
    st.title("試練失敗...")
    st.image("src/images/principals-office.png", use_container_width=True)
    
    st.markdown(f"""
    黒水校長は嘲笑うように、大きな声で笑った。
    
    「はっはっは！せいぜい{st.session_state.correct_answers}問しか答えられんとは。お前が附設の卒業生なわけなかろう！」
    
    「出直してこい！それとも二度と来ないか？弱い者に用はない！」
    
    黒水校長の嘲りの声を背に、あなたは肩を落として校長室を後にした。
    
    だが、これで諦めるわけにはいかない。もう一度挑戦しなければ...
    """)
    
    if st.button("再挑戦する"):
        # セッション状態をリセット
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def main():
    st.set_page_config(
        page_title="地獄の附設高校",
        page_icon="🏫"
    )
    init_session_state()
    
    # 画面を完全にクリア
    placeholder = st.empty()
    placeholder.empty()
    
    # 新しいコンテナで画面を構築
    with st.container():
        if st.session_state.game_state == 'opening':
            display_opening()
        elif st.session_state.game_state == 'clinic':
            display_clinic()
        elif st.session_state.game_state == 'intro':
            display_intro()
        elif st.session_state.game_state == 'quiz':
            display_quiz()
        elif st.session_state.game_state == 'success':
            display_success()
        elif st.session_state.game_state == 'failure':
            display_failure()

if __name__ == "__main__":
    main()
