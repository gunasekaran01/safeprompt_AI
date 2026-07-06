# User Guide

A walkthrough of SafePrompt AI from a new user's perspective.

## 1. Creating an account

1. Go to the SafePrompt AI homepage and click **Sign up**.
2. Enter your name, email, and a password (minimum 8 characters).
3. You'll see a confirmation that a verification link was sent to your
   email. **You must click that link before you can log in** — this is
   enforced by Supabase Auth, not something SafePrompt AI can skip.
4. Click the link in your email — it opens the app briefly ("Verifying…")
   and then sends you to log in.
5. Go to **Log in**, enter your email and password.

## 2. Logging in and staying logged in

Once logged in, your session persists across browser restarts and tabs
— you won't need to log in again unless you explicitly log out or your
session is revoked. If you close the tab mid-session and come back
later, SafePrompt AI silently refreshes your session in the background.

**Forgot your password?** Click **Forgot password?** on the login page,
enter your email, and follow the reset link it sends you. For your
security, you'll see the same "check your email" message whether or not
an account exists for that address.

## 3. Analyzing a prompt

1. Go to **Analyzer** (requires being logged in).
2. Paste or type the prompt you want to check (up to 5,000 characters).
3. Click **Analyze**. You'll get back:
   - A **safety score** (0–100, higher is safer) shown as a circular gauge.
   - A **risk level**: Safe, Low Risk, Medium Risk, High Risk, or Critical.
   - Whether **prompt injection** or **jailbreak** patterns were detected, with a confidence percentage.
   - A **toxicity breakdown** by category (toxicity, insults, threats, etc.), when the toxicity model — not the lightweight keyword fallback — is running.
   - A **recommendation** and a short list of **reasoning** for the score.
4. Every analysis you run is automatically saved to your private history — no separate "save" step.

## 4. Dashboard

Your **Dashboard** shows, across everything you've ever analyzed:

- Total analyses, safe vs. unsafe counts, injection attempts, toxic prompts, and your average safety score.
- A **score trend** chart over the trailing 14 days (adjustable).
- A **risk level distribution** chart.
- A **detection breakdown** chart (injection only / toxicity only / both / neither).
- A table of your most recent activity.

If you're brand new and haven't analyzed anything yet, you'll see an
empty state rather than blank/broken charts — analyze a few prompts to
populate it.

## 5. History

**History** lists every prompt you've ever analyzed, newest first.

- **Search** by text — matches anywhere in the prompt.
- **Filter** by risk level, or narrow to injection-only / toxicity-only results.
- **Paginate** through results 20 at a time.
- **Delete** any entry you no longer want — this is permanent and cannot be undone.

You will only ever see your own analyses here — this is enforced on the
backend, not just hidden in the UI.

## 6. PDF Reports

From an analysis (in the Analyzer or from History), you can generate a
downloadable **PDF safety report** containing the prompt, the injection
and toxicity results, the safety score, a chart, the timestamp, and the
recommendation — useful for sharing a result with someone who doesn't
have a SafePrompt AI account, or for your own records.

## 7. Settings

Go to **Settings** to manage:

- **Account** — view and edit your display name and avatar.
- **Change Password** — set a new password without needing to log out first.
- **Appearance** — Light, Dark, or System theme (follows your OS setting automatically in System mode). This preference is currently saved to this browser only, not synced across devices.
- **Preferences** — Compact Mode (denser layouts) and Auto-Analyze on Paste, also saved to this browser only.
- **Danger Zone: Delete Account** — permanently deletes your account and every analysis, report, and setting you own. You must type `DELETE` to enable the button. **This cannot be undone** — there is no recovery.

## 8. Logging out

Click **Log out** in the navigation bar at any time. This ends your
session on this device; it doesn't affect any other device you're
logged in on.

## Troubleshooting

| Problem | Likely cause / fix |
|---|---|
| "Invalid or expired session. Please log in again." | Your session token expired or was revoked. Log in again. |
| Login fails right after signing up | You haven't clicked the verification link in your email yet. |
| Password reset link says "invalid or has expired" | Reset links are single-use and time-limited. Request a new one from **Forgot password?**. |
| "Could not reach the SafePrompt AI backend" | The API server isn't reachable — if you're running this locally, confirm the backend is running on port 8000. |
| Dashboard/History looks empty right after logging in | Expected for a new account — analyze a few prompts first. |
