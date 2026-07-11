# Healthcare Voice QA Bot

This project is an automated voice bot that calls the Pretty Good AI assessment line and acts as a realistic patient. The bot is designed to test the healthcare AI agent through scheduling, cancellation, privacy, triage, location, and edge-case scenarios. It places real outbound calls using SignalWire, generates patient replies with an LLM, saves transcripts, and supports review of call recordings and bug reports.


## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file based on `.env.example`.

## Environment Variables

## API Keys and Environment Variables

This project requires OpenAI and SignalWire credentials. Real API keys should be stored in a local `.env` file and should not be committed to GitHub.

Required environment variables:

| Variable                 | Description                                                              |
| ------------------------ | ------------------------------------------------------------------------ |
| `OPENAI_API_KEY`         | OpenAI API key used to generate LLM-powered patient replies              |
| `OPENAI_MODEL`           | OpenAI model used for patient reply generation                           |
| `SIGNALWIRE_PROJECT_ID`  | SignalWire project ID used for outbound calls                            |
| `SIGNALWIRE_API_TOKEN`   | SignalWire API token used for authentication                             |
| `SIGNALWIRE_SPACE_URL`   | SignalWire space URL used to call the SignalWire API                     |
| `SIGNALWIRE_FROM_NUMBER` | SignalWire phone number used as the caller ID                            |
| `PUBLIC_BASE_URL`        | Public HTTPS URL for the FastAPI webhook, usually from Cloudflare Tunnel |
| `DRY_RUN`                | When `true`, prevents the script from placing a real SignalWire call     |
| `LLM_PATIENT_ENABLED`    | When `true`, enables real LLM-powered patient replies                    |
| `SCENARIO_NUMBER`        | Selects which patient scenario to run (refer to chart below)                                   |

Use `.env.example` as the template for required variables. Create a private `.env` file locally with real values. The `.env` file should be included in `.gitignore` and should never be committed.


Example below:
```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.4-mini

SIGNALWIRE_PROJECT_ID=
SIGNALWIRE_API_TOKEN=
SIGNALWIRE_SPACE_URL=
SIGNALWIRE_FROM_NUMBER=

PUBLIC_BASE_URL=
DRY_RUN=true
LLM_PATIENT_ENABLED=false
SCENARIO_NUMBER=1
```

## Run the FastAPI App

```powershell
uvicorn app.main:app --reload
```

If using a local tunnel, start the tunnel and set `PUBLIC_BASE_URL` to the public HTTPS URL.
We used cloudflared. Use provided URL for PUBLIC_BASE_URL

```powershell
cloudflared tunnel --url http://localhost:8000
```
Make sure .env is loaded. Check with 
```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(repr(os.getenv('PUBLIC_BASE_URL')))"
```


## To Run Tests
LLM specific tests should fail
```powershell
$env:PYTHONPATH=(Get-Location).Path
$env:LLM_PATIENT_ENABLED="false"  
pytest
```

## Run a Dry Call

Dry runs do not place a real phone call.

```powershell
$env:DRY_RUN="true"
$env:SCENARIO_NUMBER="1"
python scripts/make_signalwire_test_call.py
```

## Run a Real Call

Real calls should only be made to the approved assessment number.
SCENARIO_NUMBER can be any between 1 and 11 inclusive. More than one lines acts as a safeguard to incur unwarranted costs.

```powershell
$env:LLM_PATIENT_ENABLED="true"
$env:DRY_RUN="false"
$env:SCENARIO_NUMBER="1"
python scripts/make_signalwire_test_call.py
```

Warning: this places a real SignalWire call and may incur telephony and LLM usage costs.

## Scenario List

The project includes multiple patient scenarios designed to test different agent behaviors:

| Number | Scenario ID                       | Purpose                                           |
| -----: | --------------------------------- | ------------------------------------------------- |
|      1 | `01_simple_scheduling`            | Basic appointment scheduling                      |
|      2 | `02_appointment_cancellation`     | Appointment cancellation                          |
|      3 | `03_start_and_cancel_appointment` | Starts scheduling, then switches to cancellation  |
|      4 | `04_hipaa_status_privacy`         | Third-party privacy / HIPAA-style disclosure test |
|      5 | `05_lost`                         | Location and clinic navigation question           |
|      6 | `06_consecutive_appointment`      | Consecutive appointment handling                  |
|      7 | `07_profile_check`                | Patient profile and identity handling             |
|      8 | `08_double_appointment`           | Back-to-back appointment policy test              |
|      9 | `09_blurry_vision_triage`         | Symptom triage for blurry vision after head bump  |
|     10 | `10_stroke_triage`                | Emergency triage for possible stroke symptoms     |
|     11 | `11_pre_op_food`                  | Pre-op food and drink instruction safety          |

## Outputs

Generated outputs are saved under:

```text
outputs/
  transcripts/
```

Transcripts are saved automatically by the app. Some recordings were manually reorganized

## Bug Reports

Logged In outsputs\Final_Scenarios folder


## Safety Notes

The outbound call helper checks that calls are only placed to the approved assessment number. The default script mode is `DRY_RUN=true`, which prevents accidental real calls. API keys and credentials should be stored in `.env` and should not be committed to GitHub.
