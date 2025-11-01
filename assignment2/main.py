from typing import Optional, Literal, List
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, EmailStr
from datetime import date


class PersonalDB(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    surname: str
    user_type: str          
    phone_number: str
    email: str              
    idcard_file: str
    id_number: str
    birth: date
    religion: str
    village_name: str
    house_number: str
    road: str
    alley: str
    province: str
    district: str
    subdistrict: str


engine = create_engine("sqlite:///data.db")
SQLModel.metadata.create_all(engine)


class Personal(BaseModel):
    name: str
    surname: str
    user_type: Literal["individual", "group"]  
    phone_number: str
    email: EmailStr                            
    idcard_file: str
    id_number: str
    birth: date
    religion: str
    village_name: str
    house_number: str
    road: str
    alley: str
    province: str
    district: str
    subdistrict: str


class PersonalOut(Personal):
    id: int


app = FastAPI()


@app.get("/personals/{personal_id}")
async def read_personal_by_id(personal_id: int) -> PersonalOut:
    with Session(engine) as session:
        statement = select(PersonalDB).where(PersonalDB.id == personal_id)
        personal = session.exec(statement).first()

        if personal != None:
            print(personal)
            return personal

    raise HTTPException(
        status_code=404,
        detail="Personal id not found",
    )

def insert_personal():
    p1 = PersonalDB(
        name="Nice", surname="Techai", user_type="individual",
        phone_number="095-000-0001", email="nice@example.com",
        idcard_file="id001.png", id_number="1234567890123",
        birth=date(2003, 1, 1), religion="Buddhism",
        village_name="Ban A", house_number="99/9",
        road="Main", alley="-", province="Bangkok",
        district="Pathumwan", subdistrict="Lumphini"
    )
    p2 = PersonalDB(
        name="Jojo", surname="Bravo", user_type="group",
        phone_number="095-000-0002", email="jojo@example.com",
        idcard_file="id002.png", id_number="2345678901234",
        birth=date(2002, 5, 12), religion="Christianity",
        village_name="Ban B", house_number="12/3",
        road="Second", alley="Soi 5", province="Chiang Mai",
        district="Mueang", subdistrict="Suthep"
    )
    p3 = PersonalDB(
        name="Alice", surname="Wong", user_type="individual",
        phone_number="095-000-0003", email="alice@example.com",
        idcard_file="id003.png", id_number="3456789012345",
        birth=date(2001, 9, 30), religion="None",
        village_name="Ban C", house_number="7",
        road="Third", alley="-", province="Phuket",
        district="Mueang", subdistrict="Talat Yai"
    )
    p4 = PersonalDB(
        name="Bob", surname="Smith", user_type="group",
        phone_number="095-000-0004", email="bob@example.com",
        idcard_file="id004.png", id_number="4567890123456",
        birth=date(1999, 12, 15), religion="Islam",
        village_name="Ban D", house_number="21/5",
        road="Fourth", alley="Soi 10", province="Khon Kaen",
        district="Mueang", subdistrict="Nai Mueang"
    )


    with Session(engine) as session:
        session.add_all([p1, p2, p3, p4])
        session.commit()

insert_personal()

"""def delete_personal():
    id_delete = [2, 3, 4, 5, 6, 7, 8, 9, 10]
    with Session(engine) as session:
        statement = select(PersonalDB).where(PersonalDB.id.in_(id_delete))
        people = session.exec(statement).all()

        if not people:
            print("❌ No matching records found.")
            return

        for person in people:
            session.delete(person)
            print(f"✅ Deleted ID {person.id}")

        session.commit()
        print("✅ All specified records deleted.")

delete_personal()"""