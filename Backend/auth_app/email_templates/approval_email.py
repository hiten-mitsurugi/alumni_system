"""
Email templates for user approval notifications
"""

def get_approval_email_template(user, login_url="http://localhost:5173/login"):
    """
    Generate approval email template
    """
    subject = '🎉 Account Approved - Welcome to Alumni System!'
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to Alumni System</title>
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 30px;
            }}
            .welcome-badge {{
                background: #28a745;
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                display: inline-block;
                font-weight: bold;
                margin-bottom: 15px;
            }}
            .login-button {{
                background: #007bff;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                font-weight: bold;
                margin: 20px 0;
            }}
            .features {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .feature-item {{
                margin: 10px 0;
                padding-left: 25px;
                position: relative;
            }}
            .feature-item::before {{
                content: '✓';
                position: absolute;
                left: 0;
                color: #28a745;
                font-weight: bold;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎓 Welcome to Alumni System</h1>
                <div class="welcome-badge">Account Approved!</div>
            </div>
            
            <p>Dear <strong>{user.first_name} {user.last_name}</strong>,</p>
            
            <p>Congratulations! Your alumni account has been approved and is now active. We're excited to welcome you to our alumni community!</p>
            
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin: 0 0 10px 0; color: #1976d2;">📋 Your Account Details:</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>Name:</strong> {user.first_name} {user.last_name}</li>
                    <li><strong>Email:</strong> {user.email}</li>
                    <li><strong>Student Number:</strong> {user.username}</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{login_url}" class="login-button">🚀 Login to Your Account</a>
            </div>
            
            <div class="features">
                <h3 style="color: #333; margin-bottom: 15px;">🌟 What You Can Do Now:</h3>
                <div class="feature-item">Connect with fellow alumni worldwide</div>
                <div class="feature-item">Access exclusive job postings and career opportunities</div>
                <div class="feature-item">Join alumni events and networking sessions</div>
                <div class="feature-item">Use our professional messaging system</div>
                <div class="feature-item">Update your professional profile and achievements</div>
                <div class="feature-item">Access career development resources and mentorship</div>
            </div>
            
            <div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #ffc107;">
                <h4 style="margin: 0 0 10px 0; color: #856404;">💡 Getting Started Tips:</h4>
                <p style="margin: 5px 0;">1. Complete your profile to connect with more alumni</p>
                <p style="margin: 5px 0;">2. Upload a professional photo</p>
                <p style="margin: 5px 0;">3. Add your work history and achievements</p>
                <p style="margin: 5px 0;">4. Explore the alumni directory</p>
            </div>
            
            <div class="footer">
                <p>If you have any questions or need assistance, please contact our Alumni Relations Office:</p>
                <p>📧 <strong>Email:</strong> alumni@university.edu | 📞 <strong>Phone:</strong> (123) 456-7890</p>
                <p><small>Office Hours: Monday-Friday, 8:00 AM - 5:00 PM</small></p>
                
                <p style="margin-top: 20px;"><strong>Welcome to the family!</strong> 🎓</p>
                <p><em>Alumni Relations Team</em></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
Dear {user.first_name} {user.last_name},

🎉 CONGRATULATIONS! Your alumni account has been approved!

Account Details:
- Name: {user.first_name} {user.last_name}
- Email: {user.email}
- Student Number: {user.username}

You can now log in at: {login_url}

What You Can Do Now:
✓ Connect with fellow alumni worldwide
✓ Access exclusive job postings and career opportunities  
✓ Join alumni events and networking sessions
✓ Use our professional messaging system
✓ Update your professional profile and achievements
✓ Access career development resources and mentorship

Getting Started Tips:
1. Complete your profile to connect with more alumni
2. Upload a professional photo
3. Add your work history and achievements
4. Explore the alumni directory

Need help? Contact Alumni Relations Office:
📧 alumni@university.edu
📞 (123) 456-7890
Office Hours: Monday-Friday, 8:00 AM - 5:00 PM

Welcome to the alumni family!

Best regards,
Alumni Relations Team
    """
    
    return subject, html_content, text_content


def get_rejection_email_template(user):
    """
    Generate rejection email template
    """
    subject = '📋 Alumni Account Application - Additional Information Required'
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Alumni Account Application Update</title>
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
                background: linear-gradient(135deg, #ff7b7b 0%, #d63384 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 30px;
            }}
            .info-box {{
                background: #fff3cd;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #ffc107;
                margin: 20px 0;
            }}
            .contact-box {{
                background: #d1ecf1;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #17a2b8;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 Alumni Account Application</h1>
                <p>Additional Information Required</p>
            </div>
            
            <p>Dear <strong>{user.first_name} {user.last_name}</strong>,</p>
            
            <p>Thank you for your interest in joining our Alumni System. We have reviewed your account application and need additional information before we can approve your account.</p>
            
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin: 0 0 10px 0; color: #1976d2;">📋 Application Details:</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>Name:</strong> {user.first_name} {user.last_name}</li>
                    <li><strong>Email:</strong> {user.email}</li>
                    <li><strong>Student Number:</strong> {user.username}</li>
                </ul>
            </div>
            
            <div class="info-box">
                <h3 style="margin: 0 0 15px 0; color: #856404;">⚠️ Common Reasons for Additional Review:</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Student number verification needed</li>
                    <li>Graduation information requires confirmation</li>
                    <li>Document verification pending</li>
                    <li>Contact information needs updating</li>
                    <li>Program/degree verification required</li>
                </ul>
            </div>
            
            <div class="contact-box">
                <h3 style="margin: 0 0 15px 0; color: #0c5460;">📞 Next Steps - Contact Alumni Relations:</h3>
                <p style="margin: 5px 0;"><strong>📧 Email:</strong> alumni@university.edu</p>
                <p style="margin: 5px 0;"><strong>📞 Phone:</strong> (123) 456-7890</p>
                <p style="margin: 5px 0;"><strong>🕒 Office Hours:</strong> Monday-Friday, 8:00 AM - 5:00 PM</p>
                <p style="margin: 15px 0 5px 0;"><strong>What to prepare:</strong></p>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Valid ID or university-issued identification</li>
                    <li>Proof of graduation (diploma, transcript)</li>
                    <li>Current contact information</li>
                </ul>
            </div>
            
            <p>We appreciate your understanding and look forward to welcoming you to our alumni community once the verification process is complete. You may need to resubmit your application with the correct information after speaking with our office.</p>
            
            <div class="footer">
                <p><strong>We're here to help!</strong> 📞</p>
                <p>Our Alumni Relations team is ready to assist you with the verification process.</p>
                <p style="margin-top: 20px;"><em>Best regards,<br>Alumni Relations Team</em></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
Dear {user.first_name} {user.last_name},

Thank you for your interest in joining our Alumni System.

We have reviewed your account application and need additional information before we can approve your account.

Application Details:
- Name: {user.first_name} {user.last_name}
- Email: {user.email}
- Student Number: {user.username}

Common Reasons for Additional Review:
• Student number verification needed
• Graduation information requires confirmation  
• Document verification pending
• Contact information needs updating
• Program/degree verification required

NEXT STEPS - Contact Alumni Relations Office:
📧 Email: alumni@university.edu
📞 Phone: (123) 456-7890
🕒 Office Hours: Monday-Friday, 8:00 AM - 5:00 PM

What to prepare:
• Valid ID or university-issued identification
• Proof of graduation (diploma, transcript)
• Current contact information

We appreciate your understanding and look forward to welcoming you to our alumni community once the verification process is complete. You may need to resubmit your application with the correct information after speaking with our office.

Best regards,
Alumni Relations Team
    """
    
    return subject, html_content, text_content
