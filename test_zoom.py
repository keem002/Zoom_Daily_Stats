import requests
import base64

ACCOUNT_ID = "-4alyWSvSeay-Iz89zKrpA"
CLIENT_ID = "ECrXUAlnQTevG5hLyuYk0A"
CLIENT_SECRET = "mwuXDnpk39LNuvOEgHe2nCmVz3SAsmog"

def get_access_token():
    url = f"https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}"

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded}"
    }

    response = requests.post(url, headers=headers)
    return response.json()   # ✅ IMPORTANT



def get_participants(meeting_id, token):
    participants = []
    next_page_token = ""

    while True:
        url = f"https://api.zoom.us/v2/report/meetings/{meeting_id}/participants?page_size=300&next_page_token={next_page_token}"

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(url, headers=headers).json()

        participants.extend(response.get("participants", []))

        next_page_token = response.get("next_page_token")

        if not next_page_token:
            break

    return participants



token_data = get_access_token()
print(token_data)  # optional, to see output

token = token_data["access_token"]

get_participants("7587549734", token)



