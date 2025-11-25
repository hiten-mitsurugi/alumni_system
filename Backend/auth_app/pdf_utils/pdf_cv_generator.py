"""
Professional CV PDF Generator using HTML template
Generates professional CVs matching csv.html design EXACTLY
"""

import os
from io import BytesIO
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from xhtml2pdf import pisa


class CVPDFGenerator:
    """Generate professional PDF CV from user data using HTML template"""
    
    def __init__(self, user, include_picture=True):
        self.user = user
        self.include_picture = include_picture
        
    def _get_initials(self):
        """Get user initials for placeholder"""
        first = self.user.first_name[0].upper() if self.user.first_name else ''
        last = self.user.last_name[0].upper() if self.user.last_name else ''
        return f"{first}{last}" if first or last else "?"
    
    def _get_profile_picture_path(self):
        """Get absolute path to profile picture if it exists"""
        if not self.include_picture:
            return None
            
        try:
            if self.user.profile_picture:
                picture_path = os.path.join(settings.MEDIA_ROOT, str(self.user.profile_picture))
                if os.path.exists(picture_path):
                    return picture_path
        except:
            pass
        return None
    
    def _format_skills(self):
        """Format skills for display"""
        skills = []
        try:
            for skill in self.user.user_skills.all().order_by('-proficiency'):
                level_display = skill.get_proficiency_display() if hasattr(skill, 'get_proficiency_display') else skill.proficiency
                skills.append({
                    'name': skill.name,
                    'level': level_display
                })
        except Exception as e:
            print(f"Error getting skills: {e}")
        return skills
    
    def _format_social_links(self):
        """Get social media links"""
        links = []
        try:
            profile = self.user.profile
            
            if profile.linkedin_url:
                links.append({'name': 'LinkedIn', 'url': profile.linkedin_url})
            if profile.facebook_url:
                links.append({'name': 'Facebook', 'url': profile.facebook_url})
            if profile.twitter_url:
                links.append({'name': 'Twitter', 'url': profile.twitter_url})
            if profile.instagram_url:
                links.append({'name': 'Instagram', 'url': profile.instagram_url})
            if profile.website_url:
                links.append({'name': 'Website', 'url': profile.website_url})
        except Exception as e:
            print(f"Error getting social links: {e}")
        
        return links
    
    def _get_bio(self):
        """Get user bio/about section"""
        try:
            profile = self.user.profile
            return profile.bio if profile.bio else None
        except:
            return None
    
    def _format_work_history(self):
        """Format work experience with timeline"""
        work_list = []
        try:
            for work in self.user.work_histories.all().order_by('-start_date'):
                # Format date range
                start = work.start_date.strftime("%B %Y") if work.start_date else ""
                if work.end_date:
                    end = work.end_date.strftime("%B %Y")
                    date_range = f"{start} - {end}"
                else:
                    date_range = f"{start} - Present" if start else "Present"
                
                # Add location if available
                if hasattr(work, 'location') and work.location:
                    date_range += f" • {work.location}"
                
                work_list.append({
                    'occupation': work.occupation,
                    'agency': work.employing_agency,
                    'date_range': date_range,
                    'description': work.description if hasattr(work, 'description') else ''
                })
        except Exception as e:
            print(f"Error formatting work history: {e}")
        return work_list
    
    def _format_education(self):
        """Format education with timeline"""
        edu_list = []
        try:
            for edu in self.user.education.all().order_by('-start_date'):
                # Build degree name
                degree = edu.get_degree_type_display() if hasattr(edu, 'get_degree_type_display') else str(edu.degree_type)
                if hasattr(edu, 'field_of_study') and edu.field_of_study:
                    degree += f" in {edu.field_of_study}"
                
                # Format date range
                start = edu.start_date.strftime("%B %Y") if edu.start_date else ""
                if edu.end_date:
                    end = edu.end_date.strftime("%B %Y")
                    date_range = f"{start} - {end}"
                elif hasattr(edu, 'is_current') and edu.is_current:
                    date_range = f"{start} - Present" if start else "Present"
                else:
                    date_range = start
                
                # Add location if available
                if hasattr(edu, 'location') and edu.location:
                    date_range += f" • {edu.location}"
                
                # Build extra info (GPA, honors, etc.)
                extra = []
                if hasattr(edu, 'gpa') and edu.gpa:
                    extra.append(f"GPA: {edu.gpa}")
                if hasattr(edu, 'honors') and edu.honors:
                    extra.append(edu.honors)
                if hasattr(edu, 'description') and edu.description:
                    extra.append(edu.description)
                
                edu_list.append({
                    'degree': degree,
                    'institution': edu.institution,
                    'date_range': date_range,
                    'extra_info': '\n'.join(extra) if extra else ''
                })
        except Exception as e:
            print(f"Error formatting education: {e}")
        return edu_list
    
    def _format_achievements(self):
        """Format achievements as simple list"""
        achievements = []
        try:
            for achievement in self.user.achievements.all().order_by('-date_achieved'):
                text = achievement.title
                if hasattr(achievement, 'organization') and achievement.organization:
                    text += f" - {achievement.organization}"
                if achievement.date_achieved:
                    text += f" ({achievement.date_achieved.year})"
                achievements.append(text)
        except Exception as e:
            print(f"Error formatting achievements: {e}")
        return achievements
    
    def _format_memberships(self):
        """Format memberships as simple list"""
        memberships = []
        try:
            for membership in self.user.memberships.all().order_by('-date_joined'):
                text = membership.organization_name
                if hasattr(membership, 'position') and membership.position:
                    text += f" - {membership.position}"
                if membership.date_joined:
                    text += f" - Active since {membership.date_joined.year}"
                memberships.append(text)
        except Exception as e:
            print(f"Error formatting memberships: {e}")
        return memberships
    
    def _format_recognitions(self):
        """Format recognitions as simple list"""
        recognitions = []
        try:
            for recog in self.user.recognitions.all().order_by('-date_received'):
                text = recog.title
                if hasattr(recog, 'issuing_organization') and recog.issuing_organization:
                    text += f" - {recog.issuing_organization}"
                if recog.date_received:
                    text += f" ({recog.date_received.year})"
                recognitions.append(text)
        except Exception as e:
            print(f"Error formatting recognitions: {e}")
        return recognitions
    
    def _format_trainings(self):
        """Format trainings as simple list"""
        trainings = []
        try:
            for training in self.user.trainings.all().order_by('-date_end'):
                text = training.title
                if hasattr(training, 'organization') and training.organization:
                    text += f" - {training.organization}"
                if training.date_end:
                    text += f", {training.date_end.year}"
                trainings.append(text)
        except Exception as e:
            print(f"Error formatting trainings: {e}")
        return trainings
    
    def _format_publications(self):
        """Format publications as simple list"""
        publications = []
        try:
            for pub in self.user.publications.all().order_by('-date_published'):
                text = f'"{pub.title}"'
                if hasattr(pub, 'publisher') and pub.publisher:
                    text += f" - {pub.publisher}"
                if pub.date_published:
                    text += f", {pub.date_published.year}"
                publications.append(text)
        except Exception as e:
            print(f"Error formatting publications: {e}")
        return publications
    
    def _get_job_title(self):
        """Get current job title from latest work history"""
        try:
            # Try to find current employment
            latest_work = self.user.work_histories.filter(end_date__isnull=True).first()
            if not latest_work:
                latest_work = self.user.work_histories.order_by('-start_date').first()
            
            if latest_work:
                return latest_work.occupation
        except Exception as e:
            print(f"Error getting job title: {e}")
        
        return "Professional"
    
    def generate(self):
        """Generate PDF CV using HTML template"""
        
        # Get gender and civil status display values
        gender_display = self.user.get_gender_display() if hasattr(self.user, 'get_gender_display') and self.user.gender else ''
        civil_status_display = self.user.get_civil_status_display() if hasattr(self.user, 'get_civil_status_display') and self.user.civil_status else ''
        
        # Prepare context data for template
        context = {
            'user': self.user,
            'full_name': f"{self.user.first_name} {self.user.last_name}",
            'initials': self._get_initials(),
            'job_title': self._get_job_title(),
            'include_photo': self.include_picture,
            'profile_picture_path': self._get_profile_picture_path(),
            
            # Left column data
            'skills': self._format_skills(),
            'social_links': self._format_social_links(),
            'gender_display': gender_display,
            'civil_status_display': civil_status_display,
            
            # Right column data
            'present_address': self.user.get_formatted_present_address() if hasattr(self.user, 'get_formatted_present_address') else '',
            'permanent_address': self.user.get_formatted_permanent_address() if hasattr(self.user, 'get_formatted_permanent_address') else '',
            'bio': self._get_bio(),
            'work_history': self._format_work_history(),
            'education': self._format_education(),
            'achievements': self._format_achievements(),
            'memberships': self._format_memberships(),
            'recognitions': self._format_recognitions(),
            'trainings': self._format_trainings(),
            'publications': self._format_publications(),
        }
        
        # Render HTML template
        html_string = render_to_string('pdf_utils/cv_template.html', context)
        
        # Create PDF from HTML
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
        
        if pdf.err:
            raise Exception("Error generating PDF")
        
        # Return PDF bytes
        pdf_value = result.getvalue()
        result.close()
        
        return pdf_value
