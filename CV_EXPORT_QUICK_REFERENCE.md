# CV PDF Export - Quick Reference

## 🚀 Quick Start

### For Users
1. Go to your profile page
2. Click the blue **"Export CV"** button (next to "Edit Profile")
3. Toggle **"Include Profile Picture"** if desired
4. Click **"Download CV"**
5. PDF downloads as `YourFirstName_YourLastName_CV.pdf`

### For Developers

#### Backend Endpoint
```python
# Route: POST /api/auth/profile/export-cv/
# Authentication: Required
# Request body:
{
    "include_picture": true  # optional, default: true
}

# Response: PDF file download
# Content-Type: application/pdf
# Content-Disposition: attachment; filename="John_Doe_CV.pdf"
```

#### Generate PDF Programmatically
```python
from auth_app.pdf_utils.pdf_cv_generator import CVPDFGenerator

# For authenticated user
generator = CVPDFGenerator(user=request.user, include_picture=True)
pdf_buffer = generator.generate()

# Save to file
with open('output.pdf', 'wb') as f:
    f.write(pdf_buffer.getvalue())
```

#### Frontend Usage
```vue
<script setup>
import ExportCvModal from '@/components/profile/ExportCvModal.vue'
import { ref } from 'vue'

const showExportCvModal = ref(false)

const handleCvExportSuccess = () => {
  console.log('CV exported successfully')
}
</script>

<template>
  <button @click="showExportCvModal = true">Export CV</button>
  
  <ExportCvModal 
    :is-open="showExportCvModal"
    @close="showExportCvModal = false"
    @success="handleCvExportSuccess"
  />
</template>
```

## 📁 File Locations

### Backend
- **PDF Generator**: `Backend/auth_app/pdf_utils/pdf_cv_generator.py`
- **API Endpoint**: `Backend/auth_app/views/cv_export.py`
- **URL Route**: `Backend/auth_app/urls.py` (line ~114)
- **Tests**: `Backend/auth_app/tests/test_cv_export.py`

### Frontend
- **Modal Component**: `Frontend/src/components/profile/ExportCvModal.vue`
- **Profile Page**: `Frontend/src/views/Alumni/MyProfile.vue`

## 🎨 Customization

### Change PDF Colors
```python
# In pdf_cv_generator.py
PRIMARY_COLOR = colors.HexColor('#0a66c2')     # LinkedIn blue
SECONDARY_COLOR = colors.HexColor('#283e4a')  # Dark slate
ACCENT_COLOR = colors.HexColor('#70b5f9')     # Light blue
```

### Modify PDF Layout
```python
# Page settings
PAGE_SIZE = A4  # or letter
MARGINS = 2*cm  # all sides

# Font sizes
NAME_SIZE = 24
SECTION_HEADER_SIZE = 14
BODY_SIZE = 10
```

### Add New Section
```python
def _build_custom_section(self):
    """Add your custom section."""
    elements = []
    
    # Section header
    elements.append(Paragraph('Custom Section', self.styles['CVSectionTitle']))
    elements.append(Spacer(1, 0.2*cm))
    
    # Your content here
    content = "Your custom content"
    elements.append(Paragraph(content, self.styles['CVNormal']))
    
    return elements

# Add to generate() method:
def generate(self):
    story = []
    # ... existing sections ...
    story.extend(self._build_custom_section())  # Add this
    # ...
```

## 🧪 Testing

### Run All CV Export Tests
```bash
cd Backend
python manage.py test auth_app.tests.test_cv_export --verbosity=2
```

### Run Specific Test
```bash
python manage.py test auth_app.tests.test_cv_export.CVPDFGeneratorTestCase.test_pdf_generator_creates_valid_pdf
```

### Test Coverage
```bash
coverage run --source='auth_app' manage.py test auth_app.tests.test_cv_export
coverage report
coverage html  # generates htmlcov/index.html
```

## 🐛 Troubleshooting

### Issue: "Module 'auth_app.pdf_utils' not found"
**Solution**: Ensure `auth_app/pdf_utils/__init__.py` exists
```bash
# Check if file exists
ls Backend/auth_app/pdf_utils/__init__.py
```

