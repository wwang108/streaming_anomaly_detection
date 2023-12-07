import streamlit as st
from streamlit_autorefresh import st_autorefresh
import os, sys
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

# MongoDB client for normal transactions
normal_client = MongoDBCollection(
    os.environ.get("MONGO_USERNAME"),
    os.environ.get("MONGO_PASSWORD"),
    os.environ.get("MONGO_IP"),
    os.environ.get("MONGO_DB_NAME_NORMAL"),
    os.environ.get("MONGO_COLLECTION_NAME_NORMAL"),
)
# MongoDB client for abnormal transactions
anormal_client = MongoDBCollection(
    os.environ.get("MONGO_USERNAME"),
    os.environ.get("MONGO_PASSWORD"),
    os.environ.get("MONGO_IP"),
    os.environ.get("MONGO_DB_NAME_ANORMAL"),
    os.environ.get("MONGO_COLLECTION_NAME_ANORMAL"),
)


def get_transaction_counts(client, start_time, end_time, interval_minutes=5):
    """
    Get total count for transactions between these samll intervals
    """
    counts = []
    stats = []
    columns = [
        "size",
        "virtual_size",
        "input_count",
        "output_count",
        "input_value",
        "output_value",
        "fee",
    ]
    while start_time < end_time:
        next_time = start_time + timedelta(minutes=interval_minutes)
        count = client.count_transactions_in_interval(start_time, next_time)

        record = client.calculate_statistics_in_interval(columns, start_time, next_time)
        stats.append(record)
        counts.append(count)
        start_time = next_time

    return counts, stats


# Function to plot transaction count trends
def plot_transactions(normal_counts, anormal_counts, times, ylabel, title):
    plt.figure(figsize=(12, 6))
    plt.plot(
        times, normal_counts, marker="o", color="blue", label="Normal Transactions"
    )
    plt.plot(
        times, anormal_counts, marker="x", color="red", label="Anormal Transactions"
    )
    plt.xlabel("Time")
    plt.ylabel(ylabel)
    plt.title(title, fontsize=14)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=6))
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()


# Function to plot statistical trends for transactions
def plot_stats(normal_stats, anormal_stats, times, column, ylabel, title):
    plt.figure(figsize=(12, 6))
    normal_count_data = [round(record.get(column, 0), 2) for record in normal_stats]
    anormal_count_data = [round(record.get(column, 0), 2) for record in anormal_stats]
    plt.plot(
        times, normal_count_data, marker="o", color="green", label="Normal Transactions"
    )
    plt.plot(
        times,
        anormal_count_data,
        marker="x",
        color="orange",
        label="Anormal Transactions",
    )
    plt.xlabel("Time")
    plt.ylabel(ylabel)
    plt.title(title, fontsize=14)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M:%S"))
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=6))
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)
    plt.clf()

# Streamlit cache function to get initial data
@st.cache_resource
def get_initial_data(_client, start_time, end_time):
    counts, stats = get_transaction_counts(_client, start_time, end_time)

    return counts, stats


# Main function to run the Streamlit app
def main():
    # Setting up time intervals and fetching data
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=3)
    start_window = end_time - timedelta(minutes=5)
    times = [
        start_time + timedelta(minutes=5 * i)
        for i in range(int((end_time - start_time) / timedelta(minutes=5)))
    ]

    columns = [
        "size",
        "virtual_size",
        "input_count",
        "output_count",
        "input_value",
        "output_value",
        "fee",
    ]
    normal_counts, normal_stats = get_transaction_counts(
        normal_client, start_time, end_time
    )
    anormal_counts, anormal_stats = get_transaction_counts(
        anormal_client, start_time, end_time
    )

    st.set_page_config(layout="wide")

    st.title("Monitoring Normal and Abnormal Transaction Trends")
    with st.expander("Explanation", expanded=True):
        st.write(
            """
            Here you can find various statistics and comparisons of normal and abnormal transactions.
            The graphs update every 5 minutes to reflect the most recent data.
        """
        )
    col1, col2 = st.columns(2)
    with col1:
        plot_transactions(
            normal_counts,
            anormal_counts,
            times,
            "transaction_count",
            "Transaction Count Comparison",
        )

    with col2:
        plot_stats(
            normal_stats,
            anormal_stats,
            times,
            "size_average",
            "Average Transaction Size",
            "Transaction Size Comparison",
        )

    with col1:
        plot_stats(
            normal_stats,
            anormal_stats,
            times,
            "input_count_average",
            "Average input count",
            "Average input count Comparison",
        )

    with col2:
        plot_stats(
            normal_stats,
            anormal_stats,
            times,
            "output_count_average",
            "Average output count",
            "Average output count Comparison",
        )
    with col1:
        plot_stats(
            normal_stats,
            anormal_stats,
            times,
            "input_value_average",
            "Average input value",
            "Average input value Comparison",
        )
    with col2:
        plot_stats(
            normal_stats,
            anormal_stats,
            times,
            "output_value_average",
            "Average output value",
            "Average output value Comparison",
        )
    # Auto-refresh for Streamlit app to update data periodically
    st_autorefresh(interval=300 * 1000, key="data_refresh")


if __name__ == "__main__":
    main()
