import duckdb
import pandas as pd
import plotly.express as px
# import plotly.graph_objects as go
import streamlit as st
import subprocess
import webbrowser
import os
import time
import psutil 

# Mở ứng dụng Streamlit trong trình duyệt
def open_browser():
    url = "http://localhost:8501"
    webbrowser.open(url)
#######################################
# PAGE SETUP
#######################################

st.set_page_config(page_title="Claim Dashboard", page_icon=":bar_chart:", layout="wide")

# Thêm CSS để căn giữa
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Hiển thị tiêu đề
st.header("UPLOAD YOUR FILE")
uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True, type=["csv", "xlsx", "xls"])
st.markdown('<div class="title">CLAIM REPORT</div>', unsafe_allow_html=True)
st.title('')
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
            leapstack_desired_columns = ['Insured No. ','Insured Type','Accurate Diagnosis', 'Medical Expense ','Reimbursement','Excluded','Claim Source','Treatment Type']
            df_leapstack_cleaned = df[leapstack_desired_columns]
            df_leapstack_cleaned.columns = ['Insured ID','Nhóm', 'Nhóm bệnh', 'Yêu cầu bồi thường', 'Đã được bồi thường','Chênh lệch','Cơ sở y tế','Nhóm quyền lợi']
            df_leapstack_cleaned = df_leapstack_cleaned.reset_index(drop=True)
            dataframes.append(df_leapstack_cleaned)  
        elif "baoviet" in uploaded_file.name.lower():
            baoviet_desired_columns = ['Số GCNBH',"Thuộc Nhóm", 'Loại bệnh', 'Số tiền yêu cầu bồi thường (VND)','Tổng số tiền bồi thường (VND)','Chệnh lệch số tiền YCBT và STBT','Địa diểm tổn thất','Nguyên nhân']
            df_baoviet_cleaned = df[baoviet_desired_columns]
            df_baoviet_cleaned.columns = ['Insured ID','Nhóm', 'Nhóm bệnh', 'Yêu cầu bồi thường', 'Đã được bồi thường','Chênh lệch','Cơ sở y tế','Nhóm quyền lợi']
            df_baoviet_cleaned = df_baoviet_cleaned.reset_index(drop=True)
            dataframes.append(df_baoviet_cleaned)  
        elif "fullerton" in uploaded_file.name.lower():
            fullerton_desired_columns = ['Insured ID',"Relation", 'Chan doan benh', 'Request amount','Claim paid amount','Rejected amount - paid case','Medical providers','Beneficiary type']
            df_fullerton_cleaned = df[fullerton_desired_columns]
            df_fullerton_cleaned.columns = ['Insured ID','Nhóm', 'Nhóm bệnh', 'Yêu cầu bồi thường', 'Đã được bồi thường','Chênh lệch','Cơ sở y tế','Nhóm quyền lợi']
            df_fullerton_cleaned = df_fullerton_cleaned.reset_index(drop=True)
            dataframes.append(df_fullerton_cleaned)  
        elif "pvi" in uploaded_file.name.lower():
            pvi_desired_columns = ["Đối tượng bảo hiểm", 'Nhóm bệnh', 'Số tiền yêu cầu BT',"Số tiền bồi thường (100%)",'Số tiền từ chối BT','Cơ sở y tế','Nhóm quyền lợi']
            df_pvi_cleaned = df[pvi_desired_columns]
            df_pvi_cleaned.columns = ['Insured ID','Nhóm', 'Nhóm bệnh', 'Yêu cầu bồi thường', 'Đã được bồi thường','Chênh lệch','Cơ sở y tế','Nhóm quyền lợi']
            df_pvi_cleaned = df_pvi_cleaned.drop(index=[0, 1]).reset_index(drop=True)
            dataframes.append(df_pvi_cleaned) 
        elif "pti" in uploaded_file.name.lower():
            df['Chênh lệch'] = df['Số tiền yêu cầu bồi thường'] - df["Tổng số tiền bồi thường"]
            pti_desired_columns = ['Tên bệnh nhân',"Nhóm", 'Chẩn đoán', 'Số tiền yêu cầu bồi thường',"Tổng số tiền bồi thường",'Chênh lệch','Tên bệnh viện','Phân loại bồi thường']
            df_pti_cleaned = df[pti_desired_columns]
            df_pti_cleaned.columns = ['Insured ID','Nhóm', 'Nhóm bệnh', 'Yêu cầu bồi thường', 'Đã được bồi thường','Chênh lệch','Cơ sở y tế','Nhóm quyền lợi']
            df_pti_cleaned = df_pti_cleaned.drop(index=[0]).reset_index(drop=True)
            dataframes.append(df_pti_cleaned)  
        else:
            # File không hợp lệ, xóa nó khỏi danh sách và cảnh báo
            st.error(f"Invalid file name: {uploaded_file.name}. This file does not match expected naming conventions.")
            uploaded_files.remove(uploaded_file)  # Xóa file không hợp lệ khỏi danh sách

