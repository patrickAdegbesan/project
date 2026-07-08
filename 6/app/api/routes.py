"""FastAPI route handlers for the resume screening system."""
import json
import io
import csv
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from fastapi import (
    APIRouter, Depends, File, Form, UploadFile,
    HTTPException, BackgroundTasks, Request
)
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc
from pydantic import BaseModel
from loguru import logger

from app.models.database import (
    get_db, Candidate, Resume, ExtractedEntity,
    JobRole, CandidateScore, AuditLog, ProcessingJob
)
from app.services.processor import process_resumes
from app.config import settings

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class JobRoleCreate(BaseModel):
    title: str
    required_skills: List[str]
    hub_lat: float = settings.HUB_LAT
    hub_long: float = settings.HUB_LONG
    min_experience: float = 1.0
    description: Optional[str] = None


class ShortlistRequest(BaseModel):
    score_ids: List[int]
    shortlisted: bool = True


# ---------------------------------------------------------------------------
# Upload & Processing
# ---------------------------------------------------------------------------

@router.post("/upload")
async def upload_resumes(
    background_tasks: BackgroundTasks,
    job_role_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Accept bulk resume uploads and start background processing."""
    if not files:
        raise HTTPException(400, "No files uploaded")

    # Validate file types
    allowed = {".pdf", ".docx", ".doc"}
    for f in files:
        ext = Path(f.filename or "").suffix.lower()
        if ext not in allowed:
            raise HTTPException(400, f"Unsupported file type: {f.filename}")

    # Verify job role exists
    result = await db.execute(select(JobRole).where(JobRole.id == job_role_id))
    job_role = result.scalar_one_or_none()
    if not job_role:
        raise HTTPException(404, f"Job role {job_role_id} not found")

    # Create processing job record
    pjob = ProcessingJob(
        job_role_id=job_role_id,
        status="pending",
        total_files=len(files),
    )
    db.add(pjob)
    await db.flush()
    job_id = pjob.id
    await db.commit()

    # Read file bytes now (before background task, since UploadFile closes)
    file_data = []
    for f in files:
        content = await f.read()
        file_data.append({"filename": f.filename, "bytes": content})

    # Queue background processing
    background_tasks.add_task(
        _run_processing, job_id, job_role_id, file_data
    )

    return {
        "job_id": job_id,
        "message": f"Processing {len(files)} resume(s) for {job_role.title}",
        "total_files": len(files),
    }


async def _run_processing(job_id: int, job_role_id: int, file_data: list):
    """Bridge function for background task (needs its own DB session)."""
    from app.models.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        await process_resumes(db, job_id, job_role_id, file_data)


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

@router.get("/status/{job_id}")
async def get_status(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProcessingJob).where(ProcessingJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Processing job not found")

    progress = 0
    if job.total_files > 0:
        progress = int((job.processed_files / job.total_files) * 100)

    return {
        "job_id": job.id,
        "status": job.status,
        "current_step": job.current_step,
        "total_files": job.total_files,
        "processed_files": job.processed_files,
        "progress": progress,
        "error": job.error_message,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
    }


# ---------------------------------------------------------------------------
# Results / Ranking
# ---------------------------------------------------------------------------

@router.get("/results/{job_id}")
async def get_results(job_id: int, db: AsyncSession = Depends(get_db)):
    """Return ranked candidates for a processing job."""
    # Get the processing job to find job_role_id
    pjob_result = await db.execute(
        select(ProcessingJob).where(ProcessingJob.id == job_id)
    )
    pjob = pjob_result.scalar_one_or_none()
    if not pjob:
        raise HTTPException(404, "Job not found")

    # Fetch scores + related data
    scores_result = await db.execute(
        select(CandidateScore, Resume, Candidate, JobRole)
        .join(Resume, CandidateScore.resume_id == Resume.id)
        .join(Candidate, Resume.candidate_id == Candidate.id)
        .join(JobRole, CandidateScore.job_id == JobRole.id)
        .where(CandidateScore.job_id == pjob.job_role_id)
        .order_by(desc(CandidateScore.total_score))
    )
    rows = scores_result.all()

    results = []
    for rank, (score, resume, candidate, job_role) in enumerate(rows, 1):
        skill_gap_data = {}
        if score.skill_gap:
            try:
                skill_gap_data = json.loads(score.skill_gap)
            except Exception:
                pass

        # Get entities for this resume
        ents_result = await db.execute(
            select(ExtractedEntity).where(ExtractedEntity.resume_id == resume.id)
        )
        entities = ents_result.scalars().all()
        skills = [e.entity_value for e in entities if e.entity_type == "SKILL"]
        education = [e.entity_value for e in entities if e.entity_type == "EDUCATION"]
        location_ents = [e.entity_value for e in entities if e.entity_type == "LOCATION"]
        exp_ents = [e.entity_value for e in entities if e.entity_type == "EXPERIENCE"]

        # Proximity color
        dist = score.distance_km
        if dist is None:
            color = "secondary"
        elif dist < settings.PROXIMITY_GREEN:
            color = "success"
        elif dist < settings.PROXIMITY_YELLOW:
            color = "warning"
        else:
            color = "danger"

        results.append({
            "rank": rank,
            "score_id": score.id,
            "candidate_id": candidate.id,
            "resume_id": resume.id,
            "name": candidate.full_name,
            "email": candidate.email,
            "phone": candidate.phone,
            "location": location_ents[0] if location_ents else "",
            "experience_years": float(exp_ents[0]) if exp_ents else 0,
            "skill_score": round(score.skill_score * 100, 1),
            "exp_score": round(score.exp_score * 100, 1),
            "proximity_score": round(score.proximity_score * 100, 1),
            "total_score": round(score.total_score * 100, 1),
            "distance_km": score.distance_km,
            "proximity_color": color,
            "skills": skills,
            "education": education,
            "skill_gap_summary": skill_gap_data.get("summary", ""),
            "matched_skills": skill_gap_data.get("matched", []),
            "missing_skills": skill_gap_data.get("missing", []),
            "shortlisted": score.shortlisted,
            "job_title": job_role.title,
        })

    return {
        "job_id": job_id,
        "job_role": rows[0][3].title if rows else "",
        "total_candidates": len(results),
        "results": results,
    }


# ---------------------------------------------------------------------------
# Shortlist
# ---------------------------------------------------------------------------

@router.post("/shortlist")
async def update_shortlist(
    req: ShortlistRequest,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        update(CandidateScore)
        .where(CandidateScore.id.in_(req.score_ids))
        .values(shortlisted=req.shortlisted)
    )
    await db.execute(stmt)
    await db.commit()
    return {"updated": len(req.score_ids), "shortlisted": req.shortlisted}


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

@router.get("/export/{job_id}")
async def export_results(job_id: int, db: AsyncSession = Depends(get_db)):
    """Export ranked results as CSV download."""
    data = await get_results(job_id, db)
    results = data["results"]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "rank", "name", "email", "phone", "location",
        "experience_years", "skill_score", "exp_score",
        "proximity_score", "total_score", "distance_km",
        "shortlisted", "skills", "missing_skills", "skill_gap_summary",
    ])
    writer.writeheader()
    for r in results:
        writer.writerow({
            "rank": r["rank"],
            "name": r["name"],
            "email": r["email"],
            "phone": r["phone"],
            "location": r["location"],
            "experience_years": r["experience_years"],
            "skill_score": r["skill_score"],
            "exp_score": r["exp_score"],
            "proximity_score": r["proximity_score"],
            "total_score": r["total_score"],
            "distance_km": r["distance_km"],
            "shortlisted": r["shortlisted"],
            "skills": "; ".join(r["skills"]),
            "missing_skills": "; ".join(r["missing_skills"]),
            "skill_gap_summary": r["skill_gap_summary"],
        })

    output.seek(0)
    filename = f"lush_hair_results_job{job_id}_{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ---------------------------------------------------------------------------
# Candidate Detail
# ---------------------------------------------------------------------------

@router.get("/candidate/{candidate_id}")
async def get_candidate(candidate_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Candidate).where(Candidate.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(404, "Candidate not found")

    resumes_result = await db.execute(
        select(Resume).where(Resume.candidate_id == candidate_id)
    )
    resumes = resumes_result.scalars().all()

    all_entities = []
    all_scores = []
    for resume in resumes:
        ents = await db.execute(
            select(ExtractedEntity).where(ExtractedEntity.resume_id == resume.id)
        )
        all_entities.extend(ents.scalars().all())

        scores = await db.execute(
            select(CandidateScore).where(CandidateScore.resume_id == resume.id)
        )
        all_scores.extend(scores.scalars().all())

    def _group(etype):
        return [
            {"value": e.entity_value, "confidence": round(e.confidence_score, 2)}
            for e in all_entities if e.entity_type == etype
        ]

    return {
        "candidate": {
            "id": candidate.id,
            "name": candidate.full_name,
            "email": candidate.email,
            "phone": candidate.phone,
            "created_at": candidate.created_at,
        },
        "resumes": [
            {
                "id": r.id,
                "file_name": r.file_name,
                "lat": r.res_lat,
                "lon": r.res_long,
                "parsed_at": r.parsed_at,
            }
            for r in resumes
        ],
        "entities": {
            "skills": _group("SKILL"),
            "education": _group("EDUCATION"),
            "certifications": _group("CERTIFICATION"),
            "roles": _group("ROLE"),
            "locations": _group("LOCATION"),
            "experience": _group("EXPERIENCE"),
        },
        "scores": [
            {
                "id": s.id,
                "job_id": s.job_id,
                "skill_score": round(s.skill_score * 100, 1),
                "exp_score": round(s.exp_score * 100, 1),
                "proximity_score": round(s.proximity_score * 100, 1),
                "total_score": round(s.total_score * 100, 1),
                "distance_km": s.distance_km,
                "skill_gap": json.loads(s.skill_gap) if s.skill_gap else {},
                "shortlisted": s.shortlisted,
            }
            for s in all_scores
        ],
    }


# ---------------------------------------------------------------------------
# Job Roles
# ---------------------------------------------------------------------------

@router.get("/job-roles")
async def list_job_roles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobRole).order_by(JobRole.id))
    roles = result.scalars().all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "required_skills": json.loads(r.required_skills),
            "hub_lat": r.hub_lat,
            "hub_long": r.hub_long,
            "min_experience": r.min_experience,
            "description": r.description,
        }
        for r in roles
    ]


@router.post("/job-roles")
async def create_job_role(
    role: JobRoleCreate,
    db: AsyncSession = Depends(get_db),
):
    new_role = JobRole(
        title=role.title,
        required_skills=json.dumps(role.required_skills),
        hub_lat=role.hub_lat,
        hub_long=role.hub_long,
        min_experience=role.min_experience,
        description=role.description,
    )
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    return {"id": new_role.id, "title": new_role.title}


@router.put("/job-roles/{role_id}")
async def update_job_role(
    role_id: int,
    role: JobRoleCreate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(JobRole).where(JobRole.id == role_id))
    existing = result.scalar_one_or_none()
    if not existing:
        raise HTTPException(404, "Job role not found")

    existing.title = role.title
    existing.required_skills = json.dumps(role.required_skills)
    existing.hub_lat = role.hub_lat
    existing.hub_long = role.hub_long
    existing.min_experience = role.min_experience
    existing.description = role.description
    await db.commit()
    return {"id": existing.id, "title": existing.title, "updated": True}


@router.delete("/job-roles/{role_id}")
async def delete_job_role(role_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobRole).where(JobRole.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(404, "Job role not found")
    await db.delete(role)
    await db.commit()
    return {"deleted": True}


# ---------------------------------------------------------------------------
# Dashboard stats
# ---------------------------------------------------------------------------

@router.get("/dashboard/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    total_candidates = await db.scalar(select(func.count(Candidate.id)))
    total_resumes = await db.scalar(select(func.count(Resume.id)))
    total_jobs = await db.scalar(select(func.count(JobRole.id)))
    shortlisted = await db.scalar(
        select(func.count(CandidateScore.id)).where(CandidateScore.shortlisted == True)
    )
    avg_score_result = await db.scalar(select(func.avg(CandidateScore.total_score)))

    return {
        "total_candidates": total_candidates or 0,
        "total_resumes": total_resumes or 0,
        "total_job_roles": total_jobs or 0,
        "shortlisted_candidates": shortlisted or 0,
        "average_score": round((avg_score_result or 0) * 100, 1),
    }
