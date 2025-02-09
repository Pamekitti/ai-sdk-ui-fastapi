import requests
from pymongo import MongoClient
from datetime import datetime

mongodb_client = MongoClient('mongodb://10.10.20.104:27017/')
realtime_db = mongodb_client['realtime_data']
realtime_collection = realtime_db['cp10']

# Connect to MongoDB for automation settings
automation_db = mongodb_client['automation_settings']
automation_collection = automation_db['chiller_plant_schedule_setting']

# Connect to MongoDB for maintenance data
maintenance_db = mongodb_client['maintenance']
maintenance_collection = maintenance_db['equipment_maintenance']


def get_tools():
    """Get all available tools"""
    return {
        "get_current_weather": get_current_weather,
        "generate_mock_chart": generate_mock_chart,
        # "get_current_chiller_schedule": get_current_chiller_schedule,
        # "request_to_set_chiller_sequence_schedule": request_to_set_chiller_sequence_schedule,
        "get_chiller_status": get_chiller_status,
        "get_equipment_status": get_equipment_status,
        "get_all_chillers": get_all_chillers,
        "get_maintenance_status": get_maintenance_status,
        "get_maintenance_history": get_maintenance_history,
        "get_schedule": get_schedule,
        "check_schedule_availability": check_schedule_availability,
        "add_schedule": add_schedule,
        "requests_to_set_maintenance_status": requests_to_set_maintenance_status,
    }

def get_current_weather(latitude, longitude):
    # Format the URL with proper parameter substitution
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m&hourly=temperature_2m&daily=sunrise,sunset&timezone=auto"

    try:
        # Make the API call
        response = requests.get(url)

        # Raise an exception for bad status codes
        response.raise_for_status()

        # Return the JSON response
        return response.json()

    except requests.RequestException as e:
        # Handle any errors that occur during the request
        print(f"Error fetching weather data: {e}")
        return None