# Nếu cần ghép tất cả DataFrames lại với nhau
if dataframes:
    combined_df = pd.concat(dataframes, ignore_index=True)
else:
    combined_df = pd.DataFrame(columns=['Insured ID','Nhóm', 'Nhóm bệnh', 'Yêu cầu bồi thường', 'Đã được bồi thường','Chênh lệch','Cơ sở y tế','Nhóm quyền lợi'])
    # st.write("Combined DataFrame:")
    # st.dataframe(combined_df)
# st.subheader('Bồi thường theo nhóm khách hàng')
# with st.expander('Claim by group data view') :
#     combined_df["Nhóm"] = combined_df["Nhóm"].str.strip().str.lower()
#     combined_df["Nhóm"] = combined_df["Nhóm"].replace({
#     'others': 'Dependant',
#     'member': 'Employee',
#     'child': 'Dependant',
#     'children' : 'Dependant',
#     'nhanvien_01' : 'Employee',
#     'người thân' : 'Dependant',
#     'nguoithan_01' : 'Dependant',
#     'nhân viên' : 'Employee'
# })
#     by_group = duckdb.sql("""
#     SELECT 
#         "Nhóm",
#         count(distinct "Insured ID") as "Số người yêu cầu bồi thường",
#         count("Insured ID") as "Số hồ sơ bồi thường",
#         ROUND(SUM("Yêu cầu bồi thường")) AS "Số tiền yêu cầu được bồi thường",
#         ROUND(SUM("Đã được bồi thường")) AS "Số tiền được bồi thường",
#         ROUND(SUM("Đã được bồi thường")/count(distinct "Insured ID")) as "Số tiền bồi thường trung bình/người",
#         concat(round(SUM("Đã được bồi thường")*100/SUM("Yêu cầu bồi thường"),1),'%') as "Tỉ lệ thành công"
#     FROM combined_df
#     GROUP BY "Nhóm"
# """).df()

#     st.dataframe(by_group)

# # This dataframe has 244 lines, but 4 distinct values for `day`
# fig1 = px.pie(by_group, names='Nhóm', values="Số người yêu cầu bồi thường", title='Số người yêu cầu bồi thường theo nhóm khách hàng', 
#               color="Nhóm",  
#     color_discrete_map={
#         "Dependant": "#3A0751", 
#         "Employee": "#f2c85b"
#     }  # Ánh xạ màu
#               )
# fig2 = px.pie(by_group, names='Nhóm', values="Số tiền được bồi thường", title='Số tiền đã bồi thường theo nhóm')

# # Sử dụng st.columns để chia giao diện thành 2 cột
# col1, col2 = st.columns(2)

# # Hiển thị các pie chart trong các cột tương ứng
# with col1:
#     st.plotly_chart(fig1)

# with col2:
#     st.plotly_chart(fig2)
    
