# Assistant

Simple voice assistant in Python that executes predefined commands.

## Features
- Greetings and responses  
- Current time  
- Repeat phrases  
- Open apps and websites (browser, YouTube, GitHub)  
- Timers  
- Random numbers


## Installation
```bash
git clone https://github.com/AlmazCode/assistant.git
cd assistant
pip install -r requirements.txt
```

## Run
```bash
python src/main.py
```

## Examples

* "Hello" → assistant greets you
* "What time is it?" → tells current time
* "Say I am the best" → repeats phrase
* "Open YouTube" → opens YouTube
* "Timer for 10 seconds" → starts timer
* "Random number from 1 to 100" → generates number

## How It Works

### 1. `lexicon.json` – Input Words

Maps user phrases → tokens.

```json
"HELLO": ["hello", "hi", "hey"],
"TIME": ["time", "what time", "current time"]
```

* User says: *"What time is it?"*
* Matched to token `"TIME"`

---

### 2. `commands.yaml` – Actions

Defines what to do when a token is detected.

```yaml
TIME:
  actions:
    - { func: tts, args: ["Current time is {time}"] }
```

* Token `"TIME"` → calls function `tts()` with `{time}` (All variables like `{time}` can be configured in CONTEXT in `src/core/data.py`).

With arguments:

```yaml
SAY:
  <ARG>:
    actions:
      - { func: tts, args: ["{0}"] }
```

* User: *"Say hello world"* → `tts("hello world")`

Nested example:

```yaml
OPEN:
  YOUTUBE:
    actions:
      - { func: open_url, args: ["{youtube}"] }
```

* User: *"Open YouTube"* → opens site.

---

### 3. `assistant_lexicon.json` – Replies

Contains ready-made answers.

```json
"GREETINGS": [
  "Hello, {user}!",
  "Nice to see you, {user}!"
]
```

And in `commands.yaml`:

```yaml
HELLO:
  actions:
    - { func: reply, args: ["GREETINGS"] }
```

* Assistant randomly picks a greeting.

---

### 4. `commands.py` – Functions

Implements all available actions, e.g.:

* `tts(text)` → speak text
* `open_url(url)` → open website
* `launch_app(path)` → run application
* `start_timer(time)` → set timer
* `random_number(a, b)` → generate number

---

## Adding New Commands

1. Add token and phrases to **`lexicon.json`**
2. Add behavior to **`commands.yaml`**
3. (Optional) Add replies to **`assistant_lexicon.json`**
4. Implement new function in **`src/modules/commands.py`**