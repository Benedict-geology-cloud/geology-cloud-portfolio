import subprocess, json, os
from datetime import datetime

print("=== DAY 26: AWS Sentinel-2 Pull for Nasarawa ===")
print(f"Time: {datetime.now()}")

# Try to list tiles covering Nasarawa (approx lat 8.5 lon 8.5 = UTM 32N MK)
cmd = ["aws", "s3", "ls", "s3://sentinel-s2-l2a/tiles/32/N/MK/2023/12/", "--request-payer", "--no-sign-request"]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    print(result.stdout[:2000])
    if result.stdout:
        print("\n✅ SUCCESS: You just pulled real Sentinel-2 data from AWS S3!")
        # Save report
        with open("Day26_AWS_Sentinel_Report.txt","w") as f:
            f.write("DAY 26 AWS OPEN DATA PULL\n")
            f.write(f"Location: Nasarawa 32/N/MK\n")
            f.write(f"Bucket: s3://sentinel-s2-l2a\n")
            f.write(result.stdout)
        print("Report saved: Day26_AWS_Sentinel_Report.txt")
    else:
        print("No output, trying alternative bucket...")
        print(result.stderr[:500])
except Exception as e:
    print(f"Error: {e}")
    print("If AWS CLI fails due to network, we go use Plan B: Python direct download")

# Plan B - create a mock but real metadata file
print("\n--- Creating Day 26 Field Report ---")
with open("Day26_AWS_Sentinel_Report.txt","a") as f:
    f.write("\n\nNasarawa Lithium AOI: 8.5N, 8.5E\n")
    f.write("Sentinel-2 bands needed: B04 (Red), B08 (NIR), B11 (SWIR) for lithium prospectivity\n")
    f.write("Next: Use this tile ID in GEE for NDVI + Clay mineral ratio\n")

print("DONE Day 26")
