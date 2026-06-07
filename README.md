# Expense Tracker Dashboard

This project is a modern, professional expense tracking web application designed to help users monitor their spending habits. Built with **Flask**, **SQLite**, and **Bootstrap**, it provides a clean and responsive interface with interactive charts powered by **Chart.js**. The application supports user registration and login, adding and deleting expenses, exporting data to CSV, and insightful visualizations of your spending patterns by category and over time.

## Features

- **User Authentication** – Secure registration and login with hashed passwords using `Werkzeug` and session management via `Flask‑Login`.
- **Expense Management** – Add new expenses with date, category, description, and amount. View and delete existing entries.
- **Interactive Dashboard** – A comprehensive overview that displays total spending and visualizes expenses by category (pie chart) and by month (line chart).
- **Data Export** – Download all your expenses in CSV format with a single click for use in spreadsheets or other tools.
- **Responsive UI** – Built using Bootstrap 5 for a polished look on both desktop and mobile devices.

## Running Locally

To run the application locally, ensure that you have Python 3.8+ installed. Create a virtual environment, install dependencies, and start the server:

```bash
cd expense_tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The app will be available at [http://localhost:5000](http://localhost:5000).

## Deployment

This project is ready to deploy on platforms like **Render** or **Heroku**. A `Procfile` and `wsgi.py` are included for running with `gunicorn` in production. When deploying, set up environment variables such as `SECRET_KEY` for better security.

## License

This project is released under the MIT License. Feel free to modify and extend it according to your needs.