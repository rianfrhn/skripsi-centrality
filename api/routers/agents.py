from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session
from schemas.misc import ApprovalPoint, SimpleCount
import models
from core.security import get_current_admin, get_current_agent
import crud
from schemas import(
    agent as agent_schema
)
from crud.crud_agent import agent as agents
from core.dependencies import get_db, get_current_active_agent

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/", response_model=List[agent_schema.AgentRead])
def list_agents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return agents.get_multi(db=db, skip=skip, limit=limit)

@router.get("/me", response_model=agent_schema.AgentRead)
def get_my_info(
        db: Session = Depends(get_db),
        current: models.Agent = Depends(get_current_agent),
              ):
    agent = get_agent(current.id, db)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.get("/paged", response_model=agent_schema.AgentPagination)
def list_vehicles_paged(
    page: int = 1,
    page_size: int = 100,
    db: Session = Depends(get_db)
):
    total = agents.get_multi(db, limit=9999).__len__()
    skip = (page-1) * page_size
    return agent_schema.AgentPagination(total=total, page_content=agents.get_multi(db, skip=skip, limit=page_size))

@router.get("/approvals", response_model=list[ApprovalPoint])
def agent_approvals(weeks: int = Query(4, ge=1, le=12), db: Session = Depends(get_db)):
    return agents.agent_approvals(db, weeks=weeks)
@router.get("/pending", response_model=SimpleCount)
def pending_verifications(db: Session = Depends(get_db)):
    return agents.get_pending_verifications(db=db)

@router.get("/{agent_id}", response_model=agent_schema.AgentRead)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = agents.get(db=db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.patch("/update", response_model=agent_schema.AgentRead)
def update_me(
    obj_in: agent_schema.AgentUpdate,
    current: models.Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    agent = agents.get(db=db, id=current.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents.update(db=db, db_obj=agent, obj_in=obj_in)




@router.patch("/{agent_id}", response_model=agent_schema.AgentRead)
def update_agent(
    agent_id: int,
    obj_in: agent_schema.AgentUpdate,
    #current: agent_schema.AgentRead = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    agent = agents.get(db=db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents.update(db=db, db_obj=agent, obj_in=obj_in)


@router.delete("/{agent_id}")
def delete_agent(
    agent_id: int,
    #current=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    agents.remove(db=db, id=agent_id)
    return {"ok": True}
