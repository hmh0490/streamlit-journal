import streamlit as st
import pandas as pd
import numpy as np
import os
from navigation import make_sidebar

# # Set the page configuration to wide layout
st.set_page_config(page_title="Trading Dashboard", layout="centered")

make_sidebar()

# Retrieve settings from session_state
risk_management_fee = st.session_state.get('risk_management_fee')
ticker_data = st.session_state.get('ticker_data')
initial_balance = st.session_state.get('initial_balance')
withdrawals = st.session_state.get('withdrawals')

file_path = os.path.join(os.getcwd(), "tradelog_updated.csv")

st.title('Trading Journal')

tab1, tab2, tab3, tab4 = st.tabs(['New Entry', 'Trade Log', 'Filter', 'Settings'])

# ****** NEW ENTRY ******
with tab1:
    st.subheader(':green[New Entry]')
    col1, col2, col3, col4, col5 = st.columns([0.5, 0.5, 0.5, 0.5, 0.57])

    with col1:
        ticker = st.selectbox('Symbol',
                              options=['ES', 'GC', 'CL', 'YM', 'NQ', 'MES', 'MCL', 'MGC', 'MYM',
                                       'MNQ'])
        direction = st.selectbox('Direction', options=['Long', 'Short'])
    with col2:
        date = st.date_input('Date')
        time = st.time_input('Time')
    with col3:
        entry_price = st.number_input('Entry Price', min_value=0.0, step=0.1, format="%.2f")
        exit_price = st.number_input('Exit Price', min_value=0.0, step=0.1, format="%.2f")
    with col4:
        contract = st.number_input('Contracts', min_value=1, step=1, format="%d")
        setup = st.selectbox('Setup',
                             options=['Zone', 'Crusher', 'Sniper', 'Tug Of War',
                                      'TC', 'HY', 'IFN', 'REV', 'TF', 'DDV',
                                      'Other'])
    with col5:
        entry_exit = st.selectbox('Entry/Exit',
                                  options=['As Planned', 'Too Early', 'Too Late',
                                           'Not In Plan', 'Broke Rules', 'Stop to tight',
                                           'First 30 min', 'Didn\'t Check News'])
        emotion = st.selectbox('Emotion',
                               options=['By The Rules', 'Fear', 'Hope', 'Greed',
                                        'FOMO', 'Bored', 'Tired', 'Distracted'])


    # Define function to add trade
    def add_trade(date, time, ticker, direction, contract, entry_price, exit_price, setup,
                  entry_exit, emotion):

        if "tradelog" in st.session_state and st.session_state["tradelog"] is not None and not \
                st.session_state["tradelog"].empty:
            # Ensure the 'Trade ID' column is interpreted as numeric
            st.session_state["tradelog"]["Trade ID"] = pd.to_numeric(
                st.session_state["tradelog"]["Trade ID"], errors='coerce')

            # Get the maximum Trade ID if it exists
            if not st.session_state["tradelog"]["Trade ID"].isna().all():
                last_trade_id = st.session_state["tradelog"]["Trade ID"].max()
                trade_id = int(last_trade_id) + 1 if pd.notna(last_trade_id) else 1
            else:
                trade_id = 1
        else:
            # Start Trade ID from 1 if tradelog is empty or doesn't exist
            trade_id = 1

        # Adjust the Entry Time to display in AM/PM format
        # formatted_entry_time = time.strftime("%I:%M %p")

        new_trade = {
            "Trade ID": trade_id,
            "Date": date,
            "Entry Time": time.strftime("%I:%M %p"),  # time.strftime("%H:%M"),
            "Exit Time": None,  # Set to None or time if provided
            "Ticker": ticker,
            "Direction": direction,
            "Contracts": contract,
            "Entry Price": entry_price,
            "Exit Price": exit_price,
            "Setup": setup,
            "Entry/Exit": entry_exit,
            "Emotion": emotion
        }
        # Check if ticker_data is a DataFrame with at least one row
        if isinstance(ticker_data, pd.DataFrame) and not ticker_data.empty:
            # Retrieve the broker fees if the ticker exists in ticker_data
            broker_fees = \
            ticker_data.loc[ticker_data['Ticker'] == ticker, 'Broker Fees'].values[
                0] if ticker in ticker_data['Ticker'].values else 3
        else:
            # Default broker fee if ticker_data is empty or not a DataFrame
            broker_fees = 3

        # Calculate PnL and Net PnL
        if direction == "LONG":
            points = exit_price - entry_price
        else:
            points = entry_price - exit_price
        pnl = contract * points
        risk_management_fee_value = (risk_management_fee / 100) * entry_price * contract
        total_broker_fees = broker_fees * contract
        net_pnl = pnl - risk_management_fee_value - total_broker_fees
        percentage_return = round((exit_price - entry_price) / entry_price * 100,
                                  2) if direction == "LONG" else round(
            (entry_price - exit_price) / entry_price * 100, 2)

        # Update the new trade entry with calculated fields
        new_trade.update({

            "Risk Management Fee": risk_management_fee_value,
            "Total Broker Fees": total_broker_fees,
            "PnL": pnl,
            "Net PnL": net_pnl,
            "Return %": percentage_return,
        })
        new_trade = pd.DataFrame([new_trade])
        return new_trade


    # ****** READ IN THE TRADELOG AND PERFORM CALCULATIONS *****

    # Function to load the tradelog from disk if it exists
    def load_tradelog():
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            return None


    # Check if trade log data already exists in session_state
    if "tradelog" not in st.session_state:
        # Load from disk if available
        st.session_state["tradelog"] = load_tradelog()

    tradelog = st.session_state["tradelog"]

    # save button
    if st.button("Add Trade"):
        new_trade = add_trade(
            date=date,
            time=time,
            ticker=ticker,
            direction=direction,
            contract=contract,
            entry_price=entry_price,
            exit_price=exit_price,
            setup=setup,
            entry_exit=entry_exit,
            emotion=emotion)

        if "Cumulative Performance" in st.session_state["tradelog"].columns and not \
                st.session_state["tradelog"].empty:
            last_cumulative_performance = \
                st.session_state["tradelog"]["Cumulative Performance"].iloc[-1]
        else:
            last_cumulative_performance = initial_balance

        # Calculate metrics for new data
        new_cumulative_performance = last_cumulative_performance + new_trade["Net PnL"]
        new_performance = (new_cumulative_performance / last_cumulative_performance - 1) * 100

        # Update the new trade dictionary and add to tradelog
        new_trade["Cumulative Performance"] = new_cumulative_performance
        new_trade["Performance %"] = new_performance
        tradelog = pd.concat([tradelog, new_trade], ignore_index=True)

        tradelog["20 MA"] = tradelog["Cumulative Performance"].rolling(window=20).mean()

        tradelog.to_csv(file_path, index=False)  # Save updated tradelog to file
        st.session_state["tradelog"] = tradelog  # Update session state with new trade

        st.success("Trade added successfully with updated performance metrics!")

    # Define the calculation function
    def calculate_pnl(log):
        # Determine points based on trade direction
        if log['Direction'] == 'Long':
            points = log['Exit Price'] - log['Entry Price']
        elif log['Direction'] == 'Short':
            points = log['Entry Price'] - log['Exit Price']
        else:
            points = 0  # Set points to 0 if direction is not recognized

        # Calculate PnL
        pnl = log['Contracts'] * points * log['Point Dollar Value']

        # Calculate Net PnL by applying both the risk management fee and brokerage fee
        net_pnl = pnl - log['Risk Management Fee'] - log['Total Broker Fees']
        return pd.Series([pnl, net_pnl])


    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            # Attempt to read the CSV file
            tradelog = pd.read_csv(uploaded_file)

            # Adjust index to start at 1 instead of 0
            # tradelog = pd.DataFrame(tradelog)
            tradelog.index += 1

            # Reset index and rename it to "Trade ID"
            tradelog.reset_index(inplace=True)
            tradelog.rename(columns={'index': 'Trade ID'}, inplace=True)

            # Merge with ticker data to add Point Dollar Value and Brokerage Fee
            # Check if ticker_data exists before merging
            tradelog = pd.DataFrame(tradelog)
            tradelog_date = tradelog['Date']
            tradelog_time = tradelog['Exit Time']
            ticker_data = pd.DataFrame(ticker_data)
            tradelog = tradelog.merge(ticker_data, on='Ticker', how='left')
            tradelog['Risk Management Fee'] = risk_management_fee / 100 * tradelog[
                'Entry Price'] * tradelog['Contracts']
            tradelog['Total Broker Fees'] = tradelog['Broker Fees'] * tradelog['Contracts']

            # Calculate Returns
            if "Direction" in tradelog.columns:
                # Calculate Percentage Return based on Direction
                tradelog["Return %"] = np.where(
                    tradelog["Direction"] == "Long",
                    ((tradelog["Exit Price"] - tradelog["Entry Price"]) /
                     tradelog["Entry Price"]) * 100,
                    ((tradelog["Entry Price"] - tradelog["Exit Price"]) /
                     tradelog["Entry Price"]) * 100
                ).round(2)

            # Apply calculations to each row and add new columns
            tradelog[['PnL', 'Net PnL']] = tradelog.apply(calculate_pnl, axis=1)

            # Now calculate cumulative performance, performance, and 20-period moving average
            # Initialize Cumulative Performance list
            cumulative_performance = []

            # Iterate over the Net PnL column
            for i, pnl in enumerate(tradelog['Net PnL']):
                if i == 0:
                    # First cumulative performance
                    cumulative_performance.append(initial_balance + pnl)
                else:
                    # Add current Net PnL to previous Cumulative Performance
                    cumulative_performance.append(cumulative_performance[i - 1] + pnl)

            # Assign calculated values back to the DataFrame
            tradelog['Cumulative Performance'] = cumulative_performance

            #### Calculate Performance %
            performance = []
            for i, row in tradelog.iterrows():
                if i == 0:
                    # For the first row
                    performance.append(((row['Cumulative Performance'] / initial_balance)-1) * 100)
                else:
                    # For subsequent rows
                    prev_cum_performance = tradelog.loc[i - 1, 'Cumulative Performance']
                    current_cum_performance = row['Cumulative Performance']
                    performance.append(((current_cum_performance / prev_cum_performance) - 1) * 100)

            # Add Performance % to the dataframe
            tradelog['Performance %'] = performance


            tradelog['20 MA'] = tradelog['Cumulative Performance'].rolling(window=20).mean()

            tradelog.drop(columns=['Broker Fees', 'Point Dollar Value', 'Currency', 'Tick Size',
                                   'Ticks per 1 point', 'Equals 1 point', 'Tick Dollar Value'],
                          inplace=True)

            # Save the processed DataFrame to disk
            tradelog.to_csv(file_path, index=False)

            # Store the updated trade log with calculations in session_state
            st.session_state["tradelog"] = tradelog

            st.toast('Data Successfully Loaded and Saved ', icon='✅')
        except Exception as e:
            st.error(f"Error reading the CSV: {e}")