def generate_mock_chart():
    # Generate a simple mock chart data in ECharts format
    chart_data = {
        "title": {
            "text": "Sample Chart"
        },
        "xAxis": {
            "type": "category",
            "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        },
        "yAxis": {
            "type": "value"
        },
        "series": [{
            "data": [150, 230, 224, 218, 135, 147, 260],
            "type": "line"
        }]
    }
    return chart_data

def get_current_chiller_schedule(chiller_id: str):
    """
    Get the current schedule for a specific chiller
    Returns None if chiller doesn't exist
    """
    # This is a mock implementation - replace with actual DB/API call
    valid_chillers = {
        "chiller_1": {
            "exists": True,
            "schedule": {
                "weekday": {"start": "08:00", "stop": "18:00"},
                "weekend": {"start": "10:00", "stop": "16:00"}
            }
        },
        "chiller_2": {
            "exists": True,
            "schedule": {
                "weekday": {"start": "07:00", "stop": "19:00"},
                "weekend": {"start": "09:00", "stop": "17:00"}
            }
        }
    }
    
    if chiller_id not in valid_chillers:
        return {"exists": False, "error": f"Chiller {chiller_id} does not exist"}
    
    return valid_chillers[chiller_id]

def request_to_set_chiller_sequence_schedule(chiller_id: str, profile_type: str, old_start: str, old_stop: str, new_start: str, new_stop: str):
    """Request to set a new schedule for a chiller. This will show a confirmation UI to the user."""
    return {"message": f"Schedule change requested for {chiller_id}", "requires_confirmation": True}








def get_chiller_status(chiller_id):
    """Get status of a specific chiller with all relevant metrics"""
    try:
        latest_data = realtime_collection.find_one(
            {"raw_data." + chiller_id: {"$exists": True}},
            sort=[('_id', -1)]
        )
        if latest_data and chiller_id in latest_data["raw_data"]:
            return latest_data["raw_data"][chiller_id]
        return None
    except Exception as e:
        print(f"Error getting chiller status: {str(e)}")
        return None

def get_equipment_status(equipment_id):
    """Get status of any equipment (pumps, cooling towers, etc.)"""
    try:
        latest_data = realtime_collection.find_one(
            {"raw_data." + equipment_id: {"$exists": True}},
            sort=[('_id', -1)]
        )
        if latest_data and equipment_id in latest_data["raw_data"]:
            return latest_data["raw_data"][equipment_id]
        return None
    except Exception as e:
        print(f"Error getting equipment status: {str(e)}")
        return None

def get_all_chillers():
    """Get status of all chillers"""
    try:
        latest_data = realtime_collection.find_one(sort=[('_id', -1)])
        if latest_data:
            chiller_data = {}
            for key in latest_data["raw_data"]:
                if key.startswith("chiller_"):
                    chiller_data[key] = latest_data["raw_data"][key]
            return chiller_data
        return {}
    except Exception as e:
        print(f"Error getting all chillers: {str(e)}")
        return {}


def get_maintenance_history(equipment_id, start_date=None, end_date=None):
    """Get maintenance history for specific equipment within date range"""
    try:
        query = {"equipment_id": equipment_id}
        if start_date and end_date:
            query["timestamp"] = {
                "$gte": start_date,
                "$lte": end_date
            }
        
        history = list(maintenance_collection.find(
            query,
            sort=[('timestamp', -1)]
        ))
        return history
    except Exception as e:
        print(f"Error getting maintenance history: {str(e)}")
        return None

def get_schedule(profile_type):
    """Get schedule for a specific profile type with excluded chillers"""
    try:
        settings = automation_collection.find_one({"_id": "chiller_plant_schedule_setting"})
        if settings and "profile" in settings and profile_type in settings["profile"]:
            return settings["profile"][profile_type]
        return None
    except Exception as e:
        print(f"Error getting schedule: {str(e)}")
        return None

def check_schedule_availability(chiller_id, profile_type, start_time, stop_time):
    """Check if a chiller can be scheduled for the given time slot"""
    try:
        # Get current schedule
        schedule = get_schedule(profile_type)
        if not schedule:
            return False, "Schedule not found"

        # Check if chiller is in excluded list
        if "excluded_chiller" not in schedule or chiller_id not in schedule["excluded_chiller"]:
            return False, "Chiller not in excluded list"

        return True, "Available for scheduling"
    except Exception as e:
        return False, f"Error checking schedule: {str(e)}"

def add_schedule(profile_type, chiller_type, schedule_entry):
    """Preview schedule changes without updating MongoDB"""
    try:
        # Immediately reject if trying to schedule a normal chiller
        if chiller_type == "normal":
            return {
                "success": False,
                "message": "Cannot modify schedule for normal chillers. Only excluded chillers can be rescheduled."
            }

        settings = automation_collection.find_one({"_id": "chiller_plant_schedule_setting"})
        if not settings:
            return {
                "success": False,
                "message": "No schedule settings found"
            }

        # Get current schedules
        current_schedules = []
        if profile_type in settings.get("profile", {}) and \
            "excluded_chiller" in settings["profile"][profile_type] and \
            chiller_type in settings["profile"][profile_type]["excluded_chiller"]:
            current_schedules = settings["profile"][profile_type]["excluded_chiller"][chiller_type]

        # Format the response to match frontend expectations
        return {
            "success": True,
            "message": f"Schedule preview for {chiller_type}",
            "data": {
                "chiller_id": chiller_type,
                "profile_type": profile_type,
                "old_schedule": [{"start": entry.get("start"), "stop": entry.get("stop")} for entry in current_schedules] if current_schedules else [{"start": None, "stop": None}],
                "new_schedule": [{"start": entry["start"], "stop": entry["stop"]} for entry in schedule_entry]
            }
        }

    except Exception as e:
        print(f"Error checking schedule: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to check schedule: {str(e)}"
        }

def confirm_schedule(profile_type, chiller_type, schedule_entries):
    """Confirm and apply schedule changes to MongoDB"""
    try:
        # Check if the chiller is available for scheduling
        for schedule_entry in schedule_entries:
            is_available, message = check_schedule_availability(
                chiller_type,
                profile_type,
                schedule_entry["start"],
                schedule_entry["stop"]
            )
            if not is_available:
                return {
                    "success": False,
                    "message": f"Cannot confirm schedule: {message}"
                }

        # Get current settings or create new if not exists
        settings = automation_collection.find_one({"_id": "chiller_plant_schedule_setting"})
        if not settings:
            settings = {
                "_id": "chiller_plant_schedule_setting",
                "profile": {},
                "enable_schedule_control": True
            }

        # Ensure profile and structure exists
        if profile_type not in settings["profile"]:
            settings["profile"][profile_type] = {
                "normal_chiller": [],
                "excluded_chiller": {}
            }
        if "excluded_chiller" not in settings["profile"][profile_type]:
            settings["profile"][profile_type]["excluded_chiller"] = {}

        # Replace all schedules with the new list
        settings["profile"][profile_type]["excluded_chiller"][chiller_type] = schedule_entries

        # Update MongoDB with the new settings
        result = automation_collection.replace_one(
            {"_id": "chiller_plant_schedule_setting"},
            settings,
            upsert=True
        )

        if result.modified_count > 0 or result.upserted_id:
            return {
                "success": True,
                "message": "Schedules updated successfully in MongoDB",
                "schedules": schedule_entries,
                "mongodb_result": {
                    "modified_count": result.modified_count,
                    "upserted_id": str(result.upserted_id) if result.upserted_id else None
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to update MongoDB - no changes made",
                "schedules": schedule_entries
            }

    except Exception as e:
        print(f"Error confirming schedule: {str(e)}")
        return {
            "success": False,
            "message": f"Failed to update schedule: {str(e)}"
        }





def get_maintenance_status(device_id=None):
    """Get maintenance status for specific equipment or all equipment"""
    try:
        if device_id:
            maintenance_data = maintenance_collection.find_one(
                {"device_id": device_id},
                sort=[('timestamp', -1)]
            )
            status_ = maintenance_data.get('status')
            maintenance_history = maintenance_data.get('maintenance_history')
            return {
                "device_id": device_id, 
                "under_maintenance": status_['under_maintenance'],
                "ticket_started_by": maintenance_history[0]["ticket_started_by"] if maintenance_history else None,
                "ticked_closed_by": maintenance_history[0]["ticket_closed_by"] if maintenance_history else None,
                "technician": maintenance_history[0]["technician"] if maintenance_history else None,
                "resolved_at": maintenance_history[0]["resolved_at"] if maintenance_history else None,
                "reported_at": maintenance_history[0]["reported_at"] if maintenance_history else None,
                }
            
        return {}
            
    except Exception as e:
        print(f"Error getting maintenance status: {str(e)}")
        return None
    

def requests_to_set_maintenance_status(device_id: str, ticked_started_by: str, technician: str, description: str):
    """Requests to update maintenance status from individual equipment by device_id"""
    try:
        check_device_maintenance = get_maintenance_status(device_id)
        if not check_device_maintenance:
            return {
                "success": False,
                "message": f"Device {device_id} not found",
                "data": None
            }
        else:
            return {
                "success": True,
                "message": f"Maintenance request created for {device_id}",
                "data": {
                    "device_id": device_id,
                    "maintenance_flag": True,
                    "reporter_name": ticked_started_by,
                    "technician_name": technician,
                    "time": format(datetime.now(), "%Y-%m-%dT%H:%M:%S"),
                    "reason": description
                }
            }
        
    except Exception as e:
        print(f"Error BRO Requesting maintenance status: {str(e)}")
        return {
            "success": False,
            "message": str(e),
            "data": None
        }


