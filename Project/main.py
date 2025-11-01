from typing import List, Optional, Dict, Literal
from fastapi import FastAPI, HTTPException, Body
from sqlmodel import Session, select, desc
from data import engine, init_db
from model import (
    # core
    PersonalDB, Personal, PersonalOut, PersonalUpdate,
    FarmDB, Farm, FarmOut, FarmUpdate,
    DurianDB, Durian, DurianOut,DurianUpdate,


    # assess
    AssessmentCategoryDB, AssessmentCategoryOut,
    ActivityDB, ActivityOut, ActivityLevel, ActivitySearch,
    AnswerDB, Answer, AnswerOut,
    CriteriaDB,


    # agreement & lifecycle
    AgreementDB, Agreement, AgreementOut,
    AgreementAnswerDB, AgreementAnswer, AgreementAnswerOut,
    GAPRequestDB, GAPRequest, GAPRequestOut,
    InspectionDB, Inspection, InspectionOut,
    CertificationDB, Certification, CertificationOut,
)


app = FastAPI(title="GAP Durian Assessment API", version="1.3.0")
init_db()




# ---------------- helpers ----------------
def _ensure_user(session: Session, user_id: str):
    if session.get(PersonalDB, user_id) is None:
        raise HTTPException(404, "User not found")


def _score01(v: Optional[int]):
    if v is None:
        return
    if v not in (0, 1):
        raise HTTPException(422, "result_each must be 0 or 1")




