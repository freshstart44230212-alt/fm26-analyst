import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 画面の設定 ---
st.set_page_config(page_title="高知SC アナリスト室", page_icon="⚽", layout="wide")
st.title("⚽ 高知SC 専用アナリスト室")
st.write("リーグ順位、今後の補強計画、HTMLでのスカッド共有など、何でも相談してください。")

# --- APIキーと状況表示（サイドバー） ---
with st.sidebar:
    st.header("⚙️ システム設定")
    api_key = st.text_input("Gemini APIキー", type="password")
    
    st.markdown("---")
    st.subheader("📋 現在のフォーメーション")
    if os.path.exists("tactics.jpg"):
        st.image("tactics.jpg", caption="4-2-3-1 ワイド (流動型カウンター)", use_column_width=True)
    
    # チャットリセットボタン
    if st.button("🗑️ 会話履歴をクリア"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()

if not api_key:
    st.warning("👈 左側のメニューにAPIキーを入力するとアナリストが起動します。")
    st.stop()

genai.configure(api_key=api_key)

# --- アナリストの設定 ---
system_instruction = """
# 役割定義
あなたは『Football Manager』における「高知SCの専属チーフアナリスト」です。
監督（ユーザー）と継続的に対話しながら、リーグ順位、今後の補強計画、戦術の微調整を共に考えます。

# トーン＆ペルソナ
- プロフェッショナルかつ監督の良き相棒。
- 指示待ちではなく「次の冬の移籍に向けて、どのポジションのリストアップを開始しますか？」「現在の順位を踏まえると、次の試合は勝ち点3が必須です」など、今後の展開を見据えた提案を交える.
- HTML形式のデータ（選手一覧やスカウトレポート）が送られた場合は、表データとして読み解き、比較分析を行うこと.
- 無駄な挨拶は省き、すぐに本題に入る.
"""

# 💡修正箇所：確実かつ高速に動く「gemini-1.5-flash」に変更
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction,
    generation_config={"temperature": 0.4}
)

# --- 会話履歴（メモリ）の初期化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state or st.session_state.chat_session is None:
    st.session_state.chat_session = model.start_chat(history=[])

# --- クイックアクション（ボタン） ---
st.write("📌 **クイックアクション**")
col1, col2, col3 = st.columns(3)
preset_prompt = None
if col1.button("📊 状況共有・作戦会議"):
    preset_prompt = "現在のリーグ順位や直近のチーム課題を共有します。今後の補強や方針について相談に乗ってください。"
if col2.button("📄 スカッド・HTML分析"):
    preset_prompt = "添付したHTMLデータ（選手一覧やレポート）を読み込み、チームの強み・弱み、または獲得候補の比較分析を行ってください。"
if col3.button("👤 個別選手査定"):
    preset_prompt = "添付した選手のデータを査定し、現在の4-2-3-1における適性と獲得の是非をジャッジしてください。"

st.markdown("---")

# --- ファイルアップロード（画像＆HTML対応） ---
uploaded_file = st.file_uploader("📸 画像 または 📄 HTMLファイル を添付", type=["jpg", "png", "jpeg", "html", "txt"])

# --- 過去の会話を表示 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 入力処理 ---
prompt = st.chat_input("アナリストへの指示や状況を入力...") or preset_prompt

if prompt:
    # ユーザーの入力を画面に表示＆保存
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("データ分析中..."):
            try:
                content_to_send = [prompt]
                
                # ファイルが添付されている場合の処理
                if uploaded_file is not None:
                    file_ext = uploaded_file.name.split('.')[-1].lower()
                    if file_ext in ['jpg', 'png', 'jpeg']:
                        image = Image.open(uploaded_file)
                        content_to_send.append(image)
                    elif file_ext in ['html', 'txt']:
                        file_content = uploaded_file.getvalue().decode("utf-8", errors="replace")
                        content_to_send[0] = f"{prompt}\n\n【添付データ】\n{file_content}"
                
                # Geminiに送信（過去の履歴も踏まえて回答される）
                response = st.session_state.chat_session.send_message(content_to_send)
                st.markdown(response.text)
                
                # アナリストの回答を保存
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
