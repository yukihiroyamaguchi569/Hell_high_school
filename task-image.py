import streamlit as st
from openai import OpenAI
import json

# ページ設定を最初に配置
st.set_page_config(
    page_title="お絵かき地獄",
    page_icon="🏥"
)

# OpenAI APIキーの設定
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_image(prompt):
    """DALL-E 3で画像を生成する関数"""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        st.error("申し訳ありません。その絵はかけませんでした\n"
                "別の絵にしていただけますか？")
        return None

def evaluate_image(image_url, target_description):
    """Vision APIで画像を分析し、お題とのマッチ度をGPT-4oで評価する関数"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": f"""あなたは画像評価の専門家です。提出された画像を評価し、必ず以下の形式のJSONのみを返してください。厳しめに評価してください。
説明文や追加のコメントは一切含めないでください。

評価の重要なポイント：
1. お題の内容と画像のテーマがどれくらい一致しているか
2. 画像にオリジナリティやユニークな表現が見られるか
3. 画像の構図、色彩、ディテールの完成度は高いか
4. 画像がお題から意図される感情や雰囲気を効果的に伝えているか

{{
    "relevance_score": (1-25の整数),
    "relevance_comment": "お題との関連性についての評価",
    "creativity_score": (1-25の整数),
    "creativity_comment": "創造性やユニークさについての評価",
    "quality_score": (1-25の整数),
    "quality_comment": "画像の品質についての評価",
    "emotion_score": (1-25の整数),
    "emotion_comment": "感情や雰囲気の伝達についての評価",
    "total_score": (上記スコアの合計),
}}"""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"この画像は「{target_description}」というお題に対して評価してください。"},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
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
    """評価結果を表示する関数"""
    evaluation_container = st.empty()

    with evaluation_container.container():
        st.title("評価結果")

        if st.session_state.evaluation_result is None:
            with st.spinner("看護部長は難しい顔で画像を眺めている..."):
                result = evaluate_image(st.session_state.generated_image, st.session_state.current_theme)
                if result:
                    st.session_state.evaluation_result = result

        if st.session_state.evaluation_result:
            result = st.session_state.evaluation_result

            # 総合点に基づいて鬼看護部長のリアクションを表示
            if result['total_score'] < 60:
                st.markdown("""
                ## ふん！これが限界ですの？
                まったく期待はずれね。こんな出来では患者さんに見せる前に没にするわよ！
                やり直しなさい。**今度こそ真面目に取り組むことね？**
                """)
            elif result['total_score'] < 80:
                st.markdown("""
                ## まぁまぁね...
                及第点といったところかしら。でも私の病院では、「まぁまぁ」では通用しないわ！
                もう少し工夫できるはずよ。*次は完璧を目指しなさい！*
                """)
            else:
                st.markdown("""
                ### 素晴らしいわ！さすがね！
                これこそ私の求めていた理想的な画像よ。病院の雰囲気にぴったりだわ。
                            
                あなた、なかなかやるわね！
                
                """)

            col1, _ = st.columns(2)
            with col1:
                st.metric("総合評価", f"{result['total_score']}/100点")

            st.markdown("#### 項目別評価")
            cols = st.columns(4)
            with cols[0]:
                st.metric("関連性", f"{result['relevance_score']}/25点")
                st.markdown(f"*{result['relevance_comment']}*")
            with cols[1]:
                st.metric("創造性", f"{result['creativity_score']}/25点")
                st.markdown(f"*{result['creativity_comment']}*")
            with cols[2]:
                st.metric("品質", f"{result['quality_score']}/25点")
                st.markdown(f"*{result['quality_comment']}*")
            with cols[3]:
                st.metric("感情", f"{result['emotion_score']}/25点")
                st.markdown(f"*{result['emotion_comment']}*")

            if result['total_score'] >= 80:
                if st.session_state.current_theme_index == len(st.session_state.themes) - 1:
                    # 全てのテーマをクリアした場合
                    st.session_state.completed_tasks += 1
                    st.session_state.page = "ending"  # 直接エンディングへ移動
                    st.rerun()
                else:
                    # まだ残りのテーマがある場合
                    if st.button("次のお題へ"):
                        st.session_state.current_theme_index += 1
                        st.session_state.generated_image = None
                        st.session_state.submitted = False
                        st.session_state.evaluation_result = None
                        st.rerun()
            else:
                if st.button("再挑戦する"):
                    st.session_state.generated_image = None
                    st.session_state.submitted = False
                    st.session_state.evaluation_result = None
                    st.rerun()

def display_opening():

    st.title("第４章：画像生成試練")

    st.image("src/images/nurse.webp", caption="看護部長の刃野 千尋（はの ちひろ）")

    st.markdown("""
                
   「おい！研修医！！」

    鋭い声にあなたはドキリとして立ちどまった。
                
    振り返ると、看護部長の刃野 千尋（はの ちひろ）がこちらを睨んでいた。
                
    彼女はあなたに向かって指を指しこういった。

    「あなた優秀らしいわね。よろしい、私が特別な試練を与えてあげるわ。
                
    　私の期待に応えられるかしら？」

    その言葉に、あなたは心の中で深いため息をつきながら、鬼部長の鋭い視線に思わず体が縮こまるのを感じた。
                
    """)
    
    if st.button("試練に挑戦する", type="secondary"):
        st.session_state.page = "nurse"
        st.rerun()

def display_nurse():
    """鬼看護部長のセリフと状況説明を表示する関数"""
    st.markdown("""
    ### 鬼看護部長からの強制指令
    「院内に飾る絵を書きなさい！」

    鬼看護部長は腕を組み、鋭い眼差しであなたを見つめている。その視線の重みに思わず背筋が伸びる。

    「え...絵ですか...？」
                
    「病院の雰囲気作りは患者さんの回復に大きく影響するのよ。
                
    　だからこそ、掲示する画像には特別な配慮が必要なの。
    
    　あなたのセンスと感性を見せてもらうわ。期待を裏切らないように願うわね？ふふふ...」""")

    st.text("")
    st.text("")

    st.markdown("""
    あなたは冷や汗を流した。絵心のかけらもない自分には、とても看護部長の期待に応えられそうにない。
    
    そうだ！こころなら素晴らしい絵を描いてくれるはず。彼女の力を借りるしかない...！
    """)

    st.text("")
    st.text("")

def display_ending():
    """エンディング画面を表示する関数"""
    st.title("試練クリア！")

    st.markdown("""
    ### 看護部長からの評価
    
    「まさか...全ての試練をクリアするとは...！」

    看護部長は腕を組んだまま、あなたをじっと見つめている。
    その表情には、これまでの鋭さは影を潜め、どこか温かみのある微笑みが浮かんでいた。

    「あなた、なかなかやるじゃない。
    私の期待以上の結果を見せてくれたわ。

    どうせ、こころに手伝ってもらったんでしょうけど、他の職種との連携はますまず重要になるわ

    あなた達の協力関係は、私たちの病院にとって大きな資産になるでしょう。

    これからも期待しているわよ？」

    看護部長はそう言うと、颯爽と立ち去っていった...。
    """)

    st.markdown("### [エンディングへ進む](https://clinic-ending.streamlit.app/)")

def main():
    if 'page' not in st.session_state:
        st.session_state.page = "opening"
    if 'completed_tasks' not in st.session_state:
        st.session_state.completed_tasks = 0

    if st.session_state.page == "opening":
        display_opening()
        return
    elif st.session_state.page == "nurse":
        display_nurse()
        if st.button("試練を開始する", type="secondary"):
            st.session_state.page = "task"
            st.rerun()
        return
    elif st.session_state.page == "ending":
        display_ending()
        return
    elif st.session_state.page == "task":
        st.title("第４章：画像生成試練")

        # セッション状態の初期化
        if 'current_theme_index' not in st.session_state:
            st.session_state.current_theme_index = 0
        if 'generated_image' not in st.session_state:
            st.session_state.generated_image = None
        if 'submitted' not in st.session_state:
            st.session_state.submitted = False
        if 'evaluation_result' not in st.session_state:
            st.session_state.evaluation_result = None
        if 'themes' not in st.session_state:
            # シナリオに合わせたお題のリスト
            st.session_state.themes = [
                "患者さんに安心感を与えるリラックスできる風景",
                "子供向けの病院の待合室を飾る楽しいイラスト",
                #"最新医療技術を紹介する未来的なイメージ",
                "健康的な食事を促すカラフルな料理の写真",
                "リハビリテーションの成果を象徴する希望に満ちた光景"
            ]

        st.write(f"『{st.session_state.themes[st.session_state.current_theme_index]}』を即刻書きなさい！")
        current_theme = st.session_state.themes[st.session_state.current_theme_index]
        st.session_state.current_theme = current_theme

        prompt = st.text_input(" ",placeholder="こころにどんな絵を書いて欲しいか書いてください")

        # 画像生成ボタンの処理
        if st.button("こころに頼む"):
            if prompt:
                with st.spinner("こころは一生懸命、絵を描いている..."):
                    image_url = generate_image(prompt)
                    if image_url:
                        st.session_state.generated_image = image_url
                        st.session_state.submitted = False
                        st.session_state.evaluation_result = None # 新しい画像を生成したら評価結果をリセット
            else:
                st.error("どんな絵を書けばよいか教えてください")

        # 生成された画像の表示と選択ボタン
        if st.session_state.generated_image:
            st.markdown(
                f'<div style="text-align: left;">'
                f'<img src="{st.session_state.generated_image}" style="max-width: 100%;">'
                f'<p style="color: white; font-size: 20px; font-weight: bold; margin-top: 10px;">'
                f'さくら「できました！この絵でどうでしょうか？」</p></div>',
                unsafe_allow_html=True
            )

            # 提出済みでない場合のみ選択ボタンを表示
            if not st.session_state.submitted:
                if st.button("この絵を看護部長に提出"):
                    st.session_state.submitted = True
                    st.session_state.evaluation_result = None # 提出時に評価結果をリセット
                    st.rerun()

                if st.button("こころにもう一度描いてもらう"):
                    st.session_state.generated_image = None
                    st.session_state.submitted = False
                    st.session_state.evaluation_result = None
                    st.rerun()
            elif st.session_state.submitted:
                display_evaluation()

if __name__ == "__main__":
    main()