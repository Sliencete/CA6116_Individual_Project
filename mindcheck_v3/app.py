import streamlit as st
import os
from html import escape
from dotenv import load_dotenv
load_dotenv(override=False)
# Community Cloud secrets and local .env both work; credentials never go into source code.
try:
    for _key in ("OPENAI_API_KEY", "OPENAI_MODEL", "TEACHER_PIN", "DATABASE_URL"):
        if _key not in os.environ and _key in st.secrets:
            os.environ[_key] = str(st.secrets[_key])
except (FileNotFoundError, KeyError):
    pass
from ai_service import generate_check,evaluate_answer,connection_status,model_name
from database import init_db,create_check,get_check,save_response,response_count
from demo_seed import DEMO_CODE
from ui import inject_css,top_progress,sidebar_nav,evidence_badge
st.set_page_config(page_title="MindCheck",page_icon="🧠",layout="wide")
inject_css()
try:
    init_db()
except Exception as exc:
    st.error("Database connection failed. Check DATABASE_URL in your deployment secrets.")
    st.stop()
TEACHER_PIN = os.environ.get("TEACHER_PIN", "").strip()

D={"page":"home","teacher_scope":{"topic":"","objectives":"","required_concepts":"","out_of_scope":"","strictness":"Balanced"},"teacher_source":"","draft_questions":{},"published_code":"","active_check":None,"student_label":"","confidence_before":4,"confidence_after":3,"answers":{"explain":"","apply":"","transfer":""},"evaluations":{},"followups":{},"followup_answers":{},"reflection":"","saved":False,"teacher_authorized":False}
for k,v in D.items():
    if k not in st.session_state:st.session_state[k]=v.copy() if isinstance(v,dict) else v
def go(p):st.session_state.page=p;st.rerun()
def step():return {"student_intro":1,"explain":2,"apply":3,"transfer":4,"review":5,"reflect":5}.get(st.session_state.page,0)
def shell(t,s):
    sidebar_nav(st.session_state.page);top_progress(step(),5);st.markdown(f'<h1 class="page-title">{t}</h1><p class="page-subtitle">{s}</p>',unsafe_allow_html=True)
def item(d):return st.session_state.active_check["questions"][d]
def require_teacher():
    if st.session_state.teacher_authorized:
        return True
    st.markdown('<div class="eyebrow">TEACHER ACCESS</div><h1 class="page-title">Teacher Sign In</h1>',unsafe_allow_html=True)
    if not TEACHER_PIN:
        st.warning("Teacher setup is disabled until TEACHER_PIN is configured in deployment secrets. Students can still use the ReLU demo.")
        if st.button("Back to Home"):
            go("home")
        return False
    entered = st.text_input("Teacher PIN", type="password")
    if st.button("Unlock Teacher Workspace", type="primary"):
        import hmac
        if hmac.compare_digest(entered, TEACHER_PIN):
            st.session_state.teacher_authorized = True
            st.rerun()
        else:
            st.error("Incorrect PIN")
    return False

def task(d,n,h):
    x=item(d);shell(d.capitalize(),h)
    st.markdown(f'<div class="scope-chip">Teacher objective: {escape(x.get("objective",""))}</div><div class="question-card"><div class="question-label">{d.upper()} TASK</div><div class="question-text">{escape(x["question"])}</div></div>',unsafe_allow_html=True)
    st.caption("Answer independently. Feedback is shown after all three tasks so the check does not interrupt your thinking.")
    a=st.text_area("Your response",value=st.session_state.answers[d],height=220,key=d+"_answer")
    if st.button("Submit & continue →",type="primary",use_container_width=True):
        if len(a.strip())<5:
            st.warning("Please write a little more.");return
        st.session_state.answers[d]=a.strip()
        e=evaluate_answer(st.session_state.active_check["scope"],d,x.get("objective",""),x["question"],a.strip())
        st.session_state.evaluations[d]=e
        go(n)

p=st.session_state.page
if p.startswith("teacher") and not require_teacher():
    st.stop()
if p=="home":
    sidebar_nav(p);st.markdown('<div class="eyebrow">MINDCHECK</div><h1 class="hero-title">One check,<br><span>two clear roles.</span></h1><p class="hero-copy">Teachers generate and approve the questions once. Students join with a code and answer the same stored questions.</p>',unsafe_allow_html=True)
    st.info("Classroom demo is ready. Join with Check Code **RELU-DEMO** to answer the three fixed ReLU questions.")
    a,b=st.columns(2)
    with a:
        st.markdown('<div class="entry-card"><b>STUDENT</b><h3>Join a Check</h3><p>Use the code shared by your teacher.</p></div>',unsafe_allow_html=True)
        if st.button("I'm a Student →",type="primary",use_container_width=True):go("student_join")
    with b:
        st.markdown('<div class="entry-card"><b>TEACHER</b><h3>Create a Check</h3><p>Define, preview, edit and publish.</p></div>',unsafe_allow_html=True)
        if st.button("I'm a Teacher →",use_container_width=True):go("teacher_setup")
