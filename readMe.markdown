# Data Streaming Course - Final Project

## Project Overview

Welcome to my final project for the Data Streaming Course! This project is an **Anomaly Detection System for Transaction Data**, built using a modern tech stack that includes Kafka, FastAPI, MongoDB, and Streamlit. The goal of this system is to effectively identify and flag unusual transaction patterns in real-time, demonstrating the power of data streaming in practical applications.

## Tech Stack

This project leverages a range of technologies:

- **Kafka**: Used for building real-time data pipelines and streaming apps. It's responsible for handling the stream of transaction data.
- **FastAPI**: A modern, fast (high-performance) web framework for building APIs. It's used to handle incoming data and interact with Kafka.
- **MongoDB**: A NoSQL database that stores transaction data and results from the anomaly detection process.
- **Streamlit**: An app framework mainly for machine learning and data science teams. In this project, it's used for creating a user-friendly web interface that displays the results of anomaly detection.

## System Architecture

The system architecture is designed to handle streaming data efficiently:
![System Architecture](arch.png)

1. **Data Ingestion**: Transaction data is continuously ingested through Kafka.
2. **Processing & Anomaly Detection**: As data flows in, FastAPI processes it and performs anomaly detection.
3. **Data Storage**: Results, along with raw transaction data, are stored in MongoDB for persistence and further analysis.
4. **Visualization**: Streamlit provides an interactive dashboard to visualize anomalies detected in real-time.


This project not only demonstrates my technical skills in handling data streaming but also my ability to integrate various technologies to build a comprehensive system. Feedback and contributions are welcome!