# st.subheader('Bồi thường theo quyền lợi bảo hiểm')
# with st.expander('Claim by benefit data view') :
#     by_benefit = duckdb.sql(
#         """
#     SELECT 
#         "Nhóm quyền lợi",
#         count(distinct "Insured ID") as "Số người yêu cầu .bồi thường",
#         count("Insured ID") as "Số hồ sơ bồi thường",
#         ROUND(SUM("Yêu cầu bồi thường")) AS "Số tiền yêu cầu được bồi thường",
#         ROUND(SUM("Đã được bồi thường")) AS "Số tiền được bồi thường",
#         ROUND(SUM("Đã được bồi thường")/count(distinct "Insured ID")) as "Số tiền bồi thường trung bình/người",
#         concat(round(SUM("Đã được bồi thường")*100/SUM("Yêu cầu bồi thường"),1),'%') as "Tỉ lệ thành công"
#     FROM combined_df
#     GROUP BY "Nhóm quyền lợi"
# """
#     ).df()
#     st.dataframe(by_benefit)
# by_benefit = by_benefit.sort_values(by='Số tiền được bồi thường', ascending=False)
# fig3 = px.bar(
#     by_benefit,
#     x="Nhóm quyền lợi",
#     y="Số tiền được bồi thường",
#     title="Số tiền đã bồi thường theo nhóm quyền lợi",
#     text="Số tiền được bồi thường",  # Nhãn giá trị
#     color="Nhóm quyền lợi",
#     color_discrete_map={
#         "Quyền lợi A": "#3A0751",
#         "Quyền lợi B": "#FF5733",
#         "Quyền lợi C": "#33FF57"
#     }  # Tùy chỉnh màu sắc cho từng nhóm
# )

# # Tùy chỉnh vị trí của nhãn và hiển thị số nguyên trong nhãn
# fig3.update_traces(
#     textposition='outside',  # Nhãn hiển thị bên ngoài cột
#     texttemplate='%{text:,}' # Hiển thị số nguyên trong nhãn
# )
# fig3.update_layout(
#     height=600  # Bạn có thể điều chỉnh giá trị này tùy theo nhu cầu của bạn
# )
# st.plotly_chart(fig3)

# st.subheader('Bồi thường theo cơ sở y tế')
# with st.expander('Claim by medical provider data view') :
#     by_medicalprovider = duckdb.sql(
#         """
#     SELECT 
#         "Cơ sở y tế",
#         count(distinct "Insured ID") as "Số người yêu cầu bồi thường",
#         count("Insured ID") as "Số hồ sơ bồi thường",
#         ROUND(SUM("Yêu cầu bồi thường")) AS "Số tiền yêu cầu được bồi thường",
#         ROUND(SUM("Đã được bồi thường")) AS "Số tiền được bồi thường",
#         ROUND(SUM("Đã được bồi thường")/count(distinct "Insured ID")) as "Số tiền bồi thường trung bình/người",
#         concat(round(SUM("Đã được bồi thường")*100/SUM("Yêu cầu bồi thường"),1),'%') as "Tỉ lệ thành công"
#     FROM combined_df
#     GROUP BY "Cơ sở y tế"
# """
#     ).df()
#     st.dataframe(by_medicalprovider)
# by_medicalprovider = by_medicalprovider.sort_values(by='Số tiền được bồi thường', ascending=False)
# fig4 = px.bar(
#     by_medicalprovider,
#     x="Cơ sở y tế",
#     y="Số tiền được bồi thường",
#     title="Số tiền đã bồi thường theo Cơ sở y tế",
#     text="Số tiền được bồi thường",  # Nhãn giá trị
#     color="Cơ sở y tế",
#     color_discrete_map={
#         "Quyền lợi A": "#3A0751",
#         "Quyền lợi B": "#FF5733",
#         "Quyền lợi C": "#33FF57"
#     }  # Tùy chỉnh màu sắc cho từng nhóm
# )

# # Tùy chỉnh vị trí của nhãn và hiển thị số nguyên trong nhãn
# fig4.update_traces(
#     textposition='outside',  # Nhãn hiển thị bên ngoài cột
#     texttemplate='%{text:,}' # Hiển thị số nguyên trong nhãns
# )
# fig4.update_layout(
#     height=600  # Bạn có thể điều chỉnh giá trị này tùy theo nhu cầu của bạn
# )
# st.plotly_chart(fig4)
    
    
# # Hàm dừng tất cả các tiến trình Streamlit
# def stop_streamlit():
#     for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
#         try:
#             # Kiểm tra nếu cmdline là một danh sách và có chứa 'streamlit'
#             if isinstance(proc.info['cmdline'], list) and 'streamlit' in ' '.join(proc.info['cmdline']):
#                 print(f"Stopping Streamlit process: {proc.info['pid']}")
#                 proc.terminate()  # Dừng tiến trình Streamlit
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             pass

