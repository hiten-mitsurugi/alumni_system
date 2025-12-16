"""
Survey Reminder Email Template
================================
Email template for survey completion reminders sent to alumni.
"""


def get_survey_reminder_email_template(user, survey_name, survey_link, custom_message=None, end_date=None):
    """
    Generate survey reminder email template.
    
    Args:
        user: User object (must have first_name, last_name, email)
        survey_name: Name of the survey
        survey_link: Full URL link to the survey
        custom_message: Optional custom message to include
        end_date: Optional survey end date
    
    Returns:
        Tuple of (subject, html_content, text_content)
    """
    subject = f'⏰ Survey Reminder: {survey_name}'
    
    # Custom message section
    custom_message_html = ''
    if custom_message:
        custom_message_html = f"""
        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #1976d2;">
            <h4 style="margin: 0 0 10px 0; color: #1976d2;">💬 Message from Administrator:</h4>
            <p style="margin: 0; color: #333;">{custom_message}</p>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Survey Reminder</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f8f9fa;
            }}
            .container {{
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #ea580c 0%, #c2410c 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 30px;
            }}
            .reminder-badge {{
                background: #fbbf24;
                color: #78350f;
                padding: 8px 16px;
                border-radius: 20px;
                display: inline-block;
                font-weight: bold;
                margin-bottom: 15px;
            }}
            .survey-button {{
                background: #ea580c;
                color: white;
                padding: 14px 40px;
                text-decoration: none;
                border-radius: 6px;
                display: inline-block;
                font-weight: bold;
                margin: 20px 0;
                font-size: 16px;
            }}
            .info-box {{
                background: #fff3cd;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #ffc107;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #666;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 Survey Reminder</h1>
                <div class="reminder-badge">Action Required</div>
            </div>
            
            <p>Dear <strong>{user.first_name} {user.last_name}</strong>,</p>
            
            <p>This is a friendly reminder to complete the <strong>"{survey_name}"</strong> survey. Your response is valuable and helps us improve our services to the alumni community.</p>
            
            {custom_message_html}
            
            <div class="info-box">
                <h3 style="margin: 0 0 10px 0; color: #856404;">📊 Survey Details:</h3>
                <p style="margin: 5px 0;"><strong>Survey:</strong> {survey_name}</p>
                <p style="margin: 10px 0 5px 0;">Your participation makes a difference! We need your insights to:</p>
                <ul style="margin: 5px 0 0 0; padding-left: 20px;">
                    <li>Better understand alumni needs and preferences</li>
                    <li>Improve programs and services</li>
                    <li>Strengthen our alumni community</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{survey_link}" class="survey-button">📝 Complete Survey Now</a>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h4 style="margin: 0 0 10px 0; color: #333;">⏱️ It Only Takes a Few Minutes</h4>
                <p style="margin: 0; color: #666;">The survey is quick and easy to complete. Your honest feedback is greatly appreciated!</p>
            </div>
            
            <div class="footer">
                <p>If you have any questions about this survey, please contact our Alumni Relations Office:</p>
                <p>📧 <strong>Email:</strong> ccis@carsu.edu.ph</p>
                <p style="margin-top: 15px; font-size: 12px; color: #999;">
                    You are receiving this email because you are part of our alumni community.
                </p>
                <p style="margin-top: 20px;"><strong>Thank you for your participation!</strong> 🎓</p>
                <p><em>Alumni Relations Team</em></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
Dear {user.first_name} {user.last_name},

⏰ SURVEY REMINDER

This is a friendly reminder to complete the "{survey_name}" survey.

Your response is valuable and helps us improve our services to the alumni community.
"""
    
    if custom_message:
        text_content += f"""
Message from Administrator:
{custom_message}

"""
    
    text_content += f"""
Survey Details:
- Survey: {survey_name}

Your participation makes a difference! We need your insights to:
• Better understand alumni needs and preferences
• Improve programs and services
• Strengthen our alumni community

Complete the survey here: {survey_link}

⏱️ It Only Takes a Few Minutes
The survey is quick and easy to complete. Your honest feedback is greatly appreciated!

Questions? Contact Alumni Relations Office:
📧 ccis@carsu.edu.ph

Thank you for your participation!

Best regards,
Alumni Relations Team

---
You are receiving this email because you are part of our alumni community.
    """
    
    return subject, html_content, text_content
