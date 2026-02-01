import pandas as pd
from datetime import datetime
from db import get_database
import logging
from bson import ObjectId
from services.risk_service import run_risk_analysis

logger = logging.getLogger(__name__)

async def process_leave_file(file_id: str, file_path: str, user_id: str):
    """Process leave file and trigger risk analysis"""
    db = get_database()
    leaves_collection = db.leaves
    files_collection = db.files

    try:
        logger.info(f"📂 Processing leave file: {file_path}")
        
        # Check if file exists
        import os
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"✅ File exists, size: {os.path.getsize(file_path)} bytes")
        
        # Read Excel or CSV file
        if file_path.endswith('.csv'):
            logger.info("Reading CSV file...")
            df = pd.read_csv(file_path)
        else:
            logger.info("Reading Excel file...")
            df = pd.read_excel(file_path)
        
        logger.info(f"📊 File loaded: {len(df)} rows, columns: {list(df.columns)}")

        # Validate required columns
        required_cols = {"employee_account_id", "leave_start", "leave_end"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"File must contain {required_cols} columns. Found: {list(df.columns)}")
        
        logger.info("✅ Required columns present")

        records = []

        for idx, row in df.iterrows():
            try:
                # Parse dates with explicit format DD-MM-YYYY
                leave_start_dt = pd.to_datetime(row["leave_start"], format='%d-%m-%Y', dayfirst=True)
                leave_end_dt = pd.to_datetime(row["leave_end"], format='%d-%m-%Y', dayfirst=True)
                
                # Convert pandas Timestamp to Python datetime
                leave_start = leave_start_dt.to_pydatetime()
                leave_end = leave_end_dt.to_pydatetime()
               
                
                record = {
                    "employee_account_id": row["employee_account_id"].strip(),
                    "leave_start": leave_start,
                    "leave_end": leave_end,
                    "file_id": file_id,
                    "user_id": user_id,  # Add user ownership
                    "uploaded_at": datetime.utcnow()
                }
                records.append(record)
                logger.debug(f"  Row {idx+1}: {row['employee_account_id'].strip()} from {leave_start.date()} to {leave_end.date()}")
            except Exception as row_error:
                logger.warning(f"⚠️ Failed to process row {idx+1}: {row_error}")
                continue

        if records:
            result = await leaves_collection.insert_many(records)
            logger.info(f"✅ Inserted {len(records)} leave records into database")
        else:
            logger.warning("⚠️ No valid records to insert")

        # Mark file as processed
        try:
            oid = ObjectId(file_id)
        except Exception:
            oid = None

        if oid:
            await files_collection.update_one(
                {"_id": oid},
                {
                    "$set": {
                        "status": "processed",
                        "records": len(records),
                        "processed_at": datetime.utcnow()
                    }
                }
            )

        # Trigger risk analysis after processing leaves
        logger.info("Triggering risk analysis after leave processing...")
        try:
            risk_result = await run_risk_analysis(user_id)
            logger.info(f"Risk analysis completed: {risk_result['count']} new risks created")
        except Exception as risk_error:
            logger.error(f"Risk analysis failed: {risk_error}")

    except Exception as e:
        logger.error(f"Leave file processing failed: {e}")

        # Mark file as failed
        try:
            oid = ObjectId(file_id)
        except Exception:
            oid = None

        if oid:
            await files_collection.update_one(
                {"_id": oid},
                {
                    "$set": {
                        "status": "error",
                        "error_message": str(e),
                        "processed_at": datetime.utcnow()
                    }
                }
            )
