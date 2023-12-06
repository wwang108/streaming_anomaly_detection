import streamlit as st
from streamlit_autorefresh import st_autorefresh
import os,sys
import pandas as pd
import requests
import json
import time
from mongo_action import MongoDBCollection 
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

load_dotenv(verbose=True)


normal_client = MongoDBCollection(os.environ.get("MONGO_USERNAME"),
                                  os.environ.get("MONGO_PASSWORD"),
                                  os.environ.get("MONGO_IP"),
                                  os.environ.get("MONGO_DB_NAME_NORMAL"),
                                  os.environ.get("MONGO_COLLECTION_NAME_NORMAL"))

anormal_client = MongoDBCollection(os.environ.get("MONGO_USERNAME"),
                                   os.environ.get("MONGO_PASSWORD"),
                                   os.environ.get("MONGO_IP"),
                                   os.environ.get("MONGO_DB_NAME_ANORMAL"),
                                   os.environ.get("MONGO_COLLECTION_NAME_ANORMAL"))
def get_transaction_counts(client, start_time, end_time, interval_minutes=5):
    """
    获取从start_time到end_time，每个时间间隔的交易数量。
    """
    counts = []
    stats = []
    columns = ['size', 'virtual_size', 'input_count', 'output_count', 'input_value', 'output_value', 'fee']
    while start_time < end_time:
        next_time = start_time + timedelta(minutes=interval_minutes)
        count = client.count_transactions_in_interval(start_time, next_time)

        record = client.calculate_statistics_in_interval(columns, start_time, next_time) 
        stats.append(record)
        counts.append(count)
        start_time = next_time

    return counts, stats

def plot_transactions(normal_counts, anormal_counts, times, ylabel, title):
    plt.figure(figsize=(12, 6))
    plt.plot(times, normal_counts, marker='o', color='blue', label='Normal Transactions')
    plt.plot(times, anormal_counts, marker='x', color='red', label='Anormal Transactions')
    plt.xlabel('Time')
    plt.ylabel(ylabel)
    plt.title(title, fontsize=14)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=6))
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()
def plot_tran_bar(normal_value, anormal_value, title):
    # Set the style for the plot
    plt.style.use('ggplot')

    # Define labels and values
    labels = ['Normal', 'Anormal']
    values = [normal_value, anormal_value]
    colors = ['#1E88E5', '#FFC107']  # Green for normal, red for anormal

    # Create the figure and axis objects
    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(labels, values, color=colors, width=0.6, edgecolor='black')


    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05, round(yval, 2),
                ha='center', va='bottom', color='black', fontweight='bold')

    ax.set_ylabel('Number of Transactions', fontweight='bold', fontsize=12)
    ax.set_title(title, fontweight='bold', fontsize=16)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.tick_params(axis='x', which='both', length=0, labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    plt.tight_layout()
    st.pyplot(fig)
    plt.clf()
def plot_tran_stats(current_normal_stats, current_anormal_stats, column, ylabel,  title):
    # Set the style for the plot
    plt.style.use('ggplot')

    # Define labels and values
    labels = ['Normal', 'Anormal']
    values = [current_normal_stats.get(column, 0), current_anormal_stats.get(column, 0)]
    colors = ['#4CAF50', '#D32F2F']  # Green for normal, red for anormal

    # Create the figure and axis objects
    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar(labels, values, color=colors, width=0.6, edgecolor='black')


    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05, round(yval, 2),
                ha='center', va='bottom', color='black', fontweight='bold')

    ax.set_ylabel(ylabel, fontweight='bold', fontsize=12)
    ax.set_title(title, fontweight='bold', fontsize=16)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.tick_params(axis='x', which='both', length=0, labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    plt.tight_layout()
    st.pyplot(fig)
    plt.clf()

def plot_stats(normal_stats, anormal_stats, times, column, ylabel, title):
    plt.figure(figsize=(12, 6))
    normal_count_data = [round(record.get(column, 0), 2) for record in normal_stats]
    anormal_count_data = [round(record.get(column, 0), 2) for record in anormal_stats]
    plt.plot(times, normal_count_data, marker='o', color='green', label='Normal Transactions')
    plt.plot(times, anormal_count_data, marker='x', color='orange', label='Anormal Transactions')
    plt.xlabel('Time')
    plt.ylabel(ylabel)
    plt.title(title, fontsize=14)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=6))
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()

