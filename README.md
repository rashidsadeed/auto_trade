# Real-time Algorithmic trading Application

This project is a real-time trading application that executes algorithmic trades on cryptocurrencies or other assets. It is powered by backtested strategies, leveraging custom and pre-built indicators based on academic reserach.

## Features

- **Real-Time Data Collection**: 
  - Collects live data from the Binance API using WebSocket, which comes in JSON format.
  - Stores data in a MongoDB database, serving as a data warehouse for analysis, backtesting, and future strategy development.

- **Strategy and Decision-Making**:
  - Trading decisions are made using indicators such as **MACD**, **SMA**, **EMA**, among others.
  - Custom and pre-packed indicators can be configured based on strategy requirements.
  - Implements strategies for **buy/sell** decisions in real-time by only fetching the required data from the database, enhancing efficiency and reducing storage costs.

- **Modular, Object-Oriented Design**:
  - Each module performs a specific task, ensuring that development, maintenance, and debugging remain straightforward.
  - Data collection is handled in `data_fetch.py`, while trading logic and real-time decisions are managed in `trading.py`.

## Project Structure

- `data_fetch.py`: Handles real-time data collection from Binance API and stores it in MongoDB.
- `trading.py`: Executes trading strategies based on fetched data and modular indicator processing.
- `actions.py`: Contains possible actions to be executed based on strategies.
- `strategies.py`: Houses custom and predefined trading strategies.
