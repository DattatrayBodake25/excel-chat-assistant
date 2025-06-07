#importing all required libraries here
import streamlit as st
import pandas as pd
from utils import prepare_data, check_column_types


#designing streamlit user interface here
def sidebar_user_interface():
    with st.sidebar:
        st.header("Upload Your File & Check Data")
        uploaded_file = st.file_uploader("Upload here your Excel or CSV file", type=["xlsx", "csv"])

        df = None
        if uploaded_file is not None:
            with st.spinner("Uploading and reading file..."):
                try:
                    if uploaded_file.name.endswith(".xlsx"):
                        df = pd.read_excel(uploaded_file)
                    elif uploaded_file.name.endswith(".csv"):
                        df = pd.read_csv(uploaded_file)
                    else:
                        st.warning("Please use a file that’s Excel or CSV only.")

                    if df is not None:
                        st.success("Your Data uploaded and loaded Successfully!")
                        st.subheader("Preview Data")
                        st.dataframe(df.head(20))

                except Exception as e:
                    st.error(f"Error reading the file: {e}")
        else:
            st.info("Please upload only a .xlsx or .csv file to start.")

        if df is not None:
            df_clean = prepare_data(df)
            st.subheader("Simplified Column Headers:")
            st.write(df_clean.columns.tolist())

            types = check_column_types(df_clean)
            st.subheader("Auto Classified Column Types")
            st.json(types)
        else:
            df_clean = None

        return df_clean


#writing funtion for user query
def user_query():
    st.subheader("🤔 Ask anything about your data")
    return st.text_input("")


#showing user query response and chart visual
def display_response_and_chart(final_answer: str, chart: dict, df_clean: pd.DataFrame):
    import plotly.express as px

    st.subheader("✨ Answer from Gemini")
    st.markdown(final_answer)

    if chart["type"]:
        st.subheader("📈 Data visual")

        types_of_chart = ["bar", "line", "hist", "scatter"]
        chart_type_select = st.selectbox(
            "Select chart type (override AI suggestion):",
            options=["Auto (AI suggestion)"] + types_of_chart,
            index=0
        )
        chart_type = chart["type"] if chart_type_select == "Auto (AI suggestion)" else chart_type_select

        max_rows_for_plot = 5000
        if len(df_clean) > max_rows_for_plot:
            st.warning(f"Data has {len(df_clean)} rows; plotting may be slow or unresponsive. Showing first {max_rows_for_plot} rows instead.")
            plot_df = df_clean.head(max_rows_for_plot)
        else:
            plot_df = df_clean

        try:
            if chart["x"] not in plot_df.columns:
                st.warning(f"Column '{chart['x']}' not found in data.")

            elif chart_type != "hist" and chart["y"] not in plot_df.columns:
                st.warning(f"Column '{chart['y']}' not found in data.")

            else:
                fig = None
                if chart_type == "bar":
                    fig = px.bar(plot_df, x=chart["x"], y=chart["y"])

                elif chart_type == "line":
                    fig = px.line(plot_df, x=chart["x"], y=chart["y"])

                elif chart_type == "hist":
                    fig = px.histogram(plot_df, x=chart["x"])

                elif chart_type == "scatter":
                    fig = px.scatter(plot_df, x=chart["x"], y=chart["y"])

                else:
                    st.warning("Unknown chart type")

                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Chart error: {e}")