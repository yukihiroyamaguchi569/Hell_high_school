import streamlit as st
import time
from datetime import datetime
import openai
from openai import OpenAI
import json
from typing import Dict
from streamlit import tabs

st.set_page_config(
    page_title="鑑別診断",
    page_icon="🏥"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# サンプル患者データ
SAMPLE_PATIENT = {
    "basic_info": {
        "name": "佐藤 美咲",
        "age": 28,
        "gender": "女性",
        "occupation": "事務職"
    },
    "chief_complaint": "突然の激しい腹痛、嘔吐",
    "present_illness": """
        本日午後2時頃より突然の激しい腹痛が出現。
        痛みは右下腹部に限局し、体動で増強。
        悪心・嘔吐を2回認める。
        38.2度の発熱あり。
        食欲低下、下痢なし。
        最終月経は2週間前、規則的。
    """,
    "past_medical_history": [
        "特記すべき既往なし",
        "手術歴なし"
    ],
    "medications": [
        "常用薬なし",
        "市販薬の使用なし"
    ],
    "family_history": "特記事項なし",
    "lifestyle": {
        "smoking": "なし",
        "alcohol": "機会飲酒",
        "sleep": "良好",
        "work_hours": "通常8時間/日",
        "stress_level": "普通"
    },
    "vital_signs": {
        "blood_pressure": "118/76 mmHg",
        "pulse": "96/分",
        "body_temperature": "38.2℃",
        "respiratory_rate": "20/分",
        "SpO2": "98%（室内気）"
    },
    "physical_examination": """
        意識：清明
        全身状態：やや苦悶様
        腹部：右下腹部に強い圧痛あり
        筋性防御：軽度あり
        反跳痛：陽性
        腸蠕動音：減弱
        その他の身体所見：特記すべき異常なし
    """,
    "recent_tests": {
        "blood_tests": "未実施",
        "imaging": "未実施"
    },
    "referring_hospital": {
        "name": "当院救急外来",
        "doctor": "当直医"
    },
    "referred_hospital": {
        "name": "未定",
        "doctor": "未定"
    }
}

def init_session_state():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'opening'
    if 'diagnosis_submission' not in st.session_state:
        st.session_state.diagnosis_submission = ''
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'evaluation_result' not in st.session_state:
        st.session_state.evaluation_result = None
    if 'next_chapter' not in st.session_state:
        st.session_state.next_chapter = False

def display_patient_info():
    # 基本情報タブ
    basic_tab, history_tab, exam_tab, test_tab, all_info_tab = st.tabs([
        "基本情報・主訴", 
        "既往歴・生活歴", 
        "身体所見・バイタル",
        "検査所見",
        "すべての情報"
    ])
    
    with basic_tab:
        st.markdown("### 患者基本情報")
        basic_info = SAMPLE_PATIENT["basic_info"]
        st.write(f"氏名：{basic_info['name']}")
        st.write(f"年齢：{basic_info['age']}歳")
        st.write(f"性別：{basic_info['gender']}")
        st.write(f"職業：{basic_info['occupation']}")

        st.markdown("### 受診理由")

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
        st.write(f"呼吸数：{vital_signs['respiratory_rate']}")
        st.write(f"SpO2：{vital_signs['SpO2']}")

        st.markdown("### 身体所見")
        st.write(SAMPLE_PATIENT["physical_examination"])

    with test_tab:
        st.markdown("### 検査所見")
        recent_tests = SAMPLE_PATIENT["recent_tests"]
        st.write(f"血液検査：{recent_tests['blood_tests']}")
        st.write(f"画像検査：{recent_tests['imaging']}")

    with all_info_tab:
        st.markdown("### 患者基本情報")
        basic_info = SAMPLE_PATIENT["basic_info"]
        st.write(f"氏名：{basic_info['name']}")
        st.write(f"年齢：{basic_info['age']}歳")
        st.write(f"性別：{basic_info['gender']}")
        st.write(f"職業：{basic_info['occupation']}")

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
        st.write(f"呼吸数：{vital_signs['respiratory_rate']}")
        st.write(f"SpO2：{vital_signs['SpO2']}")

        st.markdown("### 身体所見")
        st.write(SAMPLE_PATIENT["physical_examination"])

        st.markdown("### 検査所見")
        recent_tests = SAMPLE_PATIENT["recent_tests"]
        st.write(f"血液検査：{recent_tests['blood_tests']}")
        st.write(f"画像検査：{recent_tests['imaging']}")

def evaluate_diagnosis(text: str) -> Dict[str, any]:
    """鑑別診断をGPT-4で評価する"""
    try:
        # 入力が空か最小限の長さに満たない場合は自動的に低評価
        if not text or len(text.strip()) < 50:
            return {
                "completeness_score": 0,
                "completeness_comment": "鑑別診断が入力されていないか、極めて不十分です。",
                "reasoning_score": 0,
                "reasoning_comment": "理由付けがありません。",
                "priority_score": 0,
                "priority_comment": "評価できる内容がありません。",
                "presentation_score": 0,
                "presentation_comment": "記載がありません。",
                "total_score": 0
            }

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """あなたは厳格な医療評価者です。
提出された鑑別診断を以下の基準で厳密に評価し、JSONを返してください。
口調は性格の悪い院長の皮肉交じりの口調です。優しい言葉はかけません

評価基準：
1. 網羅性（25点）
- 10個の鑑別診断が挙げられているか（各2点、最大20点）
- 重要な鑑別が含まれているか（最大5点）
- 1つも挙げられていない場合は0点

2. 理由付け（25点）
- 各鑑別診断に適切な理由が付されているか（各2点、最大20点）
- 理由の医学的妥当性（最大5点）
- 理由が書かれていない場合は0点

3. 優先順位（25点）
- 緊急度・重症度による順序付け（最大15点）
- 頻度や患者背景の考慮（最大10点）
- 順序付けがない場合は0点

4. 記載方法（25点）
- 明確な箇条書きで記載（最大10点）
- 簡潔かつ具体的な記述（最大10点）
- 医学用語の適切な使用（最大5点）
- 形式が整っていない場合は最大5点

必ず以下の形式のJSONのみを返してください：

{
    "completeness_score": (0-25の整数),
    "completeness_comment": "具体的な評価コメント",
    "reasoning_score": (0-25の整数),
    "reasoning_comment": "具体的な評価コメント",
    "priority_score": (0-25の整数),
    "priority_comment": "具体的な評価コメント",
    "presentation_score": (0-25の整数),
    "presentation_comment": "具体的な評価コメント",
    "total_score": (上記スコアの合計)
}"""},
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
    st.title("評価結果")
    
    evaluation_container = st.empty()
    
    if st.session_state.evaluation_result is None:
        with st.spinner("鬼島院長は真剣な表情で、あなたの鑑別診断に目を通している..."):
            result = evaluate_diagnosis(st.session_state.diagnosis_submission)
            if result:
                st.session_state.evaluation_result = result

    if st.session_state.evaluation_result:
        result = st.session_state.evaluation_result
        
        with evaluation_container.container():
            if result['total_score'] < 60:
                st.markdown("""
                鬼島院長は眉をひそめ、ため息をつきながら言った。
                「これでは患者を危険にさらすことになるぞ...まったく、使えないやつだな」
                """)
            elif result['total_score'] < 80:
                st.markdown("""
                鬼島院長は腕を組み、じっと考え込むような表情を見せた。
                「まあ、及第点といったところかな。この程度だと思っていたよ」
                """)
            else:
                st.markdown("""
                鬼島院長は満足げな表情を浮かべ、頷いた。
                「お前なかなかやるじゃねえか。見た目にはわからんがな」
                """)
            
            st.markdown("### 鬼島院長からの評価")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("総合評価", f"{result['total_score']}/100点")
            
            st.markdown("#### 項目別評価")
            cols = st.columns(4)
            with cols[0]:
                st.metric("網羅性", f"{result['completeness_score']}/25点")
                st.markdown(f"*{result['completeness_comment']}*")
            with cols[1]:
                st.metric("理由付け", f"{result['reasoning_score']}/25点")
                st.markdown(f"*{result['reasoning_comment']}*")
            with cols[2]:
                st.metric("優先順位", f"{result['priority_score']}/25点")
                st.markdown(f"*{result['priority_comment']}*")
            with cols[3]:
                st.metric("記載方法", f"{result['presentation_score']}/25点")
                st.markdown(f"*{result['presentation_comment']}*")
            
            if result['total_score'] >= 80:
                if st.button("次へ進む"):
                    st.session_state.game_state = 'next_chapter'
                    st.rerun()
            else:
                if st.button("もう一度挑戦する"):
                    evaluation_container.empty()
                    reset_evaluation()
                    st.rerun()

