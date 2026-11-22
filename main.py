
import csv


def analyze_login_logs(file, threshold=3):
    """
    Analyse authentication logs and identify
    IP addresses with repeated failed logins.
    """

    required_columns = {"timestamp", "ip_address", "status"}

    reader = csv.DictReader(file)

    # Validate CSV columns
    if not reader.fieldnames:
        raise ValueError("The CSV file is empty or has no header.")

    reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]

    if not required_columns.issubset(set(reader.fieldnames)):
        raise ValueError(
            "CSV must contain: timestamp, ip_address, status"
        )

    total_attempts = 0
    failed_count = 0
    success_count = 0

    ip_attempts = {}
    login_records = []
    invalid_records = 0

    for record in reader:

        # Clean input values
        timestamp = (record.get("timestamp") or "").strip()
        ip = (record.get("ip_address") or "").strip()
        status = (record.get("status") or "").strip().upper()

        # Skip incomplete or invalid records
        if not timestamp or not ip or status not in {"FAILED", "SUCCESS"}:
            invalid_records += 1
            continue

        total_attempts += 1

        login_records.append({
            "timestamp": timestamp,
            "ip_address": ip,
            "status": status
        })

        if status == "FAILED":
            failed_count += 1
            ip_attempts[ip] = ip_attempts.get(ip, 0) + 1

        elif status == "SUCCESS":
            success_count += 1

    # Identify suspicious IP addresses
    suspicious_ips = {
        ip: count
        for ip, count in ip_attempts.items()
        if count >= threshold
    }

    return {
        "total_attempts": total_attempts,
        "failed_count": failed_count,
        "success_count": success_count,
        "ip_attempts": ip_attempts,
        "suspicious_ips": suspicious_ips,
        "records": login_records,
        "invalid_records": invalid_records
    }
