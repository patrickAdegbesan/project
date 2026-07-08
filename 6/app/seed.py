"""Seed the database with initial job roles and sample data."""
import asyncio
import json
from app.models.database import AsyncSessionLocal, init_db, JobRole, Candidate, Resume, ExtractedEntity, CandidateScore
from app.config import settings


SEED_ROLES = [
    {
        "title": "Area Sales Manager (ASM)",
        "description": "Manages sales activities within a designated area, drives revenue targets, and builds client relationships across retail partners.",
        "required_skills": [
            "Sales", "Team Management", "Customer Relationship Management",
            "Target Achievement", "Hair Products", "Presentation Skills",
            "Communication", "Microsoft Excel", "Territory Management",
        ],
        "min_experience": 3.0,
        "hub_lat": settings.HUB_LAT,
        "hub_long": settings.HUB_LONG,
    },
    {
        "title": "Regional Sales Manager (RSM)",
        "description": "Oversees multiple area sales managers, sets regional KPIs, and drives strategic sales initiatives for Lush Hair across Lagos and surrounding regions.",
        "required_skills": [
            "Sales Management", "Leadership", "Business Development",
            "KPI Management", "P&L Management", "Coaching", "Negotiation",
            "Market Research", "Beauty Industry", "Strategic Planning",
        ],
        "min_experience": 5.0,
        "hub_lat": settings.HUB_LAT,
        "hub_long": settings.HUB_LONG,
    },
    {
        "title": "Dispatch Rider",
        "description": "Responsible for timely delivery of hair products to customers and retail partners across Lagos. Must be familiar with Lagos routes.",
        "required_skills": [
            "Delivery", "Route Navigation", "Customer Service",
            "Time Management", "Lagos Knowledge", "Logistics",
        ],
        "min_experience": 1.0,
        "hub_lat": settings.HUB_LAT,
        "hub_long": settings.HUB_LONG,
    },
]


SAMPLE_CANDIDATES = [
    {
        "name": "Adaeze Nwosu",
        "email": "adaeze.nwosu@email.com",
        "phone": "08031234567",
        "location": "Ikeja",
        "experience_years": 4.0,
        "skills": ["Sales", "Customer Relationship Management", "Hair Products", "Communication", "Microsoft Excel"],
        "education": "BACHELORS",
        "lat": 6.6018, "lon": 3.3515,
    },
    {
        "name": "Chukwuemeka Obi",
        "email": "emeka.obi@email.com",
        "phone": "07054321890",
        "location": "Surulere",
        "experience_years": 6.0,
        "skills": ["Sales Management", "Leadership", "Business Development", "KPI Management", "Coaching"],
        "education": "MASTERS",
        "lat": 6.4969, "lon": 3.3572,
    },
    {
        "name": "Fatima Yusuf",
        "email": "fatima.yusuf@email.com",
        "phone": "09087654321",
        "location": "Yaba",
        "experience_years": 2.0,
        "skills": ["Delivery", "Route Navigation", "Lagos Knowledge", "Time Management"],
        "education": "OND",
        "lat": 6.5076, "lon": 3.3742,
    },
]


async def seed():
    await init_db()

    async with AsyncSessionLocal() as db:
        # Check if already seeded
        from sqlalchemy import select, func
        count = await db.scalar(select(func.count(JobRole.id)))
        if count and count > 0:
            print("Database already seeded — skipping.")
            return

        # Seed job roles
        role_objects = []
        for r in SEED_ROLES:
            role = JobRole(
                title=r["title"],
                description=r["description"],
                required_skills=json.dumps(r["required_skills"]),
                hub_lat=r["hub_lat"],
                hub_long=r["hub_long"],
                min_experience=r["min_experience"],
            )
            db.add(role)
            role_objects.append(role)

        await db.flush()

        # Seed sample candidates
        for i, c in enumerate(SAMPLE_CANDIDATES):
            candidate = Candidate(
                full_name=c["name"],
                email=c["email"],
                phone=c["phone"],
            )
            db.add(candidate)
            await db.flush()

            resume = Resume(
                candidate_id=candidate.id,
                raw_text=f"Sample resume for {c['name']}.",
                file_path=f"sample_{c['name'].replace(' ', '_')}.pdf",
                file_name=f"sample_{c['name'].replace(' ', '_')}.pdf",
                res_lat=c["lat"],
                res_long=c["lon"],
            )
            db.add(resume)
            await db.flush()

            # Entities
            for skill in c["skills"]:
                db.add(ExtractedEntity(resume_id=resume.id, entity_type="SKILL",
                                       entity_value=skill, confidence_score=0.9))
            db.add(ExtractedEntity(resume_id=resume.id, entity_type="EDUCATION",
                                   entity_value=c["education"], confidence_score=0.9))
            db.add(ExtractedEntity(resume_id=resume.id, entity_type="LOCATION",
                                   entity_value=c["location"], confidence_score=0.9))
            db.add(ExtractedEntity(resume_id=resume.id, entity_type="EXPERIENCE",
                                   entity_value=str(c["experience_years"]), confidence_score=0.9))

            # Score against first matching job role (by index for demo)
            role = role_objects[min(i, len(role_objects) - 1)]
            from app.services.scoring import skill_match_score, normalize_experience, calculate_total_score
            from app.services.geospatial import haversine, distance_score
            required = json.loads(role.required_skills)
            sk, matched, missing = skill_match_score(c["skills"], required)
            ex = normalize_experience(c["experience_years"], role.min_experience)
            dist = haversine(c["lat"], c["lon"], role.hub_lat, role.hub_long)
            prx = distance_score(dist)
            total = calculate_total_score(sk, ex, prx)

            score = CandidateScore(
                resume_id=resume.id,
                job_id=role.id,
                skill_score=sk,
                exp_score=ex,
                proximity_score=prx,
                total_score=total,
                distance_km=round(dist, 2),
                skill_gap=json.dumps({
                    "summary": f"Candidate has {len(matched)} of {len(required)} required skills.",
                    "matched": matched,
                    "missing": missing,
                }),
            )
            db.add(score)

        await db.commit()
        print(f"✓ Seeded {len(SEED_ROLES)} job roles and {len(SAMPLE_CANDIDATES)} sample candidates.")


if __name__ == "__main__":
    asyncio.run(seed())
