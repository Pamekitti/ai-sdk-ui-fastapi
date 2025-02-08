from pymongo import MongoClient
from datetime import datetime, timezone


class ChillerDatabase:
    def __init__(self):
        # Connect to MongoDB for realtime data
        self.realtime_client = MongoClient('mongodb://10.10.20.104:27017/')
        self.realtime_db = self.realtime_client['realtime_data']
        self.realtime_collection = self.realtime_db['cp10']
        
        # Connect to MongoDB for automation settings
        self.automation_client = MongoClient('mongodb://10.10.20.104:27017/')
        self.automation_db = self.automation_client['automation_settings']
        self.automation_collection = self.automation_db['chiller_plant_schedule_setting']
        
        # Connect to MongoDB for maintenance data
        self.maintenance_client = MongoClient('mongodb://10.10.20.104:27017/')
        self.maintenance_db = self.maintenance_client['realtime_data']
        self.maintenance_collection = self.maintenance_db['equipment_maintenance']

    def get_chiller_status(self, chiller_id):
        """Get status of a specific chiller with all relevant metrics"""
        try:
            latest_data = self.realtime_collection.find_one(
                {"raw_data." + chiller_id: {"$exists": True}},
                sort=[('_id', -1)]
            )
            if latest_data and chiller_id in latest_data["raw_data"]:
                return latest_data["raw_data"][chiller_id]
            return None
        except Exception as e:
            print(f"Error getting chiller status: {str(e)}")
            return None

    def get_equipment_status(self, equipment_id):
        """Get status of any equipment (pumps, cooling towers, etc.)"""
        try:
            latest_data = self.realtime_collection.find_one(
                {"raw_data." + equipment_id: {"$exists": True}},
                sort=[('_id', -1)]
            )
            if latest_data and equipment_id in latest_data["raw_data"]:
                return latest_data["raw_data"][equipment_id]
            return None
        except Exception as e:
            print(f"Error getting equipment status: {str(e)}")
            return None

    def get_all_chillers(self):
        """Get status of all chillers"""
        try:
            latest_data = self.realtime_collection.find_one(sort=[('_id', -1)])
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

    def get_maintenance_history(self, equipment_id, start_date=None, end_date=None):
        """Get maintenance history for specific equipment within date range"""
        try:
            query = {"equipment_id": equipment_id}
            if start_date and end_date:
                query["timestamp"] = {
                    "$gte": start_date,
                    "$lte": end_date
                }
            
            history = list(self.maintenance_collection.find(
                query,
                sort=[('timestamp', -1)]
            ))
            return history
        except Exception as e:
            print(f"Error getting maintenance history: {str(e)}")
            return None

    def get_schedule(self, profile_type):
        """Get schedule for a specific profile type with excluded chillers"""
        try:
            settings = self.automation_collection.find_one({"_id": "chiller_plant_schedule_setting"})
            if settings and "profile" in settings and profile_type in settings["profile"]:
                return settings["profile"][profile_type]
            return None
        except Exception as e:
            print(f"Error getting schedule: {str(e)}")
            return None

    def check_schedule_availability(self, chiller_id, profile_type, start_time, stop_time):
        """Check if a chiller can be scheduled for the given time slot"""
        try:
            # Get current schedule
            schedule = self.get_schedule(profile_type)
            if not schedule:
                return False, "Schedule not found"

            # Check if chiller is in excluded list
            if "excluded_chiller" not in schedule or chiller_id not in schedule["excluded_chiller"]:
                return False, "Chiller not in excluded list"

            return True, "Available for scheduling"
        except Exception as e:
            return False, f"Error checking schedule: {str(e)}"

    def add_schedule(self, profile_type, chiller_type, schedule_entry):
        """Preview schedule changes without updating MongoDB"""
        try:
            # Immediately reject if trying to schedule a normal chiller
            if chiller_type == "normal":
                return {
                    "success": False,
                    "message": "Cannot modify schedule for normal chillers. Only excluded chillers can be rescheduled."
                }

            # Check if the chiller is available for scheduling
            is_available, message = self.check_schedule_availability(
                chiller_type,
                profile_type,
                schedule_entry["start"],
                schedule_entry["stop"]
            )
            if not is_available:
                return {
                    "success": False,
                    "message": f"Cannot add schedule: {message}"
                }

            settings = self.automation_collection.find_one({"_id": "chiller_plant_schedule_setting"})
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

            # Return both current and proposed schedules
            return {
                "success": True,
                "schedule_info": {
                    "chiller_id": chiller_type,
                    "current_schedules": current_schedules,
                    "proposed_schedule": schedule_entry
                }
            }

        except Exception as e:
            print(f"Error checking schedule: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to check schedule: {str(e)}"
            }

    def confirm_schedule(self, profile_type, chiller_type, schedule_entries):
        """Confirm and apply schedule changes to MongoDB"""
        try:
            # Check if the chiller is available for scheduling
            for schedule_entry in schedule_entries:
                is_available, message = self.check_schedule_availability(
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
            settings = self.automation_collection.find_one({"_id": "chiller_plant_schedule_setting"})
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
            result = self.automation_collection.replace_one(
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

tools = [
    {
        "name": "get_chiller_status",
        "description": "Get detailed status of a specific chiller including operational metrics",
        "input_schema": {
            "type": "object",
            "properties": {
                "chiller_id": {
                    "type": "string",
                    "enum": ["chiller_1", "chiller_2", "chiller_3", "chiller_4", "chiller_6", "chiller_7", "chiller_8"],
                    "description": "The ID of the chiller to check"
                }
            },
            "required": ["chiller_id"]
        }
    },
    {
        "name": "get_equipment_status",
        "description": "Get status of any equipment (pumps, cooling towers, etc.)",
        "input_schema": {
            "type": "object",
            "properties": {
                "equipment_id": {
                    "type": "string",
                    "description": "The ID of the equipment (e.g., pchp_1, ct_1_1, cdp_1)"
                }
            },
            "required": ["equipment_id"]
        }
    },
    {
        "name": "get_all_chillers",
        "description": "Get status overview of all chillers in the system",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_maintenance_status",
        "description": "Get maintenance status for equipment",
        "input_schema": {
            "type": "object",
            "properties": {
                "equipment_id": {
                    "type": "string",
                    "description": "Optional: The ID of the equipment to check maintenance for"
                }
            }
        }
    },
    {
        "name": "get_maintenance_history",
        "description": "Get maintenance history for specific equipment, optionally within a date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "equipment_id": {
                    "type": "string",
                    "description": "The ID of the equipment to get maintenance history for. Can be any valid equipment ID from the configuration."
                },
                "start_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Optional: Start date for maintenance history (YYYY-MM-DD)"
                },
                "end_date": {
                    "type": "string",
                    "format": "date",
                    "description": "Optional: End date for maintenance history (YYYY-MM-DD)"
                }
            },
            "required": ["equipment_id"]
        }
    },
    {
        "name": "get_schedule",
        "description": "Get the schedule for a specific profile type (weekday/weekend/holiday)",
        "input_schema": {
            "type": "object",
            "properties": {
                "profile_type": {
                    "type": "string",
                    "enum": ["weekday_profile", "weekend_profile", "holiday_profile"],
                    "description": "The type of schedule profile to retrieve"
                }
            },
            "required": ["profile_type"]
        }
    },
    {
        "name": "add_schedule",
        "description": "Add a new schedule entry for chillers with validation",
        "input_schema": {
            "type": "object",
            "properties": {
                "profile_type": {
                    "type": "string",
                    "enum": ["weekday_profile", "weekend_profile", "holiday_profile"],
                    "description": "The type of schedule profile"
                },
                "chiller_type": {
                    "type": "string",
                    "enum": ["normal", "chiller_1", "chiller_2", "chiller_3", "chiller_4", "chiller_6", "chiller_7", "chiller_8"],
                    "description": "The type of chiller schedule (normal or specific chiller ID)"
                },
                "schedule_entry": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "string",
                            "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
                            "description": "Start time in HH:MM format"
                        },
                        "stop": {
                            "type": "string",
                            "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
                            "description": "Stop time in HH:MM format"
                        }
                    },
                    "required": ["start", "stop"]
                }
            },
            "required": ["profile_type", "chiller_type", "schedule_entry"]
        }
    },
    {
        "name": "confirm_schedule",
        "description": "Confirm and apply a list of schedules to MongoDB",
        "input_schema": {
            "type": "object",
            "properties": {
                "profile_type": {
                    "type": "string",
                    "enum": ["weekday_profile", "weekend_profile", "holiday_profile"],
                    "description": "The type of schedule profile"
                },
                "chiller_type": {
                    "type": "string",
                    "enum": ["normal", "chiller_1", "chiller_2", "chiller_3", "chiller_4", "chiller_6", "chiller_7", "chiller_8"],
                    "description": "The type of chiller schedule (normal or specific chiller ID)"
                },
                "schedule_entries": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "start": {
                                "type": "string",
                                "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
                                "description": "Start time in HH:MM format"
                            },
                            "stop": {
                                "type": "string",
                                "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
                                "description": "Stop time in HH:MM format"
                            }
                        },
                        "required": ["start", "stop"]
                    },
                    "description": "List of schedule entries to apply"
                }
            },
            "required": ["profile_type", "chiller_type", "schedule_entries"]
        }
    }
]

db = ChillerDatabase()
