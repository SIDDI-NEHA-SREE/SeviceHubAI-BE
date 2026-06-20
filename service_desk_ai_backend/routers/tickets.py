from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from pydantic import BaseModel, Field
import datetime
import uuid

from .. import models, database, auth

router = APIRouter(prefix="/tickets", tags=["tickets"])

class TicketCreate(BaseModel):
    ticket_id: str = Field(..., max_length=20)
    title: str = Field(..., max_length=255)
    description: str
    category: str | None = None
    priority: str | None = None
    assigned_to: uuid.UUID | None = None

class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    priority: str | None = None
    status: str | None = None
    assigned_to: uuid.UUID | None = None

class TicketResponse(BaseModel):
    ticket_id: str
    title: str
    description: str
    category: str | None = None
    priority: str | None = None
    status: str
    created_by: uuid.UUID
    assigned_to: uuid.UUID | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    resolved_at: datetime.datetime | None = None

@router.post("/", response_model=TicketResponse)
async def create_ticket(ticket: TicketCreate, current_user: models.User = Depends(auth.get_current_user), db: AsyncSession = Depends(database.get_db)):
    db_ticket = models.Ticket(**ticket.dict(), created_by=current_user.user_id)
    db.add(db_ticket)
    await db.commit()
    await db.refresh(db_ticket)
    # Add initial history entry
    history = models.TicketHistory(ticket_id=db_ticket.ticket_id, old_status=None, new_status=db_ticket.status, changed_by=current_user.user_id, comments="Ticket created")
    db.add(history)
    await db.commit()
    return TicketResponse(**db_ticket.__dict__)

@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: str, current_user: models.User = Depends(auth.get_current_user), db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Ticket).where(models.Ticket.ticket_id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    # Permission: employees can only view their own tickets unless manager/admin
    if current_user.role not in ["admin", "manager", "service_agent"] and ticket.created_by != current_user.user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return TicketResponse(**ticket.__dict__)

@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(ticket_id: str, ticket_update: TicketUpdate, current_user: models.User = Depends(auth.require_role("admin", "manager", "service_agent")), db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Ticket).where(models.Ticket.ticket_id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    # Record old status for history
    old_status = ticket.status
    # Apply updates
    update_data = ticket_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ticket, key, value)
    ticket.updated_at = datetime.datetime.utcnow()
    await db.commit()
    await db.refresh(ticket)
    # Add history if status changed
    if "status" in update_data and old_status != ticket.status:
        history = models.TicketHistory(ticket_id=ticket.ticket_id, old_status=old_status, new_status=ticket.status, changed_by=current_user.user_id, comments="Status updated")
        db.add(history)
        await db.commit()
    return TicketResponse(**ticket.__dict__)

@router.delete("/{ticket_id}", status_code=204)
async def delete_ticket(ticket_id: str, current_user: models.User = Depends(auth.require_role("admin")), db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Ticket).where(models.Ticket.ticket_id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await db.execute(models.Ticket.__table__.delete().where(models.Ticket.ticket_id == ticket_id))
    await db.commit()
    return None