# # Hàm kiểm tra xem Streamlit có đang chạy không
# def is_streamlit_running():
#     for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
#         try:
#             # Kiểm tra nếu tiến trình là Streamlit
#             if isinstance(proc.info['cmdline'], list) and 'streamlit' in ' '.join(proc.info['cmdline']):
#                 return True
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             pass
#     return False

# # Hàm chạy Streamlit
# def run_streamlit():
#     # Kiểm tra xem Streamlit có đang chạy không
#     if not is_streamlit_running():
#         print("Streamlit is not running, starting it...")
#         subprocess.Popen(
#             ["python", "-m", "streamlit", "run", r"C:\Users\HOANG ANH\AFFINA - Sale Analyst\Official Work\Auto report\testgit.py"],
#             shell=True
#         )
#         time.sleep(5)  # Đợi một chút để đảm bảo Streamlit đã khởi động xong
#         # Mở trình duyệt sau khi Streamlit đã khởi động
#     else:
#         print("Streamlit is already running!")

# # Gọi hàm dừng Streamlit trước khi bắt đầu mới
# stop_streamlit()

# # Chạy ứng dụng Streamlit
# if __name__ == "__main__":
#     run_streamlit()


# columns = combined_df.columns.tolist()

# # Tạo checklist với tùy chọn "Chọn tất cả"
# selected_columns = st.multiselect(
#     "Chọn cột để hiển thị:",
#     options=["Chọn tất cả","Nhóm khách hàng","Nhóm quyền lợi","Cơ sở y tế"],
#     default = "Nhóm khách hàng"
# )


st.markdown("""
    <style>
    .stButton>button {
        background-color: #70C2B4;  /* Màu nền button */
        color: white;               /* Màu chữ */
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #5a9f92;  /* Màu nền khi hover */
    }
    </style>
""", unsafe_allow_html=True)

# Khởi tạo giá trị mặc định cho session_state nếu chưa có
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns = ''
if 'chon_chart' not in st.session_state:
    st.session_state.chon_chart = 'BAR CHART'

options = ["", "Nhóm khách hàng", "Nhóm quyền lợi", "Cơ sở y tế","Nhóm bệnh"]
lua_chon = ''

# Tạo các cột cho các nút radio
col1, col2, col3,col4,col5 = st.columns(5)

with col1:
    st.write("##### CHỌN DỮ LIỆU MUỐN PHÂN TÍCH:")

with col2:
    if st.button("Nhóm khách hàng"):
        st.session_state.selected_columns = "Nhóm khách hàng"
    if st.button("Nhóm quyền lợi"):
        st.session_state.selected_columns = "Nhóm quyền lợi"

with col3:
    if st.button("Cơ sở y tế"):
        st.session_state.selected_columns = "Cơ sở y tế"
    if st.button("Nhóm bệnh"):
        st.session_state.selected_columns = "Nhóm bệnh"
with col4:
    if st.button("Tất cả"):
        st.session_state.selected_columns = "Tất cả"
    if st.button("Tất cả và tắt chart"):
        st.session_state.selected_columns = "Tất cả và tắt chart"

# Kiểm tra nếu người dùng chọn "Chọn tất cả"
if "Chọn tất cả" in st.session_state.selected_columns:
    # Hiển thị toàn bộ dữ liệu
    st.write("Hiển thị toàn bộ dữ liệu:")
    st.dataframe(combined_df)
elif "Nhóm khách hàng" in st.session_state.selected_columns:
    lua_chon = "Nhóm"
elif "Nhóm quyền lợi" in st.session_state.selected_columns:
    lua_chon = "Nhóm quyền lợi"
elif "Cơ sở y tế" in st.session_state.selected_columns:
    lua_chon = "Cơ sở y tế"
elif "Nhóm bệnh" in st.session_state.selected_columns:
    lua_chon = "Nhóm bệnh"
elif st.session_state.selected_columns == "Tất cả":
    lua_chon = "Tất cả"
