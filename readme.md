# ALPR Plate Manager

This repository provides a Flask-based web application for managing license plates, designed to integrate with Home Assistant's image processing features.

---

## Prerequisites

1. Create a folder in `../share/alpr` for the storage of plates.yaml

2.  Create a folder in

    ```
    /config/images/codeproject_ai_alpr/
    ```

**Environment Variables**:

- `HA_TOKEN`: Your Home Assistant long-lived access token.
- `HA_URL`: The URL of your Home Assistant instance.

Add these variables to your environment using a `.env` file or directly in your terminal. For example:
```bash
export HA_TOKEN="your_home_assistant_token"
export HA_URL="http://your_home_assistant_url"
```

---

## Setup

### Step 1: Clone the Repository

Go to addons folder of Home Assistant, create a folder, namely **ALPR**. 

Clone the repository containing the ALPR Plate Manager code:
```bash
git clone https://github.com/your-repo/alpr-plate-manager.git
cd alpr-plate-manager
```

### Step 2: Update Environment Variables
Ensure the `HA_TOKEN` and `HA_URL` environment variables are correctly set to connect to your Home Assistant instance. 

To create `HA_TOKEN`, Profile > Security **TAB** , scroll down and Create Token on **Long-lived access tokens**

### Step 3: Adding the addon
Go to **settings** > **add-ons** > **Add-on store** then **Local Add-ons**

---

## Usage

### Web Interface
1. Go to settings > Dashboards > add dashboard > webpage and insert the URL that was created by the add on!
2. Use the input box to add new license plates.
3. View and manage your list of plates, including the option to delete entries.

### Home Assistant Integration
- The application uses Home Assistant's API to reload image processing configurations when plates are added or removed.

- Go to the **configuration.yaml**

  ```yaml
  image_processing:
    - platform: codeproject_ai_alpr
      server: http://ip_address_of_your_codeproject_device/v1/vision/alpr/
      watched_plates: !include ../share/alpr/plates.yaml
      save_file_folder: /config/images/codeproject_ai_alpr/
      save_timestamped_file: True
      always_save_latest_file: True
      source:
        - entity_id: camera.eramiz_outdoor_camera_main
  ```

  

---

### Notes:

 `server: http://ip_address_of_your_codeproject_device/v1/vision/alpr/`

change the IP address. 