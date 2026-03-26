"""
Sample Knowledge Base Generator — Creates realistic sample knowledge base
documents for a SaaS product (CloudSync Pro) covering FAQs, billing,
troubleshooting, returns/refunds, and account management.
"""

import os
from pathlib import Path

KB_DIR = Path("data/knowledge_base")

PRODUCT_FAQS = """# CloudSync Pro — Frequently Asked Questions

## What is CloudSync Pro?
CloudSync Pro is an enterprise-grade cloud collaboration and file synchronization platform. It allows teams to securely store, share, and collaborate on documents in real-time across all devices.

## What platforms does CloudSync Pro support?
CloudSync Pro is available on Windows 10+, macOS 12+, Linux (Ubuntu 20.04+, Fedora 36+), iOS 15+, Android 12+, and all modern web browsers. We also offer a CLI tool for advanced users and CI/CD integrations.

## How much storage do I get?
- Starter Plan: 100 GB per user
- Professional Plan: 1 TB per user
- Enterprise Plan: Unlimited storage
All plans include automatic file versioning with 180-day history.

## Is my data encrypted?
Yes. CloudSync Pro uses AES-256 encryption at rest and TLS 1.3 for data in transit. Enterprise plans also support customer-managed encryption keys (CMEK) and HIPAA-compliant storage.

## Can I share files with external users?
Yes. You can share files and folders with external users via secure links. You can set permissions (view-only, comment, edit), expiration dates, and password protection on shared links.

## Does CloudSync Pro integrate with other tools?
Yes. We integrate with Slack, Microsoft Teams, Google Workspace, Jira, Confluence, Salesforce, Zapier, and 200+ other tools via our API and pre-built connectors.

## What is the maximum file size?
Individual files can be up to 50 GB. Our chunked upload technology ensures reliable uploads even on slower connections.

## How does real-time collaboration work?
Multiple users can edit documents simultaneously. Changes are synced in real-time with conflict resolution. We support collaborative editing for documents, spreadsheets, and presentations.

## Is there an offline mode?
Yes. You can mark files and folders for offline access. Changes made offline are automatically synced when you reconnect.

## How do I get support?
- Starter Plan: Email support, 48-hour response time
- Professional Plan: Email + chat support, 12-hour response time
- Enterprise Plan: 24/7 phone support, dedicated account manager, 1-hour SLA for critical issues
"""

BILLING_PRICING = """# CloudSync Pro — Billing & Pricing Policies

## Pricing Plans

### Starter Plan — $12/user/month (billed annually) or $15/user/month (billed monthly)
- 100 GB storage per user
- Basic collaboration features
- Email support (48-hour response)
- 5 user minimum

### Professional Plan — $25/user/month (billed annually) or $30/user/month (billed monthly)
- 1 TB storage per user
- Advanced collaboration + admin controls
- Email + chat support (12-hour response)
- SSO integration
- No user minimum

### Enterprise Plan — Custom pricing
- Unlimited storage
- Advanced security (CMEK, HIPAA, SOC2)
- 24/7 phone support + dedicated account manager
- Custom integrations
- On-premise deployment option
- Contact sales for pricing

## Free Trial
All plans include a 14-day free trial with full feature access. No credit card required to start. You can upgrade, downgrade, or cancel at any time during the trial.

## Billing Cycle
- Annual billing is charged upfront for the full year
- Monthly billing is charged on the same date each month
- Adding users mid-cycle is prorated for the remaining period
- Invoices are available in the admin dashboard under Billing > Invoices

## Payment Methods
We accept Visa, Mastercard, American Express, wire transfer (Enterprise only), and ACH direct debit. Payment information is securely stored via Stripe.

## Upgrading or Downgrading
- Upgrades take effect immediately; charges are prorated
- Downgrades take effect at the next billing cycle
- When downgrading, ensure your usage is within the new plan's limits

## Late Payments
- A 7-day grace period is provided after a failed payment
- After 7 days, the account enters read-only mode (no uploads or edits)
- After 30 days of non-payment, the account is suspended
- Data is retained for 90 days after suspension before deletion

## Taxes
Prices are exclusive of applicable taxes. Sales tax, VAT, or GST will be added based on your billing address.

## Discounts
- Annual billing: ~20% discount over monthly billing
- Nonprofit organizations: 30% discount (verification required)
- Educational institutions: 40% discount
- Startups (YC, Techstars alumni): 25% discount for the first year
"""