elif p=="teacher_setup":
    sidebar_nav(p)
    st.markdown('<div class="eyebrow">TEACHER SETUP</div><h1 class="page-title">Define the learning boundary</h1><p class="page-subtitle">Tell MindCheck what students should understand. AI will generate one Explain, one Apply, and one Transfer task inside the boundary you define. You can review and edit all three before publishing.</p>',unsafe_allow_html=True)
    s=st.session_state.teacher_scope

    st.markdown('<div class="setup-section"><div class="setup-number">1</div><div><div class="setup-title">Topic</div><div class="setup-help">What concept or knowledge area is this check about?</div></div></div>',unsafe_allow_html=True)
    s["topic"]=st.text_input("Topic",s["topic"],placeholder="e.g. ReLU activation function",label_visibility="collapsed")
    st.caption("Example: ReLU activation function · Photosynthesis · Opportunity cost")

    st.markdown('<div class="setup-section"><div class="setup-number">2</div><div><div class="setup-title">Learning objectives</div><div class="setup-help">What should students be able to explain, apply, or transfer after learning this topic? Add one objective per line.</div></div></div>',unsafe_allow_html=True)
    s["objectives"]=st.text_area("Learning objectives",s["objectives"],height=145,placeholder="e.g.\nExplain why ReLU introduces non-linearity.\nApply ReLU to simple numerical inputs.\nReason about when ReLU may cause inactive neurons.",label_visibility="collapsed")
    st.caption("Tip: Use observable verbs such as explain, compare, apply, justify, interpret, or transfer.")

    st.markdown('<div class="setup-section"><div class="setup-number">3</div><div><div class="setup-title">Required concepts</div><div class="setup-help">Which ideas should a relevant answer engage with? These are conceptual anchors, not exact keywords students must repeat.</div></div></div>',unsafe_allow_html=True)
    s["required_concepts"]=st.text_area("Required concepts",s["required_concepts"],height=120,placeholder="e.g.\nnon-linearity\nmax(0, x)\nnegative inputs become zero",label_visibility="collapsed")
    st.caption("MindCheck uses these concepts to judge relevance and conceptual coverage, while still allowing students to answer in their own words.")

    st.markdown('<div class="setup-section"><div class="setup-number">4</div><div><div class="setup-title">Out-of-scope content</div><div class="setup-help">What should NOT be required for this check? Use this to stop the AI from testing beyond what you taught.</div></div></div>',unsafe_allow_html=True)
    s["out_of_scope"]=st.text_area("Out-of-scope content",s["out_of_scope"],height=115,placeholder="e.g.\nDetailed backpropagation derivations\nAdvanced activation functions not covered in class",label_visibility="collapsed")
    st.caption("Optional, but useful for keeping the assessment fair and aligned with your lesson.")

    st.markdown('<div class="setup-section"><div class="setup-number">5</div><div><div class="setup-title">Evaluation strictness</div><div class="setup-help">Choose how closely student responses should match the learning objectives and required concepts.</div></div></div>',unsafe_allow_html=True)
    s["strictness"]=st.select_slider("Evaluation strictness",["Flexible","Balanced","Strict"],value=s["strictness"],label_visibility="collapsed")
    strict_help={"Flexible":"Accepts broader valid explanations and alternative reasoning.","Balanced":"Looks for the key concepts while allowing reasonable variation in wording and examples.","Strict":"Requires closer alignment with the stated objectives and conceptual boundaries."}
    st.info("**"+s["strictness"]+":** "+strict_help[s["strictness"]])

    st.markdown('<div class="setup-section"><div class="setup-number">6</div><div><div class="setup-title">Reference material <span class="optional-tag">OPTIONAL</span></div><div class="setup-help">Paste a short teacher-approved definition, note, rubric, or lesson excerpt if you want AI generation and evaluation grounded in specific material.</div></div></div>',unsafe_allow_html=True)
    st.session_state.teacher_source=st.text_area("Optional reference material",st.session_state.teacher_source,height=150,placeholder="e.g. Paste the key definition, lesson notes, or assessment criteria here...",label_visibility="collapsed")

    st.markdown('<div class="teacher-note"><b>What happens next?</b><br>MindCheck generates exactly three draft tasks: Explain → Apply → Transfer. Nothing is published automatically. You will preview, edit, regenerate, or approve the questions before students can access them.</div>',unsafe_allow_html=True)
    if st.button("Generate 3 Draft Questions →",type="primary",use_container_width=True):
        if not s["topic"].strip() or not s["objectives"].strip():
            st.warning("Please add at least a topic and one learning objective before generating questions.")
        else:
            st.session_state.draft_questions=generate_check(s,st.session_state.teacher_source);go("teacher_preview")
