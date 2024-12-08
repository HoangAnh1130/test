import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

#######################################
# PAGE SETUP
#######################################

st.set_page_config(page_title="Claim Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("CLAIM REPORT")
# st.markdown("_Prototype v0.4.1_")

with st.sidebar:
    st.header("UPLOAD YOUR FILE")
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True, type=["csv", "xlsx", "xls"])

if not uploaded_files:
    st.info("Upload files", icon="ℹ️")
    st.stop()

#######################################
# DATA LOADING
#######################################

@st.cache_data
def load_data(file):
    if file.name.endswith(".xlsx"):
        return pd.read_excel(file)
    else:
        st.error(f"Unsupported file type: {file.name}")
        return None

# Load each file and display its data
dataframes = []

for uploaded_file in uploaded_files:
    df = load_data(uploaded_file)
    
    # Kiểm tra tên file và thực hiện tác vụ riêng
    if df is not None:
        if "leapstack" in uploaded_file.name.lower():
            leapstack_desired_columns = ['Insured Type', 'Accurate Diagnosis', 'Medical Expense ','Reimbursement','Excluded','Claim Source']
            df_leapstack_cleaned = df[leapstack_desired_columns]
            df_leapstack_cleaned.columns = ['Nhóm', 'Chuẩn đoán bệnh', 'Yêu cầu bồi thường', 'Đã được bồi thường','Chênh lệch','Nguồn claim']
            df_leapstack_cleaned = df_leapstack_cleaned.reset_index(drop=True)
            dataframes.append(df_leapstack_cleaned)  
        elif "baoviet" in uploaded_file.name.lower():
            baoviet_desired_columns = ["Thuộc Nhóm", 'Loại bệnh', 'Số tiền yêu cầu bồi thường (VND)','Tổng số tiền bồi thường (VND)','Chệnh lệch số tiền YCBT và STBT','Địa diểm tổn thất']
            df_baoviet_cleaned = df[baoviet_desired_columns]
            df_baoviet_cleaned.columns = ['Nhóm', 'Chuẩn đoán bệnh', 'Yêu cầu bồi thường', 'Đã được bồi thường','Chênh lệch','Nguồn claim']
            df_baoviet_cleaned = df_baoviet_cleaned.reset_index(drop=True)
            dataframes.append(df_baoviet_cleaned)  
        elif "fullerton" in uploaded_file.name.lower():
            fullerton_desired_columns = ["Relation", 'Chan doan benh', 'Request amount','Claim paid amount','Rejected amount - paid case','Medical providers']
            df_fullerton_cleaned = df[fullerton_desired_columns]
            df_fullerton_cleaned.columns = ['Nhóm', 'Chuẩn đoán bệnh', 'Yêu cầu bồi thường', 'Đã được bồi thường','Chênh lệch','Nguồn claim']
            df_fullerton_cleaned = df_fullerton_cleaned.reset_index(drop=True)
            dataframes.append(df_fullerton_cleaned)  
        elif "pvi" in uploaded_file.name.lower():
            pvi_desired_columns = ["Đối tượng bảo hiểm", 'Nhóm bệnh', 'Số tiền yêu cầu BT',"Số tiền bồi thường (100%)",'Số tiền từ chối BT','Cơ sở y tế']
            df_pvi_cleaned = df[pvi_desired_columns]
            df_pvi_cleaned.columns = ['Nhóm', 'Chuẩn đoán bệnh', 'Yêu cầu bồi thường', 'Đã được bồi thường','Chênh lệch','Nguồn claim']
            df_pvi_cleaned = df_pvi_cleaned.drop(index=[0, 1]).reset_index(drop=True)
            dataframes.append(df_pvi_cleaned) 
        elif "pti" in uploaded_file.name.lower():
            df['Chênh lệch'] = df['Số tiền yêu cầu bồi thường'] - df["Tổng số tiền bồi thường"]
            pti_desired_columns = ["Nhóm", 'Chẩn đoán', 'Số tiền yêu cầu bồi thường',"Tổng số tiền bồi thường",'Chênh lệch','Tên bệnh viện']
            df_pti_cleaned = df[pti_desired_columns]
            df_pti_cleaned.columns = ['Nhóm', 'Chuẩn đoán bệnh', 'Yêu cầu bồi thường', 'Đã được bồi thường','Chênh lệch','Nguồn claim']
            df_pti_cleaned = df_pti_cleaned.drop(index=[0]).reset_index(drop=True)
            dataframes.append(df_pti_cleaned)  
        else:
            # File không hợp lệ, xóa nó khỏi danh sách và cảnh báo
            st.error(f"Invalid file name: {uploaded_file.name}. This file does not match expected naming conventions.")
            uploaded_files.remove(uploaded_file)  # Xóa file không hợp lệ khỏi danh sách

# Nếu cần ghép tất cả DataFrames lại với nhau
if dataframes:
    combined_df = pd.concat(dataframes, ignore_index=True)
    st.write("Combined DataFrame:")
    st.dataframe(combined_df)