elif st.session_state.selected_columns == "Tất cả và tắt chart":
    lua_chon = "Tất cả và tắt chart"
else:
    st.write('')

# Kiểm tra lựa chọn phân tích
if lua_chon != '' and lua_chon != 'Tất cả' and lua_chon != 'Tất cả và tắt chart':
    st.write('')
    st.write('')
    st.markdown(f"<h3 style='text-align: center;'>Bồi thường theo {lua_chon.lower()}</h3>", unsafe_allow_html=True)
    with st.expander("Bảng thống kê"):
        group = duckdb.sql(
            f"""
        SELECT 
            "{lua_chon}",
            count(distinct "Insured ID") as "Số người yêu cầu bồi thường",
            count("Insured ID") as "Số hồ sơ bồi thường",
            ROUND(SUM("Yêu cầu bồi thường")) AS "Số tiền yêu cầu được bồi thường",
            ROUND(SUM("Đã được bồi thường")) AS "Số tiền được bồi thường",
            ROUND(SUM("Đã được bồi thường")/count(distinct "Insured ID")) as "Số tiền bồi thường trung bình/người",
            concat(round(SUM("Đã được bồi thường")*100/SUM("Yêu cầu bồi thường"),1),'%') as "Tỉ lệ thành công"
        FROM combined_df
        GROUP BY "{lua_chon}"
    """
        ).df()
        # df_numerical = group.drop(columns=['Tỉ lệ thành công',f"{lua_chon}"])
        # total_row = df_numerical.sum()
        # group.loc['Total'] = total_row
        # def format_number(x):
        #     return "{:,.0f}".format(x)
        
        
        
        #Format số
        
        def format_number(x):
            return "{:,.0f}".format(x)

        group['Số tiền yêu cầu được bồi thường'] = group['Số tiền yêu cầu được bồi thường'].apply(format_number)
        group['Số tiền được bồi thường'] = group['Số tiền được bồi thường'].apply(format_number)
        group['Số tiền bồi thường trung bình/người'] = group['Số tiền bồi thường trung bình/người'].apply(format_number)
        
        #Đổi màu bảng
        def style_table(df):
            # Màu sắc cho hàng header
            styled_df = df.style.set_table_styles([
                {'selector': 'thead th', 'props': [('background-color', '#F1798B'), ('color', 'black')]},  # Màu hồng cho header
            ])
            
            # Màu sắc luân phiên cho các hàng còn lại
            def row_style(row):
                if row.name % 2 == 0:
                    return ['background-color: #6C7EE1'] * len(row)  # Màu vàng nhạt cho hàng chẵn
                else:
                    return ['background-color: #FFC4A4'] * len(row)  # Màu xanh biển đậm cho hàng lẻ
            
            styled_df = styled_df.apply(row_style, axis=1)  # Áp dụng màu cho từng hàng
            return styled_df

        # Hiển thị DataFrame đã trang trí trong Streamlit, với độ cao cuộn
        st.dataframe(style_table(group), height=250)

    # Lựa chọn biểu đồ
    col_chart1, col_chart2,col_chart3 = st.columns(3)
    with col_chart1:
        if st.button("BAR CHART"):
            st.session_state.chon_chart = "BAR CHART"
    with col_chart2:
        if st.button("PIE CHART"):
            st.session_state.chon_chart = "PIE CHART"
    with col_chart3:
        if st.button("TẮT CHART"):
            st.session_state.chon_chart = ""
    # Vẽ biểu đồ theo lựa chọn
    if st.session_state.chon_chart == "BAR CHART":
        group = group.sort_values(by='Số tiền được bồi thường', ascending=False)
        bar_chart = px.bar(
            group,
            x=f"{lua_chon}",
            y="Số tiền được bồi thường",
            title="Số tiền đã bồi thường theo nhóm quyền lợi",
            text="Số tiền được bồi thường",  # Nhãn giá trị
            color=f"{lua_chon}",
            color_discrete_map={
                "Quyền lợi A": "#3A0751",
                "Quyền lợi B": "#FF5733",
                "Quyền lợi C": "#33FF57"
            }  # Tùy chỉnh màu sắc cho từng nhóm
        )

        # Tùy chỉnh vị trí của nhãn và hiển thị số nguyên trong nhãn
        bar_chart.update_traces(
            textposition='outside',  # Nhãn hiển thị bên ngoài cột
            texttemplate='%{text:,}' # Hiển thị số nguyên trong nhãn
        )
        bar_chart.update_layout(
            height=600  # Bạn có thể điều chỉnh giá trị này tùy theo nhu cầu của bạn
        )
        st.plotly_chart(bar_chart)
    
    elif st.session_state.chon_chart == "PIE CHART":
        top_5_case = group.sort_values(by='Số người yêu cầu bồi thường', ascending=False).head(5)
        top_5_amount = group.sort_values(by='Số tiền được bồi thường', ascending=False).head(5)
        col_pie_chart1, col_pie_chart2 = st.columns(2)
        with col_pie_chart1:
            pie_chart1 = px.pie(top_5_case, names=f'{lua_chon}', values="Số người yêu cầu bồi thường", title=f'Số người yêu cầu bồi thường theo {lua_chon.lower()}', 
                color=f'{lua_chon}',  
                color_discrete_map={
                    "Dependant": "#3A0751", 
                    "Employee": "#f2c85b"
                }  # Ánh xạ màu
            )
            st.plotly_chart(pie_chart1)
        with col_pie_chart2:
            pie_chart2 = px.pie(top_5_amount, names=f'{lua_chon}', values="Số tiền được bồi thường", title=f'Số tiền đã bồi thường theo {lua_chon.lower()}')
            st.plotly_chart(pie_chart2)
    elif st.session_state.chon_chart == "":
        st.write('')
