
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 DASHBOARD QUẢN LÝ ĐẶT PHÒNG")

# Load dữ liệu
df = pd.read_csv("process_hotel.csv")

# Thêm các cột phụ trợ nếu cần
df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
df["revenue"] = df.apply(lambda row: row["adr"] * row["total_nights"] if row["is_canceled"] == 0 else 0, axis=1)
df["stay_length"] = df["total_nights"]
df["reservation_status_date"] = pd.to_datetime(df["reservation_status_date"])
df["month"] = pd.Categorical(df["arrival_date_month"],
    categories=["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"],
    ordered=True)

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tỷ lệ phòng được cấp đúng", f"{(df['reserved_room_type'] == df['assigned_room_type']).mean() * 100:.2f}%")
col2.metric("Thời gian lưu trú trung bình", f"{df['stay_length'].mean():.2f}")
col3.metric("Tổng số yêu cầu đặc biệt", f"{df['total_of_special_requests'].sum():,}")
col4.metric("Tỷ lệ khách có yêu cầu đặc biệt", f"{(df['total_of_special_requests'] > 0).mean() * 100:.2f}%")

st.markdown("---")

# Biểu đồ loại phòng đặt vs được cấp
st.subheader("Loại phòng đặt VS được cấp")
room_count = df.groupby("reserved_room_type").size().reset_index(name="reserved")
assigned_count = df.groupby("assigned_room_type").size().reset_index(name="assigned")
room_merge = pd.merge(room_count, assigned_count, left_on="reserved_room_type", right_on="assigned_room_type", how="outer").fillna(0)
room_merge["reserved_room_type"].fillna(room_merge["assigned_room_type"], inplace=True)
room_merge["reserved"] = room_merge["reserved"].astype(int)
room_merge["assigned"] = room_merge["assigned"].astype(int)
room_merge = room_merge.rename(columns={"reserved_room_type": "room_type"})
fig1 = px.bar(room_merge, x="room_type", y=["reserved", "assigned"], barmode="group", text_auto=True)
st.plotly_chart(fig1, use_container_width=True)

# Bộ lọc
col_a, col_b = st.columns(2)
with col_a:
    hotel_filter = st.selectbox("Loại Hotel", ["All"] + sorted(df["hotel"].unique()))
with col_b:
    is_repeated = st.selectbox("Khách quen hay không", ["All", 0, 1])

filtered_df = df.copy()
if hotel_filter != "All":
    filtered_df = filtered_df[filtered_df["hotel"] == hotel_filter]
if is_repeated != "All":
    filtered_df = filtered_df[filtered_df["is_repeated_guest"] == int(is_repeated)]

# Giá phòng
min_price = int(df["adr"].min())
max_price = int(df["adr"].max())
selected_price = st.slider("Giá phòng trung bình mỗi đêm", min_value=min_price, max_value=max_price, value=max_price)
filtered_df = filtered_df[filtered_df["adr"] <= selected_price]

# Thời gian lưu trú TB theo tháng
st.subheader("Thời gian lưu trú TB theo tháng")
stay_avg = df.groupby("month")["stay_length"].mean().reset_index()
fig2 = px.line(stay_avg, x="month", y="stay_length", markers=True)
st.plotly_chart(fig2, use_container_width=True)

# Số lượng đặt phòng theo kênh
col_k1, col_k2 = st.columns(2)
with col_k1:
    st.subheader("Số lượng đặt phòng theo kênh")
    channel_count = df["distribution_channel"].value_counts().reset_index()
    channel_count.columns = ["channel", "count"]
    fig3 = px.bar(channel_count, x="channel", y="count", text_auto=True)
    st.plotly_chart(fig3, use_container_width=True)

# Tổng số lượng đặt theo ngày
with col_k2:
    st.subheader("Tổng số lượng đặt phòng theo ngày")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["day_of_week"] = df["reservation_status_date"].dt.day_name()
    booking_day = df["day_of_week"].value_counts().reindex(day_order).reset_index()
    booking_day.columns = ["day", "count"]
    fig4 = px.bar(booking_day, x="count", y="day", orientation="h", text="count")
    st.plotly_chart(fig4, use_container_width=True)
