import streamlit as st
import time
from datetime import datetime
import openai
from openai import OpenAI
import json
from typing import Dict
from PIL import Image

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def init_session_state():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'opening'
    if 'timer' not in st.session_state:
        st.session_state.timer = 300
    if 'task_submission' not in st.session_state:
        st.session_state.task_submission = ''
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'evaluation_result' not in st.session_state:
        st.session_state.evaluation_result = None
    if 'has_met_kokoro' not in st.session_state:
        st.session_state.has_met_kokoro = False

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
    
    st.markdown("<h1 class='centered-title'>地獄のクリニック</h1>", unsafe_allow_html=True)
    
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
    
    st.title("やすらぎクリニック")

    st.image("src/images/clinic.webp", use_container_width=True)
    
    st.markdown("""
    静寂な住宅街の一角に、やすらぎクリニックは佇んでいた。
                
    禍々しい雰囲気を漂わせていて、全然やすらげそうにない。
    
    私は月森 航。医学部を卒業して2年目。大学病院での研修を終えたばかりの駆け出し医師だ。
    
    このクリニックは、大学の先輩から紹介された、都内でも指折りの人気クリニック。
    
    「鬼の院長」と呼ばれる鬼島院長の下で働けることは、若手医師にとって大きなチャンス。
    
    でも同時に、その厳しさは噂になっていて...
    
    「大丈夫、自分なら...」
    
    そう自分に言い聞かせながら、重い足取りでクリニックのドアをくぐった。
                
    """)
    
    if st.button("院長室へ向かう"):
        st.session_state.game_state = 'intro'
        st.rerun()

def display_intro():
    st.title("鬼島院長")

    st.image("src/images/onishima.webp", use_container_width=True)
    
    st.markdown("""
    重厚な木製デスクの向こうで、中年の男性が険しい表情でこちらを見つめていた。
    
    やすらぎクリニック院長・鬼島正剛。
    
    「ほう、君が大学の後輩の月森 航君か、、」
    
    院長は私の履歴書に目を落としたまま、ゆっくりと口を開いた。
    
    「クリニックとはいえ、うちは忙しいぞ。患者さんはVIP揃いでね。それなりの覚悟は必要だが...」
    
    一瞬の間。
    
    「まあいい。来週から来てもらおう。初日は朝7時集合。早めに来い」
    
    「はい。ありがとうございます」
                
    「では、事務長が待っているので、そちらへ行ってくれ」
                
    「わかりました。よろしくお願いします」

    """)
    
    if st.button("事務長室へ行く"):
        st.session_state.game_state = 'task_intro'
        st.rerun()

def display_task_intro():
    # 画面を一度クリア
    intro_container = st.empty()
    
    with intro_container.container():
        st.title("第１章：入学試験")

        st.image("src/images/manager.webp", use_container_width=True)

        st.markdown("""
        

        「ようこそ、やすらぎクリニックへ。私が事務長の針生（はりう）だ。」

        事務長は、あなたの顔を見て、そう言った。
                    
        「さっそくだが、今からうちのクリニックの経営改善案を作ってくれ。800文字くらいかな」
        
        「え...今から...ですか？」
        
        「ああ。君の経営センスを見せてもらおうじゃないか。５分で頼む。これがいわば、入学試験だと思ってくれ」
        
        私の困惑した表情を楽しむように、事務長は椅子に深く寄りかかった。
        
        「じゃあ、よろしく頼むよ」

                    
        """)
        
        # ボタンを追加
        if st.button("タスクを開始する"):
            st.session_state.game_state = 'task'
            st.session_state.start_time = datetime.now()
            intro_container.empty()  # 画面をクリア
            st.rerun()

