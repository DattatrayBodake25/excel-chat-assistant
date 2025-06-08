#importing all required libraries here
import streamlit as st
import pandas as pd
from utils import data_preparing, column_types_checking
import plotly.express as px
from chart import prettify_label
import json


#writing function for UI interface using streamlit
def user_interface_sidebar():
    with st.sidebar:
        st.header("📁 Upload Your Data File")
        uploaded_data = st.file_uploader("Upload Excel or CSV", type=["xlsx", "csv"])

        df = None
        if uploaded_data:
            with st.spinner("Reading file..."):
                try:
                    if uploaded_data.name.endswith(".xlsx"):
                        df = pd.read_excel(uploaded_data)
                    elif uploaded_data.name.endswith(".csv"):
                        df = pd.read_csv(uploaded_data)

                    if df is not None:
                        st.success("Your Data file loaded successfully!")
                        st.subheader("Preview Data")
                        st.dataframe(df.head(501))
                except Exception as e:
                    st.error(f"Error reading file: {e}")
        else:
            st.info("Please upload a valid .xlsx or .csv file.")

        df_clean = data_preparing(df) if df is not None else None

        if df_clean is not None:
            st.subheader("Auto-Classified column types")
            types = column_types_checking(df_clean)
            st.code(json.dumps(types, indent=2), language='json')

        return df_clean


#writing function for allow users to write query based on loaded data
def user_question():
    st.subheader("🤔 Ask Your Question")
    return st.text_input("Ask me anything! just type your question in the box below:")


#writing function for showing chatbot generated answer and visual here
def show_response_and_chart(final_answer: str, chart: dict, df_clean: pd.DataFrame):
    st.subheader("🔯 ExcelGenie:")
    st.markdown(final_answer)

    if not chart.get("type"):
        return

    st.subheader("📊 Visualization:")

    select_chart_type = st.selectbox(
        "Override chart type (optional):",
        options=["Auto (AI suggestion)", "bar", "line", "hist", "scatter", "pie", "box"],
        index=0
    )

    chart_type = chart["type"] if select_chart_type == "Auto (AI suggestion)" else select_chart_type

    max_rows = 5000
    plot_df = df_clean.head(max_rows) if len(df_clean) > max_rows else df_clean

    all_columns = plot_df.columns.tolist()
    numeric_columns = plot_df.select_dtypes(include=['number']).columns.tolist()

    #here getting ai suggested columns
    default_x = chart.get("x") if chart.get("x") in all_columns else all_columns[0]
    default_y = chart.get("y") if chart.get("y") in numeric_columns else (numeric_columns[0] if numeric_columns else all_columns[0])

    x_column = st.selectbox("Select X-axis column:", all_columns, index=all_columns.index(default_x))
    y_column = None
    if chart_type not in ["hist", "pie"]:
        y_column = st.selectbox("Select Y-axis column:", numeric_columns, index=numeric_columns.index(default_y) if default_y in numeric_columns else 0)
    elif chart_type == "pie":
        y_column = st.selectbox("Select Value column (for pie):", numeric_columns, index=numeric_columns.index(default_y) if default_y in numeric_columns else 0)

    try:
        fig = None

        if chart_type == "bar":
            fig = px.bar(plot_df, x=x_column, y=y_column)
        elif chart_type == "line":
            fig = px.line(plot_df, x=x_column, y=y_column)
        elif chart_type == "hist":
            fig = px.histogram(plot_df, x=x_column)
        elif chart_type == "scatter":
            fig = px.scatter(plot_df, x=x_column, y=y_column)
        elif chart_type == "pie":
            fig = px.pie(plot_df, names=x_column, values=y_column)
        elif chart_type == "box":
            fig = px.box(plot_df, x=x_column, y=y_column)

        if fig:
            fig.update_layout(
                xaxis_title=prettify_label(x_column),
                yaxis_title=prettify_label(y_column) if y_column else "",
                margin=dict(l=20, r=20, t=40, b=20),
                height=450
            )
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Chart error: {e}")