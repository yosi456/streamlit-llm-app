import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# .envファイルから環境変数を読み込む
# この行が実行されると、.envファイル内のキーと値が環境変数として設定される
load_dotenv()

# --------------------------------------------------------------------------------
# 関数定義：LLMからの回答を生成する
# --------------------------------------------------------------------------------
def get_llm_response(user_input: str, expert_type: str) -> str:
    """
    LLMに質問を投げかけ、専門家として整形された回答を取得します。

    Args:
        user_input (str): ユーザーからの質問テキスト。
        expert_type (str): 選択された専門家の種類。

    Returns:
        str: LLMからの回答、またはエラー発生時はNone。
    """
    
    # 専門家の種類に応じたシステムメッセージを定義
    expert_prompts = {
        "財務アドバイザー": "あなたは優秀な財務アドバイザーです。ユーザーの質問に対して、金融、投資、貯蓄、資産形成の観点から、専門的かつ具体的で分かりやすいアドバイスをしてください。",
        "キャリアコンサルタント": "あなたは経験豊富なキャリアコンサルタントです。ユーザーの質問に対して、キャリアプラン、転職、スキルアップ、自己分析の観点から、親身かつ的確なアドバイスをしてください。"
    }
    
    system_message_content = expert_prompts.get(expert_type, "あなたは親切なアシスタントです。")

    try:
        # LLMモデルを準備
        # load_dotenv()によって環境変数に設定されたAPIキーが自動で利用される
        chat = ChatOpenAI(model="gpt-4o-mini")
        # LLMに渡すメッセージを作成
        messages = [
            SystemMessage(content=system_message_content),
            HumanMessage(content=user_input)
        ]

        # LLMから回答を生成
        response = chat.invoke(messages)
        return response.content
    
    except Exception as e:
        st.error(f"LLMからの回答生成中にエラーが発生しました: {e}")
        return None

# --------------------------------------------------------------------------------
# Streamlit UI部分
# --------------------------------------------------------------------------------

st.set_page_config(page_title="専門家AI相談室", layout="wide")
st.title("専門家AI相談室")
st.markdown("""
このアプリケーションは、あなたの質問や相談に対して、指定した分野の専門家としてAIが回答を生成するWebアプリです。

### 使い方
1.  **相談したい専門家を選択**: ラジオボタンから「財務アドバイザー」または「キャリアコンサルタント」を選んでください。
2.  **相談内容を入力**: 下のテキストエリアに、専門家に聞きたいことを自由に入力してください。
3.  **「質問する」ボタンをクリック**: AIからの回答が下に表示されます。
""")

# OpenAI APIキーの存在チェック
# load_dotenv() を実行した後に、os.environで環境変数を参照する
if "OPENAI_API_KEY" not in os.environ or os.environ["OPENAI_API_KEY"] == "":
    st.error("OpenAI APIキーが設定されていません。")
    st.info("解決策: プロジェクトのルートディレクトリに .env ファイルを作成し、'OPENAI_API_KEY=ご自身のAPIキー' の形式でキーを記述してください。")
    st.stop() # APIキーがない場合はアプリの実行を停止

# 専門家選択のラジオボタン
expert_options = ["財務アドバイザー", "キャリアコンサルタント"]
selected_expert = st.radio(
    label="**1. 相談したい専門家を選択してください**",
    options=expert_options,
    horizontal=True,
)

# 相談内容の入力フォーム
user_question = st.text_area(
    label="**2. 相談内容を入力してください**", 
    height=150,
    placeholder="例：老後のために、どのような資産運用を始めるべきですか？"
)

# 質問ボタンと回答表示
if st.button("質問する", type="primary"):
    if user_question:
        with st.spinner(f"{selected_expert}として回答を生成中です..."):
            # 定義した関数を呼び出してLLMからの回答を取得
            llm_answer = get_llm_response(user_question, selected_expert)
            
            if llm_answer:
                st.subheader("AIからの回答")
                st.markdown(llm_answer.replace("\n", "\n\n"))
    else:
        st.warning("相談内容を入力してください。")