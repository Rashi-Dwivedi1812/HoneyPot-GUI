"""
backend_app.py
Low-interaction honeypot backend with credential capture.
"""

import socket, threading, logging, csv, datetime, os, time

BASE_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_CSV = os.path.join(LOG_DIR, "connections.csv")
CREDS_CSV = os.path.join(LOG_DIR, "credentials.csv")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

PORTS = {"ssh": 2222, "http": 8080, "ftp": 2121}

BANNERS = {
    "ssh": "SSH-2.0-OpenSSH_7.4p1 Debian-10\r\n",
    "http": "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Honeypot</h1>",
    "ftp": "220 (vsFTPd 3.0.3)\r\n"
}

_stop_event = threading.Event()
_listener_threads = []


# -------------------------------
# Helper Functions
# -------------------------------
def summarize_payload(data):
    try:
        s = data.decode(errors="replace").strip()
        return (s[:200] + "...") if len(s) > 200 else s
    except Exception:
        return "<binary>"


def log_connection(service, src_ip, src_port, payload_summary, raw_data):
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    first = not os.path.exists(LOG_CSV) or os.path.getsize(LOG_CSV) == 0
    with open(LOG_CSV, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if first:
            writer.writerow(["timestamp","service","src_ip","src_port","payload_summary","raw_payload"])
        writer.writerow([timestamp, service, src_ip, src_port, payload_summary, raw_data.hex()[:400]])


def log_credentials(service, ip, username, password):
    first = not os.path.exists(CREDS_CSV) or os.path.getsize(CREDS_CSV) == 0
    with open(CREDS_CSV, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if first:
            writer.writerow(["service", "ip", "username", "password"])
        writer.writerow([service, ip, username, password])


def capture_credentials(conn, addr, service):
    try:
        conn.sendall(b"login: ")
        username = conn.recv(1024).strip().decode(errors="ignore")

        conn.sendall(b"Password: ")
        password = conn.recv(1024).strip().decode(errors="ignore")

        log_credentials(service, addr[0], username, password)

        logging.info(f"[ALERT] Credentials captured from {addr[0]} -> {username}:{password}")

        conn.sendall(b"\r\nLogin failed\r\n")

    except Exception as e:
        logging.error(f"Credential capture error: {e}")


# -------------------------------
# Main Handler Class
# -------------------------------
class ServiceHandler(threading.Thread):
    def __init__(self, serv_name, listen_port):
        super().__init__(daemon=True)
        self.serv_name = serv_name
        self.port = listen_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(5)

        logging.info(f"{serv_name.upper()} honeypot listening on 0.0.0.0:{self.port}")

    def run(self):
        while not _stop_event.is_set():
            try:
                self.sock.settimeout(1.0)
                conn, addr = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

    def handle_client(self, conn, addr):
        src_ip, src_port = addr
        logging.info(f"Connection to {self.serv_name} from {src_ip}:{src_port}")

        try:
            banner = BANNERS.get(self.serv_name, "")
            if banner:
                conn.sendall(banner.encode())

            conn.settimeout(5.0)

            # -------------------------------
            # SERVICE BEHAVIOR
            # -------------------------------
            if self.serv_name in ["ssh", "ftp"]:
                capture_credentials(conn, addr, self.serv_name)

            elif self.serv_name == "http":
                try:
                    data = conn.recv(4096)
                except:
                    data = b""

                payload_summary = summarize_payload(data)
                log_connection(self.serv_name, src_ip, src_port, payload_summary, data)

                # send fake page
                conn.sendall(BANNERS["http"].encode())

        except Exception as e:
            logging.error(f"Error handling client: {e}")

        finally:
            try:
                conn.shutdown(socket.SHUT_RDWR)
            except:
                pass
            conn.close()


# -------------------------------
# CONTROL FUNCTIONS
# -------------------------------
def start():
    global _stop_event, _listener_threads

    if _listener_threads:
        return _listener_threads

    _stop_event.clear()
    _listener_threads = []

    for name, port in PORTS.items():
        h = ServiceHandler(name, port)
        h.start()
        _listener_threads.append(h)

    return _listener_threads


def stop():
    global _stop_event, _listener_threads

    _stop_event.set()

    # unblock sockets
    for port in PORTS.values():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", port))
            s.close()
        except:
            pass

    time.sleep(0.5)
    _listener_threads = []