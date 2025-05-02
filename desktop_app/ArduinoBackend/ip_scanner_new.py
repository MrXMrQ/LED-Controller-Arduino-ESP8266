#!/usr/bin/env python3
import subprocess
import re
import sys
import socket
import time
import threading
import os
from typing import Dict, List, Set, Tuple


def get_local_ip() -> str:
    """Ermittelt die lokale IP-Adresse des eigenen Rechners."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
    return local_ip


def get_network_prefix(ip: str) -> str:
    """Extrahiert den Netzwerk-Präfix aus einer IP-Adresse."""
    parts = ip.split(".")
    return f"{parts[0]}.{parts[1]}.{parts[2]}"


def scan_arp_table() -> Dict[str, str]:
    """
    Liest die ARP-Tabelle aus, um aktive Geräte zu finden.
    Gibt ein Dictionary mit IP → MAC-Adresse zurück.
    """
    active_hosts = {}

    try:
        if sys.platform.startswith("win"):
            output = subprocess.check_output("arp -a", shell=True).decode(
                "utf-8", errors="ignore"
            )
        else:  # Linux/Mac
            output = subprocess.check_output("arp -an", shell=True).decode(
                "utf-8", errors="ignore"
            )

        ip_pattern = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        mac_pattern = r"([0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2})"

        for line in output.splitlines():
            ip_match = re.search(ip_pattern, line)
            mac_match = re.search(mac_pattern, line)

            if ip_match and mac_match:
                ip = ip_match.group(1)
                mac = mac_match.group(1)
                if not mac.lower().startswith(
                    ("00:00:00", "ff:ff:ff")
                ):  # Ignoriere ungültige MACs
                    active_hosts[ip] = mac

        print(f"ARP-Tabelle: {len(active_hosts)} aktive Hosts gefunden")
    except Exception as e:
        print(f"Fehler beim Lesen der ARP-Tabelle: {e}")

    return active_hosts


def determine_vendor(mac: str) -> str:
    """
    Versucht, den Hersteller basierend auf der MAC-Adresse zu ermitteln.
    Vereinfachte Implementierung mit häufigen Herstellern.
    """
    mac = mac.lower().replace("-", ":")
    mac_prefix = mac[:8]

    # Häufige MAC-Präfixe (sehr vereinfacht, nicht vollständig)
    vendors = {
        "00:1a:79": "Nintendo",
        "00:50:ba": "D-Link",
        "00:17:88": "Philips Lighting",
        "b8:27:eb": "Raspberry Pi",
        "8c:85:90": "Apple",
        "58:55:ca": "Apple",
        "3c:e0:72": "Apple",
        "28:cf:da": "Apple",
        "00:11:32": "Synology",
        "dc:a6:32": "Raspberry Pi",
        "d8:3a:dd": "Google/Nest",
        "f4:f5:d8": "Google",
        "00:03:7f": "Atheros",
        "a0:b4:a5": "Samsung",
        "b0:df:3a": "Samsung",
        "94:63:d1": "Samsung",
        "b8:e8:56": "Samsung",
        "30:ae:a4": "Xiaomi/Espressif",
        "18:fe:34": "Xiaomi/Espressif",
        "60:01:94": "Xiaomi/Espressif",
        "ac:d0:74": "Xiaomi/Espressif",
        "5c:cf:7f": "Xiaomi/Espressif",
        "8c:aa:b5": "Xiaomi/Espressif",
        "8c:ce:4e": "Nintendo",
        "cc:9e:a2": "Amazon",
        "c0:ee:fb": "OnePlus",
        "94:65:2d": "OnePlus",
        "00:04:4b": "Nintendo",
        "e0:63:da": "Arduino",
        "a0:20:a6": "Arduino",
        "90:a2:da": "Arduino",
        "1a:fe:34": "Xiaomi/Espressif",
    }

    for prefix, vendor in vendors.items():
        if mac.startswith(prefix):
            return vendor

    return "Unbekannt"


def ping_sweep(subnet_prefix: str, start: int = 1, end: int = 254) -> Set[str]:
    """
    Führt einen schnellen Ping-Scan durch.

    Args:
        subnet_prefix: Die ersten drei Oktette des Subnetzes (z.B. "192.168.1")
        start: Startpunkt für den letzten Oktett
        end: Endpunkt für den letzten Oktett

    Returns:
        Set mit erreichbaren IP-Adressen
    """
    reachable_ips = set()
    threads = []
    lock = threading.Lock()

    def ping_host(ip: str) -> None:
        param = "-n" if sys.platform.startswith("win") else "-c"
        command = ["ping", param, "1", "-w", "1", ip]

        try:
            if sys.platform.startswith("win"):
                # Unter Windows Ausgaben unterdrücken
                with open(os.devnull, "w") as devnull:
                    subprocess.check_call(
                        command, stdout=devnull, stderr=devnull, timeout=1.5
                    )
            else:
                subprocess.check_call(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=1.5,
                )

            with lock:
                reachable_ips.add(ip)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass

    print(
        f"Führe schnellen Ping-Scan für {subnet_prefix}.{start} bis {subnet_prefix}.{end} durch..."
    )
    start_time = time.time()

    # Starte Threads für den Ping-Scan
    for i in range(start, end + 1):
        ip = f"{subnet_prefix}.{i}"
        thread = threading.Thread(target=ping_host, args=(ip,))
        thread.daemon = True
        threads.append(thread)
        thread.start()

        # Begrenze die Anzahl gleichzeitiger Threads
        if len(threads) >= 50:
            for t in threads:
                t.join(0.1)  # Kurze Wartezeit
            threads = [t for t in threads if t.is_alive()]

    # Warte auf Abschluss aller Threads
    for t in threads:
        t.join()

    duration = time.time() - start_time
    print(
        f"Ping-Scan abgeschlossen in {duration:.2f} Sekunden, {len(reachable_ips)} aktive Hosts gefunden."
    )
    return reachable_ips


def resolve_hostname(ip: str) -> str:
    """Versucht, den Hostnamen für eine IP-Adresse zu ermitteln."""
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except (socket.herror, socket.gaierror):
        return ""


def scan_network() -> List[Tuple[str, str, str, str]]:
    """
    Scannt das Netzwerk nach aktiven Geräten.

    Returns:
        Liste mit Tupeln (IP, MAC, Hostname, Hersteller)
    """
    # Schritt 1: ARP-Tabelle auslesen (sehr schnell)
    arp_hosts = scan_arp_table()

    # Schritt 2: Eigene IP ermitteln und Netzwerkpräfix extrahieren
    local_ip = get_local_ip()
    network_prefix = get_network_prefix(local_ip)

    # Schritt 3: Schneller Ping-Scan, falls ARP-Tabelle wenig Ergebnisse liefert
    active_ips = set(arp_hosts.keys())
    if len(active_ips) < 5:
        ping_results = ping_sweep(network_prefix)
        active_ips.update(ping_results)

    # Schritt 4: Hostname-Auflösung und Herstellerermittlung
    devices = []
    print("Sammle Details zu den gefundenen Geräten...")

    for ip in sorted(active_ips, key=lambda x: [int(octet) for octet in x.split(".")]):
        mac = arp_hosts.get(ip, "")

        # Falls keine MAC in ARP-Tabelle, versuche erneut ARP abzufragen
        if not mac and ip not in arp_hosts:
            try:
                if sys.platform.startswith("win"):
                    subprocess.call(
                        f"ping -n 1 -w 500 {ip}",
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                else:
                    subprocess.call(
                        f"ping -c 1 -W 1 {ip}",
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                time.sleep(0.2)  # Kurz warten, damit ARP-Tabelle aktualisiert wird

                # Erneut ARP-Tabelle für dieses Gerät abfragen
                if sys.platform.startswith("win"):
                    cmd_output = subprocess.check_output(
                        f"arp -a {ip}", shell=True
                    ).decode("utf-8")
                else:
                    cmd_output = subprocess.check_output(
                        f"arp -n {ip}", shell=True
                    ).decode("utf-8")

                mac_pattern = r"([0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2})"
                mac_match = re.search(mac_pattern, cmd_output)
                if mac_match:
                    mac = mac_match.group(1)
            except Exception:
                pass

        # Hostname und Hersteller ermitteln
        hostname = resolve_hostname(ip)
        vendor = determine_vendor(mac) if mac else "Unbekannt"

        devices.append((ip, mac, hostname, vendor))

    return devices


def main():
    print("Ultraschneller Heimnetzwerk-Scanner")
    print("----------------------------------")

    start_time = time.time()
    devices = scan_network()
    duration = time.time() - start_time

    print(f"\nScan abgeschlossen in {duration:.2f} Sekunden")
    print(f"Gefundene Geräte im Netzwerk: {len(devices)}")
    print("\nIP-Adresse      MAC-Adresse           Hersteller       Hostname")
    print("-" * 80)

    for ip, mac, hostname, vendor in devices:
        # Formatiere die Ausgabe mit fester Breite
        mac_str = mac if mac else "nicht ermittelt"
        vendor_str = vendor[:15].ljust(15)  # Hersteller auf 15 Zeichen begrenzen
        hostname_short = hostname[:30] if hostname else ""

        print(f"{ip.ljust(16)} {mac_str.ljust(22)} {vendor_str} {hostname_short}")

    print("\nFertig! Um mehr Details zu einem Gerät zu erhalten, versuchen Sie:")
    print("- 'nslookup [IP-Adresse]' für DNS-Information")
    print("- 'ping [IP-Adresse]' für Erreichbarkeit")


main()
