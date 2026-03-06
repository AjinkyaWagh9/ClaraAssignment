# Changelog — BrightSmile Dental Clinic
**Account ID:** `brightsmile-dental-c794a2`
**Version:** v1 → v2
**Date:** 2026-03-06
**Total Changes:** 8

---

## Changed Fields

### `business_hours`
| | Value |
|---|---|
| **Before (v1)** | `{"days": "Monday through Friday", "start": "9 AM", "end": "6 PM", "timezone": "Central Time"}` |
| **After  (v2)** | `{"days": "Monday through Saturday", "start": "10 AM", "end": "2 PM", "timezone": "Central Time"}` |
| **Reason**      | Updated via onboarding call |

### `call_transfer_rules`
| | Value |
|---|---|
| **Before (v1)** | `{"timeout_seconds": 30, "retries": 1, "message_if_fails": "I'm not able to provide clinical guidance"}` |
| **After  (v2)** | `{"timeout_seconds": 30, "retries": 1, "message_if_fails": "our front desk will find the earliest available slot for you."}` |
| **Reason**      | Updated via onboarding call |

### `emergency_definition`
| | Value |
|---|---|
| **Before (v1)** | `["Severe Tooth Pain", "Knocked Out Tooth", "Dental Abscess", "Facial Swelling", "Uncontrolled Bleeding", "Broken Tooth", "Exposed Nerve"]` |
| **After  (v2)** | `["Severe Tooth Pain", "Knocked Out Tooth", "Dental Abscess", "Facial Swelling", "Uncontrolled Bleeding", "Broken Tooth", "Exposed Nerve", "Broken Dental Crown"]` |
| **Reason**      | Updated via onboarding call |

### `emergency_routing_rules`
| | Value |
|---|---|
| **Before (v1)** | `{"primary_contact": "Patel (3124458810)", "order": ["Call Patel at 3124458810"], "fallback": "I'm not able to provide clinical guidance"}` |
| **After  (v2)** | `{"primary_contact": "Kim (3124459920)", "order": ["Call Kim at 3124459920"], "fallback": "our front desk will find the earliest available slot for you."}` |
| **Reason**      | Updated via onboarding call |

### `integration_constraints`
| | Value |
|---|---|
| **Before (v1)** | `["never books appointments \u2014 patients go through our front desk", "Never discuss treatment costs or insurance \u2014 that goes to billing", "Never give medical advice", "agent must say \"I'm not able to provide clinical guidance\" and direct to the dentist"]` |
| **After  (v2)** | `["never books appointments \u2014 patients go through our front desk", "Never discuss treatment costs or insurance \u2014 that goes to billing", "Never give medical advice", "agent must say \"I'm not able to provide clinical guidance\" and direct to the dentist", "agent should never mention our office wait times"]` |
| **Reason**      | Updated via onboarding call |

### `notes`
| | Value |
|---|---|
| **Before (v1)** | `"Extracted via rule-based parser. Review unknowns list if any."` |
| **After  (v2)** | `"Updated via onboarding call \u2014 2026-03-06."` |
| **Reason**      | Updated via onboarding call |

### `services_supported`
| | Value |
|---|---|
| **Before (v1)** | `["Fillings", "Root Canal", "Orthodontics", "Emergency Dental Care"]` |
| **After  (v2)** | `["Fillings", "Root Canal", "Orthodontics", "Emergency Dental Care", "Teeth Whitening", "Dental Implants"]` |
| **Reason**      | Updated via onboarding call |

### `version`
| | Value |
|---|---|
| **Before (v1)** | `null` |
| **After  (v2)** | `"v2"` |
| **Reason**      | Updated via onboarding call |
