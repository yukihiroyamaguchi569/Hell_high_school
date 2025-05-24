import streamlit as st
import time
from datetime import datetime
import openai
from openai import OpenAI
import json
from typing import Dict
import pandas as pd

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# サンプル患者データ
SAMPLE_EXCEL_DATA = {
    "診療科": ["内科", "外科", "小児科", "内科", "整形外科"],
    "患者数": [150, 80, 60, 130, 90],
    "平均待ち時間": [45, 30, 20, 40, 25],
    "医師数": [3, 2, 1, 2, 2],
    "看護師数": [5, 4, 2, 4, 3],
    "患者満足度": [3.8, 4.2, 4.5, 3.9, 4.0]
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

def evaluate_letter(text: str) -> Dict[str, any]:
    """分析レポートをGPT-4で評価する"""
    try:
        char_count = len(text)
        length_score = max(0, 20 - abs(char_count - 800) // 40)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""あなたはデータ分析の専門家です。
提出された分析レポートを評価し、以下の形式のJSONのみを返してください。

現在の文字数は{char_count}文字です（目標は800文字）。

{{
    "analysis_score": (1-25の整数),
    "analysis_comment": "データ分析の深さと正確性についての評価",
    "solutions_score": (1-25の整数),
    "solutions_comment": "提案された解決策の実現可能性と効果についての評価",
    "logic_score": (1-25の整数),
    "logic_comment": "論理的な思考と説明の明確さについての評価",
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
            return json.loads(content)
        except json.JSONDecodeError as e:
            st.error(f"JSONのパースに失敗しました: {str(e)}")
            return None
    except Exception as e:
        st.error(f"評価中にエラーが発生しました: {str(e)}")
        return None

def display_evaluation():
    st.title("評価結果")
    
    if st.session_state.evaluation_result is None:
        with st.spinner("鬼島院長は真剣な表情で、あなたの紹介状に目を通している..."):
            result = evaluate_letter(st.session_state.letter_submission)
            if result:
                st.session_state.evaluation_result = result

    if st.session_state.evaluation_result:
        result = st.session_state.evaluation_result
        
        # 院長の表情と最初のコメント
        if result['total_score'] < 60:
            st.markdown("""
            鬼島院長は眉をひそめ、ため息をつきながら言った。
            「これはいただけないな...」
            """)
        elif result['total_score'] < 80:
            st.markdown("""
            鬼島院長は腕を組み、じっと考え込むような表情を見せた。
            「ふむ...」
            """)
        else:
            st.markdown("""
            鬼島院長は満足げな表情を浮かべ、頷いた。
            「なかなかやるじゃないか」
            """)
        
        st.markdown("### 鬼島院長からの評価")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("総合評価", f"{result['total_score']}/100点")
        with col2:
            char_count = len(st.session_state.letter_submission)
            st.metric("文字数", f"{char_count}/800文字")
        
        st.markdown("#### 項目別評価")
        cols = st.columns(5)
        with cols[0]:
            st.metric("分析深さ", f"{result['analysis_score']}/25点")
            st.markdown(f"*{result['analysis_comment']}*")
        with cols[1]:
            st.metric("解決策実現性", f"{result['solutions_score']}/25点")
            st.markdown(f"*{result['solutions_comment']}*")
        with cols[2]:
            st.metric("論理的思考", f"{result['logic_score']}/25点")
            st.markdown(f"*{result['logic_comment']}*")
        with cols[3]:
            st.metric("文字数", f"{result['length_score']}/25点")
            st.markdown(f"*{result['length_comment']}*")
        
        if st.button("再挑戦する"):
            st.session_state.letter_submission = ''
            st.session_state.evaluation_result = None
            st.session_state.game_state = 'task'
            st.session_state.start_time = datetime.now()
            st.rerun()

def display_opening():
    st.title("第２章：データ分析地獄")
    st.image('src/images/onishima.webp', width=500)
    if st.button('次へ'):
        st.session_state.game_state = 'task_intro'
        st.rerun()

def display_story():
    story_container = st.empty()
    
    with story_container.container():
        st.title("第２章：データ分析地獄")
        st.markdown("""
        深夜の院長室。鬼島院長は冷ややかな笑みを浮かべながら言った。

        「君は経営分析もできなければならない。このExcelデータを分析して、
        明日の朝までに改善案を提出してもらおうかな」

        疲れ切った体に鞭打ちながら、あなたはデータと向き合うことになった...
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
        
        st.title("第２章：データ分析地獄")
        st.subheader("以下の病院データを分析し、改善案を提案せよ")
        
        elapsed_time = int((datetime.now() - st.session_state.start_time).total_seconds())
        remaining_time = max(300 - elapsed_time, 0)
        
        st.markdown(f"### 残り時間: {remaining_time // 60}分 {remaining_time % 60}秒")
        
        if st.session_state.evaluation_result is None:
            # Excelデータの表示
            df = pd.DataFrame(SAMPLE_EXCEL_DATA)
            st.markdown("### 病院運営データ")
            st.dataframe(df)
            
            # データの可視化
            st.markdown("### データ分析グラフ")
            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(df.set_index('診療科')['患者数'])
            with col2:
                st.line_chart(df.set_index('診療科')['平均待ち時間'])
            
            st.markdown("### 分析レポートの作成")
            st.markdown("""
            上記のデータを分析し、以下の点について改善案を提案してください：
            1. 各診療科の効率性
            2. 待ち時間の改善策
            3. 人員配置の最適化
            4. 患者満足度向上のための具体的な施策
            """)
            
            st.session_state.letter_submission = st.text_area(
                "分析レポートを入力してください",
                st.session_state.letter_submission,
                height=400
            )
            
            submit = st.button("レポートを提出")
            
            if remaining_time <= 0 or submit:
                task_container.empty()
                st.session_state.game_state = 'evaluation'
                st.rerun()
            
            if remaining_time > 0:
                time.sleep(1)
                st.rerun()
        else:
            display_evaluation()

def main():
    init_session_state()
    
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

if __name__ == "__main__":
    main()
