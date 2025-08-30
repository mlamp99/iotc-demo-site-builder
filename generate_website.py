"""
Script to generate a simple static website from the supplied hardware
inventory and demo catalog.  Running this script will read the
spreadsheet ``Board Catalog3.xlsx`` and produce the HTML pages
``index.html``, ``inventory.html`` and ``demos.html`` inside the
``website`` folder.

The website consists of:
  * A consistent navigation bar with links back to the other pages
    of the catalog.
  * A home page (index.html) with a short introduction and summary
    statistics for the number of boards and demos available.
  * An inventory page listing all hardware boards in a card-based
    grid, showing the manufacturer, common name, part number and
    clickable links to the product page and GitHub index when
    available.  A small thumbnail of each board is displayed using
    the image URL provided in the spreadsheet.
  * A demos page providing details for every demo in the catalog.
    Each demo card displays the demo name, manufacturer, targets,
    description (pulled from the GitHub README when known, otherwise
    a placeholder inviting the user to follow the link), the first
    dashboard image and any additional demo images.  All available
    dashboard images are shown in a small grid below the description.

To extend the description for additional demos, add entries to the
``descriptions`` dictionary below.  Keys should match the GitHub
repository URL from the ``Github Link`` column of the ``Demos``
sheet.  The value should be a short human‑readable summary that can
appear on the web page.
"""

import pandas as pd
from pathlib import Path

# Location of the spreadsheet and output directory.  Resolve paths relative to the
# script file so that the generator works correctly when checked into a
# repository and run from any location.  When the script resides in
# ``catalog_website/``, it will read ``Board Catalog3.xlsx`` from the same
# folder and output the generated HTML into a ``website/`` subdirectory.
DATA_FILE = Path(__file__).resolve().parent / 'Board Catalog3.xlsx'
OUTPUT_DIR = Path(__file__).resolve().parent / 'website'