def reset_evaluation():
    # 評価に関連する変数をリセット
    st.session_state.diagnosis_submission = ''
    st.session_state.evaluation_result = None
    st.session_state.game_state = 'task'
    st.session_state.start_time = datetime.now()

def display_opening():
    st.title("第３章：鑑別診断")
    st.image('src/images/onishima-yoko.webp', width=500)
    if st.button('次へ'):
        st.session_state.game_state = 'task_intro'
        st.rerun()

def display_story():
    story_container = st.empty()
    
    with story_container.container():
        st.title("第３章：鑑別診断")
        st.markdown("""
        救急外来での当直勤務も終盤に差し掛かり、あなたは疲労困憊の状態だった。
                    
        「ようやく一段落したな...」
                    
        そう思った矢先、救急外来のドアが勢いよく開く。

        「月森！」

        振り返ると、そこには鬼島院長が立っていた。

        「ちょうどよかった。急患だ、具合が悪そうだから先に診ろ！」

        鬼島院長は一枚のカルテを取り出した。

        「この患者の鑑別診断を2分以内に10個挙げてもらおう。理由も付けてね」

        「え...2分ですか？」

        「なに？できないとでも？」鬼島院長の目が鋭く光る。「救急患者の対応には瞬時の判断が求められるんだよ」

        「現場では患者の命がその判断にかかっている。甘く考えるな！」

        あなたは深く息を吸い込んだ。これも医師としての腕を磨くチャンスなのだ。             
        """)
        
        if st.button('タスクを始める'):
            story_container.empty()
            st.session_state.game_state = 'task'
            st.session_state.start_time = datetime.now()
            st.rerun()

