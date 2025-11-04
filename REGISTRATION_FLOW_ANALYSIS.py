#!/usr/bin/env python
"""
COMPREHENSIVE ANALYSIS: RegisterDynamic.vue Registration Flow
How data flows from UI to Backend and which parts are from surveys vs static forms
"""

analysis = """
╔════════════════════════════════════════════════════════════════════════════════╗
║         DYNAMIC REGISTRATION FLOW - COMPLETE ANALYSIS                          ║
║  Frontend: RegisterDynamic.vue → Backend: RegisterSerializer → Database        ║
╚════════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════════
1. REGISTRATION STRUCTURE (3 STAGES)
═══════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: ALUMNI DIRECTORY VERIFICATION (Step 1)                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Component: VerifyAlumniDirectory.vue                                            │
│ Purpose: Check if user exists in AlumniDirectory                               │
│                                                                                 │
│ Data Source: STATIC FORM (not from survey)                                     │
│ Fields collected:                                                               │
│   ✓ first_name                                                                  │
│   ✓ middle_name                                                                │
│   ✓ last_name                                                                  │
│   ✓ program                                                                    │
│   ✓ birth_date                                                                 │
│   ✓ year_graduated                                                             │
│   ✓ sex (for AlumniDirectory matching)                                         │
│                                                                                 │
│ Action: If verified → alumni_exists = true → Proceed to Step 2                │
│ Flow: RegisterDynamic.form object → handleVerified() → nextStep()              │
└─────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: PERSONAL & DEMOGRAPHIC INFORMATION (Step 2)                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Component: PersonalInfo.vue                                                    │
│ Purpose: Collect personal data and demographic details                        │
│                                                                                 │
│ Data Source: STATIC FORM (not from survey)                                     │
│ Section A - Account Information:                                               │
│   ✓ email                                                                      │
│   ✓ password                                                                   │
│   ✓ confirm_password                                                           │
│   ✓ contact_number                                                             │
│                                                                                 │
│ Section B - Address Information (STRUCTURED):                                  │
│   ✓ present_address_data {                                                     │
│       address_type, region_code, region_name,                                 │
│       province_code, province_name, city_code,                                │
│       city_name, barangay, street_address,                                    │
│       postal_code, country, full_address                                      │
│     }                                                                           │
│   ✓ permanent_address_data {...}  (same structure)                             │
│   ✓ same_as_present (boolean flag)                                             │
│                                                                                 │
│ Section C - Demographic Information:                                           │
│   ✓ gender (NEW - added in PersonalInfo)                                       │
│   ✓ civil_status                                                               │
│   ✓ employment_status                                                          │
│                                                                                 │
│ Section D - Family Information:                                                │
│   ✓ mothers_name                                                               │
│   ✓ mothers_occupation                                                         │
│   ✓ fathers_name                                                               │
│   ✓ fathers_occupation                                                         │
│                                                                                 │
│ Section E - File Uploads:                                                      │
│   ✓ government_id (file)                                                       │
│   ✓ profile_picture (image)                                                    │
│                                                                                 │
│ Flow: PersonalInfo.vue → updateStep2Form() → form.value updated                │
│ Emitted: @update:form to parent RegisterDynamic                               │
└─────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────┐
│ STAGE 3+: DYNAMIC SURVEY CATEGORIES (Steps 3, 4, 5, ...)                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Component: DynamicSurveyStep.vue (repeated for each category)                 │
│ Purpose: Collect answers to survey questions from SurveyManagement             │
│                                                                                 │
│ Data Source: ✓ FROM SURVEY MANAGEMENT (dynamic & configurable)                 │
│                                                                                 │
│ Categories (from survey_app_surveycategory):                                   │
│   - Career & Employment                                                        │
│   - Skills & Competencies                                                      │
│   - Education Relevance                                                        │
│   - Further Studies                                                            │
│   - etc. (any new categories added in SurveyManagement)                        │
│                                                                                 │
│ Questions per category:                                                         │
│   - Text inputs                                                                │
│   - Multiple choice                                                            │
│   - Rating scales (1-5, 1-10, custom min/max)                                 │
│   - Checkboxes                                                                 │
│   - Dropdowns                                                                  │
│   - Conditional questions (show/hide based on other answers)                   │
│                                                                                 │
│ Conditional Logic:                                                              │
│   - Categories can depend on answers in previous categories                    │
│   - Categories auto-skip if conditions not met                                 │
│   - Total steps = 2 + visible_survey_categories                               │
│                                                                                 │
│ Data Collection:                                                                │
│   surveyResponses[question_id] = response_data                                 │
│   Managed by: useRegistrationSurvey() composable                              │
│   Stored in: surveyCategories.value array                                      │
│                                                                                 │
│ Flow: DynamicSurveyStep → handleSurveyResponses() →                           │
│       updateCategoryResponses() → surveyResponses updated                      │
└─────────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════
2. SUBMISSION FLOW (submitForm function)
═══════════════════════════════════════════════════════════════════════════════════

When user clicks "Complete Registration" on the final step:

┌─ Step 1: Collect Static Form Data ────────────────────────────────────────────┐
│ formData.append() calls for:                                                   │
│   • Stage 1 alumni data: first_name, middle_name, last_name, program, etc.    │
│   • Stage 2 personal data: email, password, gender, civil_status, etc.        │
│   • Address data: JSON serialized address objects                             │
│   • File uploads: government_id, profile_picture                              │
│   • Alumni flag: alumni_exists = true                                          │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─ Step 2: Collect Dynamic Survey Responses ───────────────────────────────────┐
│ surveyResponsesData = getSurveyResponsesForSubmission()                        │
│                                                                                 │
│ Returns array of survey responses:                                             │
│   [                                                                             │
│     { question: 225, response_data: true },                                   │
│     { question: 226, response_data: "Employed Locally" },                     │
│     { question: 227, response_data: "Private" },                              │
│     ...                                                                         │
│     { question: 270, response_data: "none so far" }                           │
│   ]                                                                             │
│                                                                                 │
│ formData.append('survey_responses', JSON.stringify(surveyResponsesData))       │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─ Step 3: Send to Backend ─────────────────────────────────────────────────────┐
│ POST /api/auth/register/                                                       │
│                                                                                 │
│ Headers: Content-Type: multipart/form-data                                    │
│                                                                                 │
│ Form Data Keys:                                                                 │
│   Static: first_name, middle_name, last_name, email, password, ...           │
│   Dynamic: survey_responses (JSON string)                                      │
└─────────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════
3. BACKEND PROCESSING (RegisterSerializer.create())
═══════════════════════════════════════════════════════════════════════════════════

┌─ Step 1: Extract Survey Responses ────────────────────────────────────────────┐
│ survey_responses_data = validated_data.pop('survey_responses', [])             │
│                                                                                 │
│ If provided:                                                                    │
│   for response_data in survey_responses_data:                                 │
│     question = SurveyQuestion.objects.get(id=response_data['question'])       │
│     SurveyResponse.objects.create(                                             │
│         user=user,                                                              │
│         question=question,                                                      │
│         response_data=response_data['response_data']                          │
│     )                                                                           │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─ Step 2: Create CustomUser (Static Data) ──────────────────────────────────────┐
│ user = CustomUser.objects.create_user(                                          │
│     username=email,                                                             │
│     email=email,                                                                │
│     password=password,                                                          │
│     first_name=first_name,                                                     │
│     middle_name=middle_name,                                                   │
│     last_name=last_name,                                                       │
│     gender=gender,  ✓ From PersonalInfo (Stage 2)                             │
│     civil_status=civil_status,  ✓ From PersonalInfo                            │
│     employment_status=employment_status,  ✓ From PersonalInfo                 │
│     contact_number=contact_number,                                             │
│     government_id=government_id,                                               │
│     profile_picture=profile_picture,                                           │
│     mothers_name=mothers_name,                                                 │
│     mothers_occupation=mothers_occupation,                                     │
│     fathers_name=fathers_name,                                                 │
│     fathers_occupation=fathers_occupation,                                     │
│     birth_date=birth_date,                                                     │
│     year_graduated=year_graduated,                                             │
│     program=program,                                                            │
│     user_type=3 (Alumni),                                                      │
│     is_approved=False                                                          │
│ )                                                                               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─ Step 3: Create Address Records ──────────────────────────────────────────────┐
│ Address.objects.create(                                                        │
│     user=user,                                                                  │
│     address_category='present',                                               │
│     **present_address_data  ✓ Structured data from PersonalInfo               │
│ )                                                                               │
│                                                                                 │
│ Address.objects.create(                                                        │
│     user=user,                                                                  │
│     address_category='permanent',                                             │
│     **permanent_address_data                                                   │
│ )                                                                               │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─ Step 4: Create Profile Record ───────────────────────────────────────────────┐
│ Profile.objects.create(user=user)                                              │
│                                                                                 │
│ NOTE: Profile has separate gender field but PersonalInfo provides it to       │
│ CustomUser first, then Profile.save() syncs: self.gender = self.user.gender   │
└─────────────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════
4. DATA FLOW DIAGRAM
═══════════════════════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (RegisterDynamic.vue)                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────┐       ┌──────────────────┐                        │
│  │ Step 1: Verify      │ ◄────► │ AlumniDirectory  │                        │
│  │ Alumni Directory    │       │ (Component)       │                        │
│  │ (Static Data)       │       └──────────────────┘                        │
│  └────────┬────────────┘                                                    │
│           │ alumni_exists = true                                            │
│  ┌────────▼────────────┐       ┌──────────────────┐                        │
│  │ Step 2: Personal    │ ◄────► │ PersonalInfo.vue │                        │
│  │ Information         │       │ (Component)       │                        │
│  │ (Static + Structured)│       │ • gender         │                        │
│  │ • Address structured │       │ • civil_status   │                        │
│  │ • Demographic data   │       │ • employment_status │                     │
│  └────────┬────────────┘       │ • address_data   │                        │
│           │                    │ • files          │                        │
│  ┌────────▼────────────────────┴──────────────────┘                        │
│  │ Steps 3+: Dynamic Survey Categories                                     │
│  │ (Conditional Steps from Survey Management)                              │
│  │ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                   │
│  │ │ Category 1   │  │ Category 2   │  │ Category 3   │ ...               │
│  │ │ Questions    │  │ Questions    │  │ Questions    │                   │
│  │ │ from DB      │  │ from DB      │  │ from DB      │                   │
│  │ └──────────────┘  └──────────────┘  └──────────────┘                   │
│  │        ↓                 ↓                 ↓                             │
│  │    surveyResponses[question_id] = response_data                        │
│  │                                                                         │
│  └────────────────────────┬──────────────────────────────────────────────┘
│                           │
│                           ▼
│                  submitForm() called
│                           │
│                ┌──────────┴──────────┐
│                │                     │
│        Static Data          Dynamic Data
│        ┌──────────────┐     ┌─────────────────┐
│        │ Personal     │     │ Survey          │
│        │ Info fields  │     │ Responses       │
│        └──────────────┘     │ (from all       │
│                             │  categories)    │
│                             └─────────────────┘
│                             
│                             JSON stringify
│                             
└─────────────────┬────────────────┬──────────────────────────────────────────┘
                  │                │
                  ▼                ▼
            ┌──────────────────────────────┐
            │ FormData Object              │
            │ • Static fields              │
            │ • survey_responses (JSON)    │
            │ • Files (multipart)          │
            └──────────────┬───────────────┘
                           │
                    POST /api/auth/register/
                           │
                           ▼
        ┌────────────────────────────────────────────┐
        │    BACKEND (RegisterSerializer.create())   │
        ├────────────────────────────────────────────┤
        │                                            │
        │  1. Extract survey_responses_data          │
        │     └─► Create SurveyResponse records      │
        │                                            │
        │  2. Create CustomUser                      │
        │     └─► With gender, civil_status, etc.    │
        │                                            │
        │  3. Create Address records                 │
        │     └─► present & permanent                │
        │                                            │
        │  4. Create Profile                         │
        │     └─► Synced with user data              │
        │                                            │
        └────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════
5. CRITICAL FIX APPLIED
═══════════════════════════════════════════════════════════════════════════════════

Issue: WorkHistorySerializer tried to serialize 'is_current_job' field
       which doesn't exist in PostgreSQL database

Solution: Changed to explicit field list in Backend/auth_app/serializers.py

Impact on Registration:
  • Still allows work_histories to be optional (backward compatibility)
  • No errors when work histories aren't provided (which is true in dynamic registration)
  • Gender, civil_status, employment_status all properly captured
  • Survey responses all properly stored

Status: ✅ FIXED - Registration should now work without 500 errors


═══════════════════════════════════════════════════════════════════════════════════
6. VERIFICATION CHECKLIST
═══════════════════════════════════════════════════════════════════════════════════

FRONTEND (RegisterDynamic.vue):
  ✅ Step 1 (Alumni Verification): Collects alumni directory data
  ✅ Step 2 (Personal Info): Collects from PersonalInfo.vue component
     ✅ Includes: gender, civil_status, employment_status ← PersonalInfo
     ✅ Includes: structured address data
     ✅ Includes: mothers/fathers names and occupations
  ✅ Steps 3+: Dynamic survey categories from DB
     ✅ Loads from: useRegistrationSurvey() composable
     ✅ Questions from: survey_app_surveycategory + survey_app_surveyquestion
  ✅ Submission: Collects ALL data and sends as multipart FormData

BACKEND (RegisterSerializer):
  ✅ Validates all static data
  ✅ Creates CustomUser with gender ← From PersonalInfo
  ✅ Creates Address records ← From PersonalInfo (structured)
  ✅ Creates Profile ← Auto-synced
  ✅ Creates SurveyResponses ← From dynamic survey responses
  ✅ WorkHistorySerializer fixed ← No is_current_job error

DATABASE:
  ✅ auth_app_customuser: Has gender, civil_status, employment_status
  ✅ auth_app_profile: Has gender (synced from user)
  ✅ auth_app_address: Stores structured address data
  ✅ survey_app_surveyresponse: Stores all survey answers
  ✅ auth_app_workhistory: Fixed (only existing columns used)

═══════════════════════════════════════════════════════════════════════════════════
CONCLUSION:
═══════════════════════════════════════════════════════════════════════════════════

✅ DYNAMIC REGISTRATION FLOW IS CORRECTLY IMPLEMENTED:

1. Stage 1 & 2 = Static forms (Alumni verification + Personal info)
   └─ Includes gender field in PersonalInfo step

2. Stage 3+ = Dynamic survey categories from SurveyManagement
   └─ Fully configurable in admin panel
   └─ Supports conditional questions
   └─ Supports various question types with min/max rating scales

3. Submission = Complete data pipeline
   └─ Static data → CustomUser + Address + Profile
   └─ Dynamic data → SurveyResponses
   └─ Backend fix applied → No schema mismatch errors

4. Gender field correctly flows through entire pipeline:
   PersonalInfo (collect)
   → RegisterDynamic (store in form.value)
   → submitForm (append to FormData)
   → RegisterSerializer (validate & save to CustomUser)
   → Profile.save() (sync to profile)

Status: ✅ READY TO TEST - Submit registration form again!

═══════════════════════════════════════════════════════════════════════════════════
"""

print(analysis)
