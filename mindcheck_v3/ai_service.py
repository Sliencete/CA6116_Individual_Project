import json, os, re
from openai import OpenAI

RUBRIC = """Explain: Strong = accurate own-words explanation with key relationships/reasons; Developing = main idea is present but reasoning is incomplete; Limited = major misconception, unclear core idea, or mostly unsupported.
Apply: Strong = correct application plus meaningful reasoning; Developing = partly correct or correct result with incomplete reasoning; Limited = inappropriate application or no meaningful reasoning.
Transfer: Strong = appropriate use in a meaningfully different/unfamiliar situation plus justification; Developing = sees a connection but adaptation/justification is weak; Limited = cannot connect the concept or reasoning is irrelevant/unsupported."""

def model_name():
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip() or "gpt-4.1-mini"

def _key():
    return os.getenv("OPENAI_API_KEY", "").strip()

def _client():
    k = _key()
    return OpenAI(api_key=k) if k else None

def _call(prompt):
    c = _client()
    if not c:
        raise RuntimeError("NO_API_KEY")
    return c.responses.create(model=model_name(), input=prompt).output_text

def _json(text):
    try:
        return json.loads(text.strip())
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            raise ValueError("The model did not return valid JSON.")
        return json.loads(m.group())

def _scope(s):
    return f"""Topic: {s.get('topic','')}
Objectives: {s.get('objectives','')}
Required concepts: {s.get('required_concepts','')}
Out of scope: {s.get('out_of_scope','')}
Strictness: {s.get('strictness','Balanced')}
Teacher-approved reference: {s.get('reference_material','(none)')}"""

def _safe_error(exc):
    msg = str(exc)
    low = msg.lower()
    if "no_api_key" in low:
        return "No API key was found. Add OPENAI_API_KEY to the .env file and restart Streamlit."
    if "incorrect api key" in low or "invalid_api_key" in low or "401" in low:
        return "The API key was rejected. Check that OPENAI_API_KEY in .env is valid, then restart Streamlit."
    if "insufficient_quota" in low or "quota" in low or "billing" in low or "429" in low:
        return "The API request could not run because the API account has no available quota/credits or hit a rate limit. Check API billing/usage."
    if "model" in low and ("not found" in low or "does not exist" in low or "access" in low):
        return f"The configured model ({model_name()}) is unavailable to this API account. Change OPENAI_MODEL in .env."
    return "The AI evaluation request failed. Check the terminal for the technical error and verify the API key, model, internet connection, and API billing."

def connection_status(run_live_test=False):
    if not _key():
        return {"state":"not_configured", "label":"AI not configured", "detail":"OPENAI_API_KEY was not found in .env."}
    if not run_live_test:
        return {"state":"configured", "label":"API key detected", "detail":f"Configured model: {model_name()}"}
    try:
        out = _call("Reply with exactly: OK")
        if out:
            return {"state":"connected", "label":"AI connected", "detail":f"Live API test succeeded with {model_name()}."}
    except Exception as exc:
        print("MindCheck API connection error:", repr(exc))
        return {"state":"error", "label":"AI connection failed", "detail":_safe_error(exc)}
    return {"state":"error", "label":"AI connection failed", "detail":"The API returned an empty response."}

def generate_check(s, source=""):
    topic=s["topic"]
    objs=[x.strip(" -•1234567890.") for x in s["objectives"].splitlines() if x.strip()]
    def o(i): return objs[min(i,len(objs)-1)] if objs else topic
    fallback={
        "explain":{"objective":o(0),"question":f"Explain the central idea of {topic} in your own words."},
        "apply":{"objective":o(1),"question":f"Apply {topic} to a new related example and explain your reasoning."},
        "transfer":{"objective":o(2),"question":f"Use {topic} in a less familiar context and justify whether it applies."}
    }
    if not _client(): return fallback
    p=f"""Create exactly three university post-AI understanding tasks using this teacher-defined boundary:
{_scope(s)}
Teacher reference: {source or '(none)'}
Generate Explain, Apply, Transfer. Each must assess a stated objective. Stay in scope; never test out-of-scope content. Required concepts are conceptual anchors, not exact keywords. Do not reveal answers. Transfer must be less familiar than Apply.
Return ONLY JSON: {{"explain":{{"objective":"...","question":"..."}},"apply":{{"objective":"...","question":"..."}},"transfer":{{"objective":"...","question":"..."}}}}"""
    try:
        return _json(_call(p))
    except Exception as exc:
        print("MindCheck question generation error:", repr(exc))
        return fallback

def evaluate_answer(s, dim, obj, q, a):
    if not _client():
        return {"status":"unavailable","scope_alignment":"Not evaluated","concept_accuracy":"Not evaluated","level":"Unavailable","evidence":"No semantic evaluation was performed.","feedback":"AI evaluation is not configured.","gap":"—","follow_up_needed":False,"error":"No API key was found."}
    p=f"""You are evaluating OBSERVABLE EVIDENCE in one student response. Do not infer hidden mastery and do not reward length, confidence, polished style, or keyword overlap.

Teacher-defined scope:
{_scope(s)}
Dimension: {dim}
Objective: {obj}
Question: {q}
Student response: {a}

Rubric:
{RUBRIC}

Decision procedure:
1. Judge whether the response actually answers THIS question: In Scope / Partially In Scope / Out of Scope.
2. Judge conceptual accuracy: Accurate / Partially Accurate / Inaccurate / Uncertain.
3. Judge evidence for THIS dimension only, against the ACTUAL question and its exact inputs. Never assume numbers or situations from another example. A correct definition is not enough for Apply or Transfer. A correct numerical result without reasoning is normally Developing for Apply.
4. Assign Strong / Developing / Limited. If the answer is In Scope, Accurate and sufficiently fulfills the actual dimension and objective, assign Strong even if additional detail could be added. Strong does not mean exhaustive or textbook-perfect. Downgrade only for a substantive missing element in this question or objective. Required concepts are semantic anchors, NOT exact required words. Equivalent wording must be accepted.
5. feedback must be a concise explanation of what the response demonstrated. If Strong, gap should normally be "No major gap identified." Otherwise gap should name a specific missing or incorrect element, or "No major gap identified." Do NOT tell the student to rewrite merely because the answer is short.
6. follow_up_needed is advisory only and should be true only when one targeted probe could resolve a specific ambiguity. MindCheck will NOT automatically force a retry.

Return ONLY JSON:
{{"scope_alignment":"In Scope|Partially In Scope|Out of Scope","concept_accuracy":"Accurate|Partially Accurate|Inaccurate|Uncertain","level":"Strong|Developing|Limited","evidence":"...","feedback":"...","gap":"...","follow_up_needed":true}}"""
    try:
        result=_json(_call(p))
        result["status"]="ok"
        return result
    except Exception as exc:
        print("MindCheck evaluation error:", repr(exc))
        return {"status":"error","scope_alignment":"Not evaluated","concept_accuracy":"Not evaluated","level":"Unavailable","evidence":"No valid AI evaluation was produced.","feedback":"AI evaluation failed; this response has not been graded.","gap":"—","follow_up_needed":False,"error":_safe_error(exc)}
