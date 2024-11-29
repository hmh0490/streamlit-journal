import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from navigation import make_sidebar

# Set the page configuration to wide layout
st.set_page_config(page_title="Trading Dashboard", layout="wide")

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

# Retrieve settings from session_state
risk_management_fee = st.session_state.get('risk_management_fee')
ticker_data = st.session_state.get('ticker_data', pd.DataFrame())
initial_balance = st.session_state.get('initial_balance')
withdrawals = st.session_state.get('withdrawals')

# Dropdown to select the reporting period (Monthly, Quarterly, Annual)
reporting_period = st.sidebar.selectbox("Select Reporting Period",
                                        ["Monthly", "Quarterly", "Annual"])

# Display relevant filters based on the selected reporting period
st.sidebar.markdown("### Filters")
#
# def calculate_metrics(filtered_trades):
#     # Directional statistics
#     long_trades = filtered_trades[filtered_trades["Direction"] == "Long"]
#     short_trades = filtered_trades[filtered_trades["Direction"] == "Short"]
#
#     volume = filtered_trades["Contracts"].sum()
#     total_fees = (filtered_trades["Total Broker Fees"] + filtered_trades["Risk Management Fee"]).sum()
#
#     long_PnL = long_trades["Net PnL"].sum()
#     short_PnL = short_trades["Net PnL"].sum()
#     monthly_netPnL = filtered_trades["Net PnL"].sum()
#
#     nr_long = long_trades.shape[0]
#     nr_short = short_trades.shape[0]
#     nr_trades = filtered_trades.shape[0]
#
#     winner_long = long_trades[long_trades["Net PnL"] > 0].shape[0]
#     winner_short = short_trades[short_trades["Net PnL"] > 0].shape[0]
#     looser_long = long_trades[long_trades["Net PnL"] < 0].shape[0]
#     looser_short = short_trades[short_trades["Net PnL"] < 0].shape[0]
#
#     gross_profit = filtered_trades[filtered_trades["PnL"] > 0]["PnL"].sum()
#     gross_losses = filtered_trades[filtered_trades["PnL"] < 0]["PnL"].sum()
#
#     win_rate = (filtered_trades[filtered_trades["Net PnL"] > 0].shape[0] / nr_trades) * 100 if nr_trades > 0 else 0
#     risk_reward = (filtered_trades[filtered_trades["Net PnL"] < 0].shape[0] /
#                    filtered_trades[filtered_trades["Net PnL"] > 0].shape[0]) if \
#         filtered_trades[filtered_trades["Net PnL"] > 0].shape[0] > 0 else None
#
#     avg_winning_days = filtered_trades[filtered_trades["Net PnL"] > 0]["Net PnL"].mean()
#     avg_loosing_days = filtered_trades[filtered_trades["Net PnL"] < 0]["Net PnL"].mean()
#
#     return {
#         "volume": volume, "total_fees": total_fees,
#         "long_PnL": long_PnL, "short_PnL": short_PnL, "monthly_netPnL": monthly_netPnL,
#         "nr_long": nr_long, "nr_short": nr_short, "nr_trades": nr_trades,
#         "winner_long": winner_long, "winner_short": winner_short,
#         "looser_long": looser_long, "looser_short": looser_short,
#         "gross_profit": gross_profit, "gross_losses": gross_losses,
#         "win_rate": win_rate, "risk_reward": risk_reward,
#         "avg_winning_days": avg_winning_days, "avg_loosing_days": avg_loosing_days
#     }
#
# def display_metrics(metrics):
#     col1, col2, col3, col4 = st.columns(4)
#
#     with col1:
#         st.metric("Gross Profits", f"${metrics['gross_profit']:,.2f}")
#     with col2:
#         st.markdown(
#             f"<div style='color:#D94758;'>Gross Losses: ${metrics['gross_losses']:,.2f}</div>",
#             unsafe_allow_html=True)
#     with col3:
#         st.markdown(f"<div style='color:#D94758;'>Total Fees: ${metrics['total_fees']:,.2f}</div>",
#                     unsafe_allow_html=True)
#     with col4:
#         st.metric("Monthly Total P/L", f"${metrics['monthly_netPnL']:,.2f}")
#
#     col5, col6, col7, col8 = st.columns(4)
#     with col5:
#         st.metric("Total Trades", metrics['nr_trades'])
#     with col6:
#         st.metric("Win Rate", f"{metrics['win_rate']:.2f}%")
#     with col7:
#         st.metric("Avg. Winning Days", f"${metrics['avg_winning_days']:,.2f}")
#     with col8:
#         st.markdown(f"<div style='color:#D94758;'>Avg. Losing Days: ${metrics['avg_loosing_days']:,.2f}</div>",
#             unsafe_allow_html=True)
#
# def create_waterfall_chart(long_PnL, short_PnL, monthly_netPnL):
#     accumulated_pl_data = {
#         "Type": ["Accumulated Long P/L", "Accumulated Short P/L", "Net P/L"],
#         "Value": [long_PnL, short_PnL, monthly_netPnL]
#     }
#     fig_waterfall = go.Figure(go.Waterfall(
#         name="Accumulated P/L",
#         orientation="v",
#         measure=["relative", "relative", "total"],
#         x=accumulated_pl_data["Type"],
#         y=accumulated_pl_data["Value"],
#         text=[f"${val:,.2f}" for val in accumulated_pl_data["Value"]],
#         textposition="outside",
#         connector=dict(line=dict(color="rgba(63, 63, 63, 0.5)")),
#         decreasing=dict(marker=dict(color="#D94758")),
#         increasing=dict(marker=dict(color="#6AB187")),
#         totals=dict(marker=dict(color="#B0B0B0"))
#     ))
#     return fig_waterfall