# Predefined descriptions for certain demos.  These were crafted
# manually based on the contents of the corresponding GitHub
# README files.  Adding more entries here will enrich the demos page
# automatically.  All keys must be lowercase to ease matching.
descriptions = {
    # Fall detection demo
    "https://github.com/avnet-iotconnect/avnet-iotc-mtb-ai-fall-detection": (
        "This fall detection demo integrates Infineon's ModusToolbox™ "
        "machine‑learning flow with Avnet's IoTConnect platform. The "
        "application uses data from the on‑board inertial measurement "
        "unit (IMU) to recognise when a person has fallen and reports "
        "these events to IoTConnect."
    ),
    # Imagimob ready model demo
    "https://github.com/avnet-iotconnect/avnet-iotc-mtb-ai-imagimob-rm": (
        "This project demonstrates ModusToolbox™ machine learning with "
        "Imagimob ready models, combining audio and radar sensor data. "
        "It can detect a variety of audio events such as sirens, baby "
        "cry, alarms, coughs and snoring, and also recognises hand "
        "gestures using the board's radar sensor."
    ),
    # WFI32 IoT board demo
    "https://github.com/avnet-iotconnect/iotc-azurertos-sdk/tree/main/samples/wfi32iot": (
        "This example connects the WFI32-IoT Development Board to Avnet's "
        "IoTConnect platform built on Microsoft Azure and uses Azure RTOS "
        "to simplify cloud firmware development.  The WFI32 board "
        "features integrated sensors and supports mikroBUS™ expansion for "
        "additional click‑board sensors."
    ),
    # AVR IoT Cellular Mini C SDK example
    "github.com/avnet-iotconnect/iotc-arduino-mchp-avr-sdk": (
        "IoTConnect C SDK example for the AVR IoT Cellular Mini board. "
        "The application records button presses and collects on‑board sensor readings "
        "(temperature and RGB light) and sends telemetry to IoTConnect. It also supports "
        "simple commands to control LEDs and guides you through provisioning the board and "
        "activating the cellular modem【874701100138764†L16-L33】."
    ),
    # LoRa device onboarding demos
    "github.com/avnet-iotconnect/iotc-lora-demos": (
        "Guide for onboarding LoRaWAN devices to IoTConnect. It walks through creating templates "
        "and configuring device attributes such as temperature, pressure, humidity and accelerometer for "
        "ST ASTRA1B and NUCLEO-WL55JC boards, creating LoRaWAN devices in the portal and sending telemetry "
        "and commands【292712103470442†L0-L37】."
    ),
    "https://github.com/avnet-iotconnect/iotc-lora-demos/blob/master/docs/iotc-lora-device-onboard.md": (
        "Guide for onboarding LoRaWAN devices to IoTConnect. It walks through creating templates "
        "and configuring device attributes such as temperature, pressure, humidity and accelerometer for "
        "ST ASTRA1B and NUCLEO-WL55JC boards, creating LoRaWAN devices in the portal and sending telemetry "
        "and commands【292712103470442†L0-L37】."
    ),
    # Azure RTOS STM32H5 Solar Demo
    "https://github.com/avnet-iotconnect/iotc-azurertos-stm32-h5/tree/solar-demo": (
        "Quick‑start application for the STM32H573I‑DK Discovery Kit using the IoTConnect Azure RTOS SDK. "
        "The guide demonstrates how to program the board, provision secure credentials using STM32 Trust TEE and connect "
        "the device to IoTConnect. It includes step‑by‑step instructions for flashing the demo firmware and configuring "
        "IoTConnect templates and devices【965771049940744†L0-L10】【965771049940744†L34-L56】."
    ),
    # EVSE example
    "https://github.com/avnet-iotconnect/iotc-evse-example": (
        "Electric Vehicle Supply Equipment (EVSE) demo that connects a charging station to IoTConnect. "
        "It showcases how to monitor charging sessions, report energy consumption and control the charger via "
        "cloud commands, providing a starting point for building smart EV charging solutions."
    ),
    # Renesas CK‑RA6M5 v2 demo
    "https://github.com/avnet-iotconnect/iotc-freertos-ck-ra6m5-v2-pmod/blob/master/quickstart.md": (
        "Example project for the Renesas CK‑RA6M5 v2 Cloud Kit. It uses an IoTConnect AT‑command‑enabled "
        "Wi‑Fi module (DA16600) to connect the board to IoTConnect. The demo sends telemetry and supports "
        "commands such as toggling the red LED and setting the LED blink frequency on the board【800432738539176†L0-L33】."
    ),
    # Renesas EK‑RA8M1 demo
    "https://github.com/avnet-iotconnect/iotc-freertos-ek-ra8m1-pmod/blob/main/quickstart.md": (
        "Example project for the Renesas EK‑RA8M1 evaluation kit that uses a DA16600 Wi‑Fi/BLE module to connect "
        "to IoTConnect. The application streams telemetry and allows controlling the on‑board LEDs via IoTConnect commands. "
        "It includes guidance for configuring IoTConnect credentials and automatically provisioning the Wi‑Fi module【690995123275253†L1-L39】."
    ),
    # Smart city noise detection
    "https://github.com/avnet-iotconnect/iotc-freertos-stm32-u5-ml-demo": (
        "Smart‑city noise detection demo for the STM32U5 MCU. The system uses machine‑learning to classify "
        "sounds such as alarms, dog barks, speech and car horns and runs inference locally on the microcontroller. "
        "Recognised events and confidence scores are sent to IoTConnect for visualisation【826445224230491†L13-L33】."
    ),
    # IoTConnect gateway mobile app
    "https://github.com/avnet-iotconnect/iotc-gateway-mobile-app": (
        "Mobile phone/tablet application that acts as a Bluetooth gateway for IoTConnect. "
        "The app connects to edge devices such as the ST SensorTile.box Pro, captures telemetry "
        "via BLE and forwards it to IoTConnect. It guides users through account setup, device "
        "onboarding and viewing live dashboards on the platform【468367397686330†L0-L12】【113733062754822†L1-L16】."
    ),
    # STM32 ISP tuning demo
    "https://github.com/avnet-iotconnect/iotc-isp-tune-stm32": (
        "Demonstration of remote ISP tuning using IoTConnect. On STM32MP257F Discovery Kit it allows users "
        "to stream live video, adjust image signal processor parameters like exposure and gain, and view "
        "real‑time telemetry from the image sensor through a cloud dashboard【217840730141104†L0-L18】."
    ),
    # IoTConnect Python Greengrass demos
    "https://github.com/avnet-iotconnect/iotc-python-greengrass-demos": (
        "Collection of AWS Greengrass components built with the IoTConnect Python SDK. "
        "Includes an AI vision demo that detects objects using a connected camera and BLE demos "
        "that gather battery, accelerometer, gyroscope and temperature data from sensors and send it to "
        "IoTConnect【274435493494004†L19-L33】."
    ),
    # IoTConnect Python Greengrass SDK
    "https://github.com/avnet-iotconnect/iotc-python-greengrass-sdk": (
        "Python SDK for building AWS Greengrass components that integrate with IoTConnect. "
        "The SDK provides examples showing how to send telemetry, receive commands and perform OTA updates "
        "from IoTConnect【687962983880631†L0-L9】."
    ),
    # IoTConnect Python Lite SDK on NXP FRDM i.MX 93
    "https://github.com/avnet-iotconnect/iotc-python-lite-sdk-demos/tree/main/nxp-frdm-imx-93": (
        "Quickstart demo for the NXP FRDM i.MX 93 platform using the IoTConnect Python Lite SDK. "
        "The board features tri‑radio connectivity (Wi‑Fi 6, Bluetooth 5.4 and 802.15.4), enabling rapid "
        "development of IoT applications. This project shows how to push telemetry to IoTConnect and receive "
        "commands from the cloud【754711850195754†L13-L21】."
    ),
    # ST image classification demo
    "https://github.com/avnet-iotconnect/iotc-st-image-classification/tree/initial": (
        "Image classification demo for the STM32MP2 platform. The project converts a TensorFlow model to "
        "TFLite, deploys it via IoTConnect OTA and performs inference on images from a USB or MIPI camera. "
        "It includes instructions for flashing the device, setting up the camera and running the application "
        "using a MobileNet V2 model【942375534736030†L8-L13】."
    ),
    # STM32 N6 demos
    "https://github.com/avnet-iotconnect/iotc-stm32-n6-demos": (
        "Edge AI demo for the STM32N6 platform demonstrating object detection using an embedded vision model. "
        "The application streams detection results to IoTConnect where bounding boxes and labels can be visualised【381494776928458†L16-L20】."
    ),
    "https://github.com/avnet-iotconnect/iotc-stm32-n6-demos/blob/main/doc/quickstart.md": (
        "Edge AI demo for the STM32N6 platform demonstrating object detection using an embedded vision model. "
        "The application streams detection results to IoTConnect where bounding boxes and labels can be visualised【381494776928458†L16-L20】."
    ),
    # RZBoard V2L AI camera demo
    "https://github.com/avnet-iotconnect/meta-iotconnect-docs/blob/main/quickstart/rzboardv2l.md": (
        "Quickstart guide for connecting the Renesas RZBoard V2L to IoTConnect and running the on‑board "
        "AI camera demo. The document covers flashing the SD card image, configuring the board and "
        "IoTConnect account, and using an attached USB camera for object recognition with real‑time "
        "telemetry streamed to IoTConnect【824565593290388†L19-L31】."
    ),
    # STM32MP257 EV1 image classification demo
    "https://github.com/avnet-iotconnect/meta-iotconnect-docs/blob/main/quickstart/st/stm32mp257/demo-iotc-x-linux-ai/quickstart_webinar.md": (
        "Quickstart for the STM32MP257‑EV1 evaluation board demonstrating an on‑board image classification "
        "application. It shows how to flash a custom Linux image, configure IoTConnect templates and run the "
        "demo which recognises objects using the board’s AI accelerator and streams results to IoTConnect【263021875027644†L19-L27】."
    ),
    # Build scripts for STM32MP1 Linux AI demo
    "https://github.com/avnet-iotconnect/meta-iotconnect-docs/tree/main/build/stm32mp1/mickledore-st-x-linux-ai-demo": (
        "This repository contains build scripts and documentation for generating the ST X-Linux AI demo image "
        "for the STM32MP1 platform with IoTConnect support. It is used to build and customise the Linux image "
        "rather than providing a standalone demo application."
    ),
    # Proteus NEAI demo
    "https://github.com/avnet-iotconnect/proteus-neai-demo": (
        "NEAI anomaly detection demo using the STM32MP157F Discovery Kit and the STEVAL‑PROTEUS1 sensor module. "
        "The application runs AI models on the edge to detect unusual patterns and reports anomalies to "
        "IoTConnect for real‑time monitoring【164214425624126†L0-L4】."
    ),
    # Qualcomm QCS6490 Vision AI demo
    "https://github.com/avnet/qcs6490-vision-ai-demo/pull/1": (
        "Vision AI demo for the Qualcomm QCS6490 platform. It demonstrates real‑time video analytics such as "
        "object detection and classification using the platform’s AI capabilities and streams results to IoTConnect. "
        "This link references an early pull request of the project."
    ),
    # XENSIV CO2 monitor quickstart
    "https://github.com/avnet-iotconnect/avnet-iotc-mtb-xensiv-example/blob/main/quickstart.md": (
        "Quickstart for Infineon’s XENSIV PAS CO2 kit. The guide shows how to connect the sensor board to "
        "IoTConnect using the Optiga Trust M secure element for hardware security. It walks through flashing the "
        "PSoC6 Wi‑Fi/Bluetooth controller, provisioning the secure element and registering the device on IoTConnect, "
        "then demonstrates streaming CO₂ measurements to an IoTConnect dashboard【956483977938127†L0-L20】."
    ),
    "https://github.com/avnet-iotconnect/avnet-iotc-mtb-xensiv-example/blob/main/QUICKSTART.md": (
        "Quickstart for Infineon’s XENSIV PAS CO2 kit. The guide shows how to connect the sensor board to "
        "IoTConnect using the Optiga Trust M secure element for hardware security. It walks through flashing the "
        "PSoC6 Wi‑Fi/Bluetooth controller, provisioning the secure element and registering the device on IoTConnect, "
        "then demonstrates streaming CO₂ measurements to an IoTConnect dashboard【956483977938127†L0-L20】."
    ),
    # RASynBoard puck demo
    "https://github.com/avnet/rasynboard-out-of-box-demo/blob/rasynboard_v2_tiny/docs/rasynpuckdemo.md": (
        "Wireless, battery‑operated demo for the Avnet RASynBoard showcasing a compact sensor puck. "
        "Telemetry from the puck (such as accelerometer and environmental data) is sent to an IoTConnect dashboard. "
        "The out‑of‑box application serves as a starting point for ML training and custom developments【112735431798390†L1-L9】."
    ),
    # SPARK smart parking demo
    "https://github.com/avnet/spark": (
        "SPARK is a smart parking and EV charging demo running on the Renesas RZBoard V2L. "
        "It uses a convolutional neural network to detect vehicle occupancy in real‑time, scales to hundreds "
        "of parking spots and can stream analytics data to IoTConnect or display it locally via HDMI【272053794077069†L8-L18】."
    ),
    # STSAFE / device logger demo
    "https://github.com/mlamp99/stsafe-demo": (
        "Device logger demo that manages two USB‑connected devices via serial communication. "
        "It integrates with IoTConnect to send telemetry, handle start/stop commands and store logs. "
        "The project demonstrates how to build a simple command and logging system using the IoTConnect "
        "SDK【973401288461139†L1-L10】."
    ),
    # Indeema drone solutions
    "https://indeema.com/industries/drones-and-uav": (
        "Overview of Indeema’s custom drone and UAV solutions. The company builds bespoke drones with integrated "
        "autopilot, advanced sensors and AI/IoT software to solve real‑world challenges across industries such as "
        "energy, agriculture and inspection【758468692581520†L85-L100】【758468692581520†L87-L99】."
    ),
    # Telehealth mobile app demo
    "https://saleshosted.z13.web.core.windows.net/dashboard/r2/mcp-telehealth.png": (
        "Telehealth demo using the IoTConnect mobile gateway application. Wearable or remote health sensors connect "
        "via Bluetooth to the mobile app, which forwards vital signs and events to IoTConnect for monitoring and "
        "visualisation."
    ),
    # EV charging blog (Witekio)
    "https://witekio.com/blog/ev-charging-software/": (
        "Article by Witekio discussing the challenges and considerations in EV charging software. "
        "It highlights the need for load balancing, secure user authentication, remote monitoring and integration "
        "with backend management platforms for smart EV chargers."
    ),
    # ASL classification Hackster demo
    "https://www.hackster.io/albertabeef/asl-classification-with-vitis-ai-025765": (
        "Hackster project that trains and deploys an American Sign Language (ASL) classification model using Vitis AI. "
        "The demo runs on an AMD/Xilinx platform and shows how to process camera images and send classified gestures "
        "to the cloud, which can be adapted for IoTConnect demonstrations."
    ),
    # AVR IoT Cellular Mini Hackster guide
    "https://www.hackster.io/nik-markovic/getting-started-with-avr-iot-cellular-mini-b08e05": (
        "Hackster guide for getting started with the AVR IoT Cellular Mini. It walks through setting up the board, "
        "activating the SIM, collecting sensor data and connecting to IoTConnect via the provided C SDK. "
        "The demo monitors temperature, light and button presses and sends telemetry to the cloud."
    ),
}


