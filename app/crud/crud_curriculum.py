from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import CourseCurriculum, CurriculumMaterial
from app.schemas.content import CurriculumCreate, CurriculumUpdate


async def get_curriculum_by_course(db: AsyncSession, course_id: int) -> list[CourseCurriculum]:
    result = await db.execute(
        select(CourseCurriculum)
        .where(CourseCurriculum.course_id == course_id, CourseCurriculum.status.is_(True))
        .order_by(CourseCurriculum.topic_order)
    )
    return list(result.scalars().all())


async def get_curriculum_item(db: AsyncSession, curriculum_id: int) -> CourseCurriculum | None:
    result = await db.execute(
        select(CourseCurriculum).where(CourseCurriculum.curriculum_id == curriculum_id)
    )
    return result.scalar_one_or_none()


async def create_curriculum(
    db: AsyncSession, course_id: int, data: CurriculumCreate
) -> CourseCurriculum:
    item = CourseCurriculum(course_id=course_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def update_curriculum(
    db: AsyncSession, item: CourseCurriculum, data: CurriculumUpdate
) -> CourseCurriculum:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


async def soft_delete_curriculum(db: AsyncSession, item: CourseCurriculum) -> None:
    item.status = False
    await db.commit()


async def hard_delete_curriculum(db: AsyncSession, item: CourseCurriculum) -> None:
    """Actually removes the row (and its materials, via DB cascade)."""
    await db.delete(item)
    await db.commit()


# ---------- study materials ----------
async def get_material(db: AsyncSession, material_id: int) -> CurriculumMaterial | None:
    result = await db.execute(
        select(CurriculumMaterial).where(CurriculumMaterial.material_id == material_id)
    )
    return result.scalar_one_or_none()


async def add_material(
    db: AsyncSession,
    curriculum_id: int,
    title: str,
    url: str,
    public_id: str | None,
    file_type: str | None,
    resource_type: str | None = None,
) -> CurriculumMaterial:
    material = CurriculumMaterial(
        curriculum_id=curriculum_id,
        title=title,
        url=url,
        public_id=public_id,
        file_type=file_type,
        resource_type=resource_type,
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return material


async def delete_material(db: AsyncSession, material: CurriculumMaterial) -> None:
    await db.delete(material)
    await db.commit()


async def delete_all_materials_for_curriculum(db: AsyncSession, curriculum_id: int) -> None:
    """Hard-deletes every material row for a topic. Call this when the topic itself is removed."""
    result = await db.execute(
        select(CurriculumMaterial).where(CurriculumMaterial.curriculum_id == curriculum_id)
    )
    for material in result.scalars().all():
        await db.delete(material)
    await db.commit()