# ---------------- seed master ----------------
@app.post("/seed/master", tags=["Master/Seed"])
def seed_master():
    with Session(engine) as session:
        if session.exec(select(AssessmentCategoryDB)).first():
            return {"message": "Already seeded"}


        cats = [
            "การจัดการน้ำ", "การจัดการที่ดิน", "การใช้ปุ๋ยและยา",
            "ยานพาหนะและอุปกรณ์", "การเก็บเกี่ยว", "การพักผลผลิต",
            "สถานที่ต่างๆ", "ผู้ปฏิบัติงาน"
        ]
        for name in cats:
            session.add(AssessmentCategoryDB(category_name=name))
        session.commit()


        specs = [
            # 1–7 (cat1)
            (1,"แหล่งน้ำที่ใช้ในการปลูกมาจากไหน?", "Major"),
            (1,"อัปโหลดรูปภาพ แหล่งน้ํา การเพาะปลูก", "Major"),
            (1,"แหล่งน้ําที่ใช้ในการปลูกทุเรียนผ่านการบําบัดมาก่อนหรือไม่?", "Major"),
            (1,"อัปโหลดรูปภาพการบำบัดน้ำ", "Major"),
            (1,"แหล่งน้ำที่ใช้หลังจากเก็บเกี่ยวผลผลิตมาจากไหน?", "Major"),
            (1,"มีเก็บตัวอย่างน้ำวิเคราะห์การปนเปื้อนในระยะเริ่มการผลิตหรือไม่?", "Minor"),
            (1,"วิธีที่ใช้บำบัดน้ำเสียคืออะไร?", "Minor"),
            # 8–15 (cat2)
            (2,"พื้นที่เพาะปลูกของคุณไม่เสี่ยงต่อการปนเปื้อนวัตถุหรือสิ่งอันตรายใช่หรือไม่?", "Major"),
            (2,"ถ้าพื้นที่ของคุณมีความเสี่ยง คุณมีการบำบัดให้อยู่ในระดับปลอดภัยหรือไม่?", "Major"),
            (2,"พื้นที่ปลูกเป็นไปตามข้อกำหนดของกฎหมายที่เกี่ยวข้องหรือไม่?", "Major"),
            (2,"มีการบันทึกการใช้สารเคมีกับพื้นที่ปลูก ครบถ้วนหรือไม่?", "Major"),
            (2,"มีการเก็บตัวอย่างดินเพื่อตรวจวิเคราะห์การปนเปื้อนในระยะเริ่มต้น และมีใบแจ้งผลวิเคราะห์ยืนยันหรือไม่?", "Minor"),
            (2,"พื้นที่ปลูกใหม่ไม่ส่งผลกระทบต่อสิ่งแวดล้อม หรือมีมาตรการป้องกันผลกระทบไว้แล้วใช่หรือไม่?", "Minor"),
            (2,"แนบรูปผังแปลง พร้อมคำอธิบายว่าคำนึงถึงสิ่งแวดล้อมอย่างไร", "Minor"),
            (2,"มีการจัดทำรหัสแปลงปลูกและข้อมูลประจำแปลง ครบถ้วน", "Minor"),
            # 16–21 (cat3)
            (3,"คุณใช้สิ่งขับถ่ายของคนเป็นปุ๋ยหรือไม่?", "Major"),
            (3,"ใช้สารเคมีตามคำแนะนำ และหยุดใช้ก่อนเก็บเกี่ยวตามฉลากหรือไม่?", "Major"),
            (3,"หากเคยตรวจพบสารพิษตกค้างเกินค่ามาตรฐาน มีการป้องกันซ้ำหรือไม่?", "Major"),
            (3,"ใช้วัตถุอันตรายที่ห้ามตามกฎหมายหรือไม่?", "Major"),
            (3,"ส่งออกปฏิบัติตามข้อกำหนดประเทศคู่ค้าหรือไม่?", "Major"),
            (3,"เลือกใช้ปุ๋ย/ปรับปรุงดินที่ขึ้นทะเบียนหรือไม่?", "Minor"),
            # 22–26 (cat4)
            (4,"วัสดุสัมผัสผลผลิตไม่ก่อปนเปื้อนหรือไม่?", "Major"),
            (4,"ล้างอุปกรณ์ทุกครั้งและจัดการน้ำล้างถูกต้องหรือไม่?", "Major"),
            (4,"ภาชนะของเสีย/สารเคมี/ปุ๋ย แยกจากภาชนะเก็บเกี่ยวหรือไม่?", "Minor"),
            (4,"ตรวจสอบเครื่องมือที่ต้องการความแม่นยำอย่างน้อยปีละครั้งหรือไม่?", "Minor"),
            (4,"สถานที่ปฏิบัติงานมีสุขลักษณะเพียงพอหรือไม่?", "Minor"),
            # 27–30 (cat5)
            (5,"เก็บเกี่ยวเมื่ออายุเหมาะสม/ตามข้อกำหนด", "Major"),
            (5,"คัดแยกผลผลิตไม่ได้คุณภาพออกก่อนส่ง", "Minor"),
            (5,"มีวิธีป้องกันการเสื่อมคุณภาพก่อนขนส่ง", "Minor"),
            (5,"มีการดูแลก่อนขนส่ง", "Minor"),
            # 31 (cat6)
            (6,"ผลผลิตที่คัดเลือก/บรรจุ/พัก ไม่สัมผัสพื้นดินโดยตรง", "Minor"),
            # 32–38 (cat7)
            (7,"มีที่เก็บสารเคมีเฉพาะ แยกชนิด ป้องกันปนเปื้อน", "Major"),
            (7,"สารเคมีเหลือใช้ปิดฝาสนิท/ติดข้อมูลครบ", "Minor"),
            (7,"กำจัดภาชนะสารเคมีหมดแล้วอย่างถูกต้อง", "Minor"),
            (7,"ภาชนะหมดอายุ/เสื่อมสภาพถูกแยกเก็บ/ทำลายถูกต้อง", "Minor"),
            (7,"ที่เก็บภาชนะ/อุปกรณ์ แยกจากสารเคมี/ปุ๋ย และกันสัตว์พาหะ", "Minor"),
            (7,"มีมาตรการกันสัตว์เลี้ยงในพื้นที่ปฏิบัติงาน", "Minor"),
            (7,"พื้นที่จัดการปุ๋ย/ปรับปรุงดิน/หมักอินทรีย์ เป็นสัดส่วน", "Minor"),
            (7,"สถานที่พัก/ขนย้าย/เก็บรักษา มีสุขลักษณะ", "Minor"),
            # 39–46 (cat8)
            (8,"จัดการสุขลักษณะป้องกันปนเปื้อน", "Major"),
            (8,"ผู้สัมผัสผลผลิตดูแลสุขลักษณะ", "Major"),
            (8,"มีความรู้สารเคมีและวิธีใช้", "Major"),
            (8,"ตรวจสุขภาพประจำปี", "Minor"),
            (8,"รู้สุขลักษณะส่วนบุคคล", "Minor"),
            (8,"รู้การปฐมพยาบาลเบื้องต้น", "Minor"),
            (8,"สวมอุปกรณ์ป้องกันครบ", "Minor"),
            (8,"อาบน้ำเปลี่ยนเสื้อผ้าหลังฉีดพ่น", "Minor"),
        ]
        for cid, name, typ in specs:
            session.add(ActivityDB(categoryapp_id=cid, activity_name=name, activity_type=ActivityLevel(typ)))
        session.commit()


        major_req = {1:5, 2:4, 3:5, 4:2, 5:1, 6:0, 7:1, 8:3}
        for cid, req in major_req.items():
            session.add(CriteriaDB(categoryapp_id=cid, activity_type=ActivityLevel.Major, score_require=req))
        session.add(CriteriaDB(categoryapp_id=None, activity_type=ActivityLevel.Minor, score_require=16))
        session.commit()
        return {"message": "seeded"}