elif p=="teacher_preview":
    sidebar_nav(p);st.markdown('<div class="eyebrow">TEACHER REVIEW</div><h1 class="page-title">Preview Before Publishing</h1><p class="page-subtitle">Review the three AI-generated tasks below. These exact questions will be stored and shown to every student using this Check Code.</p>',unsafe_allow_html=True)
    for d in ["explain","apply","transfer"]:
        x=st.session_state.draft_questions[d];st.subheader(d.capitalize())
        x["objective"]=st.text_input(d+" objective",x.get("objective",""),key="o"+d);x["question"]=st.text_area(d+" question",x["question"],key="q"+d);st.session_state.draft_questions[d]=x
    a,b,c=st.columns(3)
    with a:
        if st.button("← Edit Teacher Setup",use_container_width=True):go("teacher_setup")
    with b:
        if st.button("Regenerate",use_container_width=True):st.session_state.draft_questions=generate_check(st.session_state.teacher_scope,st.session_state.teacher_source);st.rerun()
    with c:
        if st.button("Approve & Publish →",type="primary",use_container_width=True):
            st.session_state.published_code=create_check(st.session_state.teacher_scope,st.session_state.teacher_source,st.session_state.draft_questions);go("teacher_published")
elif p=="teacher_published":
    sidebar_nav(p);st.markdown('<div class="eyebrow">PUBLISHED</div><h1 class="page-title">Your Check Is Ready</h1><p class="page-subtitle">Share this code with students. Everyone who joins with it receives the same teacher-approved Explain, Apply, and Transfer questions.</p>',unsafe_allow_html=True);st.markdown(f'<div class="code-card"><div class="question-label">CHECK CODE</div><div class="check-code">{st.session_state.published_code}</div></div>',unsafe_allow_html=True);st.markdown('<div class="teacher-note"><b>Saved to the database</b><br>The teacher-defined scope and approved questions are now stored in SQLite. Student responses will be linked to this Check Code.</div>',unsafe_allow_html=True)
    if st.button("Back to Home",use_container_width=True):go("home")
elif p=="student_join":
    sidebar_nav(p)
    st.markdown('<div class="eyebrow">STUDENT</div><h1 class="page-title">Join an Understanding Check</h1><p class="page-subtitle">Your teacher has already prepared and approved the questions. Enter the shared Check Code to begin.</p>',unsafe_allow_html=True)

    st.markdown('<div class="join-heading"><div class="join-icon">1</div><div><div class="join-title">Check Code</div><div class="join-help">Use the code provided by your teacher. It connects you to the correct topic and approved questions.</div></div></div>',unsafe_allow_html=True)
    default_code = st.query_params.get("code", DEMO_CODE)
    code=st.text_input("Check Code",value=default_code,placeholder="e.g. RELU-DEMO",label_visibility="collapsed").strip().upper()
    st.caption("The code is not case-sensitive. The fixed classroom demo uses RELU-DEMO.")

    st.markdown('<div class="join-heading"><div class="join-icon">2</div><div><div class="join-title">About You <span class="optional-tag">OPTIONAL</span></div><div class="join-help">Add a name or nickname if your teacher needs to identify your response.</div></div></div>',unsafe_allow_html=True)
    st.session_state.student_label=st.text_input("Name or nickname (optional)",value=st.session_state.student_label,placeholder="e.g. Alex",label_visibility="collapsed")
    st.caption("Leave this blank to submit as Anonymous.")

    st.markdown('<div class="student-note"><b>What happens after you join?</b><br>You will first rate your confidence, then complete the same teacher-approved Explain → Apply → Transfer tasks. MindCheck evaluates observable evidence in your responses; it does not make a final judgement about your mastery.</div>',unsafe_allow_html=True)
    back_col,load_col=st.columns([1,1])
    with back_col:
        if st.button("← Back to Home",use_container_width=True):go("home")
    with load_col:
        if st.button("Load Check →",type="primary",use_container_width=True):
            if not code:st.warning("Please enter the Check Code shared by your teacher.")
            else:
                c=get_check(code)
                if not c:st.error("Check code not found. Please check the code and try again.")
                else:
                    st.session_state.active_check=c;st.session_state.answers={"explain":"","apply":"","transfer":""};st.session_state.evaluations={};st.session_state.followups={};st.session_state.followup_answers={};st.session_state.saved=False;go("student_intro")
