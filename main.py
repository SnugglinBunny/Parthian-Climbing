import datetime
import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from bs4 import BeautifulSoup


def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list) + 1)


if __name__ == "__main__":
    print("Tracking started")
    while True:
        # Get date time and convert to a string
        time_now = datetime.datetime.now()
        date = time_now.strftime("%d/%m/%Y")
        hour = time_now.hour
        minute = time_now.minute
        seconds = time_now.second
        day = time_now.strftime("%A")

        opening_time = 9
        closing_time = 23

        if opening_time < hour < closing_time and minute == 0 and seconds == 0:
            # Get the data from the website
            web = requests.get(
                "https://portal.rockgympro.com/portal/public/c3b9019203e4bc4404983507dbdf2359/occupancy?&iframeid=occupancyCounter&fId=1644/REA/"
            )
            soup = BeautifulSoup(web.content, "lxml")
            data = soup.find_all("script")[2].string
            data = (
                data.split("function showGym(tag) {")[0]
                .split("data = ")[1]
                .strip()[:-1:]
                .replace("'", '"')
                .replace(",    }", "}")
            )
            data = json.loads(data)
            print(
                f"It is now {time_now} and there are currently",
                data["REA"]["count"],
                "climbers in reading",
            )

            if data["REA"]["count"] > 0:
                # Connect to google sheets
                scopes = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ]
                credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    "climbing-counts-log-794cb7217642.json", scopes
                )  # access the json key you downloaded earlier
                file = gspread.authorize(
                    credentials
                )  # authenticate the JSON key with gspread
                sheet = file.open("Climbing")  # open sheet
                sheet = (
                    sheet.sheet1
                )  # replace sheet_name with the name that corresponds to yours, e.g, it can be sheet1

                # Commit the data
                next_row = next_available_row(sheet)
                sheet.update_acell(f"A{next_row}", date)
                sheet.update_acell(f"B{next_row}", day)
                sheet.update_acell(f"C{next_row}", hour)
                sheet.update_acell(f"D{next_row}", minute)
                sheet.update_acell(f"E{next_row}", data["REA"]["count"])
