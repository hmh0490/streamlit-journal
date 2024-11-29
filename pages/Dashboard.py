# Dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from navigation import make_sidebar
import requests
from io import StringIO

def load_data():
    url = 'https://raw.githubusercontent.com/hmh0490/streamlit-journal/refs/heads/master/tradelog_updated.csv'
    response = requests.get(url)
    if response.status_code == 200:
        return pd.read_csv(StringIO(response.text))
    else:
        st.error("Failed to load data from GitHub.")
        return None


# Set the page configuration to wide layout
st.set_page_config(page_title="Trading Dashboard", layout="wide")

make_sidebar()

def calculate_trade_metrics(trades, ref_metrics=None):
    metrics = {}
    remarks = {}

    # Calculate all metrics
    metrics["Win rate %"] = (trades[trades['Net PnL'] > 0].shape[0] / trades.shape[0] * 100) if \
    trades.shape[0] > 0 else 0
    metrics["Largest Profit"] = trades['Net PnL'].max() if not trades['Net PnL'].empty else 0
    metrics["Largest Loss"] = trades['Net PnL'].min() if not trades['Net PnL'].empty else 0
    metrics["Largest Win %"] = trades['Return %'].max() if 'Return %' in trades else 0
    metrics["Largest Loss %"] = trades['Return %'].min() if 'Return %' in trades else 0
    metrics["Avg. Profit per trade"] = trades[trades['Net PnL'] > 0]['Net PnL'].mean() if trades[
        'Net PnL'].gt(0).any() else 0
    metrics["Avg. Loss per trade"] = trades[trades['Net PnL'] < 0]['Net PnL'].mean() if trades[
        'Net PnL'].lt(0).any() else 0
    metrics["Profit Factor"] = (trades[trades['Net PnL'] > 0]['Net PnL'].sum() / abs(
        trades[trades['Net PnL'] < 0]['Net PnL'].sum())) if trades['Net PnL'].lt(0).any() else 0
    metrics["Expectancy per trade"] = trades['Net PnL'].mean() if not trades.empty else 0

    # If reference metrics are provided, calculate remarks
    if ref_metrics is not None:
        for key in metrics:
            if key in ref_metrics:
                remarks[key] = "Improving" if metrics[key] >= ref_metrics[key] else "Declining"

    return metrics, remarks

tab1, tab2, tab3, tab4 = st.tabs(['Overall Summary', 'Performance', 'Analytics', 'Evaluation'])

file_path = os.path.join(os.getcwd(), "tradelog_updated.csv")

# Function to load the tradelog from disk if it exists
def load_tradelog():
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return None

# Check if trade log data already exists in session_state
if "tradelog" not in st.session_state:
    st.session_state["tradelog"] = load_data()  # Load from disk if available

# Retrieve settings from session_state
risk_management_fee = st.session_state.get('risk_management_fee')
ticker_data = st.session_state.get('ticker_data', pd.DataFrame())
initial_balance = st.session_state.get('initial_balance')
withdrawals = st.session_state.get('withdrawals')

