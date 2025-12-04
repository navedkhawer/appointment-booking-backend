from fastapi import APIRouter
from datetime import datetime, timedelta
from app.database import patients_collection, appointments_collection

router = APIRouter()

@router.get("/")
async def get_dashboard_stats():
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # Fetch all appointments
    all_appts = await appointments_collection.find().to_list(5000)
    
    # 1. KPI Calculations
    total_appointments = len(all_appts)
    
    today_appts = [a for a in all_appts if a['date'] == today_str]
    today_count = len(today_appts)
    
    total_completed = len([a for a in all_appts if a['status'] == 'COMPLETED'])
    total_cancelled = len([a for a in all_appts if a['status'] == 'CANCELLED'])

    # 2. Weekly Trend (Last 7 Days)
    trend_data = []
    for i in range(6, -1, -1):
        date_cursor = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        # Format date for display (e.g., "Nov 25")
        display_date = datetime.strptime(date_cursor, "%Y-%m-%d").strftime("%b %d")
        
        day_count = len([a for a in all_appts if a['date'] == date_cursor])
        trend_data.append({"date": display_date, "count": day_count})

    # 3. Status Distribution (Excluding 'CONFIRMED' as requested)
    status_counts = {
        "Pending": len([a for a in all_appts if a['status'] == 'PENDING']),
        "Completed": len([a for a in all_appts if a['status'] == 'COMPLETED']),
        "Cancelled": len([a for a in all_appts if a['status'] == 'CANCELLED']),
    }
    
    pie_data = [
        {"name": k, "value": v} for k, v in status_counts.items() if v > 0
    ]

    return {
        "kpi": {
            "total_appointments": total_appointments,
            "today_schedule": today_count,
            "total_completed": total_completed,
            "total_cancelled": total_cancelled
        },
        "weekly_trend": trend_data,
        "status_distribution": pie_data
    }