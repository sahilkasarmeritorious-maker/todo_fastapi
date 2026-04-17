import aiosmtplib
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

logger = logging.getLogger(__name__)

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM     = os.getenv("MAIL_FROM")
SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 587


# ─── Core email sender ────────────────────────────────────
# this is the base function all others use
# takes a recipient, subject and HTML body
async def send_email(to_email: str, subject: str, html_body: str):
    try:
        # build the email
        message = MIMEMultipart("alternative")
        message["From"]    = MAIL_FROM
        message["To"]      = to_email
        message["Subject"] = subject

        # attach HTML body
        html_part = MIMEText(html_body, "html")
        message.attach(html_part)

        # send via Gmail SMTP
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=MAIL_USERNAME,
            password=MAIL_PASSWORD,
            start_tls=True,   # secure connection
        )

        logger.info(f"📧 Email sent to {to_email} | Subject: {subject}")

    except Exception as e:
        # VERY important — never let email failure crash the app
        # background task errors are silent — log them but don't raise
        logger.error(f"❌ Email failed to {to_email} | Error: {str(e)}")


# ─── Email 1: Task Assigned ───────────────────────────────
# called when: POST /tasks — new task is created
async def send_task_assigned_email(
    employee_name:  str,
    employee_email: str,
    task_title:     str,
    task_description: str,
    task_priority:  str,
    deadline:       str = "No deadline set"
):
    subject = f"New Task Assigned: {task_title}"

    # priority color for visual email
    priority_colors = {
        "high":   "#dc2626",   # red
        "medium": "#d97706",   # amber
        "low":    "#16a34a",   # green
    }
    color = priority_colors.get(task_priority, "#6b7280")

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">

        <div style="background: #7c3aed; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 22px;">
                Task Management System
            </h1>
        </div>

        <div style="background: white; border: 1px solid #e5e7eb;
                border-radius: 8px; padding: 20px; margin: 20px 0;">
        <p style="margin: 0 0 8px; color: #6b7280; font-size: 13px;">
            TASK
        </p>
        <h3 style="margin: 0 0 16px; color: #1f2937; font-size: 18px;">
            {task_title}
        </h3>
        
        <!-- ← ADD THIS SECTION -->
        <p style="margin: 0 0 16px; color: #374151; font-size: 14px;">
            <strong>Description:</strong><br/>
            {task_description or 'No description provided'}
        </p>
        
        <div style="display: flex; gap: 16px;">
            <span style="background: {color}; color: white;
                         padding: 4px 12px; border-radius: 20px;
                         font-size: 12px; font-weight: bold;">
                {task_priority.upper()} PRIORITY
            </span>
        </div>
                <p style="margin: 16px 0 0; color: #374151;">
                    <strong>Deadline:</strong> {deadline}
                </p>
            </div>

            <p style="color: #6b7280; font-size: 14px;">
                Please log in to the Task Management System to view
                full details and update your progress.
            </p>
        </div>

        <div style="background: #1f2937; padding: 16px;
                    border-radius: 0 0 8px 8px; text-align: center;">
            <p style="color: #9ca3af; margin: 0; font-size: 12px;">
                Task Management System · Automated Notification
            </p>
        </div>

    </div>
    """

    await send_email(employee_email, subject, html_body)


# ─── Email 2: Task Completed ──────────────────────────────
# called when: PATCH /tasks/{id} with status = "completed"
async def send_task_completed_email(
    employee_name:  str,
    employee_email: str,
    task_title:     str,
    completed_at:   str = None
):
    subject = f"Task Completed: {task_title}"
    completed_at = completed_at or datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">

        <div style="background: #059669; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 22px;">
                Task Management System
            </h1>
        </div>

        <div style="background: #f9fafb; padding: 28px; border: 1px solid #e5e7eb;">
            <h2 style="color: #1f2937; margin-top: 0;">
                ✅ Task Completed!
            </h2>

            <div style="background: #ecfdf5; border: 1px solid #6ee7b7;
                        border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h3 style="margin: 0 0 8px; color: #065f46;">
                    {task_title}
                </h3>
                <p style="margin: 0; color: #047857;">
                    <strong>Completed by:</strong> {employee_name}<br/>
                    <strong>Completed at:</strong> {completed_at}
                </p>
            </div>

            <p style="color: #6b7280; font-size: 14px;">
                Great work! This task has been marked as completed
                in the Task Management System.
            </p>
        </div>

        <div style="background: #1f2937; padding: 16px;
                    border-radius: 0 0 8px 8px; text-align: center;">
            <p style="color: #9ca3af; margin: 0; font-size: 12px;">
                Task Management System · Automated Notification
            </p>
        </div>

    </div>
    """

    await send_email(employee_email, subject, html_body)


# ─── Email 3: Deadline Reminder ───────────────────────────
# called when: PATCH /tasks/{id} deadline is updated
async def send_deadline_reminder_email(
    employee_name:  str,
    employee_email: str,
    task_title:     str,
    deadline:       str
):
    subject = f"Deadline Reminder: {task_title}"

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">

        <div style="background: #d97706; padding: 24px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 22px;">
                Task Management System
            </h1>
        </div>

        <div style="background: #f9fafb; padding: 28px; border: 1px solid #e5e7eb;">
            <h2 style="color: #1f2937; margin-top: 0;">
                ⏰ Deadline Reminder
            </h2>

            <div style="background: #fffbeb; border: 1px solid #fcd34d;
                        border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h3 style="margin: 0 0 8px; color: #92400e;">
                    {task_title}
                </h3>
                <p style="margin: 0; color: #b45309; font-size: 15px;">
                    <strong>Deadline:</strong> {deadline}
                </p>
            </div>

            <p style="color: #6b7280; font-size: 14px;">
                Hi {employee_name}, this is a reminder that the above
                task deadline has been set. Please make sure to complete
                it on time.
            </p>
        </div>

        <div style="background: #1f2937; padding: 16px;
                    border-radius: 0 0 8px 8px; text-align: center;">
            <p style="color: #9ca3af; margin: 0; font-size: 12px;">
                Task Management System · Automated Notification
            </p>
        </div>

    </div>
    """

    await send_email(employee_email, subject, html_body)