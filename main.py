"""
Pre-interview skeleton — Machine Coding Round (Fresher)
"DUMMY-PROOF" EDITION
--------------------------------------------------------
Everything the instructions ask you to have "already working" before
the call:

  - one sample POST endpoint (reads JSON -> object, returns JSON)
  - a logger printing to console
  - boilerplate-free data modeling (dataclasses)
  - in-memory storage
  - easy to call locally (curl / IDE REST client / Swagger UI)

This version adds nothing clever on top — it just tries hard not to
silently break on you: clear error messages if a dependency is
missing, a sanity check on startup, comments explaining every block,
and defensive handling so a typo in a request body gives you a
readable error instead of a stack trace.

During the actual interview you just repurpose/extend the endpoints
below for whatever problem statement they give you. Nothing here
solves any problem for you — it's scaffolding only.

===========================================================
QUICK START (copy-paste these exactly, one at a time)
===========================================================
1) Create and activate a virtual environment (recommended but optional):
       python3 -m venv venv
       source venv/bin/activate        # on Windows: venv\\Scripts\\activate

2) Install dependencies:
       pip install -r requirements.txt

3) Run the server:
       uvicorn main:app --reload --port 8000

4) Confirm it's alive (open in a browser, or curl):
       http://localhost:8000/health
       -> {"status": "ok"}

5) Try the sample endpoint:
       curl -X POST http://localhost:8000/items \\
            -H "Content-Type: application/json" \\
            -d '{"name": "widget", "quantity": 3}'

6) Browse/click-test everything without curl at all:
       http://localhost:8000/docs

If step 3 fails with "command not found: uvicorn", your venv isn't
activated or step 2 didn't finish — re-run step 1/2.
===========================================================
"""

import logging
import sys
import Math

# ---------------------------------------------------------------------------
# Dependency check — if FastAPI/pydantic aren't installed, fail with a
# plain-English message instead of a confusing ImportError stack trace.
# This is the kind of defensive check interviewers like to see, too.
# ---------------------------------------------------------------------------
try:
    from dataclasses import dataclass, asdict
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse
    from fastapi.exceptions import RequestValidationError
    from fastapi.encoders import jsonable_encoder
    from pydantic import BaseModel, field_validator
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        "\n[SETUP ERROR] A required package is missing: "
        f"{exc.name if hasattr(exc, 'name') else exc}\n"
        "Fix: run  pip install -r requirements.txt\n"
        "If that still fails, make sure you activated your virtual "
        "environment first (see the QUICK START comment at the top of "
        "this file).\n\n"
    )
    raise

# ---------------------------------------------------------------------------
# Logging — prints to console, timestamped, at INFO level.
# Change level=logging.DEBUG below while developing if you want more noise.
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("app")

app = FastAPI(title="Machine Coding Round Scaffold")

# ---------------------------------------------------------------------------
# Storage layer — plain in-memory dict. Swap the structure out freely
# depending on what the actual problem needs (list, dict of dicts, etc).
# Kept as module-level state on purpose — simplest thing that works for
# a 60-minute, single-process interview round. No database needed.
# ---------------------------------------------------------------------------
_next_id = 1
_items: dict[int, "Item"] = {}


# ---------------------------------------------------------------------------
# Domain model — dataclass keeps this boilerplate-free (no manual
# getters/setters). This is the "business rules" layer, kept separate
# from the HTTP layer below so you can test/reason about it on its own.
# ---------------------------------------------------------------------------
@dataclass
class Vehicle:
    Vehicle_id: str
    Vehicle_type: Literal["Bike", "Car"]
    no_of_minutes: int


# ---------------------------------------------------------------------------
# Request / response schemas — pydantic handles JSON parsing + validation
# for the HTTP layer. Kept separate from the dataclass above so the wire
# format and the domain model can evolve independently.
#
# field_validator below is the "dummy-proof" bit: it rejects empty/blank
# names at the parsing stage, before your business logic even runs, and
# with a message that says exactly what was wrong.
# ---------------------------------------------------------------------------
class Response(BaseModel):
    fees: int
    ticket: str
    status: str

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("name must not be empty")
        return v


class ItemResponse(BaseModel):
    id: int
    name: str
    quantity: int


# ---------------------------------------------------------------------------
# Error handling — any bad input (missing field, wrong type, failed
# validator) returns a clean 422 with a plain message instead of a raw
# traceback. This also doubles as a demo of the "how you handle bad
# input" criterion they said they score.
# ---------------------------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation failed for %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=422,
        content={"error": "invalid request body", "details": jsonable_encoder(exc.errors())},
    )


# Catch-all safety net — if something you add later throws an unexpected
# exception, this logs it with a full stack trace (so YOU can debug it)
# but still returns a clean JSON 500 instead of crashing the server.
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"error": "internal server error"})

parking_space = {"Bike": 2, "Car": 2}
ps = {"Bike":{"B1":1,"B2":1}, "Car":{"C1":1,"C2":1}}
ticket_num=0
# ---------------------------------------------------------------------------
# Sample POST endpoint — reads a JSON body into an object, applies a
# (trivial, placeholder) business rule, stores it, returns JSON back.
# This is the "already wired up" endpoint the instructions ask for —
# during the interview you repoint/rename this for the real problem.
# ---------------------------------------------------------------------------
@app.post("/entry", response_model=Response, status_code=201)
def entry(payload: Vehicle):
    global _next_id

    logger.info("Vehicle number: %s", payload.vehicle_id, "Vehicle type: %s", payload.vehicle_type)

    if payload.vehicle_type!="Bike" or payload.vehicle_type!="Car":
        logger.warning("Vehicle type error")
        raise HTTPException(status_code=400, detail="Incorrect vehicle type")
    if parking_space[payload.vehicle_type]>0:
        parking_space[payload.vehicle_type]-=1
        if payload.vehicle_type == "Car":
            if ps["Car"]["C1"]==1:
                park = "C1"
                ps["Car"]["C1"]-=1
            else:
                park = "C2"
                ps["Car"]["C2"]-=1
        else:
            if ps["Bike"]["B1"]==1:
                park = "B1"
                ps["Bike"]["B1"]-=1
            else:
                park = "B2"
                ps["Bike"]["B2"]-=1
        ticket_num+=1
        return JSONResponse(content={"ticket_id": "tkt-"+str(ticket_num), "Vehicle_type":payload.vehicle_type, "Status": "Parked", "Slot": park})
    elif parking_space[payload.vehicle_type]==0:
        logger.warning("No parking space available")
        raise HTTPException(status_code=400, detail="No space")
@app.post("/exit", response_model=Response, status_code=201) 
def exit(payload = Vehicle):
    if payload.vehicle_type == "Car":
        fare = 40 * floor(payload.no_of_minutes/60)
        """ we then convert the slot value back to one and then print jsonresponse of time, ticket, fare, slot and do the same for bike too."""



    







@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Let the file be run directly too (python main.py), not just via uvicorn
# CLI — one less way for setup to trip someone up.
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting server directly via `python main.py` ...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
