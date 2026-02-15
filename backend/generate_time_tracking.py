import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = "/api/auth/login"
REPORTS_ENDPOINT = "/api/reports"

# Test user credentials
TEST_USER = {
    "email": "sairaj@gmail.com",
    "password": "Sairaj@123"
}

def get_auth_token():
    """Get authentication token for the test user"""
    try:
        response = requests.post(
            f"{BASE_URL}{LOGIN_ENDPOINT}",
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["access_token"]
        else:
            print(f"Login failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def generate_time_tracking_report(token, project_key="SCRUM"):
    """Generate a time tracking report"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Report generation payload
    payload = {
        "name": f"Time Tracking Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "description": "Time estimation vs actual work hours analysis",
        "report_type": "time_tracking",
        "start_date": "2026-01-01T00:00:00",
        "end_date": "2026-12-31T23:59:59",
        "project_key": project_key,
        "user_id": "",
        "status": None,
        "is_public": False
    }
    
    try:
        print("Generating time tracking report...")
        response = requests.post(
            f"{BASE_URL}{REPORTS_ENDPOINT}",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            report_data = response.json()
            print("✅ Time tracking report generated successfully!")
            print(f"📊 Report ID: {report_data['metadata']['id']}")
            print(f"📝 Report Name: {report_data['metadata']['name']}")
            print(f"📈 Report Type: {report_data['metadata']['type']}")
            print("\n📋 Summary Data:")
            for key, value in report_data['summary'].items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            
            print("\n📊 Data Points:")
            for point in report_data['data']:
                print(f"  {point['label']}: {point['value']}")
            
            return report_data['metadata']['id']
        else:
            print(f"❌ Failed to generate report: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error generating report: {e}")
        return None

def get_report_details(token, report_id):
    """Get detailed report information"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}{REPORTS_ENDPOINT}/{report_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            report_data = response.json()
            print("\n🔍 Detailed Report Information:")
            print(json.dumps(report_data, indent=2))
        else:
            print(f"Failed to get report details: {response.status_code}")
            
    except Exception as e:
        print(f"Error getting report details: {e}")

def main():
    print("🚀 Time Tracking Report Generator")
    print("=" * 40)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Authentication failed. Cannot proceed.")
        return
    
    print("✅ Authentication successful!")
    
    # Generate time tracking report
    report_id = generate_time_tracking_report(token, "SCRUM")
    
    if report_id:
        print(f"\n✅ Report generated with ID: {report_id}")
        print("You can now view this report in the frontend application!")
        
        # Optionally get detailed information
        view_details = input("\nWould you like to see detailed report information? (y/n): ")
        if view_details.lower() == 'y':
            get_report_details(token, report_id)
    else:
        print("❌ Failed to generate time tracking report")

if __name__ == "__main__":
    main()