"""Background processing pipeline: parse → extract → score → save."""
import json
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from loguru import logger

from app.models.database import (
    Candidate, Resume, ExtractedEntity, CandidateScore,
    AuditLog, ProcessingJob, JobRole
)
from app.services.parser import parse_resume
from app.services.nlp import extract_entities
from app.services.geospatial import get_proximity_info
from app.services.scoring import (
    normalize_experience, skill_match_score,
    generate_skill_gap_summary, calculate_total_score
)
from app.config import settings


async def _update_job_status(
    db: AsyncSession,
    job_id: int,
    status: str,
    step: str = "",
    processed: int = 0,
    error: str = "",
):
    stmt = (
        update(ProcessingJob)
        .where(ProcessingJob.id == job_id)
        .values(
            status=status,
            current_step=step,
            processed_files=processed,
            error_message=error or None,
            completed_at=datetime.utcnow() if status in ("completed", "failed") else None,
        )
    )
    await db.execute(stmt)
    await db.commit()


async def process_resumes(
    db: AsyncSession,
    job_id: int,
    job_role_id: int,
    files: List[dict],  # [{"filename": str, "bytes": bytes}]
):
    """
    Main processing pipeline. Runs as a background task.
    files: list of dicts with 'filename' and 'bytes' keys.
    """
    try:
        await _update_job_status(db, job_id, "processing", "Loading job requirements...")

        # Load job role
        result = await db.execute(select(JobRole).where(JobRole.id == job_role_id))
        job_role = result.scalar_one_or_none()
        if not job_role:
            await _update_job_status(db, job_id, "failed", error="Job role not found")
            return

        required_skills = json.loads(job_role.required_skills) if job_role.required_skills else []

        total = len(files)
        await _update_job_status(db, job_id, "processing",
                                 f"Parsing {total} resumes...", 0)

        for idx, file_info in enumerate(files, 1):
            filename = file_info["filename"]
            file_bytes = file_info["bytes"]

            try:
                await _update_job_status(
                    db, job_id, "processing",
                    f"Parsing resume {idx}/{total}: {filename}", idx - 1
                )

                # 1. Parse text
                raw_text = parse_resume(file_bytes, filename)
                if not raw_text.strip():
                    logger.warning(f"Empty text from {filename}, skipping")
                    continue

                # 2. Extract entities
                await _update_job_status(
                    db, job_id, "processing",
                    f"Extracting entities from {filename}...", idx - 1
                )
                extracted = extract_entities(raw_text)

                # 3. Geocode location
                await _update_job_status(
                    db, job_id, "processing",
                    f"Calculating proximity for {filename}...", idx - 1
                )
                prox = get_proximity_info(
                    extracted.get("location", ""),
                    hub_lat=job_role.hub_lat,
                    hub_lon=job_role.hub_long,
                )

                # 4. Calculate scores
                exp_score = normalize_experience(
                    extracted.get("experience_years", 0),
                    job_role.min_experience,
                )
                skill_score, matched, missing = skill_match_score(
                    extracted.get("skills", []),
                    required_skills,
                )
                proximity_score = prox["proximity_score"]
                total_score = calculate_total_score(skill_score, exp_score, proximity_score)

                skill_gap = generate_skill_gap_summary(
                    extracted.get("skills", []),
                    required_skills,
                    matched,
                    missing,
                    extracted.get("experience_years", 0),
                    job_role.min_experience,
                )

                # 5. Persist to DB
                # Candidate
                candidate = Candidate(
                    full_name=extracted.get("name", "Unknown"),
                    email=extracted.get("email", ""),
                    phone=extracted.get("phone", ""),
                )
                db.add(candidate)
                await db.flush()

                # Resume
                resume = Resume(
                    candidate_id=candidate.id,
                    raw_text=raw_text[:50000],  # cap storage
                    file_path=filename,
                    file_name=filename,
                    res_lat=prox.get("lat"),
                    res_long=prox.get("lon"),
                )
                db.add(resume)
                await db.flush()

                # Entities
                for ent in extracted.get("entities", []):
                    entity = ExtractedEntity(
                        resume_id=resume.id,
                        entity_type=ent["entity_type"],
                        entity_value=ent["entity_value"][:500],
                        confidence_score=ent.get("confidence_score", 0.8),
                    )
                    db.add(entity)

                # Score
                score_record = CandidateScore(
                    resume_id=resume.id,
                    job_id=job_role_id,
                    skill_score=skill_score,
                    exp_score=exp_score,
                    proximity_score=proximity_score,
                    total_score=total_score,
                    distance_km=prox.get("distance_km"),
                    skill_gap=json.dumps({
                        "summary": skill_gap,
                        "matched": matched,
                        "missing": missing,
                    }),
                )
                db.add(score_record)
                await db.flush()

                # Audit
                audit = AuditLog(
                    score_id=score_record.id,
                    nlp_weight=settings.WEIGHT_SKILL + settings.WEIGHT_EXPERIENCE,
                    geo_weight=settings.WEIGHT_PROXIMITY,
                )
                db.add(audit)
                await db.commit()

            except Exception as e:
                logger.error(f"Failed processing {filename}: {e}")
                await db.rollback()
                continue

        await _update_job_status(db, job_id, "completed",
                                 f"Processed {total} resumes successfully", total)

    except Exception as e:
        logger.error(f"Processing job {job_id} failed: {e}")
        await _update_job_status(db, job_id, "failed", error=str(e))
