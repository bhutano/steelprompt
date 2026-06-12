import sys, json, os

def get_mode(plugin_root):
    rc_path = os.path.join(plugin_root, '.steelpromptrc')
    try:
        with open(rc_path, encoding='utf-8') as f:
            return json.load(f).get('mode', 'full')
    except Exception:
        return 'full'

def main():
    try:
        hook_input = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    prompt = hook_input.get("prompt", "").strip()

    if prompt.startswith(("/", "*", "#")):
        sys.exit(0)

    if len(prompt.split()) < 5:
        sys.exit(0)

    plugin_root = os.environ.get(
        "CLAUDE_PLUGIN_ROOT",
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    mode = get_mode(plugin_root)

    if mode == 'off':
        sys.exit(0)

    prompt_filename = 'steelprompt-full.md' if mode in ('full', 'preview') else 'steelprompt-ask.md'
    prompt_file = os.path.join(plugin_root, 'prompts', prompt_filename)

    try:
        with open(prompt_file, encoding='utf-8') as f:
            instruction = f.read()
    except FileNotFoundError:
        sys.exit(0)

    if mode == 'preview':
        instruction += '\nSTEELPROMPT_PREVIEW=true'

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": instruction
        }
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