elif p=="student_intro":
    c=st.session_state.active_check
    shell("Before You Begin","This is a short independent check of what you can explain, apply, and transfer after AI-assisted learning.")
    st.markdown(f'<div class="scope-summary"><div class="question-label">YOUR CHECK</div><h3>{escape(c["topic"])}</h3><p>The questions were generated once, reviewed by your teacher, and stored before you joined. Other students using the same code receive the same three core tasks.</p></div>',unsafe_allow_html=True)
    api=connection_status(run_live_test=True)
    if api["state"]=="connected":
        st.success("AI evaluation connected · " + api["detail"])
    else:
        st.error(api["label"]+" · "+api["detail"]+" You may continue the questions, but MindCheck will not fabricate a grade.")
    st.markdown('<div class="join-title">How confident are you about this topic right now?</div><div class="join-help">Rate your confidence before seeing the questions. You will compare it again at the end.</div>',unsafe_allow_html=True)
    st.session_state.confidence_before=st.slider("Confidence before the check",1,5,st.session_state.confidence_before,label_visibility="collapsed")
    st.caption("1 — Not confident at all　　　　　　　　　　　　　　5 — Very confident")
    a,b=st.columns(2)
    with a:
        if st.button("← Change Check Code",use_container_width=True):go("student_join")
    with b:
        if st.button("Begin Check →",type="primary",use_container_width=True):go("explain")
elif p=="explain":task("explain","apply","Explain the key idea in your own words.")
elif p=="apply":task("apply","transfer","Use the concept in a related problem.")
elif p=="transfer":task("transfer","review","Use the concept in a less familiar context.")
elif p=="review":
    shell("Your Understanding Profile","Review the evidence after completing all three tasks. A retry is not required.")
    evals=st.session_state.evaluations
    errors=[e.get("error") for e in evals.values() if e.get("status") in ("error","unavailable") and e.get("error")]
    if errors:
        st.error("AI evaluation is unavailable, so MindCheck has not assigned evidence levels to one or more answers. " + errors[0])
    cols=st.columns(3)
    for col,d in zip(cols,["explain","apply","transfer"]):
        e=evals.get(d,{})
        with col:
            evidence_badge(d.capitalize(),e.get("level","Unavailable"),e.get("feedback","No evaluation available."))
    st.markdown('<div class="profile-divider"></div>',unsafe_allow_html=True)
    for d in ["explain","apply","transfer"]:
        e=evals.get(d,{})
        status=e.get("status")
        with st.container(border=True):
            st.subheader(d.capitalize())
            st.markdown("**Question assessed**")
            st.write(item(d)["question"])
            st.markdown("**Your response**")
            st.write(st.session_state.answers[d])
            if status == "ok":
                st.markdown("**Evidence level:** " + str(e.get("level", "—")))
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Scope alignment**")
                    st.write(e.get("scope_alignment", "—"))
                with c2:
                    st.markdown("**Concept accuracy**")
                    st.write(e.get("concept_accuracy", "—"))
                st.markdown("**Evidence**")
                st.write(e.get("evidence", "—"))
                st.markdown("**Possible gap**")
                st.write(e.get("gap", "—"))
            else:
                st.warning("Not evaluated: " + e.get("error", "AI evaluation unavailable."))
    if st.button("Next: Reflection →",type="primary"):go("reflect")
elif p=="reflect":
    shell("Reflect and Move Forward","Compare confidence and choose what to review.");st.metric("Confidence before",str(st.session_state.confidence_before)+"/5");st.session_state.confidence_after=st.slider("Confidence after",1,5,st.session_state.confidence_after);st.session_state.reflection=st.text_area("What will you do next?")
    if not st.session_state.saved and st.button("Finish & Save →",type="primary"):
        save_response(st.session_state.active_check["check_code"],st.session_state.student_label,st.session_state.confidence_before,st.session_state.answers,st.session_state.evaluations,st.session_state.confidence_after,st.session_state.reflection);st.session_state.saved=True;st.rerun()
    if st.session_state.saved:
        st.success("Check complete. Your response has been saved.")
        st.caption("This is a formative check, not a formal grade. For classroom use, avoid entering personal or sensitive information.")