# Ensure tradelog data is available
if "tradelog" in st.session_state and st.session_state["tradelog"] is not None:
    tradelog = st.session_state["tradelog"]
    tradelog["Date"] = pd.to_datetime(tradelog["Date"])
    # Get unique years and sort them
    available_years = sorted(tradelog["Date"].dt.year.unique())
    # Get the most recent date available in the data
    latest_date = st.session_state['tradelog']['Date'].max()
    # Extract the latest year and month
    latest_year = latest_date.year

    # Calculate the previous month
    if latest_date.month == 1:  # If it's January, wrap around to December of the previous year
        previous_month_date = latest_date.replace(year=latest_date.year - 1, month=12, day=1)
        latest_year = previous_month_date.year
    else:
        previous_month_date = latest_date.replace(day=1) - timedelta(days=1)

    previous_month = previous_month_date.strftime("%B")

    if reporting_period == "Monthly":

        st.title("Monthly Trading Report")

        year = st.sidebar.selectbox("Year", options=available_years, index=available_years.index(latest_year))
        month = st.sidebar.selectbox(
            "Month",
            options=["January", "February", "March", "April", "May", "June",
                     "July", "August", "September", "October", "November", "December"],
            index=["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"].index(previous_month))
        selected_month = pd.to_datetime(month, format='%B').month

        selected_year = year
        selected_month = selected_month

        # Filter the tradelog based on the selected year and month
        filtered_trades = tradelog[(tradelog["Date"].dt.year == selected_year) & (
                    tradelog["Date"].dt.month == selected_month)]

        # Check if filtered data is empty and display an appropriate message
        if filtered_trades.empty:
            st.write(f"No data available for {month} {year}.")
        else:
            filtered_trades = pd.DataFrame(filtered_trades)

            # Calculate each metric
            volume = filtered_trades["Contracts"].sum()
            total_fees = (filtered_trades["Total Broker Fees"] + filtered_trades["Risk Management Fee"]).sum()

            # Directional statistics
            long_trades = filtered_trades[filtered_trades["Direction"] == "Long"]
            short_trades = filtered_trades[filtered_trades["Direction"] == "Short"]
            long_PnL = long_trades["Net PnL"].sum()
            short_PnL = short_trades["Net PnL"].sum()
            monthly_netPnL = filtered_trades["Net PnL"].sum()

            # Number of long and short trades
            nr_long = long_trades.shape[0]
            nr_short = short_trades.shape[0]
            nr_trades = filtered_trades.shape[0]

            # Winning and losing trades
            winner_long = long_trades[long_trades["Net PnL"] > 0].shape[0]
            winner_short = short_trades[short_trades["Net PnL"] > 0].shape[0]
            looser_long = long_trades[long_trades["Net PnL"] < 0].shape[0]
            looser_short = short_trades[short_trades["Net PnL"] < 0].shape[0]

            # Gross profit and gross losses
            gross_profit = filtered_trades[filtered_trades["PnL"] > 0]["PnL"].sum()
            gross_losses = filtered_trades[filtered_trades["PnL"] < 0]["PnL"].sum()

            # Win rate and risk/reward ratio
            win_rate = (filtered_trades[filtered_trades["Net PnL"] > 0].shape[
                            0] / nr_trades) * 100 if nr_trades > 0 else 0
            risk_reward = (filtered_trades[filtered_trades["Net PnL"] < 0].shape[0] /
                           filtered_trades[filtered_trades["Net PnL"] > 0].shape[0]) if \
                filtered_trades[filtered_trades["Net PnL"] > 0].shape[0] > 0 else None

            # Average winning and losing days
            avg_winning_days = filtered_trades[filtered_trades["Net PnL"] > 0]["Net PnL"].mean()
            avg_loosing_days = filtered_trades[filtered_trades["Net PnL"] < 0]["Net PnL"].mean()
            col1, col2, col3, col4  = st.columns([1, 1, 1, 1])
            # Display metrics with custom formatting and colors
            with col1:
                st.metric(label="Gross Profits", value=f"${gross_profit:,.2f}")
            with col2:
                st.markdown(
                    f"""
                    <div style='display: flex; flex-direction: column; align-items: left;'>
                        <div style='font-size: 0.9em; color: #000000;margin-bottom: -10px;'>Gross Losses</div>
                        <div style='font-size: 2.3em;color: #D94758;'>${gross_losses:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            with col3:
                st.markdown(
                    f"""
                    <div style='display: flex; flex-direction: column; align-items: left;'>
                        <div style='font-size: 0.9em; color: #000000;margin-bottom: -10px;'>Total Commission Fees</div>
                        <div style='font-size: 2.3em;color: #D94758;'>${total_fees:,.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True)
            with col4:
                st.metric(label="Monthly Total P/L", value=f"${monthly_netPnL:,.2f}", delta_color="inverse")

            col5, col6, col7, col8 = st.columns([1,1,1,1])
            # Additional summary stats in a row with color and formatting
            with col5:
                st.metric("Total Trades", f"{nr_trades}")
            with col6:
                st.metric("Win Rate", f"{win_rate:.2f}%")
            with col7:
                st.metric("Avg. Winning Days", f"${avg_winning_days:,.2f}")
            # Display "Avg. Losing Days" in red in col8
            with col8:
                st.markdown(
                    f"""
                    <div style='display: flex; flex-direction: column; align-items: left;'>
                        <div style='font-size: 0.9em; color: #000000;margin-bottom: -10px;'>Avg. Losing Days</div>
                        <div style='font-size: 2.3em;color: #D94758;'>${avg_loosing_days:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            # Left Panel Statistics Table
            with st.container():
                stats_data = {
                    "Metric": ["Volume", "Commission Fees", "Accumulated Long P/L",
                               "Accumulated Short P/L", "Net P/L",
                               "Long Trades", "Short Trades", 'Total Trades', 'Winner Long Trades',
                               'Winner Short Trades', 'Looser Long Trades', 'Looser Short Trades',
                               'Gross Profit', 'Gross Losses', "Win Rate", "Risk/Reward Ratio",
                               "Average Winning Days", 'Average Loosing Days'],
                    "Value": [
                        volume,  # Volume (2 decimals, no dollar sign)
                        f"${total_fees:,.2f}",  # Dollar with 2 decimals
                        f"${long_PnL:,.2f}",
                        f"${short_PnL:,.2f}",
                        f"${monthly_netPnL:,.2f}",
                        nr_long,  # Integer
                        nr_short,  # Integer
                        nr_trades,  # Integer
                        winner_long,  # Integer
                        winner_short,  # Integer
                        looser_long,  # Integer
                        looser_short,  # Integer
                        f"${gross_profit:,.2f}",  # Dollar with 2 decimals
                        f"${gross_losses:,.2f}",  # Dollar with 2 decimals
                        f"{win_rate:.2f}",  # 2 decimals, no dollar sign
                        f"{risk_reward:.2f}",  # 2 decimals, no dollar sign
                        f"${avg_winning_days:,.2f}",  # Dollar with 2 decimals
                        f"${avg_loosing_days:,.2f}"  # Dollar with 2 decimals
                    ]
                }

            stats_df = pd.DataFrame(stats_data)

            # General CSS to remove grid lines and reduce row spacing
            custom_table_style = """
                        <style>
                        /* Remove the index column header and row index */
                        thead tr th:first-child {display:none}
                        tbody th {display:none}
        
                        /* Remove all borders */
                        table {border-collapse: collapse;}
                        table td, table th {border: none !important; padding: 4px 0px;}
        
                        /* Set light grey background for the table */
                        table, th, td {
                            background-color: #f5f5f5;  /* Light grey background */
                        }
        
                        /* Optional: Adjust font size for a tighter look */
                        table td {font-size: 0.9rem;}
                        </style>
                        """

            # Apply CSS
            st.markdown(custom_table_style, unsafe_allow_html=True)

            # Display the new section with 3 columns
            col1, col2, col3, col4, col5 = st.columns([0.5, 0.2, 0.6, 0.2, 0.6])

            # Display statistics table in the first column
            with col1:
                st.markdown("**Statistics**")
                st.table(stats_df)

            with col3:
                # Prepare data for the waterfall chart
                accumulated_pl_data = {
                    "Type": ["Accumulated Long P/L", "Accumulated Short P/L", "Net P/L"],
                    "Value": [long_PnL, short_PnL, monthly_netPnL]
                }

                # Create the waterfall chart
                fig_waterfall = go.Figure(go.Waterfall(
                    name="Accumulated P/L",
                    orientation="v",
                    measure=["relative", "relative", "total"],
                    x=accumulated_pl_data["Type"],
                    y=accumulated_pl_data["Value"],
                    text=[f"${val:,.2f}" for val in accumulated_pl_data["Value"]],
                    textposition="outside",
                    connector=dict(line=dict(color="rgba(63, 63, 63, 0.5)")),
                    decreasing=dict(marker=dict(color="#D94758")),
                    increasing=dict(marker=dict(color="#6AB187")),
                    totals=dict(marker=dict(color="#B0B0B0"))
                ))

                # Update layout for a longer and thinner chart
                fig_waterfall.update_layout(
                    title="Accumulated P/L",
                    showlegend=False,
                    xaxis_title="Type",
                    yaxis_title="Value",
                    width=100,  # Set the chart width to make it longer
                    height=600,  # Set the chart height to make it thinner
                    margin=dict(l=50, r=50, t=50, b=50),
                    xaxis=dict(showgrid=False),  # Remove x-axis gridlines
                    yaxis=dict(showgrid=False)  # Remove y-axis gridlines            # Adjust margins
                )

                # Increase font size of labels for better visibility
                fig_waterfall.update_traces(textfont_size=12)  # Larger label font size

                # Display the chart
                st.plotly_chart(fig_waterfall, use_container_width=True)

            with col5:
                # % Trades Pie Chart
                trade_distribution_data = pd.DataFrame({
                    "Trade Type": ["Long Trades", "Short Trades"],
                    "Percentage": [67, 33]
                })
                fig_pie = px.pie(trade_distribution_data, names="Trade Type",
                                 values="Percentage",
                                 color="Trade Type",
                                 color_discrete_map={"Long Trades": "#6AB187",
                                                     "Short Trades": "#D94758"})
                fig_pie.update_layout(title="% Trades", showlegend=True, height=300)
                st.plotly_chart(fig_pie, use_container_width=True)

                # Bar chart
                data = {
                    "Trade Type": ["Long Trades", "Short Trades"],
                    "Winners": [winner_long, winner_short],
                    # Number of winning trades for Long and Short
                    "Losers": [looser_long,
                               looser_short], }  # Number of losing trades for Long and Short

                # Create a DataFrame
                df = pd.DataFrame(data)

                # Calculate the total trades for each type
                df["Total"] = df["Winners"] + df["Losers"]

                # Calculate the percentages
                df["Winners %"] = (df["Winners"] / df["Total"]) * 100
                df["Losers %"] = (df["Losers"] / df["Total"]) * 100

                # Create the stacked bar chart
                fig = go.Figure()

                # Winners bar
                fig.add_trace(go.Bar(
                    y=df["Trade Type"],
                    x=df["Winners %"],
                    name="Winners",
                    orientation='h',
                    marker=dict(color="#6AB187"),  # Green color
                    text=df["Winners"],
                    textposition='inside'))

                # Losers bar
                fig.add_trace(go.Bar(
                    y=df["Trade Type"],
                    x=df["Losers %"],
                    name="Losers",
                    orientation='h',
                    marker=dict(color="#D94758"),  # Red color
                    text=df["Losers"],
                    textposition='inside'))

                # Customize the layout
                fig.update_layout(
                    title="Winners & Losers",
                    barmode='stack',
                    xaxis=dict(title="Percentage", range=[0, 100], ticksuffix="%"),
                    yaxis=dict(title=""),
                    height=300,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5))

                # Display the chart in Streamlit
                st.plotly_chart(fig, use_container_width=True)

    elif reporting_period == "Quarterly":

        st.title("Quarterly Trading Report")

        latest_month = latest_date.month

        # Map the latest month to its corresponding quarter
        if latest_month in [1, 2, 3]:
            default_quarter = "Q1"
        elif latest_month in [4, 5, 6]:
            default_quarter = "Q2"
        elif latest_month in [7, 8, 9]:
            default_quarter = "Q3"
        else:
            default_quarter = "Q4"

        year = st.sidebar.selectbox("Year", options=available_years, index=available_years.index(latest_year))
        quarter = st.sidebar.selectbox("Quarter",
                                       options=["Q1", "Q2", "Q3", "Q4"], index=["Q1", "Q2", "Q3", "Q4"].index(default_quarter))

        # Define the mapping of quarters to months
        quarter_to_months = {
            "Q1": (1, 3),  # January to March
            "Q2": (4, 6),  # April to June
            "Q3": (7, 9),  # July to September
            "Q4": (10, 12)  # October to December
        }

        # Get the start and end month for the selected quarter
        start_month, end_month = quarter_to_months[quarter]

        # Filter the DataFrame based on the selected year and quarter
        filtered_trades = tradelog[(tradelog["Date"].dt.year == year) &
                           (tradelog["Date"].dt.month >= start_month) &
                           (tradelog["Date"].dt.month <= end_month)]

        # Check if filtered data is empty and display an appropriate message
        if filtered_trades.empty:
            st.write(f"No data available for {quarter} {year}.")
        else:
            filtered_trades = pd.DataFrame(filtered_trades)

            # Calculate each metric
            volume = filtered_trades["Contracts"].sum()
            total_fees = (filtered_trades["Total Broker Fees"] + filtered_trades[
                "Risk Management Fee"]).sum()

            # Directional statistics
            long_trades = filtered_trades[filtered_trades["Direction"] == "Long"]
            short_trades = filtered_trades[filtered_trades["Direction"] == "Short"]
            long_PnL = long_trades["Net PnL"].sum()
            short_PnL = short_trades["Net PnL"].sum()
            monthly_netPnL = filtered_trades["Net PnL"].sum()

            # Number of long and short trades
            nr_long = long_trades.shape[0]
            nr_short = short_trades.shape[0]
            nr_trades = filtered_trades.shape[0]

            # Winning and losing trades
            winner_long = long_trades[long_trades["Net PnL"] > 0].shape[0]
            winner_short = short_trades[short_trades["Net PnL"] > 0].shape[0]
            looser_long = long_trades[long_trades["Net PnL"] < 0].shape[0]
            looser_short = short_trades[short_trades["Net PnL"] < 0].shape[0]

            # Gross profit and gross losses
            gross_profit = filtered_trades[filtered_trades["PnL"] > 0]["PnL"].sum()
            gross_losses = filtered_trades[filtered_trades["PnL"] < 0]["PnL"].sum()

            # Win rate and risk/reward ratio
            win_rate = (filtered_trades[filtered_trades["Net PnL"] > 0].shape[
                            0] / nr_trades) * 100 if nr_trades > 0 else 0
            risk_reward = (filtered_trades[filtered_trades["Net PnL"] < 0].shape[0] /
                           filtered_trades[filtered_trades["Net PnL"] > 0].shape[0]) if \
                filtered_trades[filtered_trades["Net PnL"] > 0].shape[0] > 0 else None

            # Average winning and losing days
            avg_winning_days = filtered_trades[filtered_trades["Net PnL"] > 0]["Net PnL"].mean()
            avg_loosing_days = filtered_trades[filtered_trades["Net PnL"] < 0]["Net PnL"].mean()
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            # Display metrics with custom formatting and colors
            with col1:
                st.metric(label="Gross Profits", value=f"${gross_profit:,.2f}")
            with col2:
                st.markdown(
                    f"""
                    <div style='display: flex; flex-direction: column; align-items: left;'>
                        <div style='font-size: 0.9em; color: #000000;margin-bottom: -10px;'>Gross Losses</div>
                        <div style='font-size: 2.3em;color: #D94758;'>${gross_losses:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            with col3:
                st.markdown(
                    f"""
                    <div style='display: flex; flex-direction: column; align-items: left;'>
                        <div style='font-size: 0.9em; color: #000000;margin-bottom: -10px;'>Total Commission Fees</div>
                        <div style='font-size: 2.3em;color: #D94758;'>${total_fees:,.2f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True)
            with col4:
                st.metric(label="Monthly Total P/L", value=f"${monthly_netPnL:,.2f}",
                          delta_color="inverse")

            col5, col6, col7, col8 = st.columns([1, 1, 1, 1])
            # Additional summary stats in a row with color and formatting
            with col5:
                st.metric("Total Trades", f"{nr_trades}")
            with col6:
                st.metric("Win Rate", f"{win_rate:.2f}%")
            with col7:
                st.metric("Avg. Winning Days", f"${avg_winning_days:,.2f}")
            # Display "Avg. Losing Days" in red in col8
            with col8:
                st.markdown(
                    f"""
                    <div style='display: flex; flex-direction: column; align-items: left;'>
                        <div style='font-size: 0.9em; color: #000000;margin-bottom: -10px;'>Avg. Losing Days</div>
                        <div style='font-size: 2.3em;color: #D94758;'>${avg_loosing_days:,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            # Left Panel Statistics Table
            with st.container():
                stats_data = {
                    "Metric": ["Volume", "Commission Fees", "Accumulated Long P/L",
                               "Accumulated Short P/L", "Net P/L",
                               "Long Trades", "Short Trades", 'Total Trades', 'Winner Long Trades',
                               'Winner Short Trades', 'Looser Long Trades', 'Looser Short Trades',
                               'Gross Profit', 'Gross Losses', "Win Rate", "Risk/Reward Ratio",
                               "Average Winning Days", 'Average Loosing Days'],
                    "Value": [
                        volume,  # Volume (2 decimals, no dollar sign)
                        f"${total_fees:,.2f}",  # Dollar with 2 decimals
                        f"${long_PnL:,.2f}",
                        f"${short_PnL:,.2f}",
                        f"${monthly_netPnL:,.2f}",
                        nr_long,  # Integer
                        nr_short,  # Integer
                        nr_trades,  # Integer
                        winner_long,  # Integer
                        winner_short,  # Integer
                        looser_long,  # Integer
                        looser_short,  # Integer
                        f"${gross_profit:,.2f}",  # Dollar with 2 decimals
                        f"${gross_losses:,.2f}",  # Dollar with 2 decimals
                        f"{win_rate:.2f}",  # 2 decimals, no dollar sign
                        f"{risk_reward:.2f}",  # 2 decimals, no dollar sign
                        f"${avg_winning_days:,.2f}",  # Dollar with 2 decimals
                        f"${avg_loosing_days:,.2f}"  # Dollar with 2 decimals
                    ]
                }

            stats_df = pd.DataFrame(stats_data)

            # General CSS to remove grid lines and reduce row spacing
            custom_table_style = """
                        <style>
                        /* Remove the index column header and row index */
                        thead tr th:first-child {display:none}
                        tbody th {display:none}
    
                        /* Remove all borders */
                        table {border-collapse: collapse;}
                        table td, table th {border: none !important; padding: 4px 0px;}
    
                        /* Set light grey background for the table */
                        table, th, td {
                            background-color: #f5f5f5;  /* Light grey background */
                        }
    
                        /* Optional: Adjust font size for a tighter look */
                        table td {font-size: 0.9rem;}
                        </style>
                        """

            # Apply CSS
            st.markdown(custom_table_style, unsafe_allow_html=True)

            # Display the new section with 3 columns
            col1, col2, col3, col4, col5 = st.columns([0.5, 0.2, 0.6, 0.2, 0.6])

            # Display statistics table in the first column
            with col1:
                st.markdown("**Statistics**")
                st.table(stats_df)

            with col3:
                # Prepare data for the waterfall chart
                accumulated_pl_data = {
                    "Type": ["Accumulated Long P/L", "Accumulated Short P/L", "Net P/L"],
                    "Value": [long_PnL, short_PnL, monthly_netPnL]
                }

                # Create the waterfall chart
                fig_waterfall = go.Figure(go.Waterfall(
                    name="Accumulated P/L",
                    orientation="v",
                    measure=["relative", "relative", "total"],
                    x=accumulated_pl_data["Type"],
                    y=accumulated_pl_data["Value"],
                    text=[f"${val:,.2f}" for val in accumulated_pl_data["Value"]],
                    textposition="outside",
                    connector=dict(line=dict(color="rgba(63, 63, 63, 0.5)")),
                    decreasing=dict(marker=dict(color="#D94758")),
                    increasing=dict(marker=dict(color="#6AB187")),
                    totals=dict(marker=dict(color="#B0B0B0"))
                ))

                # Update layout for a longer and thinner chart
                fig_waterfall.update_layout(
                    title="Accumulated P/L",
                    showlegend=False,
                    xaxis_title="Type",
                    yaxis_title="Value",
                    width=100,  # Set the chart width to make it longer
                    height=600,  # Set the chart height to make it thinner
                    margin=dict(l=50, r=50, t=50, b=50),
                    xaxis=dict(showgrid=False),  # Remove x-axis gridlines
                    yaxis=dict(showgrid=False)  # Remove y-axis gridlines            # Adjust margins
                )

                # Increase font size of labels for better visibility
                fig_waterfall.update_traces(textfont_size=12)  # Larger label font size

                # Display the chart
                st.plotly_chart(fig_waterfall, use_container_width=True)

            with col5:
                # % Trades Pie Chart
                trade_distribution_data = pd.DataFrame({
                    "Trade Type": ["Long Trades", "Short Trades"],
                    "Percentage": [67, 33]
                })
                fig_pie = px.pie(trade_distribution_data, names="Trade Type",
                                 values="Percentage",
                                 color="Trade Type",
                                 color_discrete_map={"Long Trades": "#6AB187",
                                                     "Short Trades": "#D94758"})
                fig_pie.update_layout(title="% Trades", showlegend=True, height=300)
                st.plotly_chart(fig_pie, use_container_width=True)

                # Bar chart
                data = {
                    "Trade Type": ["Long Trades", "Short Trades"],
                    "Winners": [winner_long, winner_short],
                    # Number of winning trades for Long and Short
                    "Losers": [looser_long,
                               looser_short], }  # Number of losing trades for Long and Short

                # Create a DataFrame
                df = pd.DataFrame(data)

                # Calculate the total trades for each type
                df["Total"] = df["Winners"] + df["Losers"]

                # Calculate the percentages
                df["Winners %"] = (df["Winners"] / df["Total"]) * 100
                df["Losers %"] = (df["Losers"] / df["Total"]) * 100

                # Create the stacked bar chart
                fig = go.Figure()

                # Winners bar
                fig.add_trace(go.Bar(
                    y=df["Trade Type"],
                    x=df["Winners %"],
                    name="Winners",
                    orientation='h',
                    marker=dict(color="#6AB187"),  # Green color
                    text=df["Winners"],
                    textposition='inside'))

                # Losers bar
                fig.add_trace(go.Bar(
                    y=df["Trade Type"],
                    x=df["Losers %"],
                    name="Losers",
                    orientation='h',
                    marker=dict(color="#D94758"),  # Red color
                    text=df["Losers"],
                    textposition='inside'))

                # Customize the layout
                fig.update_layout(
                    title="Winners & Losers",
                    barmode='stack',
                    xaxis=dict(title="Percentage", range=[0, 100], ticksuffix="%"),
                    yaxis=dict(title=""),
                    height=300,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5))

                # Display the chart in Streamlit
                st.plotly_chart(fig, use_container_width=True)

    elif reporting_period == "Annual":

        st.title("Annual Trading Report")

        year = st.sidebar.selectbox("Year", options=available_years, index=available_years.index(latest_year))

        # Filter the DataFrame based on the selected year and quarter
        filtered_trades = pd.DataFrame(tradelog[(tradelog["Date"].dt.year == year)])

        # Calculate each metric
        volume = filtered_trades["Contracts"].sum()
        total_fees = (filtered_trades["Total Broker Fees"] + filtered_trades[
            "Risk Management Fee"]).sum()

        # Directional statistics
        long_trades = filtered_trades[filtered_trades["Direction"] == "Long"]
        short_trades = filtered_trades[filtered_trades["Direction"] == "Short"]
        long_PnL = long_trades["Net PnL"].sum()
        short_PnL = short_trades["Net PnL"].sum()
        monthly_netPnL = filtered_trades["Net PnL"].sum()

        # Number of long and short trades
        nr_long = long_trades.shape[0]
        nr_short = short_trades.shape[0]
        nr_trades = filtered_trades.shape[0]

        # Winning and losing trades
        winner_long = long_trades[long_trades["Net PnL"] > 0].shape[0]
        winner_short = short_trades[short_trades["Net PnL"] > 0].shape[0]
        looser_long = long_trades[long_trades["Net PnL"] < 0].shape[0]
        looser_short = short_trades[short_trades["Net PnL"] < 0].shape[0]

        # Gross profit and gross losses
        gross_profit = filtered_trades[filtered_trades["PnL"] > 0]["PnL"].sum()
        gross_losses = filtered_trades[filtered_trades["PnL"] < 0]["PnL"].sum()

        # Win rate and risk/reward ratio
        win_rate = (filtered_trades[filtered_trades["Net PnL"] > 0].shape[
                        0] / nr_trades) * 100 if nr_trades > 0 else 0
        risk_reward = (filtered_trades[filtered_trades["Net PnL"] < 0].shape[0] /
                       filtered_trades[filtered_trades["Net PnL"] > 0].shape[0]) if \
            filtered_trades[filtered_trades["Net PnL"] > 0].shape[0] > 0 else None

        # Average winning and losing days
        avg_winning_days = filtered_trades[filtered_trades["Net PnL"] > 0]["Net PnL"].mean()
        avg_loosing_days = filtered_trades[filtered_trades["Net PnL"] < 0]["Net PnL"].mean()
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        # Display metrics with custom formatting and colors
        with col1:
            st.metric(label="Gross Profits", value=f"${gross_profit:,.2f}")
        with col2:
            st.markdown(
                f"""
                <div style='display: flex; flex-direction: column; align-items: left;'>
                    <div style='font-size: 0.9em; color: #000000;margin-bottom: -10px;'>Gross Losses</div>
                    <div style='font-size: 2.3em;color: #D94758;'>${gross_losses:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        with col3:
            st.markdown(
                f"""
                <div style='display: flex; flex-direction: column; align-items: left;'>
                    <div style='font-size: 0.9em; color: #000000;margin-bottom: -10px;'>Total Commission Fees</div>
                    <div style='font-size: 2.3em;color: #D94758;'>${total_fees:,.2f}</div>
                </div>
                """,
                unsafe_allow_html=True)
        with col4:
            st.metric(label="Monthly Total P/L", value=f"${monthly_netPnL:,.2f}",
                      delta_color="inverse")

        col5, col6, col7, col8 = st.columns([1, 1, 1, 1])
        # Additional summary stats in a row with color and formatting
        with col5:
            st.metric("Total Trades", f"{nr_trades}")
        with col6:
            st.metric("Win Rate", f"{win_rate:.2f}%")
        with col7:
            st.metric("Avg. Winning Days", f"${avg_winning_days:,.2f}")
        # Display "Avg. Losing Days" in red in col8
        with col8:
            st.markdown(
                f"""
                <div style='display: flex; flex-direction: column; align-items: left;'>
                    <div style='font-size: 0.9em; color: #000000;margin-bottom: -10px;'>Avg. Losing Days</div>
                    <div style='font-size: 2.3em;color: #D94758;'>${avg_loosing_days:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
        # Left Panel Statistics Table
        with st.container():
            stats_data = {
                "Metric": ["Volume", "Commission Fees", "Accumulated Long P/L",
                           "Accumulated Short P/L", "Net P/L",
                           "Long Trades", "Short Trades", 'Total Trades', 'Winner Long Trades',
                           'Winner Short Trades', 'Looser Long Trades', 'Looser Short Trades',
                           'Gross Profit', 'Gross Losses', "Win Rate", "Risk/Reward Ratio",
                           "Average Winning Days", 'Average Loosing Days'],
                "Value": [
                    volume,  # Volume (2 decimals, no dollar sign)
                    f"${total_fees:,.2f}",  # Dollar with 2 decimals
                    f"${long_PnL:,.2f}",
                    f"${short_PnL:,.2f}",
                    f"${monthly_netPnL:,.2f}",
                    nr_long,  # Integer
                    nr_short,  # Integer
                    nr_trades,  # Integer
                    winner_long,  # Integer
                    winner_short,  # Integer
                    looser_long,  # Integer
                    looser_short,  # Integer
                    f"${gross_profit:,.2f}",  # Dollar with 2 decimals
                    f"${gross_losses:,.2f}",  # Dollar with 2 decimals
                    f"{win_rate:.2f}",  # 2 decimals, no dollar sign
                    f"{risk_reward:.2f}",  # 2 decimals, no dollar sign
                    f"${avg_winning_days:,.2f}",  # Dollar with 2 decimals
                    f"${avg_loosing_days:,.2f}"  # Dollar with 2 decimals
                ]
            }

        stats_df = pd.DataFrame(stats_data)

        # General CSS to remove grid lines and reduce row spacing
        custom_table_style = """
                    <style>
                    /* Remove the index column header and row index */
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
    
                    /* Remove all borders */
                    table {border-collapse: collapse;}
                    table td, table th {border: none !important; padding: 4px 0px;}
    
                    /* Set light grey background for the table */
                    table, th, td {
                        background-color: #f5f5f5;  /* Light grey background */
                    }
    
                    /* Optional: Adjust font size for a tighter look */
                    table td {font-size: 0.9rem;}
                    </style>
                    """

        # Apply CSS
        st.markdown(custom_table_style, unsafe_allow_html=True)

        # Display the new section with 3 columns
        col1, col2, col3, col4, col5 = st.columns([0.5, 0.2, 0.6, 0.2, 0.6])

        # Display statistics table in the first column
        with col1:
            st.markdown("**Statistics**")
            st.table(stats_df)

        with col3:
            # Prepare data for the waterfall chart
            accumulated_pl_data = {
                "Type": ["Accumulated Long P/L", "Accumulated Short P/L", "Net P/L"],
                "Value": [long_PnL, short_PnL, monthly_netPnL]
            }

            # Create the waterfall chart
            fig_waterfall = go.Figure(go.Waterfall(
                name="Accumulated P/L",
                orientation="v",
                measure=["relative", "relative", "total"],
                x=accumulated_pl_data["Type"],
                y=accumulated_pl_data["Value"],
                text=[f"${val:,.2f}" for val in accumulated_pl_data["Value"]],
                textposition="outside",
                connector=dict(line=dict(color="rgba(63, 63, 63, 0.5)")),
                decreasing=dict(marker=dict(color="#D94758")),
                increasing=dict(marker=dict(color="#6AB187")),
                totals=dict(marker=dict(color="#B0B0B0"))
            ))

            # Update layout for a longer and thinner chart
            fig_waterfall.update_layout(
                title="Accumulated P/L",
                showlegend=False,
                xaxis_title="Type",
                yaxis_title="Value",
                width=100,  # Set the chart width to make it longer
                height=600,  # Set the chart height to make it thinner
                margin=dict(l=50, r=50, t=50, b=50),
                xaxis=dict(showgrid=False),  # Remove x-axis gridlines
                yaxis=dict(showgrid=False)  # Remove y-axis gridlines            # Adjust margins
            )

            # Increase font size of labels for better visibility
            fig_waterfall.update_traces(textfont_size=12)  # Larger label font size

            # Display the chart
            st.plotly_chart(fig_waterfall, use_container_width=True)

        with col5:
            # % Trades Pie Chart
            trade_distribution_data = pd.DataFrame({
                "Trade Type": ["Long Trades", "Short Trades"],
                "Percentage": [67, 33]
            })
            fig_pie = px.pie(trade_distribution_data, names="Trade Type",
                             values="Percentage",
                             color="Trade Type",
                             color_discrete_map={"Long Trades": "#6AB187",
                                                 "Short Trades": "#D94758"})
            fig_pie.update_layout(title="% Trades", showlegend=True, height=300)
            st.plotly_chart(fig_pie, use_container_width=True)

            # Bar chart
            data = {
                "Trade Type": ["Long Trades", "Short Trades"],
                "Winners": [winner_long, winner_short],
                # Number of winning trades for Long and Short
                "Losers": [looser_long,
                           looser_short], }  # Number of losing trades for Long and Short

            # Create a DataFrame
            df = pd.DataFrame(data)

            # Calculate the total trades for each type
            df["Total"] = df["Winners"] + df["Losers"]

            # Calculate the percentages
            df["Winners %"] = (df["Winners"] / df["Total"]) * 100
            df["Losers %"] = (df["Losers"] / df["Total"]) * 100

            # Create the stacked bar chart
            fig = go.Figure()

            # Winners bar
            fig.add_trace(go.Bar(
                y=df["Trade Type"],
                x=df["Winners %"],
                name="Winners",
                orientation='h',
                marker=dict(color="#6AB187"),  # Green color
                text=df["Winners"],
                textposition='inside'))

            # Losers bar
            fig.add_trace(go.Bar(
                y=df["Trade Type"],
                x=df["Losers %"],
                name="Losers",
                orientation='h',
                marker=dict(color="#D94758"),  # Red color
                text=df["Losers"],
                textposition='inside'))

            # Customize the layout
            fig.update_layout(
                title="Winners & Losers",
                barmode='stack',
                xaxis=dict(title="Percentage", range=[0, 100], ticksuffix="%"),
                yaxis=dict(title=""),
                height=300,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5))

            # Display the chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please upload your tradelog to proceed.")
    st.stop()




