# File Analysis Report

## A. Low-risk / Non-essential Files & Folders
These files and folders are safe to remove from the repository to reduce noise and size:

- `env/` (local Python virtualenv)
- `scan result.txt`
- `Frontend/public/sample_alumni.csv`
- `Frontend/public/sample_alumni.txt`
- `Frontend/public/sample_alumni.xlsx`

---

## B. Redundant / Backup / Duplicate Candidates
Inspect these files and delete if confirmed redundant:

- `Backend/survey_app/views_backup_20251119_170049.py`
- `Backend/survey_app/views_original.py`
- `Backend/survey_app/views/export_views_backup_20251119_175708.py`
- `Backend/auth_app/views_original_backup.py`
- `Backend/auth_app/views.py` (only delete/replace if you have a verified newer copy)
- `Backend/messaging_app/consumers_backup.py` (empty/backup)
- `Backend/messaging_app/consumers_clean.py` (empty/backup)
- Any file matching patterns: `*backup*`, `*.backup`, `*_original*`, `*_old*`, `*copy*`, `*_2025*` (timestamped backups) — review and remove duplicates you no longer need
- Local/debug HTML or test pages in `Frontend/public/` (e.g., `test-achievement.html`) — remove if unused

---

## C. Files with >600 Lines
These code/text files are large and may need inspection or refactoring:

- `Backend/survey_app/views_original.py` — 2743 lines
- `Backend/survey_app/views_backup_20251119_170049.py` — 2743 lines
- `Backend/messaging_app/views.py` — 2383 lines
- `Backend/auth_app/views.py` — 2049 lines
- `Backend/auth_app/views_original_backup.py` — 2042 lines
- `Backend/messaging_app/consumers.py` — 1909 lines
- `Backend/posts_app/views.py` — 1409 lines
- `Backend/survey_app/views/export_views_backup_20251119_175708.py` — 1213 lines
- `Backend/auth_app/serializers.py` — 1149 lines
- `Backend/survey_app/views/export/pdf_form.py` — 679 lines
- `Backend/survey_app/management/commands/populate_from_tracer.py` — 726 lines


- `Frontend/src/views/Alumni/Messaging.vue` — 3187 lines
- `Frontend/src/components/posting/PostModal.vue` — 1019 lines
- `Frontend/src/views/Alumni/AlumniHome.vue` — 1065 lines
- `Frontend/src/components/alumnidirectory/AlumniDirectoryTable.vue` — 978 lines
- `Frontend/src/components/SurveyManagement/ResponsesView.vue` — 956 lines
- `Frontend/src/views/Admin/ContentPage.vue` — 904 lines
- `Frontend/src/views/Alumni/AlumniSurvey.vue` — 675 lines
- `Frontend/src/components/modals/AnalyticsModal.vue` — 718 lines
- `Frontend/src/components/alumni/AlumniNavbar.vue` — 714 lines
- `Frontend/src/components/alumni/messaging/ChatArea.vue` — 709 lines
- `Frontend/src/components/SurveyManagement/FormEditor.vue` — 706 lines
- `Frontend/src/components/modals/QuestionModal.vue` — 687 lines


---

## D. Very Large Media Files
These are not code files but large media files. Delete to free space if uploads are not needed:

- `Backend/media/attachments/PSC-X-Clearance.pdf` — very large (~120k lines in wc output)
- Several large items under `Backend/media/post_media/` (videos/images, some ~47k lines)
- Many `Backend/media/profile_pictures/`, `government_ids/`, `cover_photos/`, `attachments/` image/pdf files listed in repo — remove the `Backend/media/` uploads if you do not need stored uploaded content.

---

### Notes
- Before deleting any backup or original file, inspect to ensure it is truly a duplicate and not the active source.
- For migrations, `__init__.py` and migration files should be kept.
- If you want to automate deletion, consider creating a script to move files to a `recycle/` folder first for review.