#### DISPLAY TRADELOG IN TAB 2 ####
with tab2:
    st.subheader(':green[Trade Journal]')

    if st.session_state['tradelog'] is not None and not st.session_state['tradelog'].empty:
        st.session_state['tradelog']['Date'] = pd.to_datetime(
            st.session_state['tradelog']['Date'], errors='coerce').dt.strftime('%Y-%m-%d')

        updated_tradelog = st.data_editor(
            st.session_state['tradelog'],
            column_config={
                'Ticker': st.column_config.TextColumn('Ticker', width='small'),
                'Entry Price': st.column_config.NumberColumn(format="$%.2f"),
                'Exit Price': st.column_config.NumberColumn(format="$%.2f"),
                'Direction': st.column_config.SelectboxColumn(options=['Long', 'Short'],
                                                              width='small'),
                'Setup': st.column_config.SelectboxColumn(
                    options=['Zone', 'Crusher', 'Sniper', 'Tug Of War',
                             'TC', 'HY', 'IFN', 'REV', 'TF', 'DDV',
                             'Other'], width='small'),
                'Entry/Exit': st.column_config.SelectboxColumn(
                    options=['As Planned', 'Too Early', 'Too Late',
                             'Not In Plan', 'Broke Rules', 'Stop to tight',
                             'First 30 min', 'Didn\'t Check News'], width='small'),
                'Emotion': st.column_config.SelectboxColumn(
                    options=['By The Rules', 'Fear', 'Hope', 'Greed',
                             'Bored', 'FOMO', 'Tired', 'Distracted'], width='small'),
                'Total Broker Fess': st.column_config.NumberColumn(format="$%.2f"),
                'Risk Management Fee': st.column_config.NumberColumn(format="$%.2f"),
                'PnL': st.column_config.NumberColumn(format="$%.2f"),
                'Net PnL': st.column_config.NumberColumn(format="$%.2f"),
            }, use_container_width=True)

        # Save the edited version back to session_state
        st.session_state['tradelog'] = updated_tradelog

        # Save button to persist changes made in the editor
        if st.button("Save Changes"):
            st.session_state['tradelog'].to_csv(file_path, index=False)

            st.success("Changes saved successfully!")

        st.divider()  # For visual separation

        # Remove Trade Section
        st.subheader(':red[Remove Trade]')

        # Create columns for the input field and button
        col1, col2 = st.columns([1, 3])

        with col1:
            remove_trade_id = st.number_input("Enter Trade ID to remove", min_value=1, step=1)

        # Place the button in a separate container to limit its width
        with st.container():
            if st.button("Remove Trade"):
                # Check if Trade ID exists
                if remove_trade_id in st.session_state['tradelog']['Trade ID'].values:
                    # Remove the trade with the specified Trade ID
                    st.session_state['tradelog'] = st.session_state['tradelog'][
                        st.session_state['tradelog']['Trade ID'] != remove_trade_id
                        ]
                    st.session_state['tradelog'].to_csv(file_path, index=False)

                    st.success(
                        f"Trade with ID {remove_trade_id} removed successfully! Please refresh the page")
                else:
                    # Error message spans full width
                    st.error(f"Trade with ID {remove_trade_id} not found.")
    else:
        st.write("No data loaded. Please upload a CSV file.")

