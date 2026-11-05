| **# Pools** | **Same-Pool Pairing**                        | **Near-pool Pairing**                       | **Half-Pool Pairing**                     | **Far-Pool Pairing**                     |
|-------------|----------------------------------------------|---------------------------------------------|-------------------------------------------|------------------------------------------|
| **2 Pools** | A1 vs A2, B1 vs B2                           | A1 vs B2, A2 vs B1                         | A1 vs A2, B1 vs B2 (same as "same-pool")  | A1 vs B2, A2 vs B1                       |
| **4 Pools** | A1 vs A2, B1 vs B2, C1 vs C2, D1 vs D2       | A1 vs B2, A2 vs B1, C1 vs D2, C2 vs D1     | A1 vs B2, A2 vs B1, C1 vs D2, C2 vs D1    | A1 vs D2, A2 vs D1, B1 vs C2, B2 vs C1   |
| **8 Pools** | A1 vs A2, B1 vs B2, C1 vs C2, D1 vs D2, E1 vs E2, F1 vs F2, G1 vs G2, H1 vs H2 | A1 vs B2, A2 vs B1, C1 vs D2, C2 vs D1, E1 vs F2, E2 vs F1, G1 vs H2, G2 vs H1 | A1 vs D2, A2 vs D1, E1 vs H2, H1 vs E2    | A1 vs H2, A2 vs H1, B1 vs G2, B2 vs G1, C1 vs F2, C2 vs F1, D1 vs E2, D2 vs E1 |

# Khel Club -- Walkover Match Outcome

## Overview

This submission extends the **Khel Club** tournament management system to support a **Walkover match outcome** while preserving the existing regular scoring flow.

A walkover is recorded when one of the two assigned teams is declared the winner without a regular played score. The match is marked completed, the winner is stored, and the winner is advanced to the successor knockout match when one exists.

Before submitting, review the implementation-specific notes below and make sure the repository contains every referenced migration and code change.

---

## Repositories

