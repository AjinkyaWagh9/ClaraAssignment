# Changelog — RapidFix Plumbing
**Account ID:** `rapidfix-plumbing-0545c0`
**Version:** v1 → v2
**Date:** 2026-03-06
**Total Changes:** 8

---

## Changed Fields

### `business_hours`
| | Value |
|---|---|
| **Before (v1)** | `{"days": "Monday through Friday", "start": "7 AM", "end": "6 PM", "timezone": "Central Time"}` |
| **After  (v2)** | `{"days": "Monday through Sunday", "start": "10 AM", "end": "2 PM", "timezone": "Central Time"}` |
| **Reason**      | Updated via onboarding call |

### `call_transfer_rules`
| | Value |
|---|---|
| **Before (v1)** | `{"timeout_seconds": 30, "retries": 1, "message_if_fails": "I wasn't able to reach our on-call technician directly. I've logged your information and a technician will call you back within 20 minutes. Please avoid using water until then."}` |
| **After  (v2)** | `{"timeout_seconds": 30, "retries": 1, "message_if_fails": "our dispatch team will confirm your technician."}` |
| **Reason**      | Updated via onboarding call |

### `emergency_definition`
| | Value |
|---|---|
| **Before (v1)** | `["Burst Pipe", "Active Flooding", "Gas Smell", "Loss Of Water Supply", "Water Heater Leaking", "Flooding"]` |
| **After  (v2)** | `["Burst Pipe", "Active Flooding", "Gas Smell", "Loss Of Water Supply", "Water Heater Leaking", "Flooding", "Sewage Backup"]` |
| **Reason**      | Updated via onboarding call |

### `emergency_routing_rules`
| | Value |
|---|---|
| **Before (v1)** | `{"primary_contact": "Marcus (5123347821)", "order": ["Call Marcus at 5123347821", "Call Linda at 5123349102"], "fallback": "I wasn't able to reach our on-call technician directly. I've logged your information and a technician will call you back within 20 minutes. Please avoid using water until then."}` |
| **After  (v2)** | `{"primary_contact": "Dispatch Team Will Confirm Your Technician", "order": ["Transfer to Dispatch Team Will Confirm Your Technician"], "fallback": "our dispatch team will confirm your technician."}` |
| **Reason**      | Updated via onboarding call |

### `integration_constraints`
| | Value |
|---|---|
| **Before (v1)** | `["AI must never create a job or appointment in ServiceTitan", "Never quote prices over the phone"]` |
| **After  (v2)** | `["AI must never create a job or appointment in ServiceTitan", "Never quote prices over the phone", "don't know if it's urgent", "agent should never confirm or deny if a specific technician is available", "agent should say \"pricing depends on the job and our team will provide a full quote on-site"]` |
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
| **Before (v1)** | `["Leak Detection", "Pipe Repair", "Drain Cleaning", "Water Heater Installation", "Fixture Replacement", "Emergency Shut-Off"]` |
| **After  (v2)** | `["Leak Detection", "Pipe Repair", "Drain Cleaning", "Water Heater Installation", "Fixture Replacement", "Emergency Shut-Off", "Tankless Water Heater"]` |
| **Reason**      | Updated via onboarding call |

### `version`
| | Value |
|---|---|
| **Before (v1)** | `null` |
| **After  (v2)** | `"v2"` |
| **Reason**      | Updated via onboarding call |
