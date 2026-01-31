# Cloud Snitcher


This project implements a lightweight IAM security monitoring and alerting system using AWS free-tier services. It analyzes CloudTrail management logs stored in Amazon S3 to detect risky identity-related activities such as root console sign-ins, multiple failed login attempts, and outdated IAM access keys.

A scheduled AWS Lambda function processes recent CloudTrail logs, identifies suspicious behavior, and sends real-time alerts via Amazon SNS. The solution demonstrates how security automation and identity monitoring can be achieved without paid services like GuardDuty, making it ideal for learning, labs, and portfolio use.

---

## Top-level repository structure 
```

Cloud-Snitcher/
├── iam-security-automation-project/
│   ├── screenshots/                    # All AWS screenshots of this project
│   └── project/                        # <- All project content lives here (matches Cloud-Security_lab style)
│       ├── README.md                   # Project-specific README (detailed instructions)
│       ├── lambda/
│       │   ├── iam_detector.py         # Main Lambda detection script
│       │   ├── requirements.txt        # Python deps (if any)
│       │   └── package.sh              # Optional helper to zip lambda
│       ├── infra/
│       │   ├── lambda-role-policy.json
│       │   ├── cloudtrail-setup.md
│       │   └── eventbridge-rule.json
│       └── samples/
│           ├── sample_root_signin.json
│           └── sample_failed_login.json
│       
├── README.md                       # Repo-level README (short overview & quick links)
└── LICENSE
```

---

## Quick links (within repository)
- `iam-security-automation-project/project/README.md` — Full project instructions, architecture, and deploy steps.
- `iam-security-automation-project/project/lambda/iam_detector.py` — Lambda detection script.
- `iam-security-automation-project/project/infra/lambda-role-policy.json` — IAM policy for Lambda execution role (replace ARNs before use).
- `iam-security-automation-project/project/infra/cloudtrail-setup.md` — CLI commands to create S3 & CloudTrail trail.
- `iam-security-automation-project/project/infra/eventbridge-rule.json` — EventBridge schedule rule snippet.
- `iam-security-automation-project/project/samples/sample_root_signin.json` — Synthetic CloudTrail event for testing root signin detection.
- `iam-security-automation-project/project/samples/sample_failed_login.json` — Synthetic CloudTrail event for testing failed logins.
- `iam-security-automation-project/screenshots` - All AWS screenshots that I tested in.