###### FILTER #####
with tab3:
    def filter_ui():
        """UI for filtering trades based on various criteria."""
        filter_value = None

        with st.container():
            st.subheader(':green[Filter Trades]')
            col1, col2 = st.columns(2)

            with col1:
                choice = st.selectbox('Filter Trades By', options=[
                    'Trade ID', 'Ticker', 'Date', 'Direction', 'Order State'])

            with col2:
                # Allow user to input filter value based on the selected filter choice
                if choice == 'Ticker':
                    filter_value = st.text_input('Enter Ticker', max_chars=4,
                                                 placeholder='Symbol')
                elif choice == 'Trade ID':
                    filter_value = st.number_input('Enter Trade ID', min_value=1, step=1,
                                                   key='filter_trade_id')
                elif choice == 'Date':
                    filter_value = st.date_input('Select Date', key='filter_date')
                elif choice == 'Direction':
                    filter_value = st.selectbox('Select Direction',
                                                options=['All', 'Long', 'Short'])
                elif choice == 'Order State':
                    filter_value = st.selectbox('Select Order State',
                                                options=['Open', 'Closed'])

        return choice, filter_value


    # Get filter criteria
    choice, filter_value = filter_ui()

    # Button to show filtered results
    show_results = st.button('Show Results')

    # Divider for visual separation
    st.divider()

    st.subheader(':green[Filter Results]')

    # Check if tradelog is available in session state
    if "tradelog" in st.session_state:
        tradelog = st.session_state["tradelog"]

        # Filtering logic
        if show_results:
            filtered_trades = tradelog.copy()

            if choice == 'Trade ID' and filter_value:
                filtered_trades = filtered_trades[
                    filtered_trades['Trade ID'] == int(filter_value)]
            elif choice == 'Ticker' and filter_value:
                filtered_trades = filtered_trades[
                    filtered_trades['Ticker'].str.upper() == filter_value.upper()]
            elif choice == 'Date' and filter_value:
                filtered_trades = filtered_trades[
                    filtered_trades['Date'] == pd.to_datetime(filter_value)]
            elif choice == 'Direction' and filter_value != 'All':
                filtered_trades = filtered_trades[filtered_trades['Direction'] == filter_value]
            elif choice == 'Order State':
                # Determine "Closed" if Exit Time is not None, otherwise "Open"
                if filter_value == 'Closed':
                    filtered_trades = filtered_trades[filtered_trades['Exit Time'].notnull()]
                elif filter_value == 'Open':
                    filtered_trades = filtered_trades[filtered_trades['Exit Time'].isnull()]

            # Display filtered results
            if not filtered_trades.empty:
                st.dataframe(filtered_trades)

                # Option to export filtered results to CSV
                if st.button('Export to CSV'):
                    filtered_trades.to_csv('tradelog_filtered.csv', index=False)
                    st.success(
                        "Filtered data exported to 'tradelog_filtered.csv' successfully!")
            else:
                st.warning("No trades found matching the filter criteria.")
    else:
        st.warning("No trade log data available. Please upload your trade log.")

