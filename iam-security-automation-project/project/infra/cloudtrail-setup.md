# CloudTrail Setup Guide (CLI)

This guide creates an S3 bucket for CloudTrail and a CloudTrail trail that records management events (including IAM events). Update placeholders before running the commands.

---

## 1) Create an S3 bucket for CloudTrail logs

Replace `YOUR-S3-BUCKET-NAME` and `YOUR-REGION` (e.g., us-east-1).

```bash
# Create bucket (example for us-east-1; for other regions, include --create-bucket-configuration)
aws s3api create-bucket --bucket YOUR-S3-BUCKET-NAME --region YOUR-REGION

# Enable versioning (recommended)
aws s3api put-bucket-versioning \
  --bucket YOUR-S3-BUCKET-NAME \
  --versioning-configuration Status=Enabled

# (Optional) Enable default encryption (SSE-S3)
aws s3api put-bucket-encryption \
  --bucket YOUR-S3-BUCKET-NAME \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
```
# Notes

- If your region requires --create-bucket-configuration LocationConstraint=REGION, add that flag.

- For KMS encryption, create a KMS key and use "SSEAlgorithm":"aws:kms", "KMSMasterKeyID":"arn:aws:kms:..." in the encryption config.

## 2) Create and start the CloudTrail trail (management events)

This trail will capture management events (read/write) across regions. Replace YOUR-S3-BUCKET-NAME.
```
aws cloudtrail create-trail \
  --name IAMSecurityTrail \
  --s3-bucket-name YOUR-S3-BUCKET-NAME \
  --is-multi-region-trail

aws cloudtrail start-logging --name IAMSecurityTrail
```

Validation

Verify logs appear in S3 under AWSLogs/<ACCOUNT-ID>/CloudTrail/.

To check status:
```
aws cloudtrail get-trail-status --name IAMSecurityTrail
```
## 3) (Optional) Send CloudTrail to CloudWatch Logs

If you want CloudTrail management events also streamed to CloudWatch Logs (useful for near-real-time processing), you must create:

A CloudWatch Log Group

An IAM role allowing CloudTrail to deliver logs to CloudWatch

Example steps:

### 1) Create log group
```
aws logs create-log-group --log-group-name /aws/cloudtrail/IAMSecurityTrail
```
### 2) Create an IAM role for CloudTrail to put logs (trust policy)
```
cat > trust-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "cloudtrail.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role --role-name CloudTrail_CloudWatchLogs_Role --assume-role-policy-document file://trust-policy.json
```
### 3) Attach policy allowing PutLogEvents/DescribeLogStreams etc.
```
cat > cw-perm.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:PutLogEvents",
        "logs:CreateLogStream",
        "logs:CreateLogGroup",
        "logs:DescribeLogStreams"
      ],
      "Resource": "arn:aws:logs:YOUR-REGION:YOUR-ACCOUNT-ID:log-group:/aws/cloudtrail/IAMSecurityTrail:*"
    }
  ]
}
EOF

aws iam put-role-policy --role-name CloudTrail_CloudWatchLogs_Role --policy-name CloudTrailCloudWatchPolicy --policy-document file://cw-perm.json
```
### 4) Configure CloudTrail to use the role and CloudWatch Logs
```
aws cloudtrail update-trail \
  --name IAMSecurityTrail \
  --cloud-watch-logs-log-group-arn arn:aws:logs:YOUR-REGION:YOUR-ACCOUNT-ID:log-group:/aws/cloudtrail/IAMSecurityTrail \
  --cloud-watch-logs-role-arn arn:aws:iam::YOUR-ACCOUNT-ID:role/CloudTrail_CloudWatchLogs_Role
```

Notes & Warnings

If you enable CloudWatch Logs streaming, you will start consuming CloudWatch Logs ingestion/retention costs. For Free Tier-friendly testing, you can skip CloudWatch and keep logs in S3 only.

Always test in a sandbox account before using in production.

## 4) Test by uploading a sample event (optional)

You can test the pipeline by uploading synthetic or downloaded CloudTrail JSON (gzipped) into your bucket in the correct prefix. Example upload:
```
aws s3 cp ./samples/sample_failed_login.json s3://YOUR-S3-BUCKET-NAME/test/sample_failed_login.json
```

Note: CloudTrail usually writes gzipped files with an internal structure — for local testing the Lambda can also be run with the provided sample files (no gzip) if you used the local runner.

## 5) Cleanup reminders

If you created resources for testing (S3 bucket, log group, roles), remember to delete them when done to avoid charges.