def load_data():
    """Load inventory and demos data from the spreadsheet.

    The inventory sheet may include additional columns beyond the standard
    fields (Manufacturer, Common Name, Partnumber, Link, Image, ImageURL,
    GithubIndex).  To preserve these extra columns (e.g. internal inventory
    counts for team members), we rename only the first seven columns to
    standard names and leave the remaining columns untouched.  All cells
    are converted to strings where appropriate and leading/trailing
    whitespace is stripped.
    """
    xl = pd.ExcelFile(DATA_FILE)
    inv_df = xl.parse('Inventory')
    demos_df = xl.parse('Demos')

    # Rename the first seven columns to standard names while preserving any
    # additional columns (e.g. inventory counts).  Some spreadsheets have
    # generic "Unnamed:" column names; we assign meaningful names here.
    col_names = inv_df.columns.tolist()
    standard_cols = ['Manufacturer', 'Common Name', 'Partnumber', 'Link', 'Image', 'ImageURL', 'GithubIndex']
    if len(col_names) >= len(standard_cols):
        new_cols = standard_cols + col_names[len(standard_cols):]
        inv_df.columns = new_cols
    else:
        # If fewer columns than expected, fill missing names
        inv_df.columns = standard_cols[:len(col_names)]

    # Drop potential duplicate header row if present
    inv_df = inv_df[inv_df['Manufacturer'].astype(str).str.lower() != 'manufacturer']

    # Trim whitespace and fill NaN with empty strings for all string columns
    inv_df = inv_df.fillna('').applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Normalise demos columns
    demos_df = demos_df.fillna('')
    return inv_df, demos_df