def display_task():
    if st.session_state.game_state != 'task':
        return
    
    task_container = st.empty()
    
    with task_container.container():
        if st.session_state.start_time is None:
            st.session_state.start_time = datetime.now()
        
        st.title("第３章：鑑別診断")
        st.subheader("以下の患者情報から考えられる鑑別診断を10個挙げよ")
        
        elapsed_time = int((datetime.now() - st.session_state.start_time).total_seconds())
        remaining_time = max(120 - elapsed_time, 0)
        
        st.markdown(f"### 残り時間: {remaining_time}秒")
        
        if st.session_state.evaluation_result is None:
            # 患者情報の表示
            display_patient_info()
            
            st.divider()
            
            # 鑑別診断入力セクション
            st.markdown("### 鑑別診断の入力")
            st.markdown("""
            患者情報を元に、考えられる鑑別診断を10個挙げ、それぞれに簡単な理由を付けてください。
            """)
            
            current_text = st.text_area(
                "鑑別診断を入力してください",
                st.session_state.get('diagnosis_submission', ''),
                height=400
            )
            st.session_state.diagnosis_submission = current_text
            
            submit = st.button("診断を提出")
            
            if remaining_time <= 0 or submit:
                task_container.empty()
                st.session_state.game_state = 'evaluation'
                st.rerun()
            
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
            remaining_time = max(120 - elapsed_time, 0)  # 2分=120秒
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
        st.title("休息なき戦いへ")
        st.markdown("""
        鬼島院長は満足げな表情を浮かべながら、あなたの肩を強く叩いた。

        「よし、お前なら大丈夫だな！実はな、待合室に20人の患者が待ってるんだ。
        全部お前に任せるから、朝までに片付けておいてくれ！」

        「あと、救急車も2台来るって連絡が入ってる。まあ、頑張れよ！」

        鬼島院長は意地の悪い笑みを浮かべながら、颯爽と立ち去っていった。

        あなたは深いため息をつきながら、カルテを手に取った...。

        ---
        
        ### [次のチャプターへ進む](https://task-image.streamlit.app/)
        """)
        return

if __name__ == "__main__":
    main()
