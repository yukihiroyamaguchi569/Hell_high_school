import streamlit as st

def display_final_ending():
    st.title("ゲームクリア！")
    


    st.markdown("""
    
    あなたは全ての試練を乗り越え、看護師「こころ」との信頼関係を築き上げた
    
    春の終わりを告げる夕暮れ時、桜の花びらが舞う病院の屋上で。
    
    「あの時、私は間違っていた」
                
    突然の院長の言葉に、皆が振り返る。
                
    「若さを不安視し、二人を別々の部署に配属しようとした私を、君たちは見事に打ち砕いてくれた」
    
    震える声に、普段は厳格な院長の瞳が潤んでいた。
    
    「規則や数字の前に、人の心があることを...」
    
    事務長は言葉を詰まらせ、深くため息をつく。
    
    「私にそれを気づかせてくれたのは、あなたたちの情熱でした」
    
    看護部長は二人に近づき、その手を優しく包み込んだ。
    
    「時に厳しく、時に優しく...私たちの後ろ姿を見て、こんなにも立派に成長してくれるなんて」
    
    声を震わせながら、彼女は続けた。
    
    「あなたたちこそ、私たちの誇りです」
    
    夕陽に照らされた病院を背に、こころがあなたに向き直る。
    
    「先輩...ありがとうございました」
    
    その瞳には、涙と共に確かな決意が宿っていた。
                
    桜吹雪の中、新たな季節の始まりを告げるように、優しい風が吹き抜けていったー。
    
    """)

    st.image("src/images/ending.webp")

    st.write("### THE END")
    
    st.link_button("タイトルに戻る", "https://hell-clinic-management.streamlit.app/")

def main():
    if 'page' not in st.session_state:
        st.session_state.page = "final_ending"
        
    display_final_ending()

if __name__ == "__main__":
    main() 