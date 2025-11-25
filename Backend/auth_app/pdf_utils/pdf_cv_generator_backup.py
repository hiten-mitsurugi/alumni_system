"""
Professional CV PDF Generator using HTML template
Generates LinkedIn-style professional CVs with clean layout and typography
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
        
        # Heading 2 - Section titles
        self.styles.add(ParagraphStyle(
            name='CVSectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.PRIMARY_COLOR,
            spaceBefore=12,
            spaceAfter=6,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=self.PRIMARY_COLOR,
            borderPadding=0,
            leftIndent=0,
            borderRadius=0
        ))
        
        # Heading 3 - Subsection (job title, degree, etc.)
        self.styles.add(ParagraphStyle(
            name='CVSubtitle',
            parent=self.styles['Heading3'],
            fontSize=11,
            textColor=self.SECONDARY_COLOR,
            spaceAfter=3,
            fontName='Helvetica-Bold'
        ))
        
        # Normal text
        self.styles.add(ParagraphStyle(
            name='CVNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.TEXT_COLOR,
            spaceAfter=6,
            fontName='Helvetica',
            leading=14
        ))
        
        # Small text (dates, metadata)
        self.styles.add(ParagraphStyle(
            name='CVSmall',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.GRAY_COLOR,
            spaceAfter=3,
            fontName='Helvetica',
            leading=12
        ))
        
        # Contact info
        self.styles.add(ParagraphStyle(
            name='CVContact',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.GRAY_COLOR,
            spaceAfter=2,
            fontName='Helvetica'
        ))
        
        # Headline/bio
        self.styles.add(ParagraphStyle(
            name='CVHeadline',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.SECONDARY_COLOR,
            spaceAfter=8,
            fontName='Helvetica',
            leading=14
        ))
    
    def generate(self):
        """Generate the complete PDF CV"""
        
        # Create PDF document
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title=f"CV - {self.user.get_full_name()}",
            author=self.user.get_full_name()
        )
        
        # Build content
        story = []
        
        # Header section (name, photo, contact)
        story.extend(self._build_header())
        story.append(Spacer(1, 0.5*cm))
        
        # Bio/Summary - check both user.bio and user.profile.bio
        has_bio = False
        if hasattr(self.user, 'profile') and hasattr(self.user.profile, 'bio') and self.user.profile.bio:
            has_bio = True
        elif hasattr(self.user, 'bio') and self.user.bio:
            has_bio = True
            
        if has_bio:
            story.extend(self._build_summary())
            story.append(Spacer(1, 0.3*cm))
        
        # Education
        education = self._get_education()
        if education:
            story.extend(self._build_education_section(education))
            story.append(Spacer(1, 0.3*cm))
        
        # Work History
        work_history = self._get_work_history()
        if work_history:
            story.extend(self._build_work_section(work_history))
            story.append(Spacer(1, 0.3*cm))
        
        # Skills
        skills = self._get_skills()
        if skills:
            story.extend(self._build_skills_section(skills))
            story.append(Spacer(1, 0.3*cm))
        
        # Achievements
        achievements = self._get_achievements()
        if achievements:
            story.extend(self._build_achievements_section(achievements))
            story.append(Spacer(1, 0.3*cm))
        
        # Publications
        publications = self._get_publications()
        if publications:
            story.extend(self._build_publications_section(publications))
            story.append(Spacer(1, 0.3*cm))
        
        # Memberships
        memberships = self._get_memberships()
        if memberships:
            story.extend(self._build_memberships_section(memberships))
            story.append(Spacer(1, 0.3*cm))
        
        # Recognitions
        recognitions = self._get_recognitions()
        if recognitions:
            story.extend(self._build_recognitions_section(recognitions))
            story.append(Spacer(1, 0.3*cm))
        
        # Trainings
        trainings = self._get_trainings()
        if trainings:
            story.extend(self._build_trainings_section(trainings))
        
        # Build PDF
        doc.build(story)
        
        # Return buffer
        self.buffer.seek(0)
        return self.buffer
    
    def _build_header(self):
        """Build header with name, photo, and contact info"""
        elements = []
        
        # Create table for layout: [Photo | Name & Contact]
        data = []
        
        # Profile picture (if included and exists)
        photo_cell = ""
        if self.include_picture and self.user.profile_picture:
            try:
                # Get absolute path to profile picture
                if self.user.profile_picture.name:
                    photo_path = self.user.profile_picture.path
                    if os.path.exists(photo_path):
                        img = Image(photo_path, width=3*cm, height=3*cm)
                        photo_cell = img
            except Exception as e:
                print(f"Could not load profile picture: {e}")
                photo_cell = ""
        
        # Name and contact info
        full_name = self.user.get_full_name() or self.user.username
        name_para = Paragraph(full_name, self.styles['CVName'])
        
        contact_info = []
        if self.user.email:
            contact_info.append(f"✉ {self.user.email}")
        if hasattr(self.user, 'contact_number') and self.user.contact_number:
            contact_info.append(f"📱 {self.user.contact_number}")
        
        # Get address from Address model if available
        try:
            present_address = self.user.normalized_addresses.filter(address_category='present').first()
            if present_address:
                city = getattr(present_address, 'city_municipality', None)
                province = getattr(present_address, 'province', None)
                if city or province:
                    location_parts = []
                    if city:
                        location_parts.append(city)
                    if province:
                        location_parts.append(province)
                    contact_info.append(f"📍 {', '.join(location_parts)}")
        except:
            pass
        
        contact_text = " • ".join(contact_info)
        contact_para = Paragraph(contact_text, self.styles['CVContact'])
        
        # Program and graduation info
        program_info = []
        if hasattr(self.user, 'program') and self.user.program:
            program_info.append(self.user.program)
        if hasattr(self.user, 'year_graduated') and self.user.year_graduated:
            program_info.append(f"Class of {self.user.year_graduated}")
        
        if program_info:
            program_para = Paragraph(" • ".join(program_info), self.styles['CVSmall'])
        else:
            program_para = ""
        
        # Build header table
        if photo_cell:
            header_table = Table(
                [[photo_cell, [name_para, contact_para, program_para]]],
                colWidths=[3.5*cm, None]
            )
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (0, 0), 0),
                ('RIGHTPADDING', (1, 0), (1, 0), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            elements.append(header_table)
        else:
            elements.append(name_para)
            elements.append(contact_para)
            if program_para:
                elements.append(program_para)
        
        # Divider line
        line_table = Table([['']], colWidths=[17*cm])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, self.PRIMARY_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(line_table)
        
        return elements
    
    def _build_summary(self):
        """Build summary/bio section"""
        elements = []
        # Try to get bio from Profile model
        bio = None
        if hasattr(self.user, 'profile') and hasattr(self.user.profile, 'bio'):
            bio = self.user.profile.bio
        elif hasattr(self.user, 'bio'):
            bio = self.user.bio
            
        if bio:
            elements.append(Paragraph("About", self.styles['CVSectionTitle']))
            elements.append(Paragraph(bio, self.styles['CVNormal']))
        return elements
    
    def _build_education_section(self, education_list):
        """Build education section"""
        elements = []
        elements.append(Paragraph("Education", self.styles['CVSectionTitle']))
        
        for edu in education_list:
            item_elements = []
            
            # Degree and institution
            degree_name = edu.get_degree_type_display() if hasattr(edu, 'get_degree_type_display') else str(edu.degree_type)
            if edu.field_of_study:
                degree_name += f" in {edu.field_of_study}"
            item_elements.append(Paragraph(degree_name, self.styles['CVSubtitle']))
            
            # Institution and dates
            meta_parts = [edu.institution]
            if edu.start_date or edu.end_date:
                date_str = self._format_date_range(edu.start_date, edu.end_date, edu.is_current)
                meta_parts.append(date_str)
            item_elements.append(Paragraph(" • ".join(meta_parts), self.styles['CVSmall']))
            
            # GPA if available
            if edu.gpa:
                item_elements.append(Paragraph(f"GPA: {edu.gpa}", self.styles['CVSmall']))
            
            # Description
            if edu.description:
                item_elements.append(Paragraph(edu.description, self.styles['CVNormal']))
            
            item_elements.append(Spacer(1, 0.2*cm))
            elements.append(KeepTogether(item_elements))
        
        return elements
    
    def _build_work_section(self, work_list):
        """Build work experience section"""
        elements = []
        elements.append(Paragraph("Experience", self.styles['CVSectionTitle']))
        
        for work in work_list:
            item_elements = []
            
            # Position title (occupation in this model)
            item_elements.append(Paragraph(work.occupation, self.styles['CVSubtitle']))
            
            # Company and dates (employing_agency in this model)
            meta_parts = [work.employing_agency]
            # Check if current job (end_date is None)
            is_current = work.end_date is None
            date_str = self._format_date_range(work.start_date, work.end_date, is_current)
            meta_parts.append(date_str)
            item_elements.append(Paragraph(" • ".join(meta_parts), self.styles['CVSmall']))
            
            # Description
            if work.description:
                item_elements.append(Paragraph(work.description, self.styles['CVNormal']))
            
            item_elements.append(Spacer(1, 0.2*cm))
            elements.append(KeepTogether(item_elements))
        
        return elements
    
    def _build_skills_section(self, skills_list):
        """Build skills section"""
        elements = []
        elements.append(Paragraph("Skills", self.styles['CVSectionTitle']))
        
        # Group skills by category if available
        categorized = {}
        uncategorized = []
        
        for skill in skills_list:
            category = getattr(skill, 'category', None) or 'Other'
            if category == 'Other':
                uncategorized.append(skill)
            else:
                if category not in categorized:
                    categorized[category] = []
                categorized[category].append(skill)
        
        # Display categorized skills
        for category, skills in categorized.items():
            skill_names = [skill.name for skill in skills]
            skills_text = " • ".join(skill_names)
            elements.append(Paragraph(f"<b>{category}:</b> {skills_text}", self.styles['CVNormal']))
        
        # Display uncategorized
        if uncategorized:
            skill_names = [skill.name for skill in uncategorized]
            skills_text = " • ".join(skill_names)
            elements.append(Paragraph(skills_text, self.styles['CVNormal']))
        
        return elements
    
    def _build_achievements_section(self, achievements_list):
        """Build achievements section"""
        elements = []
        elements.append(Paragraph("Achievements", self.styles['CVSectionTitle']))
        
        for achievement in achievements_list:
            item_elements = []
            item_elements.append(Paragraph(achievement.title, self.styles['CVSubtitle']))
            
            if achievement.date_achieved:
                item_elements.append(Paragraph(
                    achievement.date_achieved.strftime("%B %Y"),
                    self.styles['CVSmall']
                ))
            
            if achievement.description:
                item_elements.append(Paragraph(achievement.description, self.styles['CVNormal']))
            
            item_elements.append(Spacer(1, 0.15*cm))
            elements.append(KeepTogether(item_elements))
        
        return elements
    
    def _build_publications_section(self, publications_list):
        """Build publications section"""
        elements = []
        elements.append(Paragraph("Publications", self.styles['CVSectionTitle']))
        
        for pub in publications_list:
            item_elements = []
            
            # Title
            title_text = pub.title
            if pub.url:
                title_text = f'<a href="{pub.url}" color="blue">{pub.title}</a>'
            item_elements.append(Paragraph(title_text, self.styles['CVSubtitle']))
            
            # Authors, publisher, date
            meta_parts = []
            if pub.authors:
                meta_parts.append(pub.authors)
            if pub.publisher:
                meta_parts.append(pub.publisher)
            if pub.date_published:
                meta_parts.append(pub.date_published.strftime("%Y"))
            
            if meta_parts:
                item_elements.append(Paragraph(" • ".join(meta_parts), self.styles['CVSmall']))
            
            # DOI
            if pub.doi:
                item_elements.append(Paragraph(f"DOI: {pub.doi}", self.styles['CVSmall']))
            
            item_elements.append(Spacer(1, 0.15*cm))
            elements.append(KeepTogether(item_elements))
        
        return elements
    
    def _build_memberships_section(self, memberships_list):
        """Build memberships/organizations section"""
        elements = []
        elements.append(Paragraph("Professional Memberships", self.styles['CVSectionTitle']))
        
        for membership in memberships_list:
            item_elements = []
            
            # Organization name
            item_elements.append(Paragraph(membership.organization_name, self.styles['CVSubtitle']))
            
            # Role and dates
            meta_parts = []
            if membership.position:
                meta_parts.append(membership.position)
            date_str = self._format_date_range(
                membership.date_joined,
                getattr(membership, 'date_ended', None),
                not getattr(membership, 'date_ended', None)
            )
            meta_parts.append(date_str)
            item_elements.append(Paragraph(" • ".join(meta_parts), self.styles['CVSmall']))
            
            # Description
            if membership.description:
                item_elements.append(Paragraph(membership.description, self.styles['CVNormal']))
            
            item_elements.append(Spacer(1, 0.15*cm))
            elements.append(KeepTogether(item_elements))
        
        return elements
    
    def _build_recognitions_section(self, recognitions_list):
        """Build recognitions section"""
        elements = []
        elements.append(Paragraph("Honors & Awards", self.styles['CVSectionTitle']))
        
        for recog in recognitions_list:
            item_elements = []
            item_elements.append(Paragraph(recog.title, self.styles['CVSubtitle']))
            
            # Issuer and date
            meta_parts = []
            if recog.issuing_organization:
                meta_parts.append(recog.issuing_organization)
            if recog.date_received:
                meta_parts.append(recog.date_received.strftime("%B %Y"))
            
            if meta_parts:
                item_elements.append(Paragraph(" • ".join(meta_parts), self.styles['CVSmall']))
            
            if recog.description:
                item_elements.append(Paragraph(recog.description, self.styles['CVNormal']))
            
            item_elements.append(Spacer(1, 0.15*cm))
            elements.append(KeepTogether(item_elements))
        
        return elements
    
    def _build_trainings_section(self, trainings_list):
        """Build trainings section"""
        elements = []
        elements.append(Paragraph("Training & Certifications", self.styles['CVSectionTitle']))
        
        for training in trainings_list:
            item_elements = []
            item_elements.append(Paragraph(training.title, self.styles['CVSubtitle']))
            
            # Organization and dates
            meta_parts = [training.organization]
            date_str = self._format_date_range(training.date_start, training.date_end, False)
            meta_parts.append(date_str)
            
            if training.location:
                meta_parts.append(training.location)
            
            item_elements.append(Paragraph(" • ".join(meta_parts), self.styles['CVSmall']))
            item_elements.append(Spacer(1, 0.15*cm))
            elements.append(KeepTogether(item_elements))
        
        return elements
    
    def _format_date_range(self, start_date, end_date, is_current=False):
        """Format date range for display"""
        if not start_date:
            return ""
        
        start_str = start_date.strftime("%b %Y")
        
        if is_current:
            return f"{start_str} - Present"
        elif end_date:
            end_str = end_date.strftime("%b %Y")
            return f"{start_str} - {end_str}"
        else:
            return start_str
    
    # Data retrieval methods
    def _get_education(self):
        from auth_app.models import Education
        return Education.objects.filter(user=self.user).order_by('-end_date', '-start_date')
    
    def _get_work_history(self):
        from auth_app.models import WorkHistory
        from django.db.models import Case, When, Value, IntegerField
        
        # Annotate is_current based on end_date being NULL
        return WorkHistory.objects.filter(user=self.user).annotate(
            is_current=Case(
                When(end_date__isnull=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).order_by('-is_current', '-start_date')
    
    def _get_skills(self):
        from auth_app.models import UserSkill
        return UserSkill.objects.filter(user=self.user).order_by('category', 'name')
    
    def _get_achievements(self):
        from auth_app.models import Achievement
        return Achievement.objects.filter(user=self.user).order_by('-is_featured', '-date_achieved')
    
    def _get_publications(self):
        from auth_app.models import Publication
        return Publication.objects.filter(user=self.user).order_by('-date_published')
    
    def _get_memberships(self):
        from auth_app.models import Membership
        return Membership.objects.filter(user=self.user).order_by('-date_joined')
    
    def _get_recognitions(self):
        from auth_app.models import Recognition
        return Recognition.objects.filter(user=self.user).order_by('-date_received')
    
    def _get_trainings(self):
        from auth_app.models import Training
        return Training.objects.filter(user=self.user).order_by('-date_start')
