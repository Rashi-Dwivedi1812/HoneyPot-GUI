# 🛡️ GUI-Based Honeypot System

A **low-interaction honeypot with a graphical user interface (GUI)** built using Python.
This project simulates vulnerable network services (SSH, HTTP, FTP) to **attract attackers, capture their activity, and log credentials** in a safe environment.

---

## 🚀 Features

* 🔐 Simulates multiple services:

  * SSH (Port 2222)
  * HTTP (Port 8080)
  * FTP (Port 2121)
* 📊 Real-time logging of connections
* 🧾 Credential capture (username & password)
* 🖥️ Tkinter-based GUI control panel
* 📁 CSV-based log storage
* 🎭 Fake login page for simulation

---

## 🧠 Project Overview

This project demonstrates how a **honeypot system** works by mimicking real services and recording attacker behavior.

### 🔄 Workflow

1. Start honeypot using GUI
2. System opens network ports
3. Attacker connects to services
4. Honeypot logs activity and credentials
5. Logs are displayed in GUI and stored in CSV files

---

## 🏗️ Tech Stack

* **Python**
* **Socket Programming**
* **Threading**
* **Tkinter (GUI)**
* **CSV (Logging)**

---

## 📁 Project Structure

```
honeypot_gui_project/
│
├── backend_app.py        # Core honeypot logic
├── gui.py                # GUI interface (Tkinter)
├── logs/
│   ├── connections.csv   # Connection logs
│   └── credentials.csv   # Captured credentials
├── requirements.txt
├── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```
git clone https://github.com/your-username/honeypot-gui-project.git
cd honeypot-gui-project
```

### 2️⃣ Install dependencies

```
pip install -r requirements.txt
```

*(Tkinter usually comes pre-installed)*

---

## ▶️ Running the Project

```
python gui.py
```

### 🟢 Then:

* Click **Start Honeypot**
* Services will start on ports:

  * 2222 (SSH)
  * 8080 (HTTP)
  * 2121 (FTP)

---

## 🧪 Testing the Honeypot

### 🔹 HTTP Test

```
curl http://localhost:8080
```

### 🔹 SSH Test

```
telnet localhost 2222
```

### 🔹 FTP Test

```
telnet localhost 2121
```

👉 Enter any username/password to simulate attack

---

## 📊 Logs

### 📁 connections.csv

Stores:

* Timestamp
* Service used
* IP address
* Payload

### 📁 credentials.csv

Stores:

* Username
* Password
* Source IP

---

## 🔐 How It Works

* Accepts incoming connections using sockets
* Sends fake service banners
* Captures user input (credentials)
* Logs all activity in CSV files
* Displays logs in GUI

---

## ⚠️ Limitations

* Low-interaction honeypot
* No real system access provided
* Not suitable for production use

---

## 🚀 Future Improvements

* High-interaction honeypot
* Database integration
* Real-time alerts
* Attack visualization dashboard

---

## 🎯 Use Cases

* Cybersecurity learning
* Ethical hacking practice
* Intrusion detection research
* Academic projects

---

## 📌 License

This project is for **educational purposes only**.

---