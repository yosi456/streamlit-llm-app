import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# --- Streamlit SecretsからのAPIキー読み込み ---
# この方法により、ローカルの.envファイル（st.secretsが機能しない場合）と
# クラウドのSecretsの両方に対応しようと試みることもできるが、
# デプロイ時はクラウドのSecretsに一本化するのが最もシンプルで確実。
try:
    # Streamlit Community CloudのSecretsからキーを取得
    openai_api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    # Secretsにキーがない場合のエラーメッセージ
    st.error("OpenAI APIキーが設定されていません。StreamlitのSecretsにキーを設定してください。")
    st.stop() # アプリの実行を停止

# --------------------------------------------------------------------------------
# 関数定義：LLMからの回答を生成する
# --------------------------------------------------------------------------------
def get_llm_response(user_input: str, expert_type: str) -> str:
    expert_prompts = {
        "財務アドバイザー": "あなたは優秀な財務アドバイザーです。ユーザーの質問に対して、金融、投資、貯蓄、資産形成の観点から、専門的かつ具体的で分かりやすいアドバイスをしてください。",
        "キャリアコンサルタント": "あなたは経験豊富なキャリアコンサルタントです。ユーザーの質問に対して、キャリアプラン、転職、スキルアップ、自己分析の観点から、親身かつ的確なアドバイスをしてください。"
    }
    
    system_message_content = expert_prompts.get(expert_type, "あなたは親切なアシスタントです。")

    try:
        # LLMモデルを準備する際に、取得したAPIキーを明示的に渡す
        chat = ChatOpenAI(api_key=openai_api_key, model="gpt-4o-mini")

        messages = [
            SystemMessage(content=system_message_content),
            HumanMessage(content=user_input)
        ]

        response = chat.invoke(messages)
        return response.content
    
    except Exception as e:
        st.error(f"LLMからの回答生成中にエラーが発生しました: {e}")
        return None

# --------------------------------------------------------------------------------
# Streamlit UI部分
# --------------------------------------------------------------------------------
st.set_page_config(page_title="専門家AI相談室", layout="wide")
st.title("👨‍🏫 専門家AI相談室!")
st.markdown("""
このアプリケーションは、あなたの質問や相談に対して、指定した分野の専門家としてAIが回答を生成するWebアプリです。

### 使い方
1.  **相談したい専門家を選択**: ラジオボタンから「財務アドバイザー」または「キャリアコンサルタント」を選んでください。
2.  **相談内容を入力**: 下のテキストエリアに、専門家に聞きたいことを自由に入力してください。
3.  **「質問する」ボタンをクリック**: AIからの回答が下に表示されます。
""")

expert_options = ["財務アドバイザー", "キャリアコンサルタント"]
selected_expert = st.radio(
    label="**1. 相談したい専門家を選択してください**",
    options=expert_options,
    horizontal=True,
)

user_question = st.text_area(
    label="**2. 相談内容を入力してください**", 
    height=150,
    placeholder="例：老後のために、どのような資産運用を始めるべきですか？"
)

if st.button("質問する", type="primary"):
    if user_question:
        with st.spinner(f"{selected_expert}として回答を生成中です..."):
            llm_answer = get_llm_response(user_question, selected_expert)
            
            if llm_answer:
                st.subheader("🤖 AIからの回答")
                st.markdown(llm_answer.replace("\n", "\n\n"))
    else:
        st.warning("相談内容を入力してください。")