# Changelog — GreenLeaf Landscaping
**Account ID:** `greenleaf-landscaping-64c059`
**Version:** v1 → v2
**Date:** 2026-03-06
**Total Changes:** 8

---

## Changed Fields

### `business_hours`
| | Value |
|---|---|
| **Before (v1)** | `{"days": "Monday through Friday", "start": "7 AM", "end": "5 PM", "timezone": "Pacific Time"}` |
| **After  (v2)** | `{"days": "Monday through Saturday", "start": "8 AM", "end": "12 PM", "timezone": "Pacific Time"}` |
| **Reason**      | Updated via onboarding call |

### `call_transfer_rules`
| | Value |
|---|---|
| **Before (v1)** | `{"timeout_seconds": 30, "retries": 1, "message_if_fails": "I wasn't able to connect you with our field team right now. Your details have been recorded and Jorge will call you back within 45 minutes."}` |
| **After  (v2)** | `{"timeout_seconds": 30, "retries": 1, "message_if_fails": "our specialist will explain the treatment plan on-site."}` |
| **Reason**      | Updated via onboarding call |

### `emergency_definition`
| | Value |
|---|---|
| **Before (v1)** | `["Major Irrigation Line Break", "Flooding"]` |
| **After  (v2)** | `["Major Irrigation Line Break", "Flooding", "Fallen Tree"]` |
| **Reason**      | Updated via onboarding call |

### `emergency_routing_rules`
| | Value |
|---|---|
| **Before (v1)** | `{"primary_contact": "Jorge (6195542201)", "order": ["Call Jorge at 6195542201"], "fallback": "I wasn't able to connect you with our field team right now. Your details have been recorded and Jorge will call you back within 45 minutes."}` |
| **After  (v2)** | `{"primary_contact": "Rosa (6195543300)", "order": ["Call Rosa at 6195543300"], "fallback": "our specialist will explain the treatment plan on-site."}` |
| **Reason**      | Updated via onboarding call |

### `integration_constraints`
| | Value |
|---|---|
| **Before (v1)** | `["AI should never book or modify jobs in Jobber", "Never discuss HOA billing disputes \u2014 those go directly to our accounts team"]` |
| **After  (v2)** | `["AI should never book or modify jobs in Jobber", "Never discuss HOA billing disputes \u2014 those go directly to our accounts team", "agent should never discuss pesticide or herbicide application details on the phone"]` |
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
| **Before (v1)** | `["Lawn Maintenance", "Landscape Design", "Tree Trimming", "Fertilization", "Seasonal Cleanup"]` |
| **After  (v2)** | `["Lawn Maintenance", "Landscape Design", "Tree Trimming", "Fertilization", "Seasonal Cleanup", "Pool Landscaping", "Hardscaping"]` |
| **Reason**      | Updated via onboarding call |

### `version`
| | Value |
|---|---|
| **Before (v1)** | `null` |
| **After  (v2)** | `"v2"` |
| **Reason**      | Updated via onboarding call |
