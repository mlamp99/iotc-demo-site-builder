
# IoTConnect Hardware & Demo Catalog

This repository contains the source files and generator script for a static catalog website.

## Contents

- **website/** – A fully generated static website that lists available hardware boards and demos, including images, descriptions, and IoTConnect dashboards.  The site features manufacturer filtering, search functionality, image enlargement on click, and a navigation bar with an IoTConnect logo.
  It also displays per‑team inventory counts if columns for team member initials (e.g. KK, ML, NM, SD, SL, ZA) are added to the `Inventory` sheet, and shows simple tags for each demo derived from its name.
- **generate_website.py** – A Python script that reads the `Board Catalog3.xlsx` spreadsheet and regenerates the HTML files in the `website/` folder.  Update the spreadsheet and rerun this script to refresh the site.
- **Board Catalog3.xlsx** – Spreadsheet containing the hardware inventory (in the `Inventory` sheet) and demo information (in the `Demos` sheet).  The demo descriptions column has been updated with detailed summaries based on the linked GitHub repositories.

## How to Regenerate the Website

1. Make sure you have Python 3 with `pandas` and `openpyxl` installed.

```bash
pip install pandas openpyxl
```

2. Edit or update `Board Catalog3.xlsx` as needed.  The `Inventory` sheet lists all boards (manufacturer, name, part number, links and images), while the `Demos` sheet lists available demos with their targets, dashboard images and GitHub links.  When possible, provide a GitHub link for each demo so the script can automatically pull a detailed description.

   You can also add columns for your team members’ initials (e.g. KK, ML, NM, SD, SL, ZA) in the `Inventory` sheet to keep track of how many of each board are held by each person.  The generator will display these counts on the inventory cards.  Leave cells blank or set to zero for boards with no inventory.

3. Run the script to regenerate the site:

```bash
python generate_website.py
```

The HTML files in `website/` will be overwritten with the latest data.  You can open `website/index.html` in a browser to view the updated catalog.

## Usage

- **inventory.html** – shows the list of development boards.  Use the manufacturer dropdown and search box to filter boards.  Click an image to enlarge it.
- **demos.html** – lists all available demo projects with improved descriptions, dashboard images and GitHub links.  Use the manufacturer filter and search to quickly find demos.  Dashboard and demo images can be clicked to view a larger version.

Feel free to commit this directory to your GitHub repository.  Subsequent updates to the spreadsheet or script can be pushed, and the site can be regenerated accordingly.
