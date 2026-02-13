# 📊 Zoom Daily Stats

Zoom Daily Stats is a Python-based automation tool that fetches, processes, and generates daily meeting statistics from Zoom data.

This project helps in tracking meeting activity, generating reports, and storing structured data for analysis.

---

## 🚀 Features

- Fetch Zoom meeting data
- Process daily statistics
- Generate CSV reports
- Automated data handling
- Secure Google Cloud authentication
- Clean and modular Python structure

---

## 🛠️ Tech Stack

- Python 3
- Zoom API
- Google Cloud Service Account
- CSV Processing
- Environment Variables

---

## 📂 Project Structure

```
Zoom_Daily_Stats/
│── main.py
│── test_zoom.py
│── daily_report.csv
│── service_account.json   (ignored from Git)
│── .gitignore
│── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```
git clone https://github.com/keem002/Zoom_Daily_Stats.git
```

### 2️⃣ Navigate to the Project Folder

```
cd Zoom_Daily_Stats
```

### 3️⃣ Install Required Dependencies

If you have a `requirements.txt` file:

```
pip install -r requirements.txt
```

Or manually install required packages:

```
pip install requests pandas google-auth
```

---

## 🔐 Google Cloud Setup

1. Create a Service Account in Google Cloud Console.
2. Generate a JSON key.
3. Rename it to:

```
service_account.json
```

4. Place it inside the project folder.
5. Ensure `.gitignore` includes:

```
service_account.json
```

⚠️ Never upload service account credentials to GitHub.

---

## ▶️ Run the Project

```
python main.py
```

The script will:

- Fetch Zoom data
- Process statistics
- Generate/update `daily_report.csv`

---

## 📈 Output

The generated report:

```
daily_report.csv
```

Contains structured daily meeting data ready for analysis or sharing.

---

## 🎯 Purpose of the Project

This project demonstrates:

- API integration
- Data processing
- Automation scripting
- Secure credential handling
- Real-world backend workflow

---

## 👩‍💻 Author

**Keem Pohare**  
Computer Science Student  
Python Developer | Backend Enthusiast  

---

## 📜 License

This project is created for educational and development purposes.
