import os
import json
from typing import List, Any, Generator
from openai import AzureOpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

from ..utils.tools import get_tools
# from ..config.prompts import SYSTEM_PROMPT, DEFAULT_TEMPERATURE, MAX_TOKENS
from ..hammy_tools.system import SYSTEM_PROMPT

client = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
)

class OpenAIService:
    """Service for handling OpenAI operations"""

    @staticmethod
    def get_tools_config():
        """Get the tools configuration for OpenAI"""
        return [{
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather at a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "The latitude of the location",
                        },
                        "longitude": {
                            "type": "number",
                            "description": "The longitude of the location",
                        },
                    },
                    "required": ["latitude", "longitude"],
                },
            },
        },
        # {
        #     "type": "function",
        #     "function": {
        #         "name": "get_current_chiller_schedule",
        #         "description": "Get the current schedule for a specific chiller to check if it exists and can be modified",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "chiller_id": {
        #                     "type": "string",
        #                     "description": "The ID of the chiller to check which follow the format 'chiller_1', 'chiller_2', etc."
        #                 }
        #             },
        #             "required": ["chiller_id"]
        #         }
        #     }
        # },
        # {
        #     "type": "function",
        #     "function": {
        #         "name": "request_to_set_chiller_sequence_schedule",
        #         "description": "Request to set a new schedule for a chiller. Only use this after confirming the chiller exists with get_current_chiller_schedule. This will show a confirmation UI to the user.",
        #         "parameters": {
        #             "type": "object",
        #             "properties": {
        #                 "chiller_id": {
        #                     "type": "string",
        #                     "description": "The ID of the chiller"
        #                 },
        #                 "profile_type": {
        #                     "type": "string",
        #                     "description": "The type of schedule profile"
        #                 },
        #                 "old_start": {
        #                     "type": "string",
        #                     "description": "Current start time in HH:MM format"
        #                 },
        #                 "old_stop": {
        #                     "type": "string",
        #                     "description": "Current stop time in HH:MM format"
        #                 },
        #                 "new_start": {
        #                     "type": "string",
        #                     "description": "New start time in HH:MM format"
        #                 },
        #                 "new_stop": {
        #                     "type": "string",
        #                     "description": "New stop time in HH:MM format"
        #                 }
        #             },
        #             "required": ["chiller_id", "profile_type", "old_start", "old_stop", "new_start", "new_stop"]
        #         }
        #     }
        # },
        {
            "type": "function",
            "function": {
                "name": "generate_mock_chart",
                "description": "Generate a simple mock chart for today's chiller plant load profile using ECharts",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function", 
            "function": {
                "name": "get_chiller_status",
                "description": "Get detailed status of a specific chiller including operational metrics",
                "parameters": {
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
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_equipment_status",
                "description": "Get status of any equipment (pumps, cooling towers, etc.)",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "equipment_id": {
                            "type": "string",
                            "description": "The ID of the equipment (e.g., pchp_1, ct_1_1, cdp_1)"
                        }
                    },
                    "required": ["equipment_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_all_chillers",
                "description": "Get status overview of all chillers in the system",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_maintenance_status", 
                "description": "Get maintenance status for equipment",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "The ID of the equipment to check maintenance for"
                        }
                    },
                    "required": ["device_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_maintenance_history",
                "description": "Get maintenance history for specific equipment, optionally within a date range.",
                "parameters": {
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
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_schedule",
                "description": "Get the schedule for a specific profile type (weekday/weekend/holiday)",
                "parameters": {
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
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_schedule",
                "description": "Add a new schedule entry for chillers with validation",
                "parameters": {
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
                            "description": "List of schedule entries with start and stop times"
                        }
                    },
                    "required": ["profile_type", "chiller_type", "schedule_entry"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "requests_to_set_maintenance_status",
                "description": "Set maintenance status for a device with details about who initiated it and the technician assigned",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "Device ID of the equipment"
                        },
                        "ticked_started_by": {
                            "type": "string",
                            "description": "Name of person reporting/initiating the maintenance"
                        },
                        "technician": {
                            "type": "string",
                            "description": "Name of technician assigned to the maintenance"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the maintenance reason"
                        }
                    },
                    "required": ["device_id", "ticked_started_by", "technician", "description"]
                }
            }
        },
    ]

    @staticmethod
    def stream_text(messages: List[ChatCompletionMessageParam], protocol: str = 'data') -> Generator[str, None, None]:
        """
        Stream text responses from OpenAI
        
        Args:
            messages: List of messages to send to OpenAI
            protocol: Protocol to use for streaming
            
        Yields:
            Streamed responses
        """
        # Add system prompt to the beginning of the messages
        system_message = {"role": "system", "content": SYSTEM_PROMPT}
        full_messages = [system_message, *messages]

        draft_tool_calls = []
        draft_tool_calls_index = -1

        stream = client.chat.completions.create(
            messages=full_messages,
            model=os.environ.get("AZURE_OPENAI_MINI_MODEL"),
            stream=True,
            tools=OpenAIService.get_tools_config()
        )

        available_tools = get_tools()
        tool_results = []  # Store results to pass to next tool call if needed

        for chunk in stream:
            for choice in chunk.choices:
                if choice.finish_reason == "stop":
                    continue

                elif choice.finish_reason == "tool_calls":
                    for tool_call in draft_tool_calls:
                        yield '9:{{"toolCallId":"{id}","toolName":"{name}","args":{args}}}\n'.format(
                            id=tool_call["id"],
                            name=tool_call["name"],
                            args=tool_call["arguments"]
                        )

                    for tool_call in draft_tool_calls:
                        if tool_call["name"] in available_tools:
                            print(f"✅ Calling tool: {tool_call['name']}")
                            print(f"🔍 Arguments: {tool_call['arguments']}")
                            tool_result = available_tools[tool_call["name"]](
                                **json.loads(tool_call["arguments"]))
                            
                            # Store result for potential next tool call
                            tool_results.append({
                                "name": tool_call["name"],
                                "result": tool_result
                            })

                            yield 'a:{{"toolCallId":"{id}","toolName":"{name}","args":{args},"result":{result}}}\n'.format(
                                id=tool_call["id"],
                                name=tool_call["name"],
                                args=tool_call["arguments"],
                                result=json.dumps(tool_result)
                            )

                            # If this was get_current_chiller_schedule and chiller exists,
                            # the AI will automatically follow up with set_chiller_sequence_schedule
                            if tool_call["name"] == "get_current_chiller_schedule" and tool_result.get("exists"):
                                continue  # Let the AI make the next tool call

                elif choice.delta.tool_calls:
                    for tool_call in choice.delta.tool_calls:
                        id = tool_call.id
                        name = tool_call.function.name
                        arguments = tool_call.function.arguments

                        if (id is not None):
                            draft_tool_calls_index += 1
                            draft_tool_calls.append(
                                {"id": id, "name": name, "arguments": ""})
                        else:
                            draft_tool_calls[draft_tool_calls_index]["arguments"] += arguments

                else:
                    yield '0:{text}\n'.format(text=json.dumps(choice.delta.content))

            if chunk.choices == []:
                usage = chunk.usage
                prompt_tokens = usage.prompt_tokens if usage else 0
                completion_tokens = usage.completion_tokens if usage else 0

                yield 'e:{{"finishReason":"{reason}","usage":{{"promptTokens":{prompt},"completionTokens":{completion}}},"isContinued":false}}\n'.format(
                    reason="tool-calls" if len(draft_tool_calls) > 0 else "stop",
                    prompt=prompt_tokens,
                    completion=completion_tokens
                ) 