# ---------------- Personal ----------------
@app.post("/personals", response_model=PersonalOut, status_code=201, tags=["Users"])
def create_personal(item: Personal):
    with Session(engine) as session:
        row = PersonalDB(**item.model_dump())
        session.add(row); session.commit(); session.refresh(row)
        return row

@app.get("/personals/by-name-surname/{name}/{surname}", response_model=List[PersonalOut], tags=["Users"])
def check_ID_by_name(name: str, surname: str):
    with Session(engine) as session:
        return session.exec(select(PersonalDB).where(PersonalDB.name == name, PersonalDB.surname == surname)).all()
        

@app.get("/personals", response_model=List[dict], tags=["Users"])
def list_person_basic():
    with Session(engine) as session:
        rows = session.exec(select(PersonalDB)).all()
        return [{"user_id": r.user_id, "name": r.name, "surname": r.surname} for r in rows]

@app.put("/personals/by-user/{user_id}", response_model=PersonalOut, tags=["Users"])
def update_personal_by_user(user_id: str, personal_update: PersonalUpdate):
    with Session(engine) as session:
        
        personal = session.get(PersonalDB, user_id)

        if personal != None:
            
            update_data = personal_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                if key != "user_id": 
                    setattr(personal, key, value)
            
            session.add(personal)
            session.commit()
            session.refresh(personal)
            print(personal)
            return personal

    raise HTTPException(
        status_code=404,
        detail="User id not found"
    )

# ---------------- Durian ----------------
@app.post("/durians", response_model=DurianOut, status_code=201, tags=["Durians"])
def create_durian(item: Durian):
    with Session(engine) as session:
        _ensure_user(session, item.user_id)
        row = DurianDB(**item.model_dump())
        session.add(row); session.commit(); session.refresh(row)
        return row

@app.get("/durians/by-user/{user_id}", response_model=List[DurianOut], tags=["Durians"])
def list_durians_by_user(user_id: str):
    with Session(engine) as session:
        return session.exec(select(DurianDB).where(DurianDB.user_id == user_id)).all()

