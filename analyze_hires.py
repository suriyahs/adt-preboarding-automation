import gspread # for google sheets interaction
import pandas as pd # for data handling
from oauth2client.service_account import ServiceAccountCredentials # for google sheets auth
from sklearn.ensemble import IsolationForest # the ai model
from pathlib import Path  # for finding the right files

# config:

# fix for earlier obsolete issue i was facing, void
# manually telling python where my project folder is
project_folder_path = r"C:\ADT_AI_Project"


# create a Path object from hardcoded string
base_dir = Path(project_folder_path)

# the name of my google sheet
sheet_name = "Hires - ADT Preboarding"
# tell the script where to find my key file
service_account_file = base_dir / "service_account.json" 

# the column with the numbers (days)
feature_column = "DaysSinceOffer"
# the column we'll write our "flagged" message to
alert_column = "AI_Alert"

# connect to google sheets
print(f"Looking for your key file at: {service_account_file}")
print("Connecting to google sheets...")
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]


# we convert the 'path' object to a simple 'string' so the library can read it
creds = ServiceAccountCredentials.from_json_keyfile_name(str(service_account_file), scope)

client = gspread.authorize(creds)

# try to open the sheet
try:
    sheet = client.open(sheet_name).sheet1
    print(f"Successfully connected to '{sheet_name}'.")
except gspread.exceptions.SpreadsheetNotFound:
    print(f"Spreadsheet not found. Make sure the name is exactly: '{sheet_name}'")
    exit()
except Exception as e:
    print(f"Hmm, some other error connecting: {e}")
    exit()

# start the analysis
print("Grabbing all the data from the sheet...")
data = sheet.get_all_records()
if not data:
    print("Sheet is empty.")
    exit()
    
df = pd.DataFrame(data)

# check if the columns we need actually exist
if feature_column not in df.columns or alert_column not in df.columns:
    print(f"Error: cannot find the columns. I need '{feature_column}' and '{alert_column}'.")
    print(f"All I see are these columns: {df.columns.tolist()}")
    exit()


# make sure the 'dayssinceoffer' column is all numbers, not text
df[feature_column] = pd.to_numeric(df[feature_column], errors='coerce')

# drop any rows that had blank 'dayssinceoffer'
df_clean = df.dropna(subset=[feature_column])

if df_clean.empty:
    print(f"No valid numbers found in '{feature_column}'. can't run the analysis.")
    exit()

print(f"Analyzing {len(df_clean)} rows...")

# get the data ready for the ai model
X = df_clean[[feature_column]]

# set up the anomaly detector (isolationforest)
model = IsolationForest(contamination='auto', random_state=42)
model.fit(X)


# let the model predict which rows are anomalous
# it gives a -1 for (anomaly) and 1 for "normal"
predictions = model.predict(X)

# map those predictions back to main data table
df['ai_prediction'] = 1  # default everything to "normal"
df.loc[df_clean.index, 'ai_prediction'] = predictions


# create the "flagged" message
df[alert_column] = df['ai_prediction'].apply(lambda x: "FLAGGED" if x == -1 else "")

print("Analysis complete.")

# update the sheet with the results
print("Sending the 'flagged' warnings back to google sheets...")

# get the list of "flagged" or "" values to write
alerts_to_write = list(df[alert_column])

# find the column number for 'ai_alert' (like 1, 2, 3...)
try:
    alert_col_index = df.columns.tolist().index(alert_column) + 1
except ValueError:
    print(f"Fatal error: couldn't find the '{alert_column}' index.")
    exit()


# prepare all the cells for a fast batch update
cells_to_update = []
for i, val in enumerate(alerts_to_write, start=2): # start from row 2 (to skip header)
    cell = gspread.Cell(row=i, col=alert_col_index, value=str(val))
    cells_to_update.append(cell)

# send all the updates in one go
if cells_to_update:
    sheet.update_cells(cells_to_update)
    print("Success! Your sheet is updated.")
else:
    print("No cells needed updating.") # this should not happen normally