@st.cache_resource
def get_initial_data(_client, start_time, end_time):
    # 这个函数只在首次运行时调用
    counts, stats = get_transaction_counts(_client, start_time, end_time)

    return counts, stats


def main():
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=3)
    start_window =  end_time - timedelta(minutes=5)
    times = [start_time + timedelta(minutes=5*i) for i in range(int((end_time - start_time) / timedelta(minutes=5)))]

    columns = ['size', 'virtual_size', 'input_count', 'output_count', 'input_value', 'output_value', 'fee']
    normal_counts, normal_stats = get_transaction_counts(normal_client, start_time, end_time)
    anormal_counts, anormal_stats = get_transaction_counts(anormal_client, start_time, end_time)

    st.set_page_config(layout="wide")
    # with st.sidebar:
    #     selected_tab = st.radio(
    #         "Choose a tab",
    #         ( "3-Hour Trend", "Recent Activity")
    #     )
    # tab1, tab2 = st.tabs([ "3-Hour Trend", "Recent Activity"])
    
    # if selected_tab == "3-Hour Trend":
        # with tab1:
    st.title('Monitoring Normal and Abnormal Transaction Trends')      
    with st.expander("Explanation", expanded=True):
        st.write("""
            Here you can find various statistics and comparisons of normal and abnormal transactions.
            The graphs update every 5 minutes to reflect the most recent data.
        """)
    col1,  col2 = st.columns(2)
    with col1:
        plot_transactions(normal_counts, anormal_counts, times, 'transaction_count', 'Transaction Count Comparison')

    with col2:
        plot_stats(normal_stats, anormal_stats, times, 'size_average', 'Average Transaction Size', 'Transaction Size Comparison')

    with col1:
        plot_stats(normal_stats, anormal_stats, times, 'input_count_average', 'Average input count', 'Average input count Comparison')

    with col2:
        plot_stats(normal_stats, anormal_stats, times, 'output_count_average', 'Average output count', 'Average output count Comparison')
    with col1:
        plot_stats(normal_stats, anormal_stats, times, 'input_value_average', 'Average input value', 'Average input value Comparison')
    with col2:
        plot_stats(normal_stats, anormal_stats, times, 'output_value_average', 'Average output value', 'Average output value Comparison')
    # if selected_tab == "Recent Activity":
    #     with tab2:
            
    #         with st.expander("Explanation", expanded=True):
    #             st.write("""
    #                 Here you can find various statistics and comparisons of normal and abnormal transactions.
    #                 The graphs update every 5 minutes to reflect the most recent data.
    #             """)
    #         col1,  col2 = st.columns(2)
    #         with col1:
    #             plot_tran_bar(current_normal, current_anormal, 'Current Transaction Count Comparison')
    #         with col2:
    #             plot_tran_stats(current_normal_stats, current_anormal_stats,  'size_average', 'Current Average Transaction Size', 'Current Transaction Size Comparison')
    #         with col1:
    #             plot_tran_stats(current_normal_stats, current_anormal_stats, 'input_count_average', 'Current Average input count', 'Current Average input count Comparison')
    #         with col2:
    #             plot_tran_stats(current_normal_stats, current_anormal_stats, 'output_count_average', 'Current Average output count', 'Current Average output count Comparison')
    #         with col1:
    #             plot_tran_stats(current_normal_stats, current_anormal_stats, 'input_value_average', 'Current Average input value', 'Current Average input value Comparison')
    #         with col2:
    #             plot_tran_stats(current_normal_stats, current_anormal_stats, 'output_value_average', 'Current Average output value', 'Current Average output value Comparison')
    st_autorefresh(interval=300 * 1000, key="data_refresh")
        # current_normal = normal_client.count_transactions_in_interval(start_window, end_time)
        # current_anormal = anormal_client.count_transactions_in_interval(start_window, end_time)
        # current_normal_stats = normal_client.calculate_statistics_in_interval(columns, start_window,end_time)
        # current_anormal_stats = anormal_client.calculate_statistics_in_interval(columns, start_window, end_time)
        # normal_counts.append(current_normal)
        # normal_stats.append(current_normal_stats)
        # del normal_counts[0]
        # del normal_stats[0]
        # anormal_counts.append(current_anormal)
        # anormal_stats.append(current_anormal_stats)
        # del anormal_counts[0]
        # del anormal_stats[0]

if __name__ == '__main__':
    main()