@app.put("/durians/by-user/{user_id}", response_model=DurianOut, tags=["Durians"])
def update_durian_by_user(user_id: str, durian_update: DurianUpdate):
    with Session(engine) as session:
        
        durian = session.exec(select(DurianDB).where(DurianDB.user_id == user_id)).first()

        if durian != None:
            
            update_data = durian_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                if key not in ["durian_id", "user_id"]:  # do not update PK or user_id
                    setattr(durian, key, value)
            
            session.add(durian)
            session.commit()
            session.refresh(durian)
            print(durian)
            return durian

    raise HTTPException(
        status_code=404,
        detail="User id not found"
    )

# ---------------- Farm ----------------
@app.post("/farms", response_model=FarmOut, status_code=201, tags=["Farms"])
def create_farm(item: Farm):
    with Session(engine) as session:
        _ensure_user(session, item.user_id)
        row = FarmDB(**item.model_dump())
        session.add(row); session.commit(); session.refresh(row)
        return row


@app.get("/farms/by-user/{user_id}", response_model=List[FarmOut], tags=["Farms"])
def list_farms_by_user(user_id: str):
    with Session(engine) as session:
        return session.exec(select(FarmDB).where(FarmDB.user_id == user_id)).all()

@app.put("/farms/by-user/{user_id}", response_model=FarmOut, tags=["Farms"])
def update_farms_by_user(user_id: str, durian_update: FarmUpdate):
    with Session(engine) as session:
        
        farm = session.exec(select(FarmDB).where(FarmDB.user_id == user_id)).first()

        if farm != None:
            
            update_data = durian_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                if key not in ["farm_id", "user_id"]:  
                    setattr(farm, key, value)
            
            session.add(farm)
            session.commit()
            session.refresh(farm)
            print(farm)
            return farm

    raise HTTPException(
        status_code=404,
        detail="User id not found"
    )




# ---------------- Assessment (Categories/Activities/Answers/Evaluate) ----------------
@app.get("/categories", response_model=List[AssessmentCategoryOut], tags=["Assess"])
def list_categories():
    with Session(engine) as session:
        return session.exec(select(AssessmentCategoryDB)).all()


@app.get("/activities", response_model=List[ActivityOut], tags=["Assess"])
def list_activities(categoryapp_id: Optional[int] = None, activity_type: Optional[ActivityLevel] = None):
    with Session(engine) as session:
        stmt = select(ActivityDB)
        if categoryapp_id is not None:
            stmt = stmt.where(ActivityDB.categoryapp_id == categoryapp_id)
        if activity_type is not None:
            stmt = stmt.where(ActivityDB.activity_type == activity_type)
        return session.exec(stmt).all()


@app.post("/activities/search", response_model=List[ActivityOut], tags=["Assess"])
def search_activities(payload: ActivitySearch):
    with Session(engine) as session:
        stmt = select(ActivityDB)
        if payload.categoryapp_ids:
            stmt = stmt.where(ActivityDB.categoryapp_id.in_(payload.categoryapp_ids))
        if payload.activity_types:
            stmt = stmt.where(ActivityDB.activity_type.in_(payload.activity_types))
        if payload.keyword:
            stmt = stmt.where(ActivityDB.activity_name.contains(payload.keyword))
        return session.exec(stmt).all()


@app.post("/answers", response_model=AnswerOut, status_code=201, tags=["Assess"])
def insert_answer(item: Answer):
    with Session(engine) as session:
        _ensure_user(session, item.user_id)
        if session.get(ActivityDB, item.activity_id) is None:
            raise HTTPException(404, "Activity not found")
        if not item.answer_text and not item.answer_file and item.result_each is None:
            raise HTTPException(422, "Require answer_text or answer_file")
        _score01(item.result_each)
        exist = session.exec(select(AnswerDB).where(
            AnswerDB.user_id == item.user_id, AnswerDB.activity_id == item.activity_id
        )).first()
        if exist:
            for k, v in item.model_dump(exclude_unset=True).items():
                setattr(exist, k, v)
            session.add(exist); session.commit(); session.refresh(exist)
            return exist
        row = AnswerDB(**item.model_dump(exclude_unset=True))
        session.add(row); session.commit(); session.refresh(row)
        return row

