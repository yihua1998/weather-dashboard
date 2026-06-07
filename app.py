import streamlit as st
import pandas as pd
import plotly.express as px
from weather import get_7day_forecast, get_air_quality, get_current_weather
from outfit import get_outfit_suggestions
import datetime
from database import save_daily_weather, get_history

st.set_page_config(page_title="天氣穿搭助手", layout="wide", page_icon="🧳")
st.title("☀️天氣 & 穿搭建議")
st.caption("輸入目的地，查詢未來天氣與穿搭建議")

with st.sidebar:
    st.header("🔎 查詢地點")
    city = st.text_input("目的地城市（英文）", "Tokyo")
    gender = st.radio("性別", ["女", "男"])
    search_btn = st.button("查詢", type="primary", use_container_width=True)

if search_btn and city:
    with st.spinner(f"查詢 {city} 天氣中..."):
        try:
            current = get_current_weather(city)
            forecast = get_7day_forecast(city)
            air_data = get_air_quality(city)
            save_daily_weather(city, forecast)
        except Exception as e:
            st.error(f"查詢失敗，請確認城市名稱：{e}")
            st.stop()

    # 今日現況
    today = forecast[0]
    st.subheader(f"📍 {city} 現在天氣")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("現在溫度", f"{current['temp']}°C")
    c2.metric("體感溫度", f"{current['feels_like']}°C")
    c3.metric("天氣", f"{current['icon']} {current['description']}")
    c4.metric("濕度", f"{current['humidity']}%")
    c5.metric("今日降雨量", f"{forecast[0]['rain']} mm")

    st.divider()

    # 每日天氣卡片
    st.subheader(f"📅 {city} 未來天氣預報")
    cols = st.columns(len(forecast))
    for i, day in enumerate(forecast):
        with cols[i]:
            st.markdown(f"""
            <div style='text-align:center;padding:10px;background:#f0f2f6;border-radius:10px;'>
                <div style='font-size:13px;color:gray;'>{day['weekday']}</div>
                <div style='font-size:12px;color:gray;'>{day['date']}</div>
                <div style='font-size:32px;'>{day['icon']}</div>
                <div style='font-size:13px;'>{day['description']}</div>
                <div style='font-size:16px;font-weight:bold;color:#FF6B6B;'>{day['temp_max']}°</div>
                <div style='font-size:14px;color:#4ECDC4;'>{day['temp_min']}°</div>
                <div style='font-size:11px;color:gray;'>💧{day['humidity']}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # 圖表
    df = pd.DataFrame(forecast)
    df_air = pd.DataFrame(air_data)
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("🌡️ 溫度趨勢")
        fig_temp = px.line(df, x="date", y=["temp_max", "temp_min"],
            labels={"date": "日期", "value": "溫度 (°C)", "variable": ""},
            color_discrete_map={"temp_max": "#FF6B6B", "temp_min": "#4ECDC4"})
        fig_temp.update_layout(margin=dict(l=0, r=0, t=20, b=0), legend=dict(orientation="h"))
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_right:
        st.subheader("💨 AQI 趨勢")
        fig_aqi = px.line(df_air.head(40), x="datetime", y="aqi",
            labels={"datetime": "時間", "aqi": "AQI"},
            color_discrete_sequence=["#A29BFE"])
        fig_aqi.update_layout(margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig_aqi, use_container_width=True)
    # 歷史溫度趨勢
    history = get_history(city, days=30)
    if len(history) >= 1:
        st.subheader(f"📈 {city} 歷史溫度趨勢")
        df_history = pd.DataFrame(history)
        df_history = df_history.sort_values("date")
        fig_history = px.line(
            df_history, x="date", y=["temp_max", "temp_min"],
            labels={"date": "日期", "value": "溫度 (°C)", "variable": ""},
            color_discrete_map={"temp_max": "#FF6B6B", "temp_min": "#4ECDC4"},
            title=f"{city} 過去 {len(history)} 天溫度記錄"
        )
        fig_history.update_layout(margin=dict(l=0, r=0, t=40, b=0), legend=dict(orientation="h"))
        st.plotly_chart(fig_history, use_container_width=True)
        st.caption(f"最後更新：{history[-1]['saved_at'] if 'saved_at' in history[-1] else history[-1]['date']}")
    
    st.divider()
    # 空氣品質
    st.subheader("🏭 空氣品質")
    latest_air = df_air.iloc[0]
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("AQI 等級", latest_air["aqi_label"])
    a2.metric("PM2.5", f"{latest_air['pm2_5']:.1f} μg/m³")
    a3.metric("PM10", f"{latest_air['pm10']:.1f} μg/m³")
    a4.metric("NO₂", f"{latest_air['no2']:.1f} μg/m³")

    st.divider()

    # 穿搭建議
    month = datetime.datetime.now().month
    avg_temp = df["temp_avg"].mean()
    main_desc = df["description"].mode()[0]
    gender_val = "女" if "女" in gender else "男"
    gender_label = "女生" if gender_val == "女" else "男生"
    gender_icon = "👗" if gender_val == "女" else "👕"

    if month in [6, 7, 8]:
        temp_keyword = "炎熱夏天" if avg_temp >= 28 else "夏天"
    elif month in [3, 4, 5]:
        temp_keyword = "溫暖春天" if avg_temp >= 25 else "涼爽春天"
    elif month in [9, 10, 11]:
        temp_keyword = "初秋" if avg_temp >= 25 else "秋天"
    else:
        temp_keyword = "寒冷冬天" if avg_temp <= 10 else "冬天"

    st.subheader(f"{gender_icon} {gender_label} 穿搭建議")
    st.caption(f"🔍 查詢關鍵字：{city} {month}月 {avg_temp:.0f}度 {gender_label} {temp_keyword} 穿搭建議")

    with st.spinner("搜尋穿搭建議中..."):
        suggestions = get_outfit_suggestions(avg_temp, gender_val, main_desc, city=city, month=month)

    for i, s in enumerate(suggestions):
        if s["url"]:
            st.markdown(f"**{i+1}.** [{s['title']}]({s['url']})")
        else:
            st.write(s["title"])
