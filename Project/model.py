from __future__ import annotations
from typing import Optional, List
from datetime import date
from enum import Enum
from pydantic import BaseModel
from sqlmodel import SQLModel, Field




# ===============================
# ENUM
# ===============================
class ActivityLevel(str, Enum):
    Major = "Major"
    Minor = "Minor"




# ===============================
# 1) ผู้ใช้ / ฟาร์ม / ทุเรียน
# ===============================
class PersonalDB(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)  # DB gen
    name: str
    surname: str
    phone_number: str
    user_type: str
    idcard_file: str
    birth: date
    religion: str
    id_number: str
    village_name: str
    house_number: str
    road: str
    alley: str
    province: str
    district: str
    subdistrict: str


class Personal(BaseModel):  # ไม่ต้องมี user_id ตอนสร้าง
    name: str
    surname: str
    phone_number: str
    user_type: str
    idcard_file: str
    birth: date
    religion: str
    id_number: str
    village_name: str
    house_number: str
    road: str
    alley: str
    province: str
    district: str
    subdistrict: str


class PersonalOut(Personal):
    user_id: int

class PersonalUpdate(Personal):
    user_id: int




class FarmDB(SQLModel, table=True):
    farm_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    location: Optional[str] = None
    titledeed_num: Optional[str] = None
    titledeed_file: Optional[str] = None


class Farm(BaseModel):
    user_id: str
    location: Optional[str] = None
    titledeed_num: Optional[str] = None
    titledeed_file: Optional[str] = None


class FarmOut(Farm):
    farm_id: int

class FarmUpdate(Farm):
    farm_id: int


class DurianDB(SQLModel, table=True):
    durian_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    durian_type: Optional[str] = None
    durian_age: Optional[int] = None
    tree_count: Optional[int] = None
    flowering_startdate: Optional[date] = None
    harvest_month: Optional[str] = None
    weight_expected: Optional[float] = None


class Durian(BaseModel):
    user_id: str
    durian_type: Optional[str] = None
    durian_age: Optional[int] = None
    tree_count: Optional[int] = None
    flowering_startdate: Optional[date] = None
    harvest_month: Optional[str] = None
    weight_expected: Optional[float] = None


class DurianOut(Durian):
    durian_id: int

class DurianUpdate(Durian):
    durian_id: int

# ===============================
# 2) แบบประเมิน
# ===============================
class AssessmentCategoryDB(SQLModel, table=True):
    categoryapp_id: Optional[int] = Field(default=None, primary_key=True)
    category_name: str


class AssessmentCategory(BaseModel):
    category_name: str


class AssessmentCategoryOut(AssessmentCategory):
    categoryapp_id: int




class ActivityDB(SQLModel, table=True):
    activity_id: Optional[int] = Field(default=None, primary_key=True)
    categoryapp_id: int
    activity_name: str
    activity_type: ActivityLevel


class Activity(BaseModel):
    categoryapp_id: int
    activity_name: str
    activity_type: ActivityLevel


class ActivityOut(Activity):
    activity_id: int




class AnswerDB(SQLModel, table=True):
    answer_id: Optional[int] = Field(default=None, primary_key=True)
    activity_id: int
    user_id: str
    answer_file: Optional[str] = None
    answer_text: Optional[str] = None
    result_each: Optional[int] = None  # admin ใส่ 0/1 ภายหลัง


class Answer(BaseModel):
    activity_id: int
    user_id: str
    answer_file: Optional[str] = None
    answer_text: Optional[str] = None
    result_each: Optional[int] = None


class AnswerOut(Answer):
    answer_id: int




class CriteriaDB(SQLModel, table=True):
    criteria_id: Optional[int] = Field(default=None, primary_key=True)
    categoryapp_id: Optional[int] = None  # Major=มีหมวด, Minor=None (global)
    activity_type: ActivityLevel
    score_require: int


class Criteria(BaseModel):
    categoryapp_id: Optional[int] = None
    activity_type: ActivityLevel
    score_require: int


class CriteriaOut(Criteria):
    criteria_id: int




# ===============================
# 3) Agreement / GAP / Inspection / Certificate
# ===============================
class AgreementDB(SQLModel, table=True):
    agreement_id: Optional[int] = Field(default=None, primary_key=True)
    agreement_text: str


class Agreement(BaseModel):
    agreement_text: str


class AgreementOut(Agreement):
    agreement_id: int




class AgreementAnswerDB(SQLModel, table=True):
    ag_answer_id: Optional[int] = Field(default=None, primary_key=True)
    agreement_id: int
    user_id: str
    agreement_answer: str  # "ยอมรับ" / "ไม่ยอมรับ"


class AgreementAnswer(BaseModel):
    agreement_id: int
    user_id: str
    agreement_answer: str


class AgreementAnswerOut(AgreementAnswer):
    ag_answer_id: int




class GAPRequestDB(SQLModel, table=True):
    request_id: Optional[int] = Field(default=None, primary_key=True)
    farm_id: int
    request_date: date
    timeline_status: str  # ex. รอจัดผู้ตรวจสอบ / อยู่ระหว่างตรวจ / ตรวจเสร็จ / ออกเกียรติบัตรแล้ว


class GAPRequest(BaseModel):
    farm_id: int
    request_date: date
    timeline_status: str = "รอจัดผู้ตรวจสอบ"


class GAPRequestOut(GAPRequest):
    request_id: int




class InspectionDB(SQLModel, table=True):
    inspector_id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int
    complete_date: date
    status_result: str  # "ผ่าน" / "ไม่ผ่าน"


class Inspection(BaseModel):
    request_id: int
    complete_date: date
    status_result: str


class InspectionOut(Inspection):
    inspector_id: int




class CertificationDB(SQLModel, table=True):
    cert_id: Optional[int] = Field(default=None, primary_key=True)
    request_id: int
    farm_id: int
    issue_date: date
    expire_date: date
    cert_file: str
    addition: Optional[str] = None


class Certification(BaseModel):
    request_id: int
    farm_id: int
    issue_date: date
    expire_date: date
    cert_file: str
    addition: Optional[str] = None


class CertificationOut(Certification):
    cert_id: int




# ===============================
# 4) POST search activities (หลายฟิลด์)
# ===============================
class ActivitySearch(BaseModel):
    categoryapp_ids: Optional[List[int]] = None
    activity_types: Optional[List[ActivityLevel]] = None
    keyword: Optional[str] = None



