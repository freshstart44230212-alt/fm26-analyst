import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 画面の設定 ---
st.set_page_config(page_title="高知SC アナリスト室", page_icon="⚽", layout="wide")
st.title("⚽ 高知SC 専用アナリスト室")
st.write("FM26の戦術相談や、スカウトした選手の能力画面（スクショ）を送ってください。")

# --- APIキーと状況表示（サイドバー） ---
with st.sidebar:
    st.header("⚙️ システム設定")
    api_key = st.text_input("Gemini APIキー", type="password")
    st.write("※取得した `AIzaSy...` を貼り付けてください")
    
    st.markdown("---")
    st.subheader("📋 現在のフォーメーション")
    # GitHubにアップロードした tactics.jpg を表示
    if os.path.exists("tactics.jpg"):
        st.image("tactics.jpg", caption="4-2-3-1 ワイド (流動型カウンター)", use_column_width=True)
    else:
        st.info("💡 GitHubに `tactics.jpg` をアップロードすると、ここに陣形図が表示されます。")

if not api_key:
    st.warning("👈 左側のメニューにAPIキーを入力するとアナリストが起動します。")
    st.stop()

genai.configure(api_key=api_key)

# --- アナリストの設定（System Instructions） ---
system_instruction = """
# 役割定義
あなたはサッカーシミュレーションゲーム『Football Manager』において、監督（ユーザー）を支える「高知SCの専属チーフアナリスト」です。
鋭いデータ分析、戦術的視点、そして監督への深いリスペクトを併せ持ち、J1自動昇格に向けた客観的かつ情熱的なスカウティング・チーム分析を行います。

# トーン＆ペルソナ
- プロフェッショナルでありながら、監督の良き相棒としての温かみと客観的で素直なアドバイスを持つ。
- 抽象的な表現は避け、具体的な能力値の数値やFMのシステム仕様に基づいた根拠を提示する。
- 回答の冒頭で無駄な前置きや挨拶は一切行わず、1文目から直接コンテンツに入る。
- 文末にまとめのラベリングを設置せず、自然な段落で終える。

# クラブの基本文脈・引き継ぎデータ（高知SC）
- 所属・状況: J2リーグ 3位。2029年1月下旬（冬移籍ウィンドウ）。
- 採用戦術: 「積極的 4-2-3-1 ワイド・カスタム 流動型カウンター攻撃」
- 課題: 前線の主軸が離脱中。マルチアタッカー1名をレンタルで急遽獲得すること。

# 選手査定・データ分析の原則
1. 戦術的貢献度
2. 最大の懸念点・リスク
3. 最終判定（獲得/見送り）
4. 相方の推奨タイプ
"""

# Gemini 1.5 Proの設定
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=system_instruction,
    generation_config={"temperature": 0.3}
)

# --- クイックアクション（ボタン） ---
st.write("📌 **クイックアクション**")
col1, col2, col3 = st.columns(3)
preset_prompt = None
if col1.button("🔍 スカウトレポート分析"):
    preset_prompt = "添付した画像（スカウトレポート等）を分析し、高知SCの現在の戦術に適合するか、獲得すべきか詳細に評価してください。"
if col2.button("🛡️ 戦術診断"):
    preset_prompt = "現在の戦術とフォーメーションにおける弱点や、改善すべき役割（ロール）の指示について診断してください。"
if col3.button("👤 選手査定"):
    preset_prompt = "添付した選手の能力値を査定し、現在の4-2-3-1のどこで起用するのがベストか、獲得・起用の是非を判定してください。"

st.markdown("---")

# --- 画面UI ---
uploaded_file = st.file_uploader("📸 画像（選手の能力値、スカウトレポート、戦術画面など）を添付", type=["jpg", "png", "jpeg"])

prompt = st.chat_input("アナリストへの指示を入力（例: この選手を査定して）") or preset_prompt

if prompt:
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("データ分析中..."):
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                response = model.generate_content([prompt, image])
            else:
                response = model.generate_content(prompt)
            
            st.markdown(response.text)
