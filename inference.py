import os
import requests
from typing import Optional
from openai import OpenAI

# ---------------- CONFIG ----------------
ENV_BASE_URL = "http://localhost:8000"   # ✅ FIXED
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
HF_TOKEN     = os.getenv("HF_TOKEN") or os.getenv("API_KEY", "")
MODEL_NAME   = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
BENCHMARK    = "orion-trading-env"

SUCCESS_THRESHOLD = 0.50
REQUEST_TIMEOUT   = 30

TASKS = [
    {"id": "easy", "max_steps": 50},
    {"id": "medium", "max_steps": 100},
    {"id": "hard", "max_steps": 150},
]

# ---------------- LLM ----------------
_llm_client: Optional[OpenAI] = None
if HF_TOKEN:
    try:
        _llm_client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    except:
        _llm_client = None

# ---------------- HELPERS ----------------
def _clamp(value: float) -> float:
    return max(0.01, min(0.99, float(value)))

def log_start(task):
    print(f"[START] task={task} env={BENCHMARK} model={MODEL_NAME}", flush=True)

def log_step(step, action, reward, done, error):
    err = error if error else "null"
    print(
        f"[STEP] step={step} action={action} "
        f"reward={_clamp(reward):.2f} done={str(done).lower()} error={err}",
        flush=True,
    )

def log_end(success, steps, score, rewards):
    rewards_str = ",".join(f"{_clamp(r):.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={_clamp(score):.2f} rewards={rewards_str}",
        flush=True,
    )

# ---------------- RULE AGENT ----------------
def _rule_based_action(obs):
    text = obs.upper()

    regime = "SIDEWAYS"
    for r in ("BULL", "BEAR", "VOLATILE", "SIDEWAYS"):
        if r in text:
            regime = r
            break

    holdings = 0
    steps_remaining = 999

    try:
        for line in obs.split("\n"):
            if "Holdings:" in line:
                holdings = int(line.split(":")[1].strip().split()[0])
            if "Steps Remaining:" in line:
                steps_remaining = int(line.split(":")[1].strip())
    except:
        pass

    if steps_remaining < 10 and holdings > 0:
        return "SELL"

    if regime == "BULL":
        return "BUY"
    elif regime == "BEAR":
        return "SELL" if holdings > 0 else "HOLD"
    else:
        return "HOLD"

def get_action(obs):
    if _llm_client is None:
        return _rule_based_action(obs)

    try:
        res = _llm_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": obs}],
            temperature=0.0,
            max_tokens=10,
        )
        raw = res.choices[0].message.content.upper()

        for w in ("BUY", "SELL", "HOLD"):
            if w in raw:
                return w

        return _rule_based_action(obs)
    except:
        return _rule_based_action(obs)

# ---------------- HTTP ----------------
def _post(path, payload):
    try:
        r = requests.post(f"{ENV_BASE_URL}{path}", json=payload, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except:
        return None

def _get(path):
    try:
        r = requests.get(f"{ENV_BASE_URL}{path}", timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except:
        return None

# ---------------- RUN ----------------
def run_task(task_id, max_steps):
    log_start(task_id)

    rewards = []
    steps_taken = 0

    reset = _post("/reset", {"task": task_id})
    if reset is None:
        log_end(False, 0, 0.01, [])
        return {"score": 0.01}

    obs = reset.get("observation", "")

    for step in range(1, max_steps + 1):
        action = get_action(obs)
        data = _post("/step", {"action": action})

        if data is None:
            reward = 0.01
            done = True
            error = "env_call_failed"
        else:
            reward = _clamp(data.get("reward", 0.01))
            done = data.get("done", False)
            obs = data.get("observation", obs)
            error = None

         rewards.append(reward)
        steps_taken = step

        log_step(step, action, reward, done, error)

        if done:
            break

    grader = _get("/grader")
    if grader and "score" in grader:
        score = _clamp(grader["score"])
    else:
        score = _clamp(sum(rewards) / len(rewards)) if rewards else 0.01

    success = score >= SUCCESS_THRESHOLD

    log_end(success, steps_taken, score, rewards)

    return {"score": score}

# ---------------- MAIN ----------------
def main():
    scores = {}

    for t in TASKS:
        result = run_task(t["id"], t["max_steps"])
        scores[t["id"]] = result["score"]

    easy = scores.get("easy", 0.01)
    medium = scores.get("medium", 0.01)
    hard = scores.get("hard", 0.01)

    overall = _clamp((easy + medium + hard) / 3)

    print(
        f"[SUMMARY] easy={easy:.2f} medium={medium:.2f} "
        f"hard={hard:.2f} overall={overall:.2f}",
        flush=True,
    )

if name == "main":
    main()   