@app.put("/answers", response_model=AnswerOut, status_code=201, tags=["Assess"])
def update_answer(item: Answer):
    with Session(engine) as session:

        _ensure_user(session, item.user_id)

        if session.get(ActivityDB, item.activity_id) is None:
            raise HTTPException(status_code=404, detail="Activity not found")

        if not item.answer_text and not item.answer_file:
            raise HTTPException(status_code=422, detail="Require answer_text or answer_file")

        exist = session.exec(select(AnswerDB).where(AnswerDB.user_id == item.user_id,AnswerDB.activity_id == item.activity_id)).first()

        if exist != None:
            if item.answer_text is not None:
                exist.answer_text = item.answer_text
            if item.answer_file is not None:
                exist.answer_file = item.answer_file

            session.add(exist)
            session.commit()
            session.refresh(exist)
            print(exist)
            return exist

        raise HTTPException(status_code=404, detail="not found")

@app.get("/activities/with-status", response_model=List[dict], tags=["Assess"])
def activities_with_status(user_id: str):
    with Session(engine) as session:
        acts = session.exec(select(ActivityDB)).all()
        answers = session.exec(select(AnswerDB).where(AnswerDB.user_id == user_id)).all()
        ans_map = {a.activity_id: a for a in answers}
        out = []
        for a in acts:
            rec = ans_map.get(a.activity_id)
            out.append({
                "activity_id": a.activity_id,
                "categoryapp_id": a.categoryapp_id,
                "activity_type": a.activity_type,
                "activity_name": a.activity_name,
                "answered": rec is not None,
                "scored": (rec is not None and rec.result_each is not None),
                "result_each": (rec.result_each if rec else None),
                "answer_id": (rec.answer_id if rec else None),
                "answer_text": (rec.answer_text if rec else None),
                "answer_file": (rec.answer_file if rec else None),
            })
        return out


@app.patch("/answers/score/{user_id}", response_model=List[AnswerOut], tags=["Assess/Admin"])
def admin_score(user_id: int, items: List[Answer] = Body(...)):
    with Session(engine) as session:
        _ensure_user(session, user_id)
        target_ids = [it.activity_id for it in items]
        exists = session.exec(
            select(AnswerDB.activity_id).where(
                AnswerDB.user_id == user_id,
                AnswerDB.activity_id.in_(target_ids)
            )
        ).all()
        exist_set = set(exists)
        missing = [aid for aid in target_ids if aid not in exist_set]
        if missing:
            raise HTTPException(status_code=400, detail={
                "msg": "พบ activity ที่ยังไม่มีคำตอบ จึงยังให้คะแนนไม่ได้",
                "missing_activity_ids": missing
            })
        out: List[AnswerDB] = []
        for it in items:
            _score01(it.result_each)
            rec = session.exec(select(AnswerDB).where(
                AnswerDB.user_id == user_id, AnswerDB.activity_id == it.activity_id
            )).first()
            rec.result_each = it.result_each
            session.add(rec); session.commit(); session.refresh(rec)
            out.append(rec)
        return out