def display_task():
    if st.session_state.game_state != 'task':
        return
    
    task_container = st.empty()
    
    with task_container.container():
        if st.session_state.start_time is None:
            st.session_state.start_time = datetime.now()
        
        st.title("経営改善案の作成")
        
        st.markdown("""
        ### タスク内容
        やすらぎクリニックの経営改善案をA4用紙2枚程度で作成してください。
        """)
        st.markdown("")
        
        current_text = st.text_area(
            "経営改善案を入力してください",
            st.session_state.task_submission,
            height=400,
            max_chars=2000
        )
        st.session_state.task_submission = current_text
        
        submit = st.button("提出")
        
        elapsed_time = int((datetime.now() - st.session_state.start_time).total_seconds())
        remaining_time = max(300 - elapsed_time, 0)
        
        if remaining_time <= 0 or submit:
            task_container.empty()
            st.session_state.game_state = 'evaluation'
            st.rerun()
        
        if remaining_time > 0:
            time.sleep(1)
            st.rerun()

def evaluate_proposal(text: str) -> Dict[str, any]:
    """経営改善案をGPT-4で評価する"""
    try:
        # 文字数をカウント
        char_count = len(text)
        # 文字数の評価（800文字からの距離に基づいて0-20点を計算）
        length_score = max(0, 20 - abs(char_count - 800) // 20)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"""あなたは超ブラックなクリニックの辣腕事務長です。
提出された経営改善案を評価し、必ず以下の形式のJSONのみを返してください。
説明文や追加のコメントは一切含めないでください。
コメントは厳しい威圧的な口調で書いてください

現在の文字数は{char_count}文字です（目標は800文字）。

{{
    "revenue_score": (1-20の整数),
    "revenue_comment": "収益性の観点からの簡潔な評価コメント",
    "satisfaction_score": (1-20の整数),
    "satisfaction_comment": "患者満足度の観点からの簡潔な評価コメント",
    "efficiency_score": (1-20の整数),
    "efficiency_comment": "業務効率化の観点からの簡潔な評価コメント",
    "hr_score": (1-20の整数),
    "hr_comment": "人材育成の観点からの簡潔な評価コメント",
    "length_score": {length_score},
    "length_comment": "文字数に関するコメント",
    "total_score": (上記スコアの合計),
    "overall_comment": "総合的な評価コメント"
}}"""},
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        
        try:
            content = response.choices[0].message.content.strip()
            # マークダウンのコードブロック記法を取り除く
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except json.JSONDecodeError as e:
            st.error(f"JSONのパースに失敗しました: {str(e)}\nGPTからの応答: {response.choices[0].message.content}")
            return None
    except Exception as e:
        st.error(f"評価中にエラーが発生しました: {str(e)}\n送信したメッセージ: {text}\nGPTからの応答: {response.choices[0].message.content if 'response' in locals() else 'レスポンスなし'}")
        return None

def display_kokoro_scene():
    
    st.divider()
    
    st.markdown("""
    針生事務長が部屋を出て行った後...

    「あの...大丈夫ですか？」
                
    後ろを振り返ると、若い看護師 風花こころが心配そうな表情で立っていた。

    「私も最初は大変でした。本当に仕事が終わらなくて...」

    こころは周りを確認してから、小声で続けた。

    「このアドレスに連絡してくれれば、いつでも私がサポートしますから。院長や事務長には内緒ですよ？」

    そう言って、こころは小さなメモを渡してきた。
    
    メモには以下のように書かれていた：

    風花こころ：[LINEアドレス](https://cocoro-assistant.streamlit.app/)
            
    「私は隣のブースに居るので、困ったらいつでもここに連絡してください」
                        
    こころは笑顔で足早に去っていった
        """)

def display_evaluation():
    # 専用のコンテナを作成
    eval_container = st.empty()
    
    with eval_container.container():
        st.title("評価")
        
        if st.session_state.evaluation_result is None:
            with st.spinner("針生事務長は鋭い眼差しで、あなたの文章に目を通している..."):
                result = evaluate_proposal(st.session_state.task_submission)
                if result:
                    st.session_state.evaluation_result = result

        if st.session_state.evaluation_result:
            result = st.session_state.evaluation_result
            
            # 院長の表情と最初のコメント
            if result['total_score'] < 60:
                st.markdown("""
                針生事務長は眉をひそめ、ため息をつきながら言った。
                「これはいただけないな...やり直せ」
                """)
            elif result['total_score'] < 80:
                st.markdown("""
                針生事務長は腕を組み、じっと考え込むような表情を見せた。
                「ふむ...まあ、悪くはない。だが、もう少し工夫の余地はあるな。やり直しだ」
                """)
            else:
                st.markdown("""
                針生事務長は満足げな表情を浮かべ、頷いた。
                「なかなかやるじゃないか。評判に違わず優秀だな」
                """)
            
            st.markdown("### 針生事務長からの評価")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("総合評価", f"{result['total_score']}/100点")
            with col2:
                char_count = len(st.session_state.task_submission)
                st.metric("文字数", f"{char_count}/800文字")
            
            st.markdown("#### 項目別評価")
            cols = st.columns(5)  # 5列に変更
            with cols[0]:
                st.metric("収益性", f"{result['revenue_score']}/20点")
                st.markdown(f"*{result['revenue_comment']}*")
            with cols[1]:
                st.metric("患者満足度", f"{result['satisfaction_score']}/20点")
                st.markdown(f"*{result['satisfaction_comment']}*")
            with cols[2]:
                st.metric("業務効率化", f"{result['efficiency_score']}/20点")
                st.markdown(f"*{result['efficiency_comment']}*")
            with cols[3]:
                st.metric("人材育成", f"{result['hr_score']}/20点")
                st.markdown(f"*{result['hr_comment']}*")
            with cols[4]:
                st.metric("文字数", f"{result['length_score']}/20点")
                st.markdown(f"*{result['length_comment']}*")
            
            st.markdown("### 総評")
            st.markdown(f"「{result['overall_comment']}」")
            
            # こころとの出会いシーンと再挑戦ボタン
            if result['total_score'] < 60 and not st.session_state.has_met_kokoro:
                st.session_state.has_met_kokoro = True
                display_kokoro_scene()
            
            # スコアに応じてボタンを表示
            if result['total_score'] >= 80:
                if st.button("次へ進む"):
                    eval_container.empty()
                    st.session_state.game_state = 'next_chapter'
                    st.rerun()
            else:
                if st.button("課題に再挑戦する"):
                    # セッション状態をリセット
                    st.session_state.game_state = 'task'
                    st.session_state.start_time = None
                    st.session_state.task_submission = ''
                    st.session_state.evaluation_result = None
                    eval_container.empty()
                    st.rerun()

def main():
    st.set_page_config(
        page_title="経営戦略",
        page_icon="🏥"
    )
    init_session_state()
    
    # サイドバーの表示
    with st.sidebar:
        # タイマーとこころのコンテナを分けて配置
        if st.session_state.game_state in ['task', 'evaluation'] and st.session_state.start_time is not None:
            # タスク実行中と評価中はタイマーを表示
            elapsed_time = int((datetime.now() - st.session_state.start_time).total_seconds())
            remaining_time = max(300 - elapsed_time, 0)
            st.markdown("### ⏱ 残り時間")
            st.markdown(f"## {remaining_time // 60}分 {remaining_time % 60}秒")
            st.divider()
        
        # こころを下部に表示（評価画面での初回表示時は除外）
        if st.session_state.has_met_kokoro and not (st.session_state.game_state == 'evaluation' and st.session_state.evaluation_result is None):
            st.image("src/images/kokoro.webp", use_container_width=True)
            st.markdown("""
            ### 風花こころ
            「困ったことがあったら、いつでも相談してくださいね！」
            
            [こころに相談する](https://cocoro-assistant.streamlit.app/)
            """)
    
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
        elif st.session_state.game_state == 'task_intro':
            display_task_intro()
        elif st.session_state.game_state == 'task':
            display_task()
        elif st.session_state.game_state == 'evaluation':
            display_evaluation()
        elif st.session_state.game_state == 'next_chapter':
            st.title("試練の始まり")
            st.markdown("""
            なんとか最初の試練を乗り越え、深いため息をつく。
            
            しかし、針生事務長の厳しい目と、「これは始まりに過ぎない」という言葉が頭から離れない。
            
            来週からが本番。今回以上の試練が待ち受けているのだろうか...
            
            不安と期待が入り混じる中、私は帰路についた。　
            
            ---
            
            ### [次のチャプターへ進む](https://task-letter.streamlit.app/)
            """)

if __name__ == "__main__":
    main()
