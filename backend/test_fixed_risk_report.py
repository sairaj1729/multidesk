import asyncio
from services.reports_service import reports_service
from models.reports import ReportGenerationRequest
from db import connect_to_mongo, close_mongo_connection

async def test_fixed_risk_report():
    """Test the fixed risk analysis report"""
    try:
        # Initialize database
        await connect_to_mongo()
        print("✅ Database connected")
        
        user_id = "6990a3c637ed27735ff66301"
        
        # Create report request (same as what would come from frontend)
        request = ReportGenerationRequest(
            name="Fixed Risk Analysis Test",
            description="Testing fixed risk analysis report",
            report_type="risk_analysis",
            start_date="2026-01-01T00:00:00",
            end_date="2026-12-31T23:59:59",
            project_key="SCRUM",
            user_id="",  # Empty user_id like in your case
            status=None,
            is_public=False
        )
        
        print("🚀 Testing Fixed Risk Analysis Report...")
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
        risk_level_points = [p for p in data_points if p.metadata.get('category') == 'risk_levels']
        task_metric_points = [p for p in data_points if p.metadata.get('category') == 'task_metrics']
        high_risk_points = [p for p in data_points if p.metadata.get('category') == 'high_risk_details']
        
        print("Risk Levels:")
        for point in risk_level_points:
            print(f"  {point.label}: {point.value}")
            
        print("Task Metrics:")
        for point in task_metric_points:
            print(f"  {point.label}: {point.value}")
            
        if high_risk_points:
            print("High Risk Details (top 5):")
            for point in high_risk_points[:5]:
                print(f"  {point.label}: {point.value} points")
        
        # Verify we have actual risk data
        total_risks = summary.get('total_risks', 0)
        if total_risks > 0:
            print(f"\n✅ SUCCESS: Report now shows {total_risks} total risks!")
            print("✅ The risk analysis report is now working correctly!")
        else:
            print(f"\n❌ ISSUE: Still showing 0 risks")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
    finally:
        await close_mongo_connection()
        print("✅ Database connection closed")

if __name__ == "__main__":
    asyncio.run(test_fixed_risk_report())