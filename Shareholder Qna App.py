import streamlit as st
import sqlite3
import pandas as pd

# データベースの初期化
def init_db():
    conn = sqlite3.connect("shareholders.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS shareholders (
                    id INTEGER PRIMARY KEY,
                    shareholder_number TEXT UNIQUE,
                    name TEXT,
                    postal_code TEXT,
                    shares INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY,
                    shareholder_number TEXT,
                    question TEXT)''')
    conn.commit()
    conn.close()

# CSVインポート機能
def import_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)
    conn = sqlite3.connect("shareholders.db")
    df.to_sql("shareholders", conn, if_exists="append", index=False)
    conn.close()
    st.success("✅ CSVデータをインポートしました！")

# 質問一覧のエクスポート（CSV）
def export_questions():
    conn = sqlite3.connect("shareholders.db")
    df = pd.read_sql("SELECT * FROM questions", conn)
    conn.close()
    return df.to_csv(index=False, encoding='utf-8-sig')

# 質問一覧を取得
def get_all_questions():
    conn = sqlite3.connect("shareholders.db")
    df = pd.read_sql("SELECT * FROM questions", conn)
    conn.close()
    return df

# ログイン機能（株主用）
def login(shareholder_number, postal_code):
    conn = sqlite3.connect("shareholders.db")
    c = conn.cursor()
    c.execute("SELECT name, shares FROM shareholders WHERE shareholder_number = ? AND postal_code = ?", 
              (shareholder_number, postal_code))
    result = c.fetchone()
    conn.close()
    return result

# 質問を保存
def save_question(shareholder_number, question):
    conn = sqlite3.connect("shareholders.db")
    c = conn.cursor()
    c.execute("INSERT INTO questions (shareholder_number, question) VALUES (?, ?)", 
              (shareholder_number, question))
    conn.commit()
    conn.close()
    st.success("✅ 質問が送信されました！")

# **🔹 管理者ページ**
def admin_page():
    st.title("🛠 管理者専用ページ")

    admin_password = st.text_input("🔑 管理者パスワード", type="password")
    if st.button("ログイン"):
        if admin_password == "admin123":
            st.success("✅ 管理者としてログインしました！")

            # CSVアップロード
            st.subheader("📂 CSVデータのインポート")
            uploaded_file = st.file_uploader("CSVファイルを選択", type=["csv"])
            if uploaded_file:
                import_csv(uploaded_file)

            # 質問一覧
            st.subheader("📋 質問一覧")
            df = get_all_questions()
            st.dataframe(df)

            # 質問のエクスポート
            st.subheader("⬇ 質問一覧をCSVエクスポート")
            csv_data = export_questions()
            st.download_button(label="📥 CSVをダウンロード", data=csv_data, file_name="questions.csv", mime="text/csv")
        else:
            st.error("❌ パスワードが違います！")

# **🔹 株主ページ**
def shareholder_page():
    st.title("📢 株主専用ページ")
    
    st.subheader("🔑 ログイン")
    shareholder_number = st.text_input("📌 株主番号")
    postal_code = st.text_input("📮 郵便番号", type="password")

    if st.button("ログイン"):
        user_data = login(shareholder_number, postal_code)
        if user_data:
            name, shares = user_data
            st.session_state["logged_in"] = True
            st.session_state["shareholder_number"] = shareholder_number
            st.session_state["name"] = name
            st.session_state["shares"] = shares
            st.experimental_set_query_params(page="shareholder")  # クエリパラメータをセット
            st.experimental_rerun()
        else:
            st.error("❌ ログイン情報が正しくありません")

    # ログイン後の画面
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.subheader(f"👋 ようこそ、{st.session_state['name']} 様")
        st.write(f"📊 持ち株数: {st.session_state['shares']} 株")

        question = st.text_area("📝 質問を入力してください")
        if st.button("送信"):
            save_question(st.session_state["shareholder_number"], question)

# **🔹 メイン関数**
def main():
    st.sidebar.title("🔗 ナビゲーション")

    # 現在のページをクエリパラメータから取得
    query_params = st.experimental_get_query_params()
    page = query_params.get("page", ["home"])[0]

    # 管理者ページへのリンク
    if st.sidebar.button("🔧 管理者専用ページへ"):
        st.experimental_set_query_params(page="admin")
        st.experimental_rerun()

    # 株主ページへのリンク
    if st.sidebar.button("👥 株主専用ページへ"):
        st.experimental_set_query_params(page="shareholder")
        st.experimental_rerun()

    # ページの切り替え
    if page == "admin":
        admin_page()
    elif page == "shareholder":
        shareholder_page()
    else:
        st.title("🏛 株主事前質問受付アプリ")
        st.write("サイドバーからページを選択してください。")

if __name__ == "__main__":
    init_db()
    main()