elif lua_chon == 'Tất cả' :
    full_option = ["Nhóm", "Nhóm quyền lợi", "Cơ sở y tế", "Nhóm bệnh"]
    ten_bang = ''
    
    # Duyệt qua từng nhóm và hiển thị bảng và biểu đồ
    for option in full_option:
        if option == "Nhóm":
            ten_bang = "Nhóm khách hàng"
        elif option == "Nhóm quyền lợi":
            ten_bang = "Nhóm quyền lợi"
        elif option == "Cơ sở y tế":
            ten_bang = "Cơ sở y tế"
        elif option == "Nhóm bệnh":
            ten_bang = "Nhóm bệnh"
        
        st.markdown(f"<h3 style='text-align: center;'>Bồi thường theo {ten_bang.lower()}</h3>", unsafe_allow_html=True)
        
        # Truy vấn dữ liệu cho từng nhóm
        group = duckdb.sql(
            f"""
        SELECT 
            "{option}",
            count(distinct "Insured ID") as "Số người yêu cầu bồi thường",
            count("Insured ID") as "Số hồ sơ bồi thường",
            ROUND(SUM("Yêu cầu bồi thường")) AS "Số tiền yêu cầu được bồi thường",
            ROUND(SUM("Đã được bồi thường")) AS "Số tiền được bồi thường",
            ROUND(SUM("Đã được bồi thường")/count(distinct "Insured ID")) as "Số tiền bồi thường trung bình/người",
            concat(round(SUM("Đã được bồi thường")*100/SUM("Yêu cầu bồi thường"),1),'%') as "Tỉ lệ thành công"
        FROM combined_df
        GROUP BY "{option}"
    """
        ).df()

        # Hàm để trang trí bảng
        def style_table(df):
            # Màu sắc cho hàng header
            styled_df = df.style.set_table_styles([{'selector': 'thead th', 'props': [('background-color', '#F1798B'), ('color', 'black')]},])
            
            # Màu sắc luân phiên cho các hàng còn lại
            def row_style(row):
                if row.name % 2 == 0:
                    return ['background-color: #6C7EE1'] * len(row)  # Màu vàng nhạt cho hàng chẵn
                else:
                    return ['background-color: #FFC4A4'] * len(row)  # Màu xanh biển đậm cho hàng lẻ
            
            styled_df = styled_df.apply(row_style, axis=1)  # Áp dụng màu cho từng hàng
            return styled_df
        # Hiển thị bảng cuộn trong Streamlit với chiều rộng đầy đủ
        st.markdown(
            """
            <style>
            .streamlit-table {
                width: 100% !important;
                overflow-x: auto;
            }
            </style>
            """, unsafe_allow_html=True)
        # Hiển thị DataFrame đã trang trí trong Streamlit, với độ cao cuộn
        st.dataframe(style_table(group), height=250)

        # Hiển thị 2 biểu đồ pie
        col_pie_chart1, col_pie_chart2 = st.columns(2)

        # Top 5 dựa trên số người yêu cầu bồi thường
        top_5_case = group.sort_values(by='Số người yêu cầu bồi thường', ascending=False).head(5)
        top_5_amount = group.sort_values(by='Số tiền được bồi thường', ascending=False).head(5)

        with col_pie_chart1:
            pie_chart1 = px.pie(top_5_case, names=option, values="Số người yêu cầu bồi thường", title=f'Số người yêu cầu bồi thường theo {ten_bang}', 
                color=option,  
                color_discrete_map={
                    "Dependant": "#3A0751", 
                    "Employee": "#f2c85b"
                }  # Ánh xạ màu
            )
            st.plotly_chart(pie_chart1)

        with col_pie_chart2:
            pie_chart2 = px.pie(top_5_amount, names=option, values="Số tiền được bồi thường", title=f'Số tiền đã bồi thường theo {ten_bang}')
            st.plotly_chart(pie_chart2)
    st.write("Đang chạy nhánh 'Tất cả'")
