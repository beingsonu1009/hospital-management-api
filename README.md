
<!-- IN api router -->
prefix="/patients"
Instead of writing
@router.post("/patients")
@router.get("/patients")
@router.delete("/patients")
we define it once.
Now every route automatically starts with
/patients

Example
@router.post("")
becomes
POST /patients
and
@router.get("/{id}")
becomes
GET /patients/{id}