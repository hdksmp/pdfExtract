import streamlit as st
import pdfplumber
import pandas as pd
import io
import os

st.title("PDF内の表をCSVに変換するアプリ")

# ① PDFアップロード
uploaded_file = st.file_uploader("① PDFファイルをアップロード", type="pdf")

if uploaded_file:
    # PDF名からデフォルトCSVファイル名を生成
    pdf_filename = uploaded_file.name
    default_csv_filename = os.path.splitext(pdf_filename)[0] + ".csv"

    # ② 出力ファイル名
    output_name = st.text_input("② 出力ファイル名（.csv）", value=default_csv_filename)

    # ③ ④ ページ範囲
    start_page = st.number_input("③ 開始ページ番号（1始まり）", min_value=1, value=1)
    end_page = st.number_input("④ 終了ページ番号（1始まり）", min_value=start_page, value=start_page)

    # 変換ボタン
    if st.button("変換開始"):
        with st.spinner("処理中..."):
            # アップロードファイルを読み込み
            pdf = pdfplumber.open(uploaded_file)
            combined_tables = []

            # ページごとに表抽出
            for i in range(start_page - 1, end_page):
                try:
                    page = pdf.pages[i]
                    tables = page.extract_tables()
                    for table in tables:
                        df = pd.DataFrame(table)
                        combined_tables.append(df)
                except IndexError:
                    st.warning(f"ページ {i+1} は存在しませんでした")
                    continue

            pdf.close()

            if combined_tables:
                result_df = pd.concat(combined_tables, ignore_index=True)

                # バッファに保存
                buffer = io.StringIO()
                result_df.to_csv(buffer, index=False)
                buffer.seek(0)

                # ダウンロードボタン
                st.success("変換成功！以下からダウンロードしてください👇")
                st.download_button(
                    label="CSVファイルをダウンロード",
                    data=buffer.getvalue(),
                    file_name=output_name,
                    mime="text/csv"
                )
            else:
                st.error("指定範囲に表が見つかりませんでした。")
