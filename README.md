# Log Notifier: Job Log Processor

## Description

The primary goal of this program is to track job start and end with stateful implementation. If the time processing the job is greater than give threshold of two levels, it will either logs as warning or error level.

## Usage

Run `python main.py logs.log`. It will output the warning and error logs.


## How It Works

1. Read the logs and parse the input before passing to the inner part of the program, the core.
2. The core is a hashmap for instant pid lookup and assign multiple fields. The `START` entry will trigger the storing of PID in the hashmap, the `END` entry will trigger the release of pid in the hashmap and log the outcome based on given conditions (Logs WARNING when over 5 minutes, ERROR when over 10 minutes. This is configurable in the code).

## Code Structure

```
simple_log_parser/
│
├── log_notifier/
│   └── core.py             # Core processing logic (BaseLogProcessor, StandardLogProcessor)
│
├── utils/
│   └── time.py             # Time conversion utility functions
│
├── tests/
│   ├── test_core.py        # Unit tests for core.py
│   └── test_utils.py       # Unit tests for time.py
│
├── main.py                 # Main application script (entry point)
└── README.md               # This file
```

## Setup Development

1. Create Python venv: `python -m venv venv`
2. Install `direnv`
3. Run `direnv allow` to enable virtual env using `.envrc` and `.local.env` if required
4. Verify if virtual env is correctly enabled: Run `pip -V`. Output should have path of the project: `/path/to/project/simple_log_parser/venv/lib/pythonxx/site-packages/pip`
5. Install pre commit: `pip install pre-commit`
6. Enable pre commit hook: `pre-commit install`. This will automatically run the unit test on test/test_*.py before commit.
