# Manual API and UI Test Results

Run the commands below in **PowerShell**, from the folder containing `compose.yaml`. They are manual checks, not an automated test suite. Keep the same terminal open so variables such as `$ticket1` and `$before` remain available.

## Results checked so far

These results reflect only checks performed or reports made in this conversation; they do not mean every test below has been run.

| Test | Result so far | Evidence / remaining checks                                                                                                                                                                                                                         |
| ---- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T01  | Partial       | Both Compose services were running. A clean unzip, successful build, and `GET /api/health` returning 200 were not confirmed.                                                                                                                        |
| T02  | Not run       | An empty ticket list on a new volume was not checked.                                                                                                                                                                                               |
| T03  | Partial       | Title trimming was checked in the backend model. A valid `POST` response with HTTP 201 and all required fields was not confirmed.                                                                                                                   |
| T04  | Partial       | The user reported creating a ticket through the UI. The specific `WiFi unstable` ticket, two-ticket list, and filter counts were not confirmed.                                                                                                     |
| T05  | Not run       | Status changes, refresh persistence, and filter counts were not checked.                                                                                                                                                                            |
| T06  | Partial       | Correctly formed invalid requests for blank title, an 81-character title, invalid priority, non-string title, and an extra field returned HTTP 422 with JSON errors. Invalid status, malformed JSON, and an unchanged ticket list were not checked. |
| T07  | Not run       | A missing-ticket PATCH returning HTTP 404 was not checked.                                                                                                                                                                                          |
| T08  | Not run       | Persistence after recreating containers was not checked.                                                                                                                                                                                            |

## T01 — Start from a clean project copy and check health✅

## T02 — Check the initial list✅

## T03 — Create a ticket through the API✅

```powershell
$response = Invoke-WebRequest -Uri "http://localhost:8080/api/tickets" -Method Post -ContentType "application/json" -Body '{"title":" Printer offline ","priority":"high"}'
"HTTP $([int]$response.StatusCode)"
$ticket1 = $response.Content | ConvertFrom-Json
$ticket1 | ConvertTo-Json -Depth 5
```

Expected: HTTP 201; title `Printer offline`; priority `high`; status `open`; and a positive integer `id`. Keep `$ticket1` for later commands.

## T04 — Create and check a ticket through the UI✅

## T05 — Change statuses and check filters✅

## T06 — Send invalid data and check the list stays unchanged✅

First record the current list:

```powershell
$before = @(Invoke-RestMethod -Uri "http://localhost:8080/api/tickets" -Method Get)
"Tickets before invalid requests: $($before.Count)"
```

Run each request separately. Each should return HTTP 400 or 422 with a JSON error.

Blank title:

```powershell
curl.exe -i -X POST "http://localhost:8080/api/tickets" -H "Content-Type: application/json" --data-raw '{"title":"","priority":"high"}'
```

Title of 81 characters:

```powershell
$body = '{"title":"' + ('d' * 81) + '","priority":"high"}'
curl.exe -i -X POST "http://localhost:8080/api/tickets" -H "Content-Type: application/json" --data-raw $body
```

Title is not a string:

```powershell
curl.exe -i -X POST "http://localhost:8080/api/tickets" -H "Content-Type: application/json" --data-raw '{"title":123,"priority":"high"}'
```

Invalid priority:

```powershell
curl.exe -i -X POST "http://localhost:8080/api/tickets" -H "Content-Type: application/json" --data-raw '{"title":"Bad priority","priority":"urgent"}'
```

Invalid status (replace `1` with an existing ticket ID if needed):

```powershell
curl.exe -i -X PATCH "http://localhost:8080/api/tickets/1" -H "Content-Type: application/json" --data-raw '{"status":"invalid"}'
```

Malformed JSON:

```powershell
curl.exe -i -X POST "http://localhost:8080/api/tickets" -H "Content-Type: application/json" --data-raw '{"title":"broken",'
```

Finally, fetch the list again and compare it with `$before`; the invalid requests must not add or change tickets:

```powershell
$after = @(Invoke-RestMethod -Uri "http://localhost:8080/api/tickets" -Method Get)
ConvertTo-Json -InputObject $after -Depth 5
```

## T07 — PATCH a ticket that does not exist✅

```powershell
curl.exe -i -X PATCH "http://localhost:8080/api/tickets/999999999" -H "Content-Type: application/json" --data-raw '{"status":"doing"}'
```

Expected: HTTP 404 and a JSON error.

## T08 — Recreate containers and check saved data✅

Run this after T05, using the same PowerShell terminal. It saves the current response in `$before`, stops and recreates the containers **without deleting the named volume**, then fetches the tickets again.

```powershell
$before = @(Invoke-RestMethod -Uri "http://localhost:8080/api/tickets" -Method Get)
ConvertTo-Json -InputObject $before -Depth 5
docker compose down
docker compose up -d
```

After `docker compose up -d` finishes, run:

```powershell
$after = @(Invoke-RestMethod -Uri "http://localhost:8080/api/tickets" -Method Get)
ConvertTo-Json -InputObject $after -Depth 5
```

Compare the output before and after: both tickets should retain their IDs, titles, priorities, and statuses. Do **not** use `docker compose down -v`; that deletes the saved volume and its database.
