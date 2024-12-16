import os
import yaml
from flask import Flask, request, render_template_string, redirect, url_for
import requests

app = Flask(__name__)

CONFIG_PATH = "/share/alpr/plates.yaml"  # Updated to use the mapped share directory
HOME_ASSISTANT_TOKEN = os.getenv("HA_TOKEN")
HOME_ASSISTANT_URL = os.getenv("HA_URL")


@app.route('/')
def home():
    print("Accessing home page...")
    if not os.path.exists(CONFIG_PATH):
        print(f"Warning: {CONFIG_PATH} does not exist. Creating a new file.")
        plates = []
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, 'w') as file:
                yaml.dump(plates, file)
            print(f"Created {CONFIG_PATH} successfully.")
        except Exception as e:
            print(f"Error creating plates.yaml: {e}")
    else:
        try:
            with open(CONFIG_PATH, 'r') as file:
                plates = yaml.safe_load(file) or []
            print(f"Loaded plates: {plates}")
        except Exception as e:
            print(f"Error loading plates from {CONFIG_PATH}: {e}")
            plates = []

    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ALPR Plate Manager</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #f0f2f5;
                color: #333;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background: #fff;
                padding: 2rem;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                max-width: 500px;
                width: 100%;
                text-align: center;
            }
            .logo {
                max-width: 100%;
                height: auto;
                width: 150px;
                margin-bottom: 1rem;
            }
            h1 {
                color: #fe640b;
                margin-bottom: 1rem;
            }
            form {
                display: flex;
                margin-bottom: 1.5rem;
            }
            input[type="text"] {
                flex: 1;
                padding: 0.5rem;
                font-size: 1rem;
                border: 1px solid #ccc;
                border-radius: 5px 0 0 5px;
                text-transform: uppercase;
            }
            button[type="submit"] {
                background-color: #fe640b;
                color: #fff;
                border: none;
                padding: 0.5rem 1rem;
                cursor: pointer;
                font-size: 1rem;
                border-radius: 0 5px 5px 0;
                transition: background-color 0.3s;
            }
            button[type="submit"]:hover {
                background-color: #fe640b;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                background: #f9f9f9;
                padding: 0.75rem;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-bottom: 0.5rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            li a {
                color: #e74c3c;
                text-decoration: none;
                font-size: 1.2rem;
                transition: color 0.3s;
            }
            li a:hover {
                color: #c0392b;
            }
        </style>
    </head>
    <body>
        <div class="container">
                        <h1>Manage License Plates</h1>
            <form action="/add_plate" method="POST">
                <input type="text" name="plate" placeholder="Enter License Plate" required oninput="this.value = this.value.toUpperCase()">
                <button type="submit"><i class="fas fa-plus"></i> Add Plate</button>
            </form>
            <h2>Watched Plates:</h2>
            <ul>
                {% for plate in plates %}
                <li>{{ plate }} <a href="/delete_plate/{{ plate }}"><i class="fas fa-trash-alt"></i></a></li>
                {% endfor %}
            </ul>
        </div>
    </body>
    </html>
    '''

    return render_template_string(html_content, plates=plates)

@app.route('/add_plate', methods=['POST'])
def add_plate():
    new_plate = request.form.get('plate')
    if new_plate:
        new_plate = new_plate.upper()  # Ensure the plate is in uppercase
        spaced_plate = f"{new_plate[:3]} {new_plate[3:]}"  # Add space after the first 3 characters
        print(f"Attempting to add new plates: {new_plate} and {spaced_plate}")

        if not os.path.exists(CONFIG_PATH):
            print("Creating plates.yaml file.")
            try:
                os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
                with open(CONFIG_PATH, 'w') as file:
                    yaml.dump([], file)
                print(f"Created {CONFIG_PATH} successfully.")
            except Exception as e:
                print(f"Error creating plates.yaml: {e}")

        # Read the existing plates
        try:
            with open(CONFIG_PATH, 'r') as file:
                plates = yaml.safe_load(file) or []
            print(f"Current plates: {plates}")
        except Exception as e:
            print(f"Error reading plates.yaml: {e}")
            plates = []

        # Add the new plates if they are not already in the list
        if new_plate not in plates:
            plates.append(new_plate)
        if spaced_plate not in plates:
            plates.append(spaced_plate)

        # Write the updated plates list
        print(f"Writing plates to {CONFIG_PATH}: {plates}")
        try:
            with open(CONFIG_PATH, 'w') as file:
                yaml.dump(plates, file)
            print(f"Successfully wrote plates to {CONFIG_PATH}.")
        except Exception as e:
            print(f"Error writing plates.yaml: {e}")

        # Reload Home Assistant image processing configuration
        reload_image_processing()

    else:
        print("No plate provided to add.")

    return redirect(url_for('home'))

@app.route('/delete_plate/<plate>')
def delete_plate(plate):
    plate = plate.upper()  # Ensure the plate is in uppercase
    print(f"Attempting to delete plate: {plate}")
    if not os.path.exists(CONFIG_PATH):
        plates = []
    else:
        try:
            with open(CONFIG_PATH, 'r') as file:
                plates = yaml.safe_load(file) or []
            print(f"Current plates: {plates}")
        except Exception as e:
            print(f"Error reading plates.yaml: {e}")
            plates = []

    if plate in plates:
        plates.remove(plate)

        # Write the updated plates list
        print(f"Writing updated plates to {CONFIG_PATH}: {plates}")
        try:
            with open(CONFIG_PATH, 'w') as file:
                yaml.dump(plates, file)
            print(f"Successfully updated {CONFIG_PATH}.")
        except Exception as e:
            print(f"Error writing plates.yaml: {e}")

    # Reload Home Assistant image processing configuration
    reload_image_processing()

    return redirect(url_for('home'))

def reload_image_processing():
    headers = {
        "Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(
            f"{HOME_ASSISTANT_URL}/api/services/image_processing/reload",
            headers=headers
        )
        if response.status_code == 200:
            print("Image processing reloaded successfully.")
        else:
            print(f"Failed to reload image processing: {response.status_code}")
    except Exception as e:
        print(f"Error reloading image processing: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
