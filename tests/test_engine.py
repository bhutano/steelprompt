import subprocess, json, sys, os

PLUGIN_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ENGINE = os.path.join(PLUGIN_ROOT, "scripts", "engine.py")

def run_engine(prompt):
    inp = json.dumps({"prompt": prompt})
    result = subprocess.run(
        [sys.executable, ENGINE],
        input=inp, capture_output=True, text=True,
        env={**os.environ, "CLAUDE_PLUGIN_ROOT": PLUGIN_ROOT}
    )
    return result

RC_PATH = os.path.join(PLUGIN_ROOT, '.steelpromptrc')

def write_rc(mode):
    with open(RC_PATH, 'w', encoding='utf-8') as f:
        json.dump({'mode': mode}, f)

def remove_rc():
    if os.path.exists(RC_PATH):
        os.remove(RC_PATH)

def test_missing_rc_defaults_to_full():
    remove_rc()
    r = run_engine("improve the authentication code in the project")
    assert r.returncode == 0
    out = json.loads(r.stdout)
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert "TIER 3" in ctx  # only present in steelprompt-full.md

def test_malformed_rc_defaults_to_full():
    with open(RC_PATH, 'w', encoding='utf-8') as f:
        f.write("not json {{{")
    try:
        r = run_engine("improve the authentication code in the project")
        assert r.returncode == 0
        out = json.loads(r.stdout)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        assert "TIER 3" in ctx
    finally:
        remove_rc()

def test_mode_off_produces_no_output():
    write_rc('off')
    try:
        r = run_engine("improve the authentication code in the project")
        assert r.returncode == 0
        assert r.stdout.strip() == ""
    finally:
        remove_rc()

def test_slash_command_skipped():
    r = run_engine("/help")
    assert r.returncode == 0
    assert r.stdout.strip() == ""

def test_star_bypass_skipped():
    r = run_engine("* lista file")
    assert r.returncode == 0
    assert r.stdout.strip() == ""

def test_hash_bypass_skipped():
    r = run_engine("# something")
    assert r.returncode == 0
    assert r.stdout.strip() == ""

def test_short_prompt_skipped():
    r = run_engine("fix")
    assert r.returncode == 0
    assert r.stdout.strip() == ""

def test_vague_prompt_injects():
    r = run_engine("improve the authentication code in the project")
    assert r.returncode == 0
    out = json.loads(r.stdout)
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert "steelprompt" in ctx
    assert "AskUserQuestion" in ctx

def test_clear_prompt_injects():
    r = run_engine("change the submit button color to red in Button.svelte")
    assert r.returncode == 0
    out = json.loads(r.stdout)
    ctx = out["hookSpecificOutput"]["additionalContext"]
    assert "steelprompt" in ctx

def test_mode_ask_only_loads_ask_prompt():
    write_rc('ask-only')
    try:
        r = run_engine("improve the authentication code in the project")
        assert r.returncode == 0
        out = json.loads(r.stdout)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        assert "TIER 3" not in ctx
        assert "AskUserQuestion" in ctx
    finally:
        remove_rc()

def test_mode_full_loads_full_prompt():
    write_rc('full')
    try:
        r = run_engine("improve the authentication code in the project")
        assert r.returncode == 0
        out = json.loads(r.stdout)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        assert "TIER 3" in ctx
    finally:
        remove_rc()

def test_mode_preview_appends_flag():
    write_rc('preview')
    try:
        r = run_engine("improve the authentication code in the project")
        assert r.returncode == 0
        out = json.loads(r.stdout)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        assert "TIER 3" in ctx
        assert ctx.endswith('\nSTEELPROMPT_PREVIEW=true')
    finally:
        remove_rc()
