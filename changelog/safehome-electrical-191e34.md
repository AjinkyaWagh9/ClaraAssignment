# Changelog — SafeHome Electrical Services
**Account ID:** `safehome-electrical-191e34`
**Version:** v1 → v2
**Date:** 2026-03-06
**Total Changes:** 7

---

## Changed Fields

### `call_transfer_rules`
| | Value |
|---|---|
| **Before (v1)** | `{"timeout_seconds": 30, "retries": 1, "message_if_fails": "I wasn't able to reach our on-call electrician immediately. If you see flames or smell smoke, call 911 right away. Otherwise Devon will call you back within 15 minutes. I have your contact details."}` |
| **After  (v2)** | `{"timeout_seconds": 30, "retries": 1, "message_if_fails": "I wasn't able to reach our on-call electrician. If you see flames or smell smoke, call 911 immediately. Devon or Aria will call you back within 15 minutes. Please stay away from the affected area."}` |
| **Reason**      | Updated via onboarding call |

### `emergency_definition`
| | Value |
|---|---|
| **Before (v1)** | `["Total Power Outage", "Burning Smell", "Visible Sparks", "Exposed Live Wire", "Tripped Breakers", "Electrical Fire"]` |
| **After  (v2)** | `["Total Power Outage", "Burning Smell", "Visible Sparks", "Exposed Live Wire", "Tripped Breakers", "Electrical Fire", "Flickering Lights", "Water Damage Affecting Electrical"]` |
| **Reason**      | Updated via onboarding call |

### `emergency_routing_rules`
| | Value |
|---|---|
| **Before (v1)** | `{"primary_contact": "James (6028874411)", "order": ["Call James at 6028874411"], "fallback": "I wasn't able to reach our on-call electrician immediately. If you see flames or smell smoke, call 911 right away. Otherwise Devon will call you back within 15 minutes. I have your contact details."}` |
| **After  (v2)** | `{"primary_contact": "Aria (6028875500)", "order": ["Call Aria at 6028875500"], "fallback": "I wasn't able to reach our on-call electrician. If you see flames or smell smoke, call 911 immediately. Devon or Aria will call you back within 15 minutes. Please stay away from the affected area."}` |
| **Reason**      | Updated via onboarding call |

### `integration_constraints`
| | Value |
|---|---|
| **Before (v1)** | `["AI must never create, edit, or view jobs in Housecall Pro", "Never tell callers a specific arrival time until dispatch confirms"]` |
| **After  (v2)** | `["AI must never create, edit, or view jobs in Housecall Pro", "Never tell callers a specific arrival time until dispatch confirms", "agent should never quote permit fees"]` |
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
| **Before (v1)** | `["Electrical Repair", "Panel Upgrade", "Breaker Replacement", "Wiring Installation", "Lighting Install", "Safety Inspection"]` |
| **After  (v2)** | `["Electrical Repair", "Panel Upgrade", "Breaker Replacement", "Wiring Installation", "Lighting Install", "Safety Inspection", "Solar Panel Electrical"]` |
| **Reason**      | Updated via onboarding call |

### `version`
| | Value |
|---|---|
| **Before (v1)** | `null` |
| **After  (v2)** | `"v2"` |
| **Reason**      | Updated via onboarding call |
