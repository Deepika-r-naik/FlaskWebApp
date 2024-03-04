from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from faker import Faker
import sqlite3
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)
Bootstrap(app)
fake = Faker()

@app.route('/')
def index():
    api_key = "your_api_key"  # Replace with your actual API key
    warranty_details = fetch_fake_warranty_details(api_key)

    # Additional functionality: Search by device name
    search_query = request.args.get('search', '')
    if search_query:
        warranty_details = [device for device in warranty_details if search_query.lower() in device['DeviceModel'].lower()]

    save_to_sqlite(warranty_details)  # Save fake data to SQLite

    # Create charts
    chart1_url = generate_chart1(warranty_details)
    chart2_url = generate_chart2(warranty_details)

    return render_template('index.html', warranty_details=warranty_details, chart1_url=chart1_url, chart2_url=chart2_url, search_query=search_query)

def fetch_fake_warranty_details(api_key):
    # Generate fake warranty details for demonstration
    fake_details = []
    for _ in range(10):  # Adjust the number of fake devices as needed
        device_detail = {
            'DeviceIdentifier': fake.uuid4(),
            'EndDate': fake.date_this_decade(),
            'DeviceModel': fake.word(),
            'Page': fake.random_int(1, 5)
        }
        fake_details.append(device_detail)
    return fake_details

def save_to_sqlite(warranty_details):
    conn = sqlite3.connect('warranty_data.db')
    cursor = conn.cursor()

    # Create a table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warranty_data (
            id INTEGER PRIMARY KEY,
            device_identifier TEXT,
            end_date TEXT,
            device_model TEXT,
            page INTEGER
        )
    ''')

    # Insert data into the table
    for warranty_detail in warranty_details:
        cursor.execute('''
            INSERT INTO warranty_data (device_identifier, end_date, device_model, page)
            VALUES (?, ?, ?, ?)
        ''', (warranty_detail['DeviceIdentifier'], warranty_detail['EndDate'], warranty_detail['DeviceModel'], warranty_detail['Page']))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def generate_chart1(warranty_details):
    days_left = [device['Page'] for device in warranty_details]
    labels = [device['DeviceModel'] for device in warranty_details]

    plt.figure(figsize=(8, 4))
    plt.bar(labels, days_left, color='skyblue')
    plt.title('Days Left for Warranty Expiry')
    plt.xlabel('Devices')
    plt.ylabel('Days Left')
    plt.xticks(rotation=45, ha='right')

    # Save the chart to a BytesIO buffer
    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format='png')
    plt.close()

    # Convert the chart buffer to a base64-encoded string
    chart_data = chart_buffer.getvalue()
    chart_url = f'data:image/png;base64,{chart_data.hex()}'
    
    return chart_url

def generate_chart2(warranty_details):
    # Generate chart showing devices with many days left in warranty
    days_left = [fake.random_int(100, 365) for _ in warranty_details]
    labels = [device['DeviceModel'] for device in warranty_details]

    plt.figure(figsize=(8, 4))
    plt.bar(labels, days_left, color='lightgreen')
    plt.title('Remaining Warranty Days')
    plt.xlabel('Devices')
    plt.ylabel('Days Left')
    plt.xticks(rotation=45, ha='right')

    # Save the chart to a BytesIO buffer
    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format='png')
    plt.close()

    # Convert the chart buffer to a base64-encoded string
    chart_data = chart_buffer.getvalue()
    chart_url = f'data:image/png;base64,{chart_data.hex()}'
    
    return chart_url
def save_chart_to_temp_file():
    # Save the current chart to a temporary file and return the URL
    chart_filename = 'temp_chart.png'
    plt.savefig(chart_filename, bbox_inches='tight')
    plt.close()

    with open(chart_filename, 'rb') as chart_file:
        chart_data = chart_file.read()

    return f'data:image/png;base64,{chart_data.hex()}'

if __name__ == '__main__':
    app.run(debug=True)
