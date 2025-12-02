# Cloud-Security_lab


## CONTENTS
- Cloud_Security_Lab_File
- iam-security-automation project


## Top-level repository structure (new)
```

Cloud-Security_lab/
│       ├──iam-security-automation-project/
│       │   ├── project/                        # <- All project content lives here (matches Cloud-Security_lab style)
│       │   │   ├── README.md                   # Project-specific README (detailed instructions)
│       │   │   ├── lambda/
│       │   │   │   ├── iam_detector.py         # Main Lambda detection script
│       │   │   │   ├── requirements.txt        # Python deps (if any)
│       │   │   │   └── package.sh              # Optional helper to zip lambda
│       │   │   ├── infra/
│       │   │   │   ├── lambda-role-policy.json
│       │   │   │   ├── cloudtrail-setup.md
│       │   │   │   └── eventbridge-rule.json
│       │   │   ├── samples/
│       │   │   │   ├── sample_root_signin.json
│       │   │   │   └── sample_failed_login.json
│       │   │   └── .gitignore
├── README.md                       # Repo-level README (short overview & quick links)
└── LICENSE
```

---

## Quick links (within repository)
- `project/README.md` — Full project instructions, architecture, and deploy steps.
- `project/lambda/iam_detector.py` — Lambda detection script.
- `project/infra/lambda-role-policy.json` — IAM policy for Lambda execution role (replace ARNs before use).
- `project/infra/cloudtrail-setup.md` — CLI commands to create S3 & CloudTrail trail.
- `project/infra/eventbridge-rule.json` — EventBridge schedule rule snippet.
- `project/samples/sample_root_signin.json` — Synthetic CloudTrail event for testing root signin detection.
- `project/samples/sample_failed_login.json` — Synthetic CloudTrail event for testing failed logins.


---

## Made by
- Sankarshan Kshtriya
- B.Tech CSE (Cyber Security) [Vth Sem]
- 2301410027