##### BACKGROUND DATA #####
with tab4:
    # Page Title
    st.title("Settings")

    # Section for Initial Balance and RM fee
    st.subheader("Initial Balance and Risk Management Fee")
    col1, _ = st.columns([1.1, 2.5])  # Adjust the ratio as needed

    with col1:
        initial_balance = st.number_input(
            "Enter your initial balance:", min_value=0.0,
            value=50000.0, step=100.0)
        risk_management_fee = st.number_input(
            "Enter risk management fee (%):",
            min_value=0.0, max_value=100.0,
            value=2.0, step=0.1)
    st.write(
        f"Your initial balance is set to: ${initial_balance:,.2f}")
    st.write(
        f"The current risk management fee is set to: {risk_management_fee}%")

    # Data for the Ticker Table
    ticker_data = {
        "Ticker": ["ES", "MES", "YM", "MYM", "GC", "MGC", "CL", "MCL",
                   "NQ", "MNQ"],
        "Tick Size": [0.25, 0.25, 1, 1, 0.1, 0.1, 0.01, 0.01, 0.25,
                      0.25],
        "Ticks per 1 point": [4, 4, 1, 1, 10, 10, 100, 100, 4, 4],
        "Equals 1 point": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "Tick Dollar Value": [12.5, 1.25, 5, 0.5, 10, 1, 10, 1, 5,
                              0.5],
        "Point Dollar Value": [50, 5, 5, 0.5, 100, 10, 1000, 100, 20,
                               2],
        "Currency": ["USD"] * 10,
        "Broker Fees": [3] * 10
    }

    # Display the Ticker Table
    st.subheader("Ticker Information")
    ticker_data = st.data_editor(ticker_data)

    # Store settings in session_state for consistent access across pages
    st.session_state['initial_balance'] = initial_balance
    st.session_state['risk_management_fee'] = risk_management_fee
    st.session_state['ticker_data'] = ticker_data

    ############# Section for Withdrawals ############
    # Define the file path for storing withdrawals
    withdrawals_file = "../withdrawals.csv"


    # Function to save withdrawals to CSV
    def save_withdrawals_to_csv():
        if st.session_state['withdrawals']:
            withdrawals_df = pd.DataFrame(st.session_state['withdrawals'])
            withdrawals_df.to_csv(withdrawals_file, index=False)


    # Initialize the session state for withdrawals
    if "withdrawals" not in st.session_state:
        if os.path.exists(withdrawals_file):
            # Load withdrawals from the CSV file if it exists
            st.session_state['withdrawals'] = pd.read_csv(withdrawals_file).to_dict(
                orient='records')
            st.success("Withdrawals loaded from file!")
        else:
            st.session_state['withdrawals'] = []

    st.subheader("Withdrawals Information")

    # Use columns to control the width of input fields
    col1, col2, col3 = st.columns([1, 1, 1])  # Adjust the column width as needed

    # Form to input a new withdrawal
    with st.form(key='withdrawal_form'):
        with col1:
            withdrawal_date = st.date_input("Date of Withdrawal")
        with col2:
            withdrawal_amount = st.number_input("Amount", min_value=0.0, value=0.0, step=100.0)
        with col3:
            withdrawal_currency = st.selectbox("Currency",
                                               options=["USD"])

        # Submit button for the form
        submit_button = st.form_submit_button(label="Add Withdrawal")

    # Adding a new withdrawal entry when the form is submitted
    if submit_button:
        new_withdrawal = {
            "Date": withdrawal_date,
            "Amount": withdrawal_amount,
            "Currency": withdrawal_currency
        }

        # Append the new withdrawal to the session state
        st.session_state['withdrawals'].append(new_withdrawal)
        # st.success("Withdrawal added successfully!")

        # Save the updated withdrawals to CSV
        save_withdrawals_to_csv()

    # Display the withdrawals table if there are any entries
    if st.session_state['withdrawals']:
        st.markdown("### Withdrawals List")
        withdrawals_df = pd.DataFrame(st.session_state['withdrawals'])
        st.dataframe(withdrawals_df)

import pandas as pd
import os

# Define the data to save
data = {'Column1': [1, 2, 3], 'Column2': [4, 5, 6]}
df = pd.DataFrame(data)

# Build the path relative to the "pages" directory
file_path = os.path.join(os.getcwd(), "test.csv")

# Resolve the path to the absolute path
absolute_file_path = os.path.abspath(file_path)

# Save the file
df.to_csv(absolute_file_path, index=False)

print("File saved at:", absolute_file_path)