def generate_nav(current_page: str) -> str:
    """
    Return HTML for the navigation bar.  In addition to simple links this
    function prepends the IoTConnect logo to every page.  The logo file
    (``iotconnect_logo.png``) must be present in the output directory.  The
    ``logo`` CSS class is defined in ``style.css`` to constrain the image
    height and add margin so that it sits nicely next to the navigation
    links.  The currently active page is underlined for clarity.
    """
    links = {
        'index.html': 'Home',
        'inventory.html': 'Inventory',
        'demos.html': 'Demos',
    }
    nav_items = []
    # Insert the logo at the very beginning of the nav
    nav_items.append('<img src="iotconnect_logo.png" alt="IoTConnect logo" class="logo">')
    for page, name in links.items():
        if page == current_page:
            nav_items.append(f'<a href="{page}" style="text-decoration:underline">{name}</a>')
        else:
            nav_items.append(f'<a href="{page}">{name}</a>')
    return '<nav><div class="container">' + ' '.join(nav_items) + '</div></nav>'


def generate_index(num_boards: int, num_demos: int) -> str:
    """Generate the HTML for the landing page."""
    nav = generate_nav('index.html')
    html = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '  <title>Hardware & Demo Catalog</title>',
        '  <link rel="stylesheet" href="style.css">',
        '</head>',
        '<body>',
        nav,
        '<div class="container">',
        '  <h1>Hardware & Demo Catalog</h1>',
        '  <p>This site provides a convenient reference for the hardware platforms '
        'available to your team and the demonstration projects built on top of them. '
        'Browse the inventory to learn about each development board and explore the demos '
        'to see how they are used with Avnet\'s IoTConnect platform.</p>',
        f'  <p><strong>{num_boards}</strong> boards and <strong>{num_demos}</strong> demos are currently catalogued.</p>',
        '  <p>Use the navigation bar above to jump directly to the inventory or demos pages.</p>',
        '</div>',
        '</body>',
        '</html>'
    ]
    return '\n'.join(html)


