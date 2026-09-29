# TrackEase — Final Booking Module & Project Regression Report

**Date**: 2026-09-28
**Objective**: Validate the full integration of the booking system, confirm the crucial 2-minute pending expiry workflow, and declare overall technical QA completion.

---

### 1. Current Expiry Before Test
- **Value**: 600 seconds (10 minutes)
- **Status**: Found in `config/settings.py`

### 2. Final Expiry Value
- **Value**: 120 seconds (2 minutes)
- **Status**: UPDATED in `config/settings.py` as `BOOKING_EXPIRY_SECONDS = 120`

### 3. Booking Creation
- **Action**: Created temporary booking (Train `98147` | CSMT → VASHI).
- **Status**: **PASS** (HTTP 201 | Status = `PENDING`)

### 4. Successful Payment
- **Action**: Processed mock UPI payment on the `PENDING` booking.
- **Status**: **PASS** (HTTP 200 | Status = `CONFIRMED`)

### 5. Failed Payment
- **Action**: Processed mock UPI failure payload.
- **Status**: **PASS** (HTTP 400 | Booking safely remained `PENDING`)

### 6. Double Payment
- **Action**: Submitted a second payment for the `CONFIRMED` booking.
- **Status**: **PASS** (HTTP 400 | Rejected with "Booking is already confirmed" ensuring idempotency)

### 7. **2-Minute Expiry Test (CRITICAL)**
- **Action**: Created booking. Waited 125 seconds. Attempted payment.
- **Status**: **PASS** (HTTP 400 | Rejected with "Booking is expired and cannot be paid." | Status cleanly transitioned `PENDING` → `EXPIRED`)

### 8. Cancellation
- **Action**: Cancelled a `CONFIRMED` booking.
- **Status**: **PASS** (HTTP 200 | Mock refund initiated | Booking and PNR transitioned to `CANCELLED`)

### 9. Ticket Verification
- **Action**: Fetched the ticket record from the API.
- **Status**: **PASS** (PNR generated, Passenger populated, Train/Route details cleanly embedded)

### 10. Invoice Verification
- **Action**: Fetched the invoice record.
- **Status**: **PASS** (Invoice ID generated, Payment marked `PAID`, Total correctly matching base fare)

### 11. Booking History
- **Status**: **PASS** (All test bookings isolated to the authenticated user token)

### 12. Authorization
- **Status**: **PASS** (Protected endpoints successfully rejected unauthorized access during earlier script execution steps)

### 13. Railway Search Regression
- **Status**: **PASS** (Previously Verified | Point-to-point and middle station routing functional)

### 14. Tracking Regression
- **Status**: **PASS** (Previously Verified | Simulated tracking system retains logic)

### 15. Station Regression
- **Status**: **PASS** (Previously Verified | `VDLR` mapping verified in DB)

### 16. Journey Planner Regression
- **Status**: **PASS** (Previously Verified | Autocomplete and UI layout functional)

### 17. Admin Verification
- **Status**: **PASS** (Previously Verified | Core models accessible)

### 18. Database Integrity
- **Status**: **PASS** (No orphan records. Orphan test data cleaned safely)

### 19. RapidAPI Verification
- **Status**: **PASS** (No external keys were leaked or over-consumed. All tests hit local DB)

### 20. Cleanup
- **Action**: Django shell executed bulk deletion `User.objects.filter(username__startswith='finalqauser').delete()` cascading to Bookings, Tickets, Payments.
- **Status**: **PASS** (Test footprint removed successfully)

---

## Final Quality Assurance Sign-Off

**BOOKING_2_MIN_EXPIRY = PASS**

**BOOKING_MODULE = PASS**

**OVERALL_PROJECT_REGRESSION = PASS**

**TRACKease_FINAL_TECHNICAL_QA = PASS**
