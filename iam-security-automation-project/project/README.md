## Deployment Instructions 

---

1. **Create resources**
   - Create S3 bucket (see infra/cloudtrail-setup.md).
   - Create SNS topic for alerts and subscribe your email.

2. **Create IAM role for Lambda**
   - In the AWS Console, create a new role for Lambda and attach an inline policy using `infra/lambda-role-policy.json` (replace ARNs).

3. **Package and deploy Lambda**
   - Zip the `lambda/` directory contents. Example:

   ```bash
   cd lambda
   zip -r ../iam_detector.zip iam_detector.py
   cd ..
   aws lambda create-function --function-name IAMSecurityDetector \
     --runtime python3.12 --role arn:aws:iam::123456789012:role/YourLambdaRole \
     --handler iam_detector.lambda_handler --zip-file fileb://iam_detector.zip --timeout 60 --memory-size 128
   ```

   - Set environment variables for the function (`S3_BUCKET`, `SNS_TOPIC_ARN`, etc.) via Console or CLI.

4. **Schedule the Lambda**
   - Create an EventBridge rule (schedule) and add the Lambda function as a target.

5. **Test**
   - Upload sample files from `samples/` to the S3 bucket (use the same folder structure CloudTrail uses or just drop files). The Lambda will process and publish alerts to SNS.

6. **Monitor**
   - Check CloudWatch Logs for Lambda function execution logs.
   - Confirm email alerts arrive.

---

## Safety & Notes

- **Do not auto-disable production credentials** without review: for this repo the default behavior is to notify. If you decide to enable automatic disabling, do so only in a sandbox account.
- **Replace resource ARNs** in the policy and scripts with your own values.
- Keep the scanning window and frequency conservative to avoid hitting free-tier limits.

---

## License

This repository is provided under the MIT License — see LICENSE file.