def generate_inventory(inv_df: pd.DataFrame) -> str:
    """Generate the HTML for the inventory page."""
    nav = generate_nav('inventory.html')
    # Build manufacturer options (lowercase values for filtering)
    manufacturers = sorted({m.strip() for m in inv_df['Manufacturer'] if m.strip()})
    options = ['<option value="all">All Manufacturers</option>'] + [
        f'<option value="{m.lower()}">{m}</option>' for m in manufacturers
    ]
    # Start building the page
    body = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '  <title>Hardware Inventory</title>',
        '  <link rel="stylesheet" href="style.css">',
        '</head>',
        '<body>',
        nav,
        '<div class="container">',
        '  <h1>Hardware Inventory</h1>',
        '  <label for="inventory-filter">Filter by manufacturer:</label> ',
        '  <select id="inventory-filter">',
        *options,
        '  </select>',
        '  <input type="text" id="inventory-search" placeholder="Search..." style="margin-left:10px; padding:4px;">',
        '  <div class="grid">'
    ]
    # Iterate over boards
    for _, row in inv_df.iterrows():
        manufacturer = row['Manufacturer'].strip()
        name = row['Common Name']
        partnum = row['Partnumber']
        link = row['Link']
        image = row['ImageURL'] if row['ImageURL'] else row['Image']
        gh_index = row['GithubIndex']
        # Build card with data-manufacturer attribute
        card_parts = [
            f'<div class="card" data-manufacturer="{manufacturer.lower()}">'  # start card
        ]
        # Place the title at the top of the card. The <h2> element has a dark
        # background defined in style.css so that it stands out above the board image.
        card_parts.append(f'  <h2>{name}</h2>')
        # Use image if available. The image appears below the title.
        if image and image.lower() != 'no':
            card_parts.append(f'  <img src="{image}" alt="{name}">')
        card_parts.append(f'  <p><strong>Manufacturer:</strong> {manufacturer}</p>')
        card_parts.append(f'  <p><strong>Part Number:</strong> {partnum}</p>')
        # Add link to product page
        if link and isinstance(link, str) and link.strip() and link.lower() != 'no':
            card_parts.append(f'  <p><a href="{link}">Product page</a></p>')
        # Add GitHub index if available
        gh_index_clean = str(gh_index).strip().lower()
        if gh_index_clean and gh_index_clean not in ('', 'no', 'in github index'):
            card_parts.append(f'  <p><a href="{row["GithubIndex"]}">GitHub reference</a></p>')

        # If internal inventory columns exist (e.g. ML, KK, NM, ZA, SL, SD), display counts.
        team_members = sorted(['KK', 'ML', 'NM', 'SD', 'SL', 'ZA'])
        inventory_info = []
        for member in team_members:
            if member in row.index:
                # Use the value if not blank; default to 0
                val = row[member]
                try:
                    count = int(val) if str(val).strip() else 0
                except (ValueError, TypeError):
                    count = 0
                inventory_info.append(f'<span><strong>{member}:</strong> {count}</span>')
        if inventory_info:
            card_parts.append('  <p><strong>Team inventory:</strong></p>')
            card_parts.append('  <div class="inventory-counts">' + ' '.join(inventory_info) + '</div>')
        card_parts.append('</div>')  # close card
        body.append('\n'.join(card_parts))
    body.extend([
        '  </div>',  # close grid
        '</div>',    # close container
        # Modal overlay for image expansion
        '<div id="image-modal" class="image-modal">',
        '  <span class="close">&times;</span>',
        '  <img id="modal-img" src="" alt="Expanded image">',
        '</div>',
        # Filtering, search and modal script
        '<script>',
        'document.addEventListener("DOMContentLoaded", function() {',
        '  const select = document.getElementById("inventory-filter");',
        '  const searchInput = document.getElementById("inventory-search");',
        '  const cards = document.querySelectorAll(".card");',
        '  function filterCards() {',
        '    const selected = select.value;',
        '    const query = searchInput.value.toLowerCase();',
        '    cards.forEach(card => {',
        '      const matchesManufacturer = (selected === "all" || card.dataset.manufacturer === selected);',
        '      const matchesQuery = card.textContent.toLowerCase().includes(query);',
        '      if (matchesManufacturer && matchesQuery) {',
        '        card.style.display = "";',
        '      } else {',
        '        card.style.display = "none";',
        '      }',
        '    });',
        '  }',
        '  select.addEventListener("change", filterCards);',
        '  searchInput.addEventListener("input", filterCards);',
        '  // Image modal functionality',
        '  const modal = document.getElementById("image-modal");',
        '  const modalImg = document.getElementById("modal-img");',
        '  const closeBtn = modal.querySelector(".close");',
        '  document.querySelectorAll(".card img").forEach(img => {',
        '    img.addEventListener("click", function(e) {',
        '      modalImg.src = this.src;',
        '      modal.style.display = "flex";',
        '      e.stopPropagation();',
        '    });',
        '  });',
        '  modal.addEventListener("click", function(e) {',
        '    if (e.target === modal || e.target === closeBtn) {',
        '      modal.style.display = "none";',
        '    }',
        '  });',
        '});',
        '</script>',
        '</body>',
        '</html>'
    ])
    return '\n'.join(body)


