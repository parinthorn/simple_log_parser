# Log Notifier: Job Log Processor

## Description

The primary goal of this program is for process job's logs that have start time and stop time for notify that the time usage may greater than two layers


## How It Works

1. Read the logs and parse the input before passing to the inner part of the program, the core.
2. The core is a hashmap for instant pid lookup and assign multiple fields. The `START` entry will trigger the storing of PID in the hashmap, the `END` entry will trigger the release of pid in the hashmap and log the outcome based on given conditions (Logs WARNING when over 5 minutes, ERROR when over 10 minutes. This is configurable in the code).

## Code Structure

```
log-notifier/
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