### Issue: PDF generation fails with "Profile picture not found"
**Solution**: Either disable picture or ensure file exists
```python
# Disable picture
generator = CVPDFGenerator(user=user, include_picture=False)

# Or check file exists
if user.profile_picture and os.path.exists(user.profile_picture.path):
    generator = CVPDFGenerator(user=user, include_picture=True)
```

### Issue: PDF is blank or incomplete
**Solution**: Check user has profile data
```python
# Check what sections have data
education = Education.objects.filter(user=user).exists()
work = WorkHistory.objects.filter(user=user).exists()
skills = Skill.objects.filter(user=user).exists()
print(f"Has education: {education}, work: {work}, skills: {skills}")
```

### Issue: Modal not showing
**Solution**: Check Vue component import and state
```vue
<script setup>
// Ensure imports
import ExportCvModal from '@/components/profile/ExportCvModal.vue'
import { ref } from 'vue'

// Ensure state
const showExportCvModal = ref(false)
</script>
```

## 📊 Data Sources

The PDF pulls data from these models:
- `CustomUser` - Name, email, phone, bio, profile picture
- `Education` - Degrees, institutions, GPA
- `WorkHistory` - Positions, companies, dates
- `Skill` - Skills by category
- `Achievement` - Featured achievements
- `Publication` - Research papers, articles
- `Membership` - Professional organizations
- `Recognition` - Awards, honors
- `Training` - Certifications, courses

## 🔒 Security Notes

- ✅ Authentication required (JWT token)
- ✅ Users can only export their own CV
- ✅ No file system access (in-memory generation)
- ✅ Safe filename generation (no path traversal)
- ✅ Content-Type and Content-Disposition headers set correctly

## 🎯 API Examples

### cURL
```bash
# Export CV with picture
curl -X POST https://your-domain.com/api/auth/profile/export-cv/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"include_picture": true}' \
  --output my_cv.pdf

# Export CV without picture (GET method)
curl -X GET "https://your-domain.com/api/auth/profile/export-cv/?include_picture=false" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  --output my_cv.pdf
```

### JavaScript (Fetch)
```javascript
const token = localStorage.getItem('token')

fetch('/api/auth/profile/export-cv/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ include_picture: true })
})
.then(response => response.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'my_cv.pdf'
  a.click()
  window.URL.revokeObjectURL(url)
})
```

### Python (Requests)
```python
import requests

token = 'YOUR_JWT_TOKEN'
url = 'https://your-domain.com/api/auth/profile/export-cv/'

response = requests.post(
    url,
    headers={'Authorization': f'Bearer {token}'},
    json={'include_picture': True}
)

with open('my_cv.pdf', 'wb') as f:
    f.write(response.content)
```

## 📈 Performance

- **Generation Time**: ~100-500ms (typical profile)
- **PDF Size**: ~50-200KB
- **Database Queries**: 8 (one per section)
- **Memory Usage**: Minimal (in-memory buffer)
- **Concurrent Users**: Scales well (stateless)

## 🔄 Future Enhancements

Potential improvements:
1. **Multiple Formats**: Export as DOCX, HTML
2. **Templates**: Multiple CV templates to choose from
3. **Customization**: User-selectable colors/fonts
4. **Preview**: Show PDF preview before download
5. **Email**: Send CV via email
6. **Share**: Generate shareable link
7. **Analytics**: Track download counts
8. **Localization**: Multi-language support
9. **QR Code**: Add QR code to CV
10. **Cover Letter**: Include cover letter option

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review implementation summary: `CV_EXPORT_IMPLEMENTATION_SUMMARY.md`
3. Check test file for examples: `auth_app/tests/test_cv_export.py`
4. Review code comments in `pdf_cv_generator.py`

## 📚 Resources

- **ReportLab Docs**: https://www.reportlab.com/docs/reportlab-userguide.pdf
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Vue 3 Composition API**: https://vuejs.org/guide/extras/composition-api-faq.html
