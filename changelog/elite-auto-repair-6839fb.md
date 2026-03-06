# Changelog — Elite Auto Repair
**Account ID:** `elite-auto-repair-6839fb`
**Version:** v1 → v2
**Date:** 2026-03-06
**Total Changes:** 7

---

## Changed Fields

### `call_transfer_rules`
| | Value |
|---|---|
| **Before (v1)** | `{"timeout_seconds": 30, "retries": 1, "message_if_fails": "I wasn't able to reach our roadside coordinator. Please call AAA or your insurance roadside assistance. We'll also have someone call you back within 30 minutes."}` |
| **After  (v2)** | `{"timeout_seconds": 30, "retries": 1, "message_if_fails": "If you are in an unsafe location, please move away from traffic and call 911."}` |
| **Reason**      | Updated via onboarding call |

### `emergency_definition`
| | Value |
|---|---|
| **Before (v1)** | `["Stranded", "Brake Failure", "Smoking Engine", "Oil Pressure Warning"]` |
| **After  (v2)** | `["Stranded", "Brake Failure", "Smoking Engine", "Oil Pressure Warning", "Airbag Warning"]` |
| **Reason**      | Updated via onboarding call |

### `emergency_routing_rules`
| | Value |
|---|---|
| **Before (v1)** | `{"primary_contact": "Ray (2147763300)", "order": ["Call Ray at 2147763300"], "fallback": "I wasn't able to reach our roadside coordinator. Please call AAA or your insurance roadside assistance. We'll also have someone call you back within 30 minutes."}` |
| **After  (v2)** | `{"primary_contact": "Diane (2147763301)", "order": ["Call Diane at 2147763301"], "fallback": "If you are in an unsafe location, please move away from traffic and call 911."}` |
| **Reason**      | Updated via onboarding call |

### `integration_constraints`
| | Value |
|---|---|
| **Before (v1)** | `["cannot look up, create, or modify any repair order in Mitchell1", "Never promise same-day service \u2014 we always have a wait list"]` |
| **After  (v2)** | `["cannot look up, create, or modify any repair order in Mitchell1", "Never promise same-day service \u2014 we always have a wait list", "agent should never promise a loaner car", "don't offer loaners \u2014 that's caused confusion before"]` |
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
| **Before (v1)** | `["Engine Diagnostics", "Brake Repair", "Oil Change", "Battery Replacement", "Transmission Service", "Tire Rotation"]` |
| **After  (v2)** | `["Engine Diagnostics", "Brake Repair", "Oil Change", "Battery Replacement", "Transmission Service", "Tire Rotation", "Fleet Vehicle Maintenance"]` |
| **Reason**      | Updated via onboarding call |

### `version`
| | Value |
|---|---|
| **Before (v1)** | `null` |
| **After  (v2)** | `"v2"` |
| **Reason**      | Updated via onboarding call |
