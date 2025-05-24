import streamlit as st
import time
from datetime import datetime
import openai
from openai import OpenAI
import json
from typing import Dict

# ページ設定を最初に配置
st.set_page_config(
    page_title="紹介状地獄",
    page_icon="🏥"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# サンプル患者データ
SAMPLE_PATIENT = {
    "basic_info": {
        "name": "山田 太郎",
        "age": 45,
        "gender": "男性",
        "occupation": "IT企業管理職"
    },
    "referral_reason": "医師移動に伴う閉診のため",
    "recent_treatment": """
        1. 頭痛に対する治療経過：
           - 当初（1年前）：市販の頭痛薬で対応
           - 9ヶ月前：ロキソプロフェン 60mg 頓用処方開始
           - 6ヶ月前：肩頸部のストレッチ指導追加
           - 3ヶ月前：症状増悪のため、投薬調整（ロキソプロフェン 60mg 1日2回まで）

        2. 高血圧に対する治療経過：
           - 1年前：アムロジピン 2.5mg/日で開始
           - 9ヶ月前：血圧コントロール不十分のため 5mg/日に増量
           - 6ヶ月前：生活指導（減塩、運動療法）を強化
           - 現在：血圧は140-150/90前後で推移

        3. 生活指導の経過：
           - 6ヶ月前：残業時間の制限を提案（月45時間以内）
           - 3ヶ月前：昼休憩での仮眠導入を指導
           - 1ヶ月前：産業医面談を実施し、業務調整を依頼
    """,
    "chief_complaint": "慢性的な頭痛、めまい、首の痛み",
    "present_illness": """
        約3ヶ月前から徐々に頭痛が出現。特に午後から夕方にかけて増悪。
        VAS（痛みスケール）で7-8/10程度。
        市販の頭痛薬では改善乏しい。
        最近はめまいも伴うようになり、仕事への支障が出始めている。
    """,
    "past_medical_history": [
        "高血圧（3年前から加療中）",
        "胃潰瘍（5年前）"
    ],
    "medications": [
        "アムロジピン 5mg 1回/日",
        "ロキソプロフェン 60mg 頓用"
    ],
    "family_history": "父：脳梗塞（65歳）、母：高血圧",
    "lifestyle": {
        "smoking": "なし",
        "alcohol": "機会飲酒",
        "sleep": "6時間程度/日",
        "work_hours": "平均12時間/日",
        "stress_level": "高い"
    },
    "vital_signs": {
        "blood_pressure": "145/92 mmHg",
        "pulse": "84/分",
        "body_temperature": "36.7℃"
    },
    "physical_examination": """
        頸部：後頸部の圧痛あり、可動域制限軽度
        神経学的所見：明らかな局所神経症状なし
        眼底：KW分類 I度
        呼吸音：清、ラ音なし
        心音：整、雑音なし、S1→S2正常
    """,
    "recent_tests": {
        "blood_tests": "特記すべき異常なし",
        "ECG": "正常洞調律"
    },
    "referring_hospital": {
        "name": "やすらぎクリニック",
        "address": "福岡県福岡市中央区天神2-1-1",
        "phone": "092-123-4567",
        "doctor": "月森 航"
    },
    "referred_hospital": {
        "name": "天神内科クリニック",
        "address": "福岡県福岡市中央区天神1-10-20",
        "phone": "092-987-6543",
        "doctor": "田中 内科部長"
    }
}

def init_session_state():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'opening'
    if 'timer' not in st.session_state:
        st.session_state.timer = 300
    if 'letter_submission' not in st.session_state:
        st.session_state.letter_submission = ''
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'evaluation_result' not in st.session_state:
        st.session_state.evaluation_result = None

def display_patient_info():
    # 基本情報タブ
    basic_tab, history_tab, exam_tab, test_tab, hospital_tab, all_info_tab = st.tabs([
        "基本情報", 
        "既往歴・生活歴", 
        "身体所見・バイタル・検査",
        "治療経過",
        "医療機関情報",
        "全ての情報"
    ])
    
    with basic_tab:
        st.markdown("### 患者基本情報")
        basic_info = SAMPLE_PATIENT["basic_info"]
        st.write(f"氏名：{basic_info['name']}")
        st.write(f"年齢：{basic_info['age']}歳")
        st.write(f"性別：{basic_info['gender']}")
        st.write(f"職業：{basic_info['occupation']}")

        st.markdown("### 紹介理由")
        st.write(SAMPLE_PATIENT["referral_reason"])

        st.markdown("### 主訴")
        st.write(SAMPLE_PATIENT["chief_complaint"])

        st.markdown("### 現病歴")
        st.write(SAMPLE_PATIENT["present_illness"])

    with history_tab:
        st.markdown("### 既往歴")
        for history in SAMPLE_PATIENT["past_medical_history"]:
            st.write(f"- {history}")

        st.markdown("### 服薬中の薬剤")
        for med in SAMPLE_PATIENT["medications"]:
            st.write(f"- {med}")

        st.markdown("### 家族歴")
        st.write(SAMPLE_PATIENT["family_history"])

        st.markdown("### 生活歴")
        lifestyle = SAMPLE_PATIENT["lifestyle"]
        st.write(f"喫煙：{lifestyle['smoking']}")
        st.write(f"飲酒：{lifestyle['alcohol']}")
        st.write(f"睡眠：{lifestyle['sleep']}")
        st.write(f"労働時間：{lifestyle['work_hours']}")
        st.write(f"ストレスレベル：{lifestyle['stress_level']}")

    with exam_tab:
        st.markdown("### バイタルサイン")
        vital_signs = SAMPLE_PATIENT["vital_signs"]
        st.write(f"血圧：{vital_signs['blood_pressure']}")
        st.write(f"脈拍：{vital_signs['pulse']}")
        st.write(f"体温：{vital_signs['body_temperature']}")

        st.markdown("### 身体所見")
        st.write(SAMPLE_PATIENT["physical_examination"])

        st.markdown("### 検査所見")
        recent_tests = SAMPLE_PATIENT["recent_tests"]
        st.write(f"血液検査：{recent_tests['blood_tests']}")
        st.write(f"心電図：{recent_tests['ECG']}")

    with test_tab:
        st.markdown("### 最近の治療内容")
        st.write(SAMPLE_PATIENT["recent_treatment"])

    with hospital_tab:
        st.markdown("### 紹介元医療機関")
        referring = SAMPLE_PATIENT["referring_hospital"]
        st.write(f"医療機関：{referring['name']}")
        st.write(f"住所：{referring['address']}")
        st.write(f"電話番号：{referring['phone']}")
        st.write(f"担当医：{referring['doctor']}")

        st.markdown("### 紹介先医療機関")
        referred = SAMPLE_PATIENT["referred_hospital"]
        st.write(f"医療機関：{referred['name']}")
        st.write(f"住所：{referred['address']}")
        st.write(f"電話番号：{referred['phone']}")
        st.write(f"担当医：{referred['doctor']}")

    with all_info_tab:
        st.markdown("### 患者基本情報")
        basic_info = SAMPLE_PATIENT["basic_info"]
        st.write(f"氏名：{basic_info['name']}")
        st.write(f"年齢：{basic_info['age']}歳")
        st.write(f"性別：{basic_info['gender']}")
        st.write(f"職業：{basic_info['occupation']}")

        st.markdown("### 紹介理由")
        st.write(SAMPLE_PATIENT["referral_reason"])

        st.markdown("### 主訴")
        st.write(SAMPLE_PATIENT["chief_complaint"])

        st.markdown("### 現病歴")
        st.write(SAMPLE_PATIENT["present_illness"])

        st.markdown("### 既往歴")
        for history in SAMPLE_PATIENT["past_medical_history"]:
            st.write(f"- {history}")

        st.markdown("### 服薬中の薬剤")
        for med in SAMPLE_PATIENT["medications"]:
            st.write(f"- {med}")

        st.markdown("### 家族歴")
        st.write(SAMPLE_PATIENT["family_history"])

        st.markdown("### 生活歴")
        lifestyle = SAMPLE_PATIENT["lifestyle"]
        st.write(f"喫煙：{lifestyle['smoking']}")
        st.write(f"飲酒：{lifestyle['alcohol']}")
        st.write(f"睡眠：{lifestyle['sleep']}")
        st.write(f"労働時間：{lifestyle['work_hours']}")
        st.write(f"ストレスレベル：{lifestyle['stress_level']}")

        st.markdown("### バイタルサイン")
        vital_signs = SAMPLE_PATIENT["vital_signs"]
        st.write(f"血圧：{vital_signs['blood_pressure']}")
        st.write(f"脈拍：{vital_signs['pulse']}")
        st.write(f"体温：{vital_signs['body_temperature']}")

        st.markdown("### 身体所見")
        st.write(SAMPLE_PATIENT["physical_examination"])

        st.markdown("### 検査所見")
        recent_tests = SAMPLE_PATIENT["recent_tests"]
        st.write(f"血液検査：{recent_tests['blood_tests']}")
        st.write(f"心電図：{recent_tests['ECG']}")

        st.markdown("### 最近の治療内容")
        st.write(SAMPLE_PATIENT["recent_treatment"])

        st.markdown("### 医療機関情報")
        st.markdown("#### 紹介元医療機関")
        referring = SAMPLE_PATIENT["referring_hospital"]
        st.write(f"医療機関：{referring['name']}")
        st.write(f"住所：{referring['address']}")
        st.write(f"電話番号：{referring['phone']}")
        st.write(f"担当医：{referring['doctor']}")

        st.markdown("#### 紹介先医療機関")
        referred = SAMPLE_PATIENT["referred_hospital"]
        st.write(f"医療機関：{referred['name']}")
        st.write(f"住所：{referred['address']}")
        st.write(f"電話番号：{referred['phone']}")
        st.write(f"担当医：{referred['doctor']}")

def evaluate_letter(text: str) -> Dict[str, any]:
    """紹介状をGPT-4で評価する"""
    try:
        # 文字数をカウント
        char_count = len(text)
        # 文字数の評価（400文字からの距離に基づいて0-20点を計算）
        length_score = max(0, 20 - abs(char_count - 400) // 40)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"""あなたは医療文書の専門家です。
提出された紹介状を評価し、必ず以下の形式のJSONのみを返してください。厳しめに評価してください。
説明文や追加のコメントは一切含めないでください。

評価の重要なポイント：
1. 紹介状は手紙形式の文章として完結している必要があります
2. 箇条書きの使用は大きな減点対象です（-10点）
3. 手紙としての基本的な形式を守っているかを確認してください
4. 文章の流れが自然で、一貫性があるかを評価してください

現在の文字数は{char_count}文字です（目標は400文字）。

{{
    "format_score": (1-25の整数。箇条書きの使用は-10点。手紙形式でない場合は-15点),
    "format_comment": "文書形式についての評価。一連の文章になっているかを採点。箇条書きの使用は原点",
    "content_score": (1-25の整数),
    "content_comment": "必要な情報が含まれているか,不要な情報がないかの簡潔な評価コメント",
    "clarity_score": (1-25の整数),
    "clarity_comment": "医師から見た明確さの観点からの簡潔な評価コメント",
    "length_score": {length_score},
    "length_comment": "文字数に関するコメント",
    "total_score": (上記スコアの合計),
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

def display_evaluation():
    # 専用のコンテナを作成
    evaluation_container = st.empty()
    
    with evaluation_container.container():
        st.title("評価結果")
        
        if st.session_state.evaluation_result is None:
            with st.spinner("鬼島院長は真剣な表情で、あなたの紹介状に目を通している..."):
                result = evaluate_letter(st.session_state.letter_submission)
                if result:
                    st.session_state.evaluation_result = result

        if st.session_state.evaluation_result:
            result = st.session_state.evaluation_result
            
            # 総合点に基づいて院長の反応を3段階で表示
            if result['total_score'] < 60:
                st.markdown("""
                ## 不合格
                鬼島院長は眉をひそめ、ため息をつきながら言った。
                「これはいただけないな...基本的な要件も満たしていない。
                医師として必要な文書作成能力も身についていないのか...」
                """)
            elif result['total_score'] < 80:
                st.markdown("""
                ## 改善の余地あり
                鬼島院長は腕を組み、眉間にしわを寄せながらじっと考え込むような表情を見せた。
                「ふむ...まあ、及第点といったところだな。
                だが、まだまだ改善の余地はあるな。やり直しだ！」
                """)
            else:
                st.markdown("""
                ## 高評価
                鬼島院長は満足げな表情を浮かべ、頷いた。
                「なかなかやるじゃないか。簡潔かつ必要な情報が過不足なく含まれている。
                これなら受け取った医師も患者の状態を十分に理解できるだろう」
                """)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("総合評価", f"{result['total_score']}/100点")
            with col2:
                char_count = len(st.session_state.letter_submission)
                st.metric("文字数", f"{char_count}/400文字")
            
            st.markdown("#### 項目別評価")
            cols = st.columns(5)
            with cols[0]:
                st.metric("文書形式", f"{result['format_score']}/25点")
                st.markdown(f"*{result['format_comment']}*")
            with cols[1]:
                st.metric("内容充実度", f"{result['content_score']}/25点")
                st.markdown(f"*{result['content_comment']}*")
            with cols[2]:
                st.metric("明確さ", f"{result['clarity_score']}/25点")
                st.markdown(f"*{result['clarity_comment']}*")
            with cols[3]:
                st.metric("文字数", f"{result['length_score']}/25点")
                st.markdown(f"*{result['length_comment']}*")
            
            if result['total_score'] >= 80:
                if st.button("次へ進む"):
                    evaluation_container.empty()
                    st.session_state.game_state = 'next_chapter'
                    st.rerun()
            else:
                if st.button("再挑戦する"):
                    evaluation_container.empty()  # コンテナをクリア
                    st.session_state.letter_submission = ''
                    st.session_state.evaluation_result = None
                    st.session_state.game_state = 'task'
                    st.session_state.start_time = datetime.now()
                    st.rerun()

def display_opening():
    st.title("第２章：紹介状地獄")
    st.image('src/images/onishima.webp', width=500)
    if st.button('次へ'):
        st.session_state.game_state = 'task_intro'
        st.rerun()

def display_story():
    # 専用のコンテナを作成
    story_container = st.empty()
    
    with story_container.container():
        st.title("第２章：紹介状地獄")
        st.markdown("""
        今日は午前と午後で100人以上の患者を診察した。時間は21時を過ぎていた。
                    
        このクリニックは患者が多すぎる
                    
        疲労困憊の体を引きずりながら、ロッカールームへ戻ろうとすると、事務員から「鬼島院長が院長室で待っている」と声をかけられた。        

        蛍光灯が不気味にちらつく中、鬼島院長の巨大な革張りの椅子がゆっくりと回転する。

        「おやおや、お疲れのようだね。初日からそんなことでは先が思いやられるぞ。」
                    
        「はい、明日からはもっと頑張ります！」
        
        「ん？何を言っているんだ？君はまだ帰れないよ。今日のタスクが残っているからね」

        鬼島院長の唇が歪んだ笑みを形作る。机の上には山積みの患者カルテが積み上げられている。

        「明日の朝9時までに、この100人の患者全員の紹介状を書いてもらおうかな
                    
        昨日ひとり医師をクビにしたんだが、外来も整理せずにいなくなりやがったんだよ」

        あなたの顔から血の気が引く。通常、1通の紹介状を書くのに30分はかかる。100通となれば50時間...物理的に不可能な要求だ。

        「え...でも、それは...」

        「なにか？できないとでも？」鬼島院長の声が冷たく響く。「君、研修医としての適性を疑われても構わないのかな？」

        あなたは覚悟を決めた。紹介状を1通あたり5分で書くしかない             
        """)
        
        if st.button('タスクを始める'):
            story_container.empty()  # コンテナをクリア
            st.session_state.game_state = 'task'
            st.session_state.start_time = datetime.now()  # タイマーの開始時間を設定
            st.rerun()

def display_task():
    if st.session_state.game_state != 'task':  # タスク画面でない場合は処理を行わない
        return
    
    task_container = st.empty()
    
    with task_container.container():
        # タスク開始時に start_time が設定されていない場合は設定
        if st.session_state.start_time is None:
            st.session_state.start_time = datetime.now()
        
        st.title("第２章：紹介状地獄")
        st.subheader("以下の患者情報を元に、紹介状を作成せよ")
        
        elapsed_time = int((datetime.now() - st.session_state.start_time).total_seconds())
        remaining_time = max(300 - elapsed_time, 0)
        
        st.markdown(f"### 残り時間: {remaining_time // 60}分 {remaining_time % 60}秒")
        
        if st.session_state.evaluation_result is None:
            display_patient_info()
            
            st.divider()
            
            st.markdown("### 紹介状の作成")
            
            # 入力欄の内容を常にセッションステートに保存
            current_text = st.text_area(
                "紹介状を入力してください",
                st.session_state.letter_submission,
                height=400
            )
            st.session_state.letter_submission = current_text
            
            submit = st.button("紹介状を提出")
            
            # 時間切れまたは提出ボタンが押された場合の処理
            if remaining_time <= 0 or submit:
                # 現在の入力内容を保持したまま評価画面へ移行
                task_container.empty()
                st.session_state.game_state = 'evaluation'
                st.rerun()
            
            # タイマー更新のための処理
            if remaining_time > 0:
                time.sleep(1)
                st.rerun()
        else:
            display_evaluation()

def display_sidebar():
    with st.sidebar:
        # タイマーの表示
        if st.session_state.start_time is not None:
            elapsed_time = int((datetime.now() - st.session_state.start_time).total_seconds())
            remaining_time = max(300 - elapsed_time, 0)  # 5分=300秒
            st.markdown("### ⏱ 残り時間")
            st.markdown(f"## {remaining_time // 60}分 {remaining_time % 60}秒")
            st.divider()
        
        # こころの表示
        st.image("src/images/kokoro.webp", use_container_width=True)
        st.markdown("""
        ### 風花こころ
        「困ったことがあったら、いつでも相談してくださいね！」
        
        [こころに相談する](https://cocoro-assistant.streamlit.app/)
        """)

def main():
    init_session_state()
    display_sidebar()  # サイドバーの表示を追加
    
    if st.session_state.game_state == 'opening':
        display_opening()
        return
    
    if st.session_state.game_state == 'task_intro':
        display_story()
        return
        
    if st.session_state.game_state == 'task':
        display_task()
        return
    
    if st.session_state.game_state == 'evaluation':
        display_evaluation()
        return

    if st.session_state.game_state == 'next_chapter':
        st.title("100通の紹介状")
        st.markdown("""
        「よし、合格だ。」

        鬼島院長は満足げな表情を浮かべながら、紹介状から目を上げた。

        「これなら他の100通も任せられそうだな。」

        「え？100通...ですか？」
        """)

        st.text("")
        st.text("")

        st.text("こうなったらやるしかない")

        st.text("")
        st.text("")

        st.markdown("""
        こころの助けを借りながら、あなたは1時間足らずで100通の紹介状を書き上げた。

        モニターに映し出される完成された紹介状の山は、あなたの集中力と、こころのサポートの証だ。 
                    
        最後の紹介状を保存し、あなたは深く息を吐き出した。 短時間での驚異的な作業量に、 自分でも信じられないような感覚を覚える。 
        
        疲労はあるものの、それ以上に達成感が胸を満たしていた。

        ---
        
        ### [次のチャプターへ進む](https://dif-diagnosis.streamlit.app/)
        """)
        return

if __name__ == "__main__":
    main()