@app.get("/assessment/evaluate", tags=["Assess"])
def evaluate(user_id: str):
    with Session(engine) as session:
        acts = session.exec(select(ActivityDB)).all()
        if not acts: raise HTTPException(400, "No activities configured")


        bycat: Dict[int, Dict[str, List[int]]] = {}
        for a in acts:
            bycat.setdefault(a.categoryapp_id, {"Major": [], "Minor": []})
            bycat[a.categoryapp_id][a.activity_type.value].append(a.activity_id)


        scored = session.exec(select(AnswerDB).where(
            AnswerDB.user_id == user_id, AnswerDB.result_each != None  # noqa
        )).all()
        scored_map = {a.activity_id: a.result_each for a in scored}


        missing = {}
        for cid, grp in bycat.items():
            miss_major = [x for x in grp["Major"] if x not in scored_map]
            miss_minor = [x for x in grp["Minor"] if x not in scored_map]
            if miss_major or miss_minor:
                cat = session.get(AssessmentCategoryDB, cid)
                missing[cid] = {
                    "category_name": cat.category_name if cat else str(cid),
                    "Major_missing": miss_major,
                    "Minor_missing": miss_minor
                }
        if missing:
            return {"user_id": user_id, "status": "incomplete", "missing": missing}


        per_cat_major: Dict[int, int] = {}
        minor_total = 0
        amap = {a.activity_id: (a.categoryapp_id, a.activity_type) for a in acts}
        for aid, val in scored_map.items():
            cid, typ = amap[aid]
            if typ == ActivityLevel.Major:
                per_cat_major[cid] = per_cat_major.get(cid, 0) + (1 if val == 1 else 0)
            else:
                minor_total += (1 if val == 1 else 0)


        crits = session.exec(select(CriteriaDB)).all()
        major_req = {c.categoryapp_id: c.score_require for c in crits if c.activity_type == ActivityLevel.Major}
        minor_req = next((c.score_require for c in crits if c.activity_type == ActivityLevel.Minor), None)


        per_cat_result = {}
        all_major_ok = True
        for cid in sorted(bycat.keys()):
            got = per_cat_major.get(cid, 0)
            req = major_req.get(cid, None)
            cat = session.get(AssessmentCategoryDB, cid)
            if req is None:
                per_cat_result[cid] = {"category_name": cat.category_name, "major_pass": got, "major_require": None, "status": "no_criteria"}
                all_major_ok = False
            else:
                ok = got >= req
                per_cat_result[cid] = {"category_name": cat.category_name, "major_pass": got, "major_require": req, "status": "pass" if ok else "fail"}
                if not ok: all_major_ok = False


        minor_ok = True if minor_req is None else (minor_total >= minor_req)
        eligible = all_major_ok and minor_ok


        return {
            "user_id": user_id,
            "status": "complete",
            "per_category": per_cat_result,
            "minor_total_pass": minor_total,
            "minor_require": minor_req,
            "eligible_for_request": eligible
        }




# ---------------- Agreement / GAP lifecycle ----------------
@app.post("/agreements", response_model=AgreementOut, status_code=201, tags=["GAP/Admin"])
def create_agreement(item: Agreement):
    with Session(engine) as session:
        row = AgreementDB(**item.model_dump())
        session.add(row); session.commit(); session.refresh(row)
        return row


@app.post("/agreement-answers", response_model=AgreementAnswerOut, status_code=201, tags=["GAP/User"])
def create_agreement_answer(item: AgreementAnswer):
    with Session(engine) as session:
        _ensure_user(session, item.user_id)
        if session.get(AgreementDB, item.agreement_id) is None:
            raise HTTPException(404, "Agreement not found")
        row = AgreementAnswerDB(**item.model_dump())
        session.add(row); session.commit(); session.refresh(row)
        return row


