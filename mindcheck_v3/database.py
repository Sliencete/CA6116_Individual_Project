"""SQLite for local/pilot, optional persistent PostgreSQL via DATABASE_URL."""
import json
import os
import secrets
import string
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from demo_seed import DEMO_CODE, DEMO_SCOPE, DEMO_SOURCE, DEMO_QUESTIONS

DB_URL = os.environ.get("DATABASE_URL", "").strip()
if DB_URL.startswith("postgres://"):
    DB_URL = "postgresql+psycopg2://" + DB_URL[len("postgres://"):]
elif DB_URL.startswith("postgresql://"):
    DB_URL = "postgresql+psycopg2://" + DB_URL[len("postgresql://"):]
if not DB_URL:
    DB_URL = "sqlite:///" + str(Path(__file__).with_name("mindcheck.db").resolve()).replace("\\", "/")
ENGINE = create_engine(DB_URL, pool_pre_ping=True, pool_recycle=1800, connect_args={"timeout": 30} if DB_URL.startswith("sqlite:") else {})
IS_POSTGRES = ENGINE.dialect.name == "postgresql"

def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def init_db():
    id_col = "BIGSERIAL PRIMARY KEY" if IS_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"
    with ENGINE.begin() as c:
        c.execute(text(f"""CREATE TABLE IF NOT EXISTS checks(
            id {id_col}, check_code TEXT UNIQUE NOT NULL, topic TEXT NOT NULL,
            objectives TEXT NOT NULL, required_concepts TEXT, out_of_scope TEXT,
            strictness TEXT NOT NULL, source_work TEXT, questions_json TEXT NOT NULL,
            created_at TEXT NOT NULL)"""))
        c.execute(text(f"""CREATE TABLE IF NOT EXISTS responses(
            id {id_col}, check_code TEXT NOT NULL, student_label TEXT,
            confidence_before INTEGER, answers_json TEXT, evaluations_json TEXT,
            confidence_after INTEGER, reflection TEXT, submitted_at TEXT NOT NULL)"""))
        c.execute(text("CREATE INDEX IF NOT EXISTS idx_responses_code ON responses(check_code)"))
        c.execute(text("""INSERT INTO checks
            (check_code,topic,objectives,required_concepts,out_of_scope,strictness,source_work,questions_json,created_at)
            VALUES (:code,:topic,:objectives,:required,:out,:strictness,:source,:questions,:created)
            ON CONFLICT (check_code) DO NOTHING"""), {
            "code": DEMO_CODE, "topic": DEMO_SCOPE["topic"],
            "objectives": DEMO_SCOPE["objectives"], "required": DEMO_SCOPE["required_concepts"],
            "out": DEMO_SCOPE["out_of_scope"], "strictness": DEMO_SCOPE["strictness"],
            "source": DEMO_SOURCE, "questions": json.dumps(DEMO_QUESTIONS), "created": _now()
        })

def _code(topic):
    prefix = "".join(ch for ch in topic.upper() if ch.isalnum())[:4] or "CHECK"
    return prefix + "-" + "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))

def create_check(scope, source, questions):
    for _ in range(20):
        code = _code(scope["topic"])
        try:
            with ENGINE.begin() as c:
                c.execute(text("""INSERT INTO checks
                    (check_code,topic,objectives,required_concepts,out_of_scope,strictness,source_work,questions_json,created_at)
                    VALUES (:code,:topic,:objectives,:required,:out,:strictness,:source,:questions,:created)"""), {
                    "code":code, "topic":scope["topic"], "objectives":scope["objectives"],
                    "required":scope.get("required_concepts", ""), "out":scope.get("out_of_scope", ""),
                    "strictness":scope["strictness"], "source":source,
                    "questions":json.dumps(questions, ensure_ascii=False), "created":_now()
                })
            return code
        except IntegrityError:
            continue
    raise RuntimeError("Could not generate a unique check code")

def get_check(code):
    with ENGINE.connect() as c:
        row = c.execute(text("SELECT * FROM checks WHERE check_code=:code"), {"code":code.strip().upper()}).mappings().first()
    if not row:
        return None
    d = dict(row)
    d["questions"] = json.loads(d["questions_json"])
    d["scope"] = {k:d[k] for k in ("topic","objectives","required_concepts","out_of_scope","strictness")}
    d["scope"]["reference_material"] = d.get("source_work") or ""
    return d

def save_response(code,name,before,answers,evaluations,after,reflection):
    with ENGINE.begin() as c:
        c.execute(text("""INSERT INTO responses
            (check_code,student_label,confidence_before,answers_json,evaluations_json,confidence_after,reflection,submitted_at)
            VALUES (:code,:name,:before,:answers,:evaluations,:after,:reflection,:submitted)"""), {
            "code":code, "name":name or "Anonymous", "before":before,
            "answers":json.dumps(answers,ensure_ascii=False),
            "evaluations":json.dumps(evaluations,ensure_ascii=False),
            "after":after, "reflection":reflection, "submitted":_now()
        })

def response_count(code=DEMO_CODE):
    with ENGINE.connect() as c:
        return c.execute(text("SELECT COUNT(*) FROM responses WHERE check_code=:code"), {"code":code}).scalar_one()
