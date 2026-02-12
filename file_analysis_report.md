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



---

## C. Files with >600 Lines
These code/text files are large and may need inspection or refactoring:





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