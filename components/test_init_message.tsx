import { Message } from "ai";

const InitMessage: Message = {
  id: "init",
  content: "Hello! How can I help you today?",
  role: "assistant" as const,
};

const InitScheduleMessage: Message = {
  id: "init_schedule",
  content: "",
  role: "assistant" as const,
  toolInvocations: [
    {
      state: "result",
      step: 1,
      toolCallId: "call_cCZ3cpaGUrD6R4XYIXxxhFOT",
      toolName: "request_to_set_chiller_sequence_schedule",
      args: {
        chiller_id: "chiller_1",
        profile_type: "Weekend",
        old_schedule: [
          {
            start: null,
            stop: null
          },
          {
            start: "02:00",
            stop: null
          }
        ],
        new_schedule: [
          {
            start: "20:30",
            stop: "23:40"
          },
          {
            start: "02:30",
            stop: "05:30"
          }
        ]
      },
      result: { success: true }
    }
  ]
};

const InitMaintenanceMessage: Message = {
  id: "init_maintenance",
  content: "",
  role: "assistant" as const,
  toolInvocations: [
    {
      state: "result",
      step: 1,
      toolCallId: "call_dDZ4dqbHVsE7S5YJIYxxiFPU",
      toolName: "set_device_maintenance_flag",
      args: {
        device_id: ["chiller_2", "pchp_2", "ct_2"],
        maintenance_flag: true,
        reporter_name: "John Smith",
        technician_name: "Mike Johnson",
        time: "2024-02-15T14:30:00",
        reason: "Scheduled maintenance for pump replacement and cooling tower inspection"
      },
      result: { success: true }
    }
  ]
};

const InitWeatherMessage: Message = {
  id: "init_weather",
  content: "The sun is up and the weather is sunny.",
  role: "assistant" as const,
  toolInvocations: [
    {
      state: "result",
      step: 1,
      toolCallId: "call_xtcxPfG0uGRwuEkQ6A0eRKGq",
      toolName: "get_current_weather",
      args: {
        latitude: 13.7563,
        longitude: 100.5018
      },
      result: {
        latitude: 13.75,
        longitude: 100.5,
        generationtime_ms: 0.04017353057861328,
        utc_offset_seconds: 25200,
        timezone: "Asia/Bangkok",
        timezone_abbreviation: "GMT+7",
        elevation: 4,
        current_units: {
          time: "iso8601",
          interval: "seconds",
          temperature_2m: "°C"
        },
        current: {
          time: "2025-02-08T15:00",
          interval: 900,
          temperature_2m: 33
        },
        hourly_units: {
          time: "iso8601",
          temperature_2m: "°C"
        },
        hourly: {
          time: ["2025-02-08T00:00", "2025-02-08T01:00", "2025-02-08T02:00", "2025-02-08T03:00", "2025-02-08T04:00", "2025-02-08T05:00", "2025-02-08T06:00", "2025-02-08T07:00", "2025-02-08T08:00", "2025-02-08T09:00", "2025-02-08T10:00", "2025-02-08T11:00", "2025-02-08T12:00", "2025-02-08T13:00", "2025-02-08T14:00", "2025-02-08T15:00", "2025-02-08T16:00", "2025-02-08T17:00", "2025-02-08T18:00", "2025-02-08T19:00", "2025-02-08T20:00", "2025-02-08T21:00", "2025-02-08T22:00", "2025-02-08T23:00", "2025-02-09T00:00"],
          temperature_2m: [26.3, 26.2, 26.1, 26, 25.8, 25.7, 25.5, 25.4, 26, 27.6, 29.1, 30.4, 31.5, 32.4, 32.9, 32.9, 32.9, 32.2, 31.1, 29.8, 28.8, 28.1, 27.4, 26.6, 25.6]
        },
        daily_units: {
          time: "iso8601",
          sunrise: "iso8601",
          sunset: "iso8601"
        },
        daily: {
          time: ["2025-02-08", "2025-02-09", "2025-02-10", "2025-02-11", "2025-02-12", "2025-02-13", "2025-02-14"],
          sunrise: ["2025-02-08T06:43", "2025-02-09T06:43", "2025-02-10T06:42", "2025-02-11T06:42", "2025-02-12T06:42", "2025-02-13T06:41", "2025-02-14T06:41"],
          sunset: ["2025-02-08T18:20", "2025-02-09T18:21", "2025-02-10T18:21", "2025-02-11T18:21", "2025-02-12T18:22", "2025-02-13T18:22", "2025-02-14T18:22"]
        }
      }
    }
  ]
};

export const InitMessageList: Message[] = [
  // InitMessage,
  // InitWeatherMessage,
  // InitScheduleMessage,
  // InitMaintenanceMessage
];

