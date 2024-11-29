import pandas as pd
import streamlit as st
import calendar
from datetime import datetime
import os
from navigation import make_sidebar

st.set_page_config(page_title="Trading Dashboard", layout="centered")

make_sidebar()

file_path = os.path.join(os.getcwd(), "tradelog_updated.csv")

# Function to load the tradelog from disk if it exists
def load_tradelog():
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return None

# Check if trade log data already exists in session_state
if "tradelog" not in st.session_state:
    st.session_state["tradelog"] = load_tradelog()  # Load from disk if available

# Ensure tradelog data is available
if "tradelog" in st.session_state and st.session_state["tradelog"] is not None:
    tradelog = st.session_state["tradelog"]
    tradelog["Date"] = pd.to_datetime(tradelog["Date"])

    available_years = sorted(tradelog["Date"].dt.year.unique())

    # Get the most recent date available in the data
    latest_date = st.session_state['tradelog']['Date'].max()
    # # Extract the latest year and month
    latest_year = latest_date.year
    latest_month = latest_date.month

    # Sidebar inputs for year and month
    year = st.sidebar.selectbox("Year", options=available_years, index=available_years.index(latest_year))
    month_name = st.sidebar.selectbox("Month", options=list(calendar.month_name[1:]), index=latest_month-1)
    month = list(calendar.month_name).index(month_name)  # Convert month name to index

    # Get the weekday of the first day of the month and number of days in the selected month
    first_day_of_month, days_in_month = calendar.monthrange(year, month)

    # Adjust to start from Sunday as first column in Streamlit
    # (calendar.monthrange assumes Monday as the start of the week )
    first_day_of_month = (first_day_of_month + 1) % 7

    # Display the selected month and year
    st.markdown(f"### {calendar.month_name[month]} {year}")

    # Define CSS for row grouping
    row_style = """
    <style>
        .calendar-row {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #e6e6e6;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }
        .calendar-cell {
            text-align: center;
            width: 13%;
            padding: 10px;
            font-size: 14px;
        }
        .calendar-cell.positive {background-color: #6AB187; color: white;}
        .calendar-cell.negative {background-color: #D94758; color: white;}
        .calendar-cell.neutral {background-color: #F5F5F5; color: black;}
    </style>
    """
    st.markdown(row_style, unsafe_allow_html=True)

    # Weekday headers
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    header = "".join([f"<div class='calendar-cell'>{day}</div>" for day in weekdays])
    st.markdown(f"<div class='calendar-row'>{header}</div>", unsafe_allow_html=True)

    # Loop through weeks and days to populate calendar
    day_counter = 1
    while day_counter <= days_in_month:
        row_cells = []

        for i in range(7):
            if day_counter == 1 and i < first_day_of_month:
                # Empty cell at the start of the month
                row_cells.append("<div class='calendar-cell neutral'></div>")
            elif day_counter > days_in_month:
                # Empty cell at the end of the month
                row_cells.append("<div class='calendar-cell neutral'></div>")
            else:
                # Define the specific date for the day in the selected month
                current_date = datetime(year, month, day_counter)

                # Filter the tradelog for the current date
                daily_trades = tradelog[
                    (tradelog['Date'].dt.year == year) &
                    (tradelog['Date'].dt.month == month) &
                    (tradelog['Date'].dt.day == day_counter)]

                # Calculate PnL and trade count for the day
                pnl = daily_trades['Net PnL'].sum()
                trades = daily_trades.shape[0]

                # Format PnL and trade count for display
                pnl_text = f"${pnl:,.2f}" if pnl else "$0.00"
                trade_text = f"{trades} Trades" if trades > 0 else "0 Trades"

                # Set cell class based on PnL value
                cell_class = "positive" if pnl > 0 else "negative" if pnl < 0 else "neutral"

                # Create calendar cell
                cell_html = (
                    f"<div class='calendar-cell {cell_class}'>"
                    f"<div style='font-weight: bold;'>{day_counter}</div>"
                    f"<div>{pnl_text}</div>"
                    f"<div style='color: #4A4A4A; font-weight: 600;'>{trade_text}</div>"
                    f"</div>"
                )
                row_cells.append(cell_html)
                day_counter += 1

        # Render the row
        st.markdown(f"<div class='calendar-row'>{''.join(row_cells)}</div>", unsafe_allow_html=True)
else:
    st.warning("Please upload your tradelog to proceed.")
    st.stop()