@app.post("/gap-requests", response_model=GAPRequestOut, status_code=201, tags=["GAP/Admin"])
def create_gap_request(item: GAPRequest, user_id: str):
    with Session(engine) as session:
        farm = session.get(FarmDB, item.farm_id)
        if not farm: raise HTTPException(404, "Farm not found")
        if farm.user_id != user_id: raise HTTPException(403, "ไม่ใช่เจ้าของฟาร์ม")


        result = evaluate(user_id=user_id)
        if result.get("status") != "complete" or not result.get("eligible_for_request"):
            raise HTTPException(400, "ยังไม่ผ่านเกณฑ์ประเมิน")


        has_durian = session.exec(select(DurianDB).where(DurianDB.user_id == user_id)).first() is not None
        if not has_durian: raise HTTPException(400, "ต้องบันทึกข้อมูล Durian ให้เรียบร้อย")


        all_agrs = session.exec(select(AgreementDB)).all()
        accepted = session.exec(select(AgreementAnswerDB).where(
            AgreementAnswerDB.user_id == user_id, AgreementAnswerDB.agreement_answer == "ยอมรับ"
        )).all()
        if len(all_agrs) > 0 and len(accepted) < len(all_agrs):
            raise HTTPException(400, "ยังไม่ได้ยอมรับข้อตกลงครบ")


        row = GAPRequestDB(**item.model_dump())
        session.add(row); session.commit(); session.refresh(row)
        return row


@app.patch("/gap-requests/status/{request_id}", response_model=GAPRequestOut, tags=["GAP/Admin"])
def update_gap_request_status(request_id: int, timeline_status: str):
    """อัปเดตสถานะคำขอ (เช่น รอจัดผู้ตรวจสอบ → อยู่ระหว่างตรวจ → ตรวจเสร็จ → ออกเกียรติบัตรแล้ว)"""
    with Session(engine) as session:
        req = session.get(GAPRequestDB, request_id)
        if not req:
            raise HTTPException(404, "GAP request not found")
        req.timeline_status = timeline_status
        session.add(req); session.commit(); session.refresh(req)
        return req


@app.get("/gap-requests/by-user/{user_id}", response_model=List[GAPRequestOut], tags=["GAP/User"])
def list_gap_requests_by_user(user_id: str):
    with Session(engine) as session:
        _ensure_user(session, user_id)
        farm_ids = session.exec(select(FarmDB.farm_id).where(FarmDB.user_id == user_id)).all()
        if not farm_ids:
            return []
        rows = session.exec(
            select(GAPRequestDB)
            .where(GAPRequestDB.farm_id.in_(farm_ids))
            .order_by(desc(GAPRequestDB.request_id))
        ).all()
        return rows


@app.post("/inspections", response_model=InspectionOut, status_code=201, tags=["GAP/Admin"])
def create_inspection(item: Inspection):
    with Session(engine) as session:
        if session.get(GAPRequestDB, item.request_id) is None:
            raise HTTPException(404, "Request not found")
        row = InspectionDB(**item.model_dump())
        session.add(row); session.commit(); session.refresh(row)
        return row


@app.get("/inspections/by-request/{request_id}", response_model=List[InspectionOut], tags=["GAP/Admin"])
def list_inspections_by_request(request_id: int):
    with Session(engine) as session:
        return session.exec(
            select(InspectionDB).where(InspectionDB.request_id == request_id).order_by(desc(InspectionDB.inspector_id))
        ).all()


@app.post("/certifications", response_model=CertificationOut, status_code=201, tags=["GAP/Admin"])
def create_cert(item: Certification):
    with Session(engine) as session:
        if session.get(GAPRequestDB, item.request_id) is None:
            raise HTTPException(404, "Request not found")
        row = CertificationDB(**item.model_dump())
        session.add(row); session.commit(); session.refresh(row)
        return row


@app.get("/certifications/by-user/{user_id}", response_model=List[CertificationOut], tags=["GAP/User"])
def list_certs_by_user(user_id: str):
    """ให้ผู้ใช้ดูใบรับรองของตนเองสะดวก ๆ"""
    with Session(engine) as session:
        _ensure_user(session, user_id)
        farm_ids = session.exec(select(FarmDB.farm_id).where(FarmDB.user_id == user_id)).all()
        if not farm_ids:
            return []
        req_ids = session.exec(select(GAPRequestDB.request_id).where(GAPRequestDB.farm_id.in_(farm_ids))).all()
        if not req_ids:
            return []
        return session.exec(select(CertificationDB).where(CertificationDB.request_id.in_(req_ids))).all()



