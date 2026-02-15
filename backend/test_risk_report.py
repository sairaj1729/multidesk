import asyncio
from services.reports_service import reports_service
from models.reports import ReportGenerationRequest
from datetime import datetime

async def test_risk_analysis_report():
    """Test the improved risk analysis report generation"""
    try:
        # Test data - using a real user ID from your system
        user_id = "6990a3c637ed27735ff66301"  # This should be a valid user ID
        
        # Create report request
        request = ReportGenerationRequest(
            name="Test Risk Analysis Report",
            description="Testing improved risk analysis implementation",
            report_type="risk_analysis",
            start_date="2026-01-01T00:00:00",
            end_date="2026-12-31T23:59:59",
            project_key="SCRUM",
            user_id="",
            status=None,
            is_public=False
        )
        
        print("🚀 Testing Risk Analysis Report Generation...")
        print("=" * 50)
        
        # Generate the report
        result = await reports_service._generate_risk_analysis_report(user_id, request)
        
        data_points, summary = result
        
        print("✅ Risk Analysis Report Generated Successfully!")
        print(f"\n📊 Summary Data:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        print(f"\n📈 Data Points Generated: {len(data_points)}")
        print("Key data points:")
        for i, point in enumerate(data_points[:10]):  # Show first 10
            print(f"  {i+1}. {point.label}: {point.value} ({point.metadata.get('category', 'no category')})")
        
        if len(data_points) > 10:
            print(f"  ... and {len(data_points) - 10} more data points")
            
        print("\n✅ Risk analysis report implementation is working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing risk analysis report: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_risk_analysis_report())