# Ensure tradelog data is available
if "tradelog" in st.session_state and st.session_state["tradelog"] is not None:
    tradelog = st.session_state["tradelog"]
    tradelog["Date"] = pd.to_datetime(tradelog["Date"])

    # Calculation of metrics
    long_pnl = tradelog[tradelog["Direction"] == "Long"]["Net PnL"].sum()
    short_pnl = tradelog[tradelog["Direction"] == "Short"]["Net PnL"].sum()
    total_pnl = long_pnl + short_pnl
    long_pnl_percentage = (long_pnl / total_pnl) * 100 if total_pnl != 0 else 0
    short_pnl_percentage = (short_pnl / total_pnl) * 100 if total_pnl != 0 else 0
    total_pnl_percentage = long_pnl_percentage + short_pnl_percentage  # should equal 100%
    total_profit = tradelog[tradelog["Net PnL"] > 0]["Net PnL"].sum()
    total_loss = tradelog[tradelog["Net PnL"] < 0]["Net PnL"].sum()

    with tab1:

        # Layout: Summary on the left
        col1, col2, col3 = st.columns([0.8, 2, 1])

        with col1:

            #### Aggregate Net Profit and Average Performance (%) by Setup ###
            performance_summary = tradelog.groupby("Setup").agg(
                Net_Profit=("Net PnL", "sum"),
                Average_Performance=("Performance %", "mean")).reset_index()

            # Sort to get Top 3 and Bottom 3 setups
            top_3_setups = performance_summary.nlargest(3, 'Net_Profit')
            bottom_3_setups = performance_summary.nsmallest(3, 'Net_Profit')

            # Calculate Grand Total
            grand_total = pd.DataFrame({
                "Setup": ["Grand Total"],
                "Net_Profit": [performance_summary["Net_Profit"].sum()],
                "Average_Performance": [
                    performance_summary["Average_Performance"].mean()]})

            # Apply custom CSS for table styling
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
    
                        /* Optional: Adjust font size and text alignment */
                        table td {font-size: 0.9rem; centered: right; padding-right: 8px;}
                        table th {text-align: right; font-weight: bold;}
                        </style>
                        """

            # Apply CSS
            st.markdown(custom_table_style, unsafe_allow_html=True)

            # Format Top 3 Setups
            top_3_formatted = pd.concat([top_3_setups, grand_total], ignore_index=True)

            top_3_formatted['Net_Profit'] = top_3_formatted['Net_Profit'].apply(lambda x: f"${x:,.2f}")
            top_3_formatted['Average_Performance'] = top_3_formatted['Average_Performance'].apply(lambda x: f"{x:.2f}%")
            top_3_formatted.rename(columns={
                "Net_Profit": "Net Profit",
                "Average_Performance": "Avg Performance %"}, inplace=True)

            # Format Bottom 3 Setups
            bottom_3_formatted = pd.concat([bottom_3_setups, grand_total], ignore_index=True)
            bottom_3_formatted['Net_Profit'] = bottom_3_formatted['Net_Profit'].apply(lambda x: f"${x:,.2f}")
            bottom_3_formatted['Average_Performance'] = bottom_3_formatted['Average_Performance'].apply(
                lambda x: f"{x:.2f}%")
            bottom_3_formatted.rename(columns={
                "Net_Profit": "Net Profit",
                "Average_Performance": "Avg Performance %"}, inplace=True)

            # Display Top 3 Setups
            st.markdown("### Top 3 Setups")
            st.table(top_3_formatted)

            # Display Bottom 3 Setups
            st.markdown("### Bottom 3 Setups")
            st.table(bottom_3_formatted)

            ### Create the stacked bar chart ###
            fig = go.Figure()

            # Add the Total Profit bar
            fig.add_trace(go.Bar(
                x=[total_profit],  # Use the profit value
                y=["Total"],  # Placeholder for y-axis (single bar)
                orientation='h',
                marker=dict(color='#6AB187'),  # Green color for profit
                text=f"${total_profit:,.2f}",  # Display the profit amount
                textposition='inside',  # Position text inside the bar
                textfont=dict(color="white", size=14)
            ))

            # Add the Total Loss bar (make sure to use absolute value for width)
            fig.add_trace(go.Bar(
                x=[abs(total_loss)],  # Use the absolute value of loss
                y=["Total"],  # Same y-axis placeholder
                orientation='h',
                marker=dict(color='#D94758'),  # Red color for loss
                text=f"${total_loss:,.2f}",  # Display the loss amount
                textposition='inside',  # Position text inside the bar
                textfont=dict(color="white", size=14)
            ))

            # Update layout for appearance
            fig.update_layout(
                barmode='stack',
                title={
                    'text': "Total Profit vs Total Loss",
                    'y': 1,  # Adjust the vertical position (increase to move it higher)
                    'x': 0.25,  # Adjust the horizontal position (increase to move it to the right)
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 14}},
                xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
                margin=dict(t=20, b=0, l=0, r=0),  # Increase top margin for title space
                height=50,
                showlegend=False)

            # Display the chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)




            # Data preparation
            performance_data = {
                "Category": ["Long Trades", "Short Trades"],
                "Net PnL": [long_pnl, short_pnl],
                "Percentage": [long_pnl_percentage, short_pnl_percentage]}

            performance_df = pd.DataFrame(performance_data)

            ### Create a pie chart using Plotly ###
            fig_pie = px.pie(
                performance_df,
                names="Category",
                values="Net PnL",
                color="Category",
                color_discrete_map={"Long Trades": "#6AB187", "Short Trades": "#D94758"},)

            fig_pie.update_traces(
                texttemplate='$%{value:,.2f} (%{percent:.0%})',
                hovertemplate='$%{value:,.2f} (%{percent:.0%})',
                textposition='inside',
                textfont_size=14,)

            # Customize the chart layout
            fig_pie.update_traces(
                textinfo='percent+label',
                hovertemplate='%{label}: %{value:$,.2f} <br>(%{percent:.2f})',
                textposition='inside')

            # Adjust the size of the pie chart
            fig_pie.update_layout(
                height=400,  # Set the height to a smaller value
                width=400,  # Set the width to a smaller value
                margin=dict(l=15, r=15, t=15, b=15),
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.1))

            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # Define the percentage intervals and initialize the count
            intervals = [
                "-20% below", "-18% to -16%", "-16% to -14%", "-14% to -12%",
                "-12% to -10%", "-10% to -8%", "-8% to -6%", "-6% to -4%", "-4% to -2%",
                "-2% to 0%",
                "0% to 2%", "2% to 4%", "4% to 6%", "6% to 8%", "8% to 10%",
                "10% to 12%", "12% to 14%", "14% to 16%", "16% to 18%", "18% to 20%", "20% above"]

            # Set up the interval boundaries
            interval_bounds = [
                (-float("inf"), -20), (-18, -16), (-16, -14), (-14, -12), (-12, -10),
                (-10, -8), (-8, -6), (-6, -4), (-4, -2), (-2, 0),
                (0, 2), (2, 4), (4, 6), (6, 8), (8, 10), (10, 12),
                (12, 14), (14, 16), (16, 18), (18, 20), (20, float("inf"))]

            ### Wins and Losses ###
            # Calculate trade counts for each interval
            trade_counts = []
            for lower, upper in interval_bounds:
                count = tradelog[(tradelog["Return %"] >= lower) & (
                        tradelog["Return %"] < upper)].shape[0]
                trade_counts.append(count)

            # Create a DataFrame for plotting
            df = pd.DataFrame({
                "Profit %": intervals,
                "Trades": trade_counts})

            # Define colors for positive and negative intervals
            df["Color"] = df["Profit %"].apply(
                lambda x: "#D94758" if "below" in x or x.startswith("-") else "#6AB187")

            # Create the bar chart with custom colors
            fig_wins_losses = px.bar(
                df,
                x="Profit %",
                y="Trades",
                title="Wins & Losses",
                color="Color",
                color_discrete_map="identity", )

            # Update layout for consistent styling
            fig_wins_losses.update_layout(
                xaxis_title="",  # Remove x-axis title
                yaxis_title="NUMBER OF TRADES",
                title_x=0.5,  # Center the title
                showlegend=False,  # Remove legend for colors
                plot_bgcolor="rgba(0,0,0,0)", )  # Transparent background

            # Add data labels for average Net PnL
            fig_wins_losses.update_traces(
                text=df["Trades"],
                textposition="outside", )

            ### Profit and Loss ###
            trade_averages = []
            for lower, upper in interval_bounds:
                # Filter trades within the percentage interval and calculate the average Net PnL
                avg_pnl = tradelog[(tradelog["Return %"] >= lower) &
                                   (tradelog["Return %"] < upper)][
                    "Net PnL"].mean()
                # Append the result to the list (use 0 if there are no trades in the interval)
                trade_averages.append(avg_pnl if not pd.isna(avg_pnl) else 0)

            df = pd.DataFrame({
                "Profit %": intervals,
                "Average Net PnL": trade_averages
            })

            # Define colors for positive and negative intervals
            df["Color"] = df["Profit %"].apply(
                lambda x: "#D94758" if "below" in x or x.startswith(
                    "-") else "#6AB187")

            # Create the bar chart with average Net PnL and data labels
            fig_avg_pnl = px.bar(
                df,
                x="Profit %",
                y="Average Net PnL",
                title="Average Net PnL by Profit Percentage Interval",
                color="Color",
                color_discrete_map="identity",
                # Use the colors defined in the "Color" column
            )

            # Update layout for consistent styling with Streamlit
            fig_avg_pnl.update_layout(
                xaxis_title="",  # Remove x-axis title
                yaxis_title="AVERAGE NET PnL",
                title_x=0.5,  # Center the title
                showlegend=False,  # Remove legend for colors
                plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
            )

            # Add data labels for average Net PnL
            fig_avg_pnl.update_traces(
                text=df["Average Net PnL"].round(2),
                # Data labels showing average Net PnL
                textposition="outside", )  # Position labels outside the bars

            # Add a toggle switch (using st.radio) for selecting between the two charts
            chart_option = st.radio(
                "", ["Wins & Losses", "Average Profit & Loss"],
                horizontal=True,
                index=0)

            # Conditional display based on the selected option
            if chart_option == "Wins & Losses":
                # Display the Wins & Losses chart
                st.subheader("Wins & Losses")
                st.plotly_chart(fig_wins_losses, use_container_width=True)
            elif chart_option == "Average Profit & Loss":
                # Display the Average Profit & Loss chart
                st.subheader("Average Profit & Loss")
                st.plotly_chart(fig_avg_pnl, use_container_width=True)

        with col3:
            win_trades = round(tradelog[tradelog["Net PnL"] > 0].shape[0], 2)
            loss_trades = round(tradelog[tradelog["Net PnL"] <= 0].shape[0], 2)
            average_profit = round(tradelog[tradelog["Net PnL"] > 0]["Net PnL"].mean(), 2)
            average_loss = round(tradelog[tradelog["Net PnL"] < 0]["Net PnL"].mean(), 2)
            average_win = round(tradelog[tradelog["Return %"] > 0]["Return %"].mean(), 2)
            average_loss_percentage = round(tradelog[tradelog["Return %"] < 0]["Return %"].mean(), 2)
            win_loss_ratio = round(win_trades / loss_trades, 2) if loss_trades > 0 else float("inf")
            pl_ratio = round(average_profit / abs(average_loss), 2) if average_loss != 0 else float("inf")
            total_trades = win_trades + loss_trades
            win_rate = round((win_trades / total_trades), 2) * 100 if total_trades > 0 else 0
            loss_rate = round(100 - win_rate, 2)

            # Calculate Profit Factor
            profit_factor = round((average_profit * (win_rate / 100)) / (
                        abs(average_loss) * (loss_rate / 100)),
                                  2) if loss_rate > 0 else float("inf")

            # Calculate Expectancy
            expectancy = round((average_profit * (win_rate / 100)) - \
                         (abs(average_loss) * (loss_rate / 100)),2)

            # Define values for the donut chart
            win_rate_value = win_rate  # Use calculated win rate
            loss_rate_value = 100 - win_rate  # Complement to make a full circle

            # Create the donut chart
            fig = go.Figure(go.Pie(
                labels=['Win Rate', 'Loss Rate'],
                values=[win_rate_value, loss_rate_value],
                hole=0.8,
                # Increase the hole size to make the chart appear smaller
                marker=dict(colors=['#6AB187', '#D94758']),
                # Green for wins, red for losses
                textinfo='none')) # Hide text inside the segments

            # Add a centered annotation for the win rate percentage
            fig.add_annotation(
                text=f"{win_rate_value:.2f}%",  # Format to 2 decimal places
                x=0.5, y=0.5,  # Center of the chart
                font=dict(size=18, color="black"),
                # Adjust font size and color for smaller chart
                showarrow=False)

            # Update layout for the chart title and appearance
            fig.update_layout(
                title="Win Rate",
                title_x=0.4,  # Center the title
                margin=dict(t=60, b=60, l=60, r=60),
                # Add padding around the chart to make it smaller
                showlegend=False,
                height=200,  # Set a fixed height for the chart to control its size
                width=200) # Set a fixed width to control diameter

            # Display the chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)

            # Create two nested columns within col3
            col_left, col_right = st.columns(2)

            # Place the metrics in alternating columns

            with col_left:
                st.markdown("#### Trade Statistics")
                st.markdown(f"Win Trades: **{win_trades}**")
                st.markdown(f"Average Profit: **${average_profit:,.2f}**")
                st.markdown(f"Average Win: **{average_win:.2f}%**")
                st.markdown(f"Win/Loss Ratio: **{win_loss_ratio:.2f}**")
                st.markdown(f"Profit Factor: **{profit_factor:.2f}**")

            with col_right:
                st.markdown("###")
                st.markdown(f"Loss Trades: **{loss_trades}**")

                # Always display Average Loss in red
                st.markdown(
                    f"Average Loss: <span style='color:#D94758;'>**${average_loss:,.2f}**</span>",
                    unsafe_allow_html=True
                )

                # Always display Average Loss Percentage in red
                st.markdown(
                    f"Average Loss %: <span style='color:#D94758;'>**{average_loss_percentage:.2f}%**</span>",
                    unsafe_allow_html=True
                )

                st.markdown(f"P/L Ratio: **{pl_ratio:.2f}**")
                st.markdown(f"Expectancy: **{expectancy:.2f}**")

    with tab2:
        ### Calculate Performance metrics ###
        col1, col2, col3 = st.columns([0.8, 2, 1])

        # Current date for reference
        current_date = datetime.now()
        current_year = current_date.year
        previous_year = current_year - 1

        # Filter data for the current year and previous year
        current_year_data = tradelog[tradelog["Date"].dt.year == current_year]
        previous_year_data = tradelog[
            tradelog["Date"].dt.year == previous_year]

        # This Month
        this_month_data = current_year_data[
            current_year_data["Date"].dt.month == current_date.month]
        this_month = this_month_data["Net PnL"].sum()

        # 1st Quarter (January to March)
        first_quarter_data = current_year_data[
            current_year_data["Date"].dt.month.isin([1, 2, 3])]
        first_quarter = first_quarter_data["Net PnL"].sum()

        # 2nd Quarter (April to June)
        second_quarter_data = current_year_data[
            current_year_data["Date"].dt.month.isin([4, 5, 6])]
        second_quarter = second_quarter_data["Net PnL"].sum()

        # 3rd Quarter (July to September)
        third_quarter_data = current_year_data[
            current_year_data["Date"].dt.month.isin([7, 8, 9])]
        third_quarter = third_quarter_data["Net PnL"].sum()

        # 4th Quarter (October to December)
        fourth_quarter_data = current_year_data[
            current_year_data["Date"].dt.month.isin([10, 11, 12])]
        fourth_quarter = fourth_quarter_data["Net PnL"].sum()

        # Year To Date (YTD) - from January 1 to the current date
        year_to_date = \
            current_year_data[current_year_data["Date"] <= current_date][
                "Net PnL"].sum()

        # Previous YTD - from January 1 to the same date last year
        previous_ytd = previous_year_data[
            previous_year_data["Date"] <= current_date.replace(
                year=previous_year)]["Net PnL"].sum()


        # Function to style numbers based on value
        def format_currency(value):
            color = "#6AB187" if value >= 0 else "#D94758"  # Green for positive, red for negative
            return f'<span style="color:{color}">${value:,.2f}</span>'


        with col1:
            # # Apply custom CSS for table styling
            custom_table_style = """
            <style>
            /* Remove table borders and row lines */
            table {
                border-collapse: collapse;
                border: none !important;
            }

            /* Remove borders around table cells */
            table tr, table td, table th {
                border: none !important;
                padding: 6px 0 !important;
            }

            /* Set light grey background for the table */
            table, th, td {
                background-color: #ffffff; /* Light grey background */
            }

            /* Optional: Adjust font size and text alignment */
            table td {font-size: 0.9rem; text-align: left; padding-left: 8px;}
            table th {text-align: left; font-weight: bold;}
            </style>
            """

            # Define the performance metrics in an HTML table format with a title
            performance_table = f"""
            <h3 style='margin-bottom: 10px;'>Quarterly Performance</h3>
            <table style='width: 100%;'>
                <tr><td>This Month:</td><td>{format_currency(this_month)}</td></tr>
                <tr><td>1st Quarter:</td><td>{format_currency(first_quarter)}</td></tr>
                <tr><td>2nd Quarter:</td><td>{format_currency(second_quarter)}</td></tr>
                <tr><td>3rd Quarter:</td><td>{format_currency(third_quarter)}</td></tr>
                <tr><td>4th Quarter:</td><td>{format_currency(fourth_quarter)}</td></tr>
                <tr><td>Year To Date (YTD):</td><td>{format_currency(year_to_date)}</td></tr>
                <tr><td>Previous YTD:</td><td>{format_currency(previous_ytd)}</td></tr>
            </table>
            """

            # Apply CSS and display the table with the title
            st.markdown(custom_table_style + performance_table, unsafe_allow_html=True)

        with col2:
            ### Display the 20 MA chart in Streamlit
            # Options for filtering number of trades to display
            options = [20, 50, 100, 200, 500, 'All']
            selected_trades = st.radio("Last Number of Trades", options,
                                       index=options.index('All'),
                                       horizontal=True)

            tradelog_filtered = tradelog.iloc[20:]
            # Filter based on selected number of trades
            if selected_trades != 'All':
                tradelog_filtered = tradelog_filtered.tail(selected_trades)
            else:
                tradelog_filtered = tradelog_filtered

            # Extract Performance data
            df = tradelog_filtered[["Date", "Cumulative Performance"]].copy()
            df["Metric"] = "Performance"

            # Extract 20 MA data and rename it to match the Performance column
            df2 = tradelog_filtered[["Date", "20 MA"]].rename(
                columns={"20 MA": "Cumulative Performance"}).copy()
            df2["Metric"] = "20 MA (Performance)"

            # Combine both DataFrames
            combined_data = pd.concat([df, df2])

            fig = px.line(
                combined_data,
                x="Date",
                y="Cumulative Performance",
                color="Metric",
                title="Performance Curve",
                line_shape="spline",
                color_discrete_map={
                    "Performance": "#6AB187",  # Green for Performance
                    "20 MA (Performance)": "#D94758",}  # Red for 20 MA
            )

            # Customize layout
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Cumulative Net PnL",
                plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
                legend=dict(
                    orientation="h",  # Horizontal legend
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            # Display chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)

        with col3:
            # Filter the data to include only the last 2 months
            two_months_ago = pd.Timestamp.now() - pd.DateOffset(months=2)
            filtered_tradelog = tradelog[tradelog["Date"] >= two_months_ago]

            # Set the Date as the index temporarily for resampling
            filtered_tradelog = filtered_tradelog.set_index("Date")

            # Resample data by week and calculate the sum of Net PnL for each week
            weekly_performance = filtered_tradelog["Net PnL"].resample("W").sum().reset_index()

            # Create the line chart using Plotly
            fig = px.line(
                weekly_performance,
                x="Date",
                y="Net PnL",
                title="Weekly Performance Curve",
                markers=True,
                labels={"Date": "Week", "Net PnL": "Profit/Loss ($)"},
                line_shape='spline'
            )

            # Update layout for better aesthetics
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Net PnL ($)",
                plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
                height=300,  # Adjust height
                margin=dict(t=40, b=30, l=30, r=30)
            )

            # Display the chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)

    with tab3:

        col1, col2, col3 = st.columns([0.5, 0.7, 0.5])

        with col2:
            # Calculate metrics for all trades and last 20 trades
            all_trades_metrics, all_trades_remarks = calculate_trade_metrics(tradelog)
            last_20_trades_metrics, last_20_trades_remarks = calculate_trade_metrics(
                tradelog.tail(20), all_trades_metrics)

            # Create a DataFrame for summary with updated formatting
            summary_data = {
                "STATISTICS": list(all_trades_metrics.keys()),
                "ALL TRADES": [
                    f"${v:,.2f}" if any(
                        x in k for x in ["Profit", "Loss", "Expectancy"]) and "%" not in k else
                    f"{v:.2f}%" if "%" in k else
                    f"{v:.2f}" if "Factor" in k or "Risk Ratio" in k else
                    f"${v:,.2f}" if "Average Profit" in k else
                    f"{v}" for k, v in all_trades_metrics.items()
                ],
                "LAST 20 TRADES": [
                    f"${v:,.2f}" if any(
                        x in k for x in ["Profit", "Loss", "Expectancy"]) and "%" not in k else
                    f"{v:.2f}%" if "%" in k else
                    f"{v:.2f}" if "Factor" in k or "Risk Ratio" in k else
                    f"${v:,.2f}" if "Average Profit" in k else
                    f"{v}" for k, v in last_20_trades_metrics.items()
                ],
                "REMARKS": [last_20_trades_remarks.get(k, "") for k in all_trades_metrics.keys()]
            }

            summary_df = pd.DataFrame(summary_data)


            # Function to format the "REMARKS" column with colors
            def format_remarks(remark):
                if remark == "Improving":
                    return f"<span style='color:#6AB187; font-weight:bold'>{remark}</span>"
                elif remark == "Declining":
                    return f"<span style='color:#D94758; font-weight:bold'>{remark}</span>"
                return remark


            # Apply formatting to the "REMARKS" column
            summary_df["REMARKS"] = summary_df["REMARKS"].apply(format_remarks)

            # Custom CSS for table styling
            custom_table_style = """
              <style>
                  table {
                      border-collapse: collapse;
                      width: 100%;
                      margin-top: 20px;
                  }
                  table th {
                      text-align: left;
                      font-weight: bold;
                      padding-right: 20px;
                      font-size: 1rem;
                      border-bottom: 2px solid #333;
                  }
                  table td {
                      padding: 8px;
                      border: none !important;
                      text-align: left;
                  }
                  table tr:nth-child(odd) {
                      background-color: #f5f5f5;
                  }
                  table tr:nth-child(even) {
                      background-color: #ffffff;
                  }
              </style>
              """

            # Apply the custom CSS
            st.markdown(custom_table_style, unsafe_allow_html=True)

            # Display the data in four columns using Streamlit
            with st.container():
                col1, col2, col3, col4 = st.columns(4)

                # Column 1: "STATISTICS"
                with col1:
                    st.markdown("<h6 style='text-align: left;'>STATISTICS</h6>",
                                unsafe_allow_html=True)
                    for stat in summary_df["STATISTICS"]:
                        st.markdown(f"**{stat}**")

                # Column 2: "ALL TRADES"
                with col2:
                    st.markdown("<h6 style='text-align: left;'>ALL TRADES</h6>",
                                unsafe_allow_html=True)
                    for value in summary_df["ALL TRADES"]:
                        st.markdown(f"{value}")

                # Column 3: "LAST 20 TRADES"
                with col3:
                    st.markdown("<h6 style='text-align: left;'>LAST 20 TRADES</h6>",
                                unsafe_allow_html=True)
                    for value in summary_df["LAST 20 TRADES"]:
                        st.markdown(f"{value}")

                # Column 4: "REMARKS"
                with col4:
                    st.markdown("<h6 style='text-align: left;'>REMARKS</h6>",
                                unsafe_allow_html=True)
                    for remark in summary_df["REMARKS"]:
                        st.markdown(f"{remark}", unsafe_allow_html=True)

            ### Calculate Win Rate for each setup ###
            win_rate_data = tradelog.groupby("Setup").apply(
                lambda x: (x["Net PnL"] > 0).mean() * 100).reset_index()
            win_rate_data.columns = ["Setup", "Win Rate (%)"]

            # Calculate Unprofitable % as (100% - Win Rate)
            win_rate_data["Unprofitable (%)"] = 100 - win_rate_data["Win Rate (%)"]

            # Create the stacked bar chart
            fig = go.Figure()

            # Add Unprofitable (%) bars (bottom red segment)
            fig.add_trace(go.Bar(
                x=win_rate_data["Setup"],
                y=win_rate_data["Unprofitable (%)"],
                name="Unprofitable (%)",
                marker=dict(color="#D94758"),  # Red for unprofitable
                text=win_rate_data["Unprofitable (%)"].round(0).astype(int).astype(
                    str) + "%",  # Add percentage labels
                textposition='inside'
            ))

            # Add Win Rate (Profitable %) bars (top green segment)
            fig.add_trace(go.Bar(
                x=win_rate_data["Setup"],
                y=win_rate_data["Win Rate (%)"],
                name="Profitable (%)",
                marker=dict(color="#6AB187"),  # Green for profitable
                text=win_rate_data["Win Rate (%)"].round(0).astype(int).astype(
                    str) + "%",  # Add percentage labels
                textposition='inside'
            ))

            # Add Win Rate line with a dash and show in legend
            fig.add_trace(go.Scatter(
                x=win_rate_data["Setup"],
                y=win_rate_data["Win Rate (%)"],
                mode='lines+text',
                name="Win Rate (%)",  # This name will appear in the legend
                line=dict(color="black", dash="dash"),
                text=win_rate_data["Win Rate (%)"].round(0).astype(int).astype(
                    str) + "%",  # Add win rate text on top
                textposition="top center",
                showlegend=True  # Ensure the Win Rate line appears in the legend
            ))

            # Update layout for stacked bars
            fig.update_layout(
                barmode='stack',  # Stack the bars on top of each other
                title="Win Rate by Setup",
                xaxis=dict(title="Setup"),
                yaxis=dict(title="Percentage", range=[0, 100]),
                # y-axis from 0 to 100%
                plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                )
            )

            # Display the chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        col1, col2, col3 = st.columns([0.4, 1.2, 0.4])

        # Define the scoring system for Entry/Exit
        score_mapping = {
            "As Planned": 1,
            "Too Early": -1,
            "Too Late": -1,
            "Not In Plan": -1,
            "Broke Rules": -1,
            "Stop to tight": -1,
            "First 30 min": -1,
            "Didn't Check News": -1
        }
        # Add a new column for scores based on the Entry/Exit column
        tradelog["Score_Entry/Exit"] = tradelog["Entry/Exit"].map(score_mapping)

        # Group by Entry/Exit category and calculate the sum of scores
        summary_table = tradelog.groupby("Entry/Exit")["Score_Entry/Exit"].sum().reset_index()

        # Sort by score for better visualization
        summary_table = summary_table.sort_values("Score_Entry/Exit", ascending=False)

        # Define the scoring system for Emotion
        emotion_score_mapping = {
            "By The Rules": 1,
            "Fear": -1,
            "Hope": -1,
            "Greed": -1,
            "Bored": -1,
            "FOMO": -1,
            "Tired": -1,
            "Distracted": -1,
        }

        # Add a new column for scores based on the Entry/Exit column
        tradelog["Score_Emotion"] = tradelog["Emotion"].map(emotion_score_mapping)

        # Group by Entry/Exit category and calculate the sum of scores
        summary_table2 = tradelog.groupby("Emotion")["Score_Emotion"].sum().reset_index()

        # Sort by score for better visualization
        summary_table2 = summary_table2.sort_values("Score_Emotion", ascending=False)

        with col2:
            col1, col2 = st.columns([1, 1])
            with col1:
                # Create a bar chart for Entry/Exit
                fig = px.bar(
                    summary_table,
                    x="Score_Entry/Exit",
                    y="Entry/Exit",
                    orientation="h",
                    title="Entry/Exit",
                    color="Score_Entry/Exit",
                    color_continuous_scale=["#D94758", "#6AB187"],
                    # Red for negative, green for positive
                )

                # Update layout for better appearance
                fig.update_layout(
                    xaxis_title="Score",
                    yaxis_title="Entry/Exit",
                    title_x=0.5,  # Center the title
                    plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
                )

                # Display the chart
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Create a bar chart for Emotion
                fig = px.bar(
                    summary_table2,
                    x="Score_Emotion",
                    y="Emotion",
                    orientation="h",
                    title="Emotion",
                    color="Score_Emotion",
                    color_continuous_scale=["#D94758", "#6AB187"],
                    # Red for negative, green for positive
                )

                # Update layout for better appearance
                fig.update_layout(
                    xaxis_title="Score",
                    yaxis_title="Emotion",
                    title_x=0.5,  # Center the title
                    plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
                )

                # Display the chart
                st.plotly_chart(fig, use_container_width=True)

            #### Calculate the Trade Evaluation Score as the cumulative sum of scores
            tradelog["Trade Evaluation Score"] = (tradelog["Score_Entry/Exit"] + tradelog["Score_Emotion"]).cumsum()

            # Select the last 20 trades
            latest_20_trades = tradelog.tail(20)

            # Create a line chart for the Trade Evaluation Curve
            fig = px.line(
                latest_20_trades,
                x="Trade ID",
                y="Trade Evaluation Score",
                title="Trade Evaluation Curve",
                markers=True,
                labels={"Trade ID": "Last 20 Trades",
                        "Trade Evaluation Score": "Cumulative Evaluation Score"},
                line_shape='spline'  # Apply spline smoothing
            )

            # Update layout for aesthetics
            fig.update_layout(
                xaxis_title="Last 20 Trades",
                yaxis_title="Cumulative Evaluation Score",
                title_x=0.5,  # Center the title
                showlegend=False,  # Hide legend
                plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
                height=300,  # Adjust height
                margin=dict(t=40, b=30, l=30, r=30)  # Adjust margins
            )

            # Add data labels for each point
            fig.update_traces(
                text=latest_20_trades["Trade Evaluation Score"],
                textposition="top center",
            )

            # Display the chart in Streamlit
            st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please upload your tradelog to proceed.")
    st.stop()