TROUBLESHOOTING = """# CloudSync Pro — Troubleshooting Guide

## Sync Issues

### Files not syncing
1. Check your internet connection
2. Ensure the CloudSync Pro desktop app is running (look for the icon in system tray)
3. Right-click the tray icon → "Check for sync issues"
4. Verify you have sufficient storage quota (Settings → Storage)
5. Try pausing and resuming sync
6. If the issue persists, go to Settings → Advanced → "Reset sync database" (this does not delete files)

### Sync conflicts
When the same file is edited on multiple devices simultaneously, CloudSync Pro creates a conflict copy. To resolve:
1. Open the file location in CloudSync Pro
2. You'll see the original file and a conflict copy (named with timestamp)
3. Compare both versions and merge changes manually
4. Delete the conflict copy once resolved
5. To prevent future conflicts, use real-time collaboration mode for shared documents

### Slow sync speeds
1. Check if bandwidth throttling is enabled: Settings → Network → Bandwidth
2. Temporarily disable other cloud sync services
3. Large initial syncs may take time — check progress in the Activity tab
4. If behind a corporate firewall/proxy, contact your IT admin to whitelist *.cloudsyncpro.com
5. Try switching between the "Efficient" and "Fast" sync modes in Settings

## Login Issues

### Cannot log in
1. Verify your email address is correct
2. Try resetting your password at https://app.cloudsyncpro.com/reset-password
3. Check if your account is locked (after 5 failed attempts, wait 15 minutes)
4. If you use SSO, contact your IT administrator
5. Clear browser cache and cookies if using the web app
6. Contact support if the issue persists

### Two-factor authentication issues
1. If you've lost your 2FA device, use one of your backup codes
2. Backup codes were provided when you enabled 2FA
3. If you have no backup codes, contact support with identity verification

## Desktop App Issues

### App crashes on startup
1. Update to the latest version of CloudSync Pro
2. Try running the app as administrator (Windows) or from terminal (macOS)
3. Check the log file: Windows: %APPDATA%/CloudSyncPro/logs/, macOS: ~/Library/Logs/CloudSyncPro/
4. Uninstall and reinstall the app
5. If the issue persists, send the log file to support@cloudsyncpro.com

### High CPU/memory usage
1. Check how many files are being synced (Activity tab)
2. Exclude large folders from sync if they don't need real-time syncing
3. Adjust sync frequency: Settings → Advanced → Sync Interval
4. Update to the latest version (performance improvements are released regularly)

## Mobile App Issues

### App not connecting
1. Ensure you have a stable internet connection (try switching between Wi-Fi and cellular)
2. Force-close and reopen the app
3. Check the CloudSync Pro status page at status.cloudsyncpro.com
4. Update to the latest version from the App Store / Google Play
"""

