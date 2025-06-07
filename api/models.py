from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, func

from sqlalchemy.orm import relationship

from api.database import Base, engine

class Installment(Base):
    __tablename__ = "installments"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    installment_duration = Column(Integer) # in days
    remaining_duration = Column(Integer) 
    total_paid = Column(Integer)
    status = Column(String(63)) #Pending, Accepted, Declined
    applied_at = Column(DateTime, default=func.now())
    accepted_at = Column(DateTime)
    vehicle = relationship("Vehicle", backref="installments")
    agent = relationship("Agent", backref="installments")

    


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    hashed_password = Column(String(1000))
    name = Column(String(50), unique=True, nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(255), nullable=True)
    gov_address = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    marriage_status = Column(String(50))
    settlement_status = Column(String(50))
    installment_status = Column(Boolean)
    verified = Column(Boolean, default=False)
    reference_key = Column(String(50), unique=True)

    referred_by_id   = Column(Integer, ForeignKey("agents.id"), nullable=True)
    
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),   # populate existing rows & future inserts
    )
    verified_at = Column(
        DateTime,
        nullable=True,
        default=None,
    )
    referred_by      = relationship(
        "Agent",
        back_populates="referrals",
        remote_side=[id]
    )


    #reference = Column(String(50), ForeignKey('agents.reference_key'))
    referrals        = relationship(
        "Agent",
        back_populates="referred_by",
        cascade="all, delete-orphan"
    )
    

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    hashed_password = Column(String(1000))

class Document(Base):
    __tablename__ = "documents"
    agent_id = Column(Integer, ForeignKey("agents.id"), primary_key=True)
    owner = relationship("Agent", backref="documents")
    national_id_url = Column(String(255), nullable=True)
    self_portrait_url = Column(String(255), nullable=True)
    partner_portrait_url = Column(String(255), nullable=True)
    family_card_url = Column(String(255), nullable=True) 

class Dealer(Base):
    __tablename__ = "dealers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    phone_number = Column(Integer)
    address = Column(String(255))

class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)
    quantity = Column(Integer)
    price = Column(Integer)
    display_image = Column(String(255))
    description = Column(String(2047))
    dealer_id = Column(Integer, ForeignKey("dealers.id"))
    dealer = relationship("Dealer", backref="vehicles")

class AgentBonus(Base):
    __tablename__ = "agent_bonuses"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    agent = relationship("Agent")
    amount = Column(Float)

class InstallmentPayment(Base):
    __tablename__ = "InstallmentPayment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    installment_id = Column(Integer, ForeignKey("installments.id"))
    installment = relationship("Installment")
    amount = Column(Float)
    payment_date = Column(DateTime, nullable=True)

class SpecialKeys(Base):
    __tablename__ = "special_keys"
    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True)
    value = Column(String(60))

    

def initialize(base, engine):
    base.metadata.create_all(engine)