elif lua_chon == 'Tất cả và tắt chart':
    full_option = ["Nhóm", "Nhóm quyền lợi", "Cơ sở y tế", "Nhóm bệnh"]
    ten_bang = ''
    
    # Duyệt qua từng nhóm và hiển thị bảng và biểu đồ
    for option in full_option:
        if option == "Nhóm":
            ten_bang = "Nhóm khách hàng"
        elif option == "Nhóm quyền lợi":
            ten_bang = "Nhóm quyền lợi"
        elif option == "Cơ sở y tế":
            ten_bang = "Cơ sở y tế"
        elif option == "Nhóm bệnh":
            ten_bang = "Nhóm bệnh"
        
        st.markdown(f"<h3 style='text-align: center;'>Bồi thường theo {ten_bang.lower()}</h3>", unsafe_allow_html=True)
        
        # Truy vấn dữ liệu cho từng nhóm
        group = duckdb.sql(
            f"""
        SELECT 
            "{option}",
            count(distinct "Insured ID") as "Số người yêu cầu bồi thường",
            count("Insured ID") as "Số hồ sơ bồi thường",
            ROUND(SUM("Yêu cầu bồi thường")) AS "Số tiền yêu cầu được bồi thường",
            ROUND(SUM("Đã được bồi thường")) AS "Số tiền được bồi thường",
            ROUND(SUM("Đã được bồi thường")/count(distinct "Insured ID")) as "Số tiền bồi thường trung bình/người",
            concat(round(SUM("Đã được bồi thường")*100/SUM("Yêu cầu bồi thường"),1),'%') as "Tỉ lệ thành công"
        FROM combined_df
        GROUP BY "{option}"
    """
        ).df()

        # Hàm để trang trí bảng
        def style_table(df):
            # Màu sắc cho hàng header
            styled_df = df.style.set_table_styles([{'selector': 'thead th', 'props': [('background-color', '#F1798B'), ('color', 'black')]},])
            
            # Màu sắc luân phiên cho các hàng còn lại
            def row_style(row):
                if row.name % 2 == 0:
                    return ['background-color: #6C7EE1'] * len(row)  # Màu vàng nhạt cho hàng chẵn
                else:
                    return ['background-color: #FFC4A4'] * len(row)  # Màu xanh biển đậm cho hàng lẻ
            
            styled_df = styled_df.apply(row_style, axis=1)  # Áp dụng màu cho từng hàng
            return styled_df

        # Hiển thị DataFrame đã trang trí trong Streamlit, với độ cao cuộn
        st.dataframe(style_table(group), height=250)
else:
    st.header('CHỌN GIÁ TRỊ MUỐN PHÂN TÍCH')