RETURNS_REFUNDS = """# CloudSync Pro — Return & Refund Policy

## 30-Day Money-Back Guarantee
All paid plans come with a 30-day money-back guarantee from the date of first payment. If you're not satisfied, request a full refund within 30 days — no questions asked.

## How to Request a Refund
1. Go to Settings → Billing → Request Refund
2. Or email billing@cloudsyncpro.com with your account email and reason
3. Or contact support via live chat
4. Refunds are processed within 5-7 business days
5. Refunds are issued to the original payment method

## Refund Eligibility After 30 Days
- Monthly plans: No refund for the current billing period; cancel to prevent future charges
- Annual plans: Prorated refund for remaining unused months (minus a 10% early termination fee)
- Enterprise plans: Refer to your enterprise agreement terms

## Cancellation Policy
- You can cancel at any time from Settings → Billing → Cancel Subscription
- After cancellation, your account remains active until the end of the current billing period
- Your data remains accessible in read-only mode for 30 days after the billing period ends
- Export your data before cancellation: Settings → Data → Export All Data
- After the 30-day grace period, data is permanently deleted

## Plan Downgrade vs. Cancellation
If cost is a concern, consider downgrading to a lower plan instead of canceling:
1. Go to Settings → Billing → Change Plan
2. Select a lower-tier plan
3. The downgrade takes effect at the next billing cycle
4. Ensure your storage usage fits within the new plan's limit

## Disputes
If you believe you were charged incorrectly:
1. Check your invoice history: Settings → Billing → Invoices
2. Contact billing@cloudsyncpro.com with the invoice number
3. We respond to billing disputes within 24 hours
4. Unauthorized charges are fully refunded upon verification
"""

ACCOUNT_MANAGEMENT = """# CloudSync Pro — Account Management Procedures

## Creating an Account
1. Visit https://app.cloudsyncpro.com/signup
2. Enter your work email address
3. Choose a password (minimum 12 characters with uppercase, lowercase, number, and symbol)
4. Verify your email address
5. Select a plan or start your 14-day free trial

## Resetting Your Password
1. Go to https://app.cloudsyncpro.com/reset-password
2. Enter your registered email address
3. Check your email for the reset link (valid for 1 hour)
4. Set a new password meeting the security requirements
5. All active sessions will be logged out after a password reset

## Enabling Two-Factor Authentication (2FA)
1. Go to Settings → Security → Two-Factor Authentication
2. Click "Enable 2FA"
3. Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)
4. Enter the 6-digit code to verify
5. Save your backup codes in a secure location
6. 2FA is required for all Enterprise plan users

## Managing Team Members (Admin Only)
1. Go to Admin Dashboard → Users
2. Click "Invite Users" and enter email addresses
3. Assign roles: Admin, Editor, Viewer
4. Set department/group assignments
5. Users receive an invitation email and must accept within 7 days
6. To remove a user: click the user → "Remove from organization"
7. Removed users' files are transferred to the admin by default

## Updating Account Information
1. Go to Settings → Profile
2. You can update: display name, profile photo, phone number, timezone
3. To change your email address: Settings → Account → Change Email (requires re-verification)
4. To change your organization name: Admin Dashboard → Organization Settings

## Data Export
1. Go to Settings → Data → Export
2. Choose export format: ZIP (files), JSON (metadata), or full backup
3. Large exports are processed in the background; you'll receive an email when ready
4. Export links are valid for 7 days

## Deleting Your Account
1. Export your data first (see above)
2. Go to Settings → Account → Delete Account
3. Enter your password to confirm
4. Account deletion is irreversible
5. Your data is purged within 30 days per our data retention policy
6. If you're an admin, transfer ownership before deleting your account
"""

DOCUMENTS = {
    "faq_product.txt": PRODUCT_FAQS,
    "billing_pricing.txt": BILLING_PRICING,
    "troubleshooting_guide.txt": TROUBLESHOOTING,
    "returns_refunds.txt": RETURNS_REFUNDS,
    "account_management.txt": ACCOUNT_MANAGEMENT,
}


def generate_knowledge_base(output_dir: Path = KB_DIR):
    """Write all sample knowledge base documents to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in DOCUMENTS.items():
        filepath = output_dir / filename
        filepath.write_text(content.strip(), encoding="utf-8")
        print(f"Created: {filepath}")

    print(f"\nGenerated {len(DOCUMENTS)} knowledge base files in {output_dir}/")


if __name__ == "__main__":
    generate_knowledge_base()