* **Backend fork:** [https://github.com/Khel-Club/v0_backend](https://github.com/Khel-Club/v0_backend)
* **Frontend fork:** [https://github.com/Khel-Club/v0_frontend](https://github.com/Khel-Club/v0_frontend)

---

## How the Existing Scoring Flow Works

The scoreboard obtains the initial match data from the match-score endpoint:

```http
GET /score/match?match_id=<MATCH_ID>&tournament_id=<TOURNAMENT_ID>

```

The frontend stores the returned match information in its `scoreData` state and displays the two teams and their scores.

For live updates, the frontend connects to the **Socket.IO** `/scores` namespace and subscribes using the tournament and match identifiers. Regular `score_update` events update the team identifiers and score values in the existing `scoreData` object.

This keeps the initial REST response and subsequent live score events in sync with the scoreboard.

---

## Walkover Behavior

The backend exposes a walkover declaration endpoint:

```http
POST /score/walkover
Content-Type: application/json

```

### Request Body

```json
{
  "match_id": 12,
  "tournament_id": 5,
  "winner_team_id": 3
}

```

> *Note: The identifiers above are illustrative; use IDs that exist in the local database when testing.*

### The Backend Flow

1. Validate that `match_id`, `tournament_id`, and `winner_team_id` are provided.
2. Find the match belonging to the supplied tournament.
3. Reject a match that is already completed.
4. Require both teams to be assigned and ready.
5. Verify that the selected winner is one of the two teams in the match and belongs to the tournament.
6. Record `outcome = 'walkover'`, the `winner_team_id`, `status = 'completed'`, and `is_final = True`.
7. If the match has a successor, place the winning team into the correct successor slot based on the predecessor relationship.
8. Create zero-valued score records for the successor only when both successor teams are assigned, and avoid creating duplicates.
9. Commit the transaction and emit a `score_update` event in the `/scores` namespace.

The API response includes the match and tournament identifiers, outcome, status, winner, and successor match identifier.

---

## Frontend Changes

The `MatchOverlay` component keeps its existing scoreboard layout and uses the same `scoreData` state for both regular scoring and walkover metadata.

### Socket Listener Event Distinctions

* **For a regular score update:** It updates the team IDs and score values while preserving the rest of the match data.
* **For a walkover event:** It merges the outcome, status, winner ID, and final-state information into the existing `scoreData` object.

The UI can then display a visible **WALKOVER** indicator and identify the winning team without replacing the existing team and score information.

The component should also receive the walkover fields from the initial match-score API response. This is necessary so that a page refresh still displays a previously declared walkover even if no new socket event is emitted.

---

## API Validation and Expected Errors

The walkover endpoint is expected to reject invalid requests, including:

* Missing required identifiers.
* Match not found in the specified tournament.
* Match already completed.
* Either team not assigned or a team still marked as `TBD`.
* Winner not participating in the match.
* Winning team not found in the tournament.

The endpoint returns an appropriate HTTP error response for these cases. The frontend should surface API errors to the user in the match-management flow.

---

## Database and Migration Notes

The implementation uses the match fields `outcome`, `winner_team_id`, `status`, and `is_final`, as shown in the backend walkover handler.

### Checklist Before Submitting

* Confirm the actual database schema before submitting.
* If `outcome` and `winner_team_id` already exist, no new column migration is needed for those fields.
* If either field is missing, add it through a versioned migration and include that migration in the backend fork.
* Confirm that the `outcome` field can store values such as `walkover` and can be extended for future outcomes.
* Confirm that `winner_team_id` has the appropriate relationship or validation for the project's existing team model.

> **Important:** Do not rely only on a local manual database alteration; the schema change must be reproducible for someone setting up the project from the repository.

---

## Local Setup and Testing

Follow the setup instructions already present in each upstream repository, including the backend's SQL dump and environment configuration. Do not commit secrets or local environment files.

### Suggested End-to-End Verification

1. Start the backend and frontend locally.
2. Set up the database using the provided SQL dump and any migrations included in this fork.
3. Open a tournament and a knockout match with two assigned teams.
4. Declare a walkover for one of the participating teams.
5. Verify the API response reports `outcome: "walkover"`, `status: "completed"`, and the selected `winner_team_id`.
6. Verify the winner is placed into the correct successor match slot.
7. Verify the frontend displays the **WALKOVER** indicator and winner.
8. Refresh the scoreboard and verify the walkover remains visible from the initial API response.
9. Test a regular match and confirm normal score updates still work.
10. Test invalid cases, such as selecting a team that is not in the match or declaring a second result for a completed match.

---

## Assumptions

* A walkover is a completed match outcome, not a regular played score.
* A walkover winner must be one of the two teams assigned to that match.
* The existing knockout predecessor/successor relationship determines where the winner advances.
* The walkover endpoint is responsible for validating and recording the result and advancing the winner.
* The frontend listens for the backend's `score_update` event in the `/scores` namespace.
* A walkover does not require inventing a regular score; the winner is represented explicitly by `winner_team_id`.

---

## Design and Future Improvements

To support additional outcomes such as forfeit and bye, keep the match outcome separate from the numeric score.

### Possible Next Steps

* Define a documented set of supported outcome types and validate them centrally.
* Move result validation and winner advancement into a shared backend service rather than duplicating rules across route handlers.
* Define outcome-specific rules for whether teams must be assigned, whether a score is required, and how a winner is determined.
* Make result recording and successor advancement one atomic transaction.
* Return a consistent match representation from the REST API and Socket.IO events.
* Add automated tests for regular results, walkovers, invalid winners, completed matches, successor advancement, and repeated requests.
* Add an audit trail recording who declared the outcome and when.

---

## Important Implementation Checks Before Submission

* Ensure the initial `GET /score/match` response includes `outcome`, `winner_team_id`, and `status`.
* Ensure the frontend checks match IDs consistently, including string/number ID differences.
* Ensure the socket subscription implementation actually targets the requested match and tournament.
* Ensure the frontend has an administrator action that calls `POST /score/walkover` after the winner is selected. The scoreboard overlay itself should display the result; it should not arbitrarily choose a winner.
* Verify the database migration and all tests against a clean local database.