def generate_demos(demos_df: pd.DataFrame) -> str:
    """Generate the HTML for the demos page."""
    nav = generate_nav('demos.html')
    # Build manufacturer options for demos (unique non-empty values)
    manufacturers = sorted({row['Manufacturer'].strip() for _, row in demos_df.iterrows() if row['Manufacturer'].strip()})
    options = ['<option value="all">All Manufacturers</option>'] + [
        f'<option value="{m.lower()}">{m}</option>' for m in manufacturers
    ]
    parts = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '  <meta charset="UTF-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '  <title>Demo Catalog</title>',
        '  <link rel="stylesheet" href="style.css">',
        '</head>',
        '<body>',
        nav,
        '<div class="container">',
        '  <h1>Demo Catalog</h1>',
        '  <label for="demos-filter">Filter by manufacturer:</label> ',
        '  <select id="demos-filter">',
        *options,
        '  </select>',
        '  <input type="text" id="demos-search" placeholder="Search..." style="margin-left:10px; padding:4px;">',
        '  <div class="grid">'
    ]

    # Iterate over demos
    for _, row in demos_df.iterrows():
        manufacturer = row['Manufacturer'].strip()
        demo_name = row['Demo'].strip()
        targets = [row[col].strip() for col in ['Target 1', 'Target 2', 'Target 3', 'Target 4'] if row[col]]
        gh_link = row['Github Link'].strip()
        # Determine description
        # Prefer the description provided in the spreadsheet if available.
        description = row['Demo Description'].strip()
        # If the spreadsheet description is empty, fall back to a predefined summary for
        # the given GitHub link (stored in the ``descriptions`` dictionary).  The
        # dictionary key is the lower‑case of the link to ensure case‑insensitive matching.
        if not description:
            desc_key = gh_link.lower()
            description = descriptions.get(desc_key, '').strip()
        # If neither the spreadsheet nor dictionary provides a description, use a generic message.
        if not description:
            description = 'Refer to the linked repository for more details.'
        # Collect dashboard images
        dash_cols = ['Dashboard 1', 'Dashboard 2', 'Dashboard 3', 'Dashboard 4', 'Dashboard 5', 'Dashboard 6']
        dashboards = [row[col] for col in dash_cols if isinstance(row[col], str) and row[col].strip() and row[col].strip() != '-']
        # Collect demo images
        demo_img_cols = ['Demo Image 1', 'Demo Image 2', 'Demo Image 3', 'Demo Image 4', 'Demo Image 5']
        demo_imgs = [row[col] for col in demo_img_cols if isinstance(row[col], str) and row[col].strip()]

        card = [
            f'<div class="card" data-manufacturer="{manufacturer.lower()}">',
            f'  <h2>{demo_name}</h2>',
            f'  <p><strong>Manufacturer:</strong> {manufacturer}</p>'
        ]
        # Show targets if any
        if targets:
            target_list = ', '.join(filter(None, targets))
            card.append(f'  <p><strong>Target boards:</strong> {target_list}</p>')

        # Derive simple tags from the demo name.  Split on whitespace and hyphens,
        # convert to lower case and remove common stopwords to produce concise tags.
        import re
        ignore = {"ai", "kit", "demo", "demos", "project", "and", "the", "with", "example", "fall", "sensor", "detection", "autonomous", "mini", "all"}
        words = re.split(r'[\s\-]+', demo_name)
        tags = [w.lower() for w in words if w and w.lower() not in ignore]
        if tags:
            tag_spans = ' '.join([f'<span class="tag">{t}</span>' for t in tags])
            card.append(f'  <div class="tags">{tag_spans}</div>')

        card.append(f'  <p>{description}</p>')
        # Show GitHub link if available
        if gh_link and gh_link.lower() != 'no' and gh_link.lower() != '-':
            # ensure https prefix
            prefix_link = gh_link
            if not gh_link.lower().startswith('http'):
                prefix_link = 'https://' + gh_link
            card.append(f'  <p><a href="{prefix_link}">GitHub Repository</a></p>')
        # Insert dashboard images grid
        if dashboards:
            card.append('  <h3>Dashboard Snapshots</h3>')
            card.append('  <div class="dash-grid">')
            for d in dashboards:
                if d and d != '-':
                    card.append(f'    <img src="{d}" alt="Dashboard image">')
            card.append('  </div>')
        # Insert demo images
        if demo_imgs:
            card.append('  <h3>Demo Images</h3>')
            card.append('  <div class="dash-grid">')
            for img in demo_imgs:
                card.append(f'    <img src="{img}" alt="Demo image">')
            card.append('  </div>')
        card.append('</div>')
        parts.append('\n'.join(card))

    parts.extend([
        '  </div>',  # close grid
        '</div>',    # close container
        # Modal overlay for image expansion
        '<div id="image-modal" class="image-modal">',
        '  <span class="close">&times;</span>',
        '  <img id="modal-img" src="" alt="Expanded image">',
        '</div>',
        # Filtering, search and modal script for demos
        '<script>',
        'document.addEventListener("DOMContentLoaded", function() {',
        '  const select = document.getElementById("demos-filter");',
        '  const searchInput = document.getElementById("demos-search");',
        '  const cards = document.querySelectorAll(".card");',
        '  function filterCards() {',
        '    const selected = select.value;',
        '    const query = searchInput.value.toLowerCase();',
        '    cards.forEach(card => {',
        '      const matchesManufacturer = (selected === "all" || card.dataset.manufacturer === selected);',
        '      const matchesQuery = card.textContent.toLowerCase().includes(query);',
        '      if (matchesManufacturer && matchesQuery) {',
        '        card.style.display = "";',
        '      } else {',
        '        card.style.display = "none";',
        '      }',
        '    });',
        '  }',
        '  select.addEventListener("change", filterCards);',
        '  searchInput.addEventListener("input", filterCards);',
        '  // Image modal functionality',
        '  const modal = document.getElementById("image-modal");',
        '  const modalImg = document.getElementById("modal-img");',
        '  const closeBtn = modal.querySelector(".close");',
        '  document.querySelectorAll(".card img").forEach(img => {',
        '    img.addEventListener("click", function(e) {',
        '      modalImg.src = this.src;',
        '      modal.style.display = "flex";',
        '      e.stopPropagation();',
        '    });',
        '  });',
        '  modal.addEventListener("click", function(e) {',
        '    if (e.target === modal || e.target === closeBtn) {',
        '      modal.style.display = "none";',
        '    }',
        '  });',
        '});',
        '</script>',
        '</body>',
        '</html>'
    ])
    return '\n'.join(parts)


def build_site():
    """Generate all pages and write them to the output directory."""
    inv_df, demos_df = load_data()
    num_boards = len(inv_df)
    num_demos = len(demos_df)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    index_html = generate_index(num_boards, num_demos)
    (OUTPUT_DIR / 'index.html').write_text(index_html, encoding='utf-8')

    inventory_html = generate_inventory(inv_df)
    (OUTPUT_DIR / 'inventory.html').write_text(inventory_html, encoding='utf-8')

    demos_html = generate_demos(demos_df)
    (OUTPUT_DIR / 'demos.html').write_text(demos_html, encoding='utf-8')


if __name__ == '__main__':
    build_site()