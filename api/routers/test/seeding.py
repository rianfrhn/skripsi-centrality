import re
from fastapi import APIRouter, Depends
import pandas as pd
from sqlalchemy.orm import Session
import models
from routers.auth import register
from routers.agents import list_agents

from core.dependencies import get_db
from schemas.auth import UserRegister


router = APIRouter(prefix="/asdaszqnfg", tags=["test"])

@router.post("/seed_users", deprecated=True, summary="Menambahkan data dari excel, harap utk tidak digunakan")
def seed_users(
    db: Session = Depends(get_db)
):
    users = {}
    user_map = {}

    df = pd.read_excel('data/Formulir pendaftaran mitra R2.xlsx')
    for index, row in df.iterrows():
        data = row['Timestamp']
        if pd.isna(data): continue
        personname = row['Nama ( Sesuai KTP )'] 
        ref_key = row['ReferenceKey']
        reftarget = row['ReferenceTo']
        if pd.isna(ref_key):
            ref_key = None
        if pd.isna(reftarget):
            reftarget = None
        personaddress = row['Alamat Tempat Tinggal ( Sesuai KTP )']
        govaddress = row['Alamat Domisili ( Jika Berbeda dengan KTP ) wajib di tulis']
        telephone = str(row['No Telephone'])
        auto_username = to_username(personname)
        temp_email = f"tempx.{auto_username}@gmail.com"
        register_schema = UserRegister(
            name=personname,
            username=auto_username,
            email=temp_email,
            password=f"{auto_username}1234",
            reference_key=ref_key,
            #referral_key=reftarget,
            address=personaddress,
            gov_address=govaddress,
            phone=telephone,

        )
        try:
            new_user = register(
                credentials= register_schema,
                db= db
            )
            users[new_user.id] = (new_user, reftarget)
            user_map[ref_key] = new_user.id  # reference_key -> user_id


        except:
            print(f"error in seeding with user: {auto_username}")
    print(user_map)
    new_users = {}
    for user in users:
        userdata = users[user][0]
        user_refto = users[user][1]
        if user_refto and not pd.isna(user_refto) and not (user_refto in user_map):
            print(f"user reference key: {user_refto} not found,")
            auto_username = to_username(user_refto)
            print(f"registering {auto_username}")
            new_schema = UserRegister(
                name=user_refto,
                username=auto_username,
                email=f"tempx.{auto_username}@gmail.com",
                password=f"{auto_username}1234",
                reference_key=user_refto,
                #referral_key=reftarget,
                address="unknown",
                gov_address="unknown",
                phone="00000000000",

            )
            new_user = register(new_schema, db)

            new_users[new_user.id] = (new_user, None)
            user_map[user_refto] = new_user.id
    users.update(new_users)
    
    print(user_map)
    for user in users:
        userdata = users[user][0]
        refto = users[user][1]
        if refto in user_map:
            user_to_update = db.query(models.Agent).filter_by(id=user).first()
            if user_to_update:
                user_to_update.referred_by_id = user_map[refto]
                db.add(user_to_update)
    db.commit()


    # for index, row in df.iterrows():
    #     reference_key = row['ReferenceKey']
    #     reference_to = row['ReferenceTo']
        
    #     if reference_to in user_map:
    #         user_to_update = db.query(models.Agent).filter_by(reference_key=reference_key).first()
    #         if user_to_update:
    #             user_to_update.referred_by_id = user_map[reference_to]
    #             db.add(user_to_update)

    # db.commit()



def refresh_referrals(db: Session = Depends(get_db)):
    agents = list_agents(0,200,db=db)
    for agent in agents:
        referred = db.query(models.Agent).filter_by(reference_key=agent.referral_key).first()
        if referred:
            agent.referred_by = referred.id
            db.add(agent)
    db.commit()
            



def to_username(s):
    return re.sub(r'[^a-zA-Z0-9]', '', s)
