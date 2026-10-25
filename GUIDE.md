# Run the experiment yourself, step by step

This guide assumes you have never set up a Python project or used an AI API. Each step says what to do, what you should see, and why.

Total time: about 20 minutes of setup, then the experiment runs on its own for 30 to 90 minutes.

---

## Part 1: One-time setup

### Step 1. Open a terminal in the project folder

A terminal is a window where you type commands.

- **Windows:** open File Explorer, go to the `agent-engineering-series\01-harness-engineering` folder, click the address bar, type `cmd` and press Enter. A black window opens, already inside that folder.
- **macOS:** open Terminal, type `cd ` (with a space), drag the `01-harness-engineering` folder into the window, press Enter.

Every command below is typed into this window, followed by Enter.

### Step 2. Check Python is installed

```bash
python --version
```

You should see `Python 3.10` or newer. If you see "not recognized", install Python from https://www.python.org/downloads/ and tick **"Add python.exe to PATH"** in the installer, then open a new terminal.

### Step 3. Create a virtual environment and install the two libraries

A virtual environment is a private folder of Python libraries for this project, so it can't break anything else on your computer.

```bash
python -m venv .venv
```

Then activate it (you must do this every time you open a new terminal):

- Windows: `.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`

Your prompt now starts with `(.venv)`. Install the libraries:

```bash
pip install -r requirements.txt
```

This installs `openai` (talks to the model API) and `pytest` (runs the tests that grade the agent).

### Step 4. Prove the code works, without spending anything

```bash
python selftest.py
python validate_tasks.py
```

`selftest.py` drives both harnesses with a fake, scripted model and checks each harness part behaves as designed. Expect `12/12 checks passed`.

`validate_tasks.py` checks all 20 tasks are fair: the starting code fails, and the reference fix passes. Expect `20/20 tasks valid`.

### Step 5. Get a free API key

An API key is a password that lets your code call a model. We use Google Gemini because its free tier needs no credit card.

1. Go to https://aistudio.google.com/apikey and sign in with a Google account.
2. Click **Create API key**. Copy the long string it shows.
3. Treat it like a password: never paste it into a chat, a screenshot, or a file that goes on GitHub.

### Step 6. Put the key in a `.env` file

`.env` is a settings file the code reads at startup. It is listed in `.gitignore`, so git will never upload it.

- Windows: `copy .env.example .env` then `notepad .env`
- macOS: `cp .env.example .env` then `open -e .env`

Replace `paste-your-key-here` with your key. Save and close.

### Step 7. Choose the model

```bash
python run.py --list-models
```

This prints every model your key can use. Pick a small, cheap one (its name usually contains `flash-lite` or `flash`), and put that exact name after `LLM_MODEL=` in `.env`.

Why a small model? The harness matters most when the model is not strong enough to rescue a weak setup, and that's where most production agents live, because small models are cheap. Free-tier limits are also higher for small models.

---

## Part 2: Run the experiment

### Step 8. A two-run smoke test

```bash
python run.py --tasks 01
```

This runs task 01 once through each harness. You'll see two lines like:

```
  fail  naive        01-slugify   r1  finished   steps=3   tokens=4,210
  PASS  engineered   01-slugify   r1  finished   steps=9   tokens=21,877
```

If you see an error about the API key or the model name, fix `.env` and run it again.

### Step 9. The main run: 20 tasks x 2 harnesses

```bash
python run.py
```

40 runs. On a free tier this takes roughly 30 to 60 minutes, because the code waits 4.5 seconds between calls to stay under the per-minute limit. Each result is saved the moment it finishes, so if anything stops it (a closed laptop, a quota message), just run the same command again and it continues where it left off.

### Step 10 (optional). Ablations: which part matters most?

```bash
python run.py --ablation
```

This adds 12 more harnesses: the naive one with a single part switched on, and the engineered one with a single part switched off. That's 240 more runs. Free tiers also have a daily request limit, so this may take two days; stop with Ctrl+C at any time and rerun the command tomorrow.

### Step 11. Build the report

```bash
python report.py
```

This writes `results/<model>/results.md` (tables) and `results/<model>/report.html` (charts). Double-click `report.html` to open it in your browser.

---

## Part 3: Material for the blog

- **Results chart:** screenshot the top of `report.html`.
- **Results table:** screenshot `results.md` in VS Code's Markdown preview, or rebuild it in Medium.
- **A failure, as evidence:** `results/<model>/traces/naive/` has a readable `.md` file for every run. Look for runs that ended `finished` but were not solved (the model said "done" and was wrong), `harness_crash`, or very high token counts (task 08, the big log).
- **Code snippets:** the clearest ones are `structured_system()`, `build_view()`, `verify()` and the `run_agent()` loop in `harness/agent.py`, and `designed_edit_file()` in `harness/tools.py`. For nice images, paste them into https://ray.so or https://carbon.now.sh.

---

## Part 4: Put it on GitHub

### Step 12. Create an empty repository

1. Sign in at https://github.com.
2. Click **+** (top right), then **New repository**.
3. Name it `agent-engineering-series`, set it to **Public**, and do **not** tick "Add a README" (we already have one).
4. Click **Create repository**. Keep that page open; it shows your repository URL.

### Step 13. Upload the code

In a terminal opened in the `agent-engineering-series` folder (one level up from `01-harness-engineering`):

```bash
git init
git add .
git status
```

Read the `git status` list. You should **not** see `.env` or `.venv` in it. If you do, stop and check that `.gitignore` is in this folder.

```bash
git commit -m "Harness engineering experiment: same model, two harnesses"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/agent-engineering-series.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. The first push opens a browser window asking you to sign in to GitHub; approve it. Refresh the GitHub page and your code is there.

When the later blogs in this series add folders (`02-...`, `03-...`), you only need:

```bash
git add .
git commit -m "Add part 2"
git push
```
