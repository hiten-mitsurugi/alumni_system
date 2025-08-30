# FILES TO DELETE/REMOVE FROM PROJECT
# Analysis completed on: August 30, 2025

## 🗂️ **MAIN ROOT DIRECTORY**

### ❌ **Documentation Files (Safe to Delete)**
- `ADVANCED_MESSAGING_FEATURES.md` - Development documentation
- `DYNAMIC_SURVEY_INTEGRATION.md` - Development documentation  
- `INTEGRATION_COMPLETE.md` - Development documentation
- `SECURITY_IMPROVEMENTS.md` - Development documentation
- `req.txt` - Informal installation notes (has secrets!)

### ❌ **Sample Data Files (Safe to Delete)**
- `sample_alumni.csv` - Test data
- `sample_alumni.txt` - Test data
- `sample_alumni.xlsx` - Test data

### ❌ **Misc Development Files**
- `views` - Old/backup views file (not in proper directory structure)

## 🔧 **BACKEND DIRECTORY**

### ❌ **Development/Debug Scripts (Safe to Delete)**
- `check_usernames.py` - User debugging script
- `check_users.py` - User debugging script
- `debug_jwt.py` - JWT debugging script
- `debug_query.py` - Query debugging script
- `debug_users.py` - User debugging script
- `debug_users_simple.py` - Simple user debugging script

### ❌ **Test Scripts (Safe to Delete)**
- `test_api.py` - API testing script
- `test_api_direct.py` - Direct API testing script
- `test_endpoint.py` - Endpoint testing script
- `test_group_unread.py` - Group unread testing script
- `test_login_comprehensive.py` - Login testing script
- `test_login_fix.py` - Login fix testing script
- `test_new_reactions.py` - Reactions testing script
- `test_posts_api.py` - Posts API testing script
- `test_posts_quick.py` - Quick posts testing script
- `test_real_login.py` - Real login testing script
- `test_status_broadcast.py` - Status broadcast testing script
- `test_status_debug.py` - Status debugging script
- `test_status_realtime.py` - Real-time status testing script
- `test_status_system.py` - Status system testing script
- `test_survey_api.py` - Survey API testing script
- `test_user_blocking.py` - User blocking testing script
- `test_user_management.py` - User management testing script
- `test_view_logic.py` - View logic testing script

### ❌ **Data Creation Scripts (Safe to Delete)**
- `create_sample_posts.py` - Sample posts creation script
- `create_test_alumni.py` - Test alumni creation script

### ❌ **Fix/Migration Scripts (Safe to Delete)**
- `fix_emoji_display.py` - Emoji display fix script
- `fix_models_encoding.py` - Models encoding fix script

### ❌ **Documentation Files**
- `ADMIN_ACCOUNTS_README.md` - Admin accounts documentation
- `AUTHENTICATION_FIXED.md` - Authentication fix documentation

### ❌ **Log Files**
- `debug.log` - Debug log file

### ⚠️ **SECURITY RISK FILES (URGENT - REMOVE)**
- `secret key` - Contains Django secret key in plain text!
- `.env.sqlite` - May contain sensitive environment variables

## 🎨 **FRONTEND DIRECTORY**

### ❌ **Development Files (Safe to Delete)**
- `clear-auth.html` - Development utility file
- `extra` - Contains old Vue component code (backup file)

### ❌ **Build Output (Can Regenerate)**
- `dist/` - Build output directory (can be regenerated with npm run build)

### ⚠️ **Consider Keeping**
- `.vscode/` - VS Code settings (keep if using VS Code)
- `node_modules/` - Dependencies (can regenerate with npm install)

## 📊 **SUMMARY**

### 🚨 **HIGH PRIORITY (Security Risk)**
1. `Backend/secret key` - CONTAINS DJANGO SECRET KEY
2. `Backend/.env.sqlite` - May contain sensitive data
3. `req.txt` - Contains Django secret key in plain text

### 🗑️ **Safe to Delete (Development Files)**
- **25 test scripts** in Backend/
- **6 debug scripts** in Backend/
- **4 documentation markdown files** in root
- **3 sample data files** in root
- **2 creation scripts** in Backend/
- **2 fix scripts** in Backend/
- **1 log file** in Backend/
- **2 frontend development files**

### 💾 **Total Space Savings**
Estimated: **50+ files** can be safely removed

### ✅ **Files to KEEP**
- All core application files (models, views, serializers, etc.)
- `requirements.txt` (Backend dependencies)
- `package.json` (Frontend dependencies)
- `.env` files (if properly secured)
- `manage.py`
- All app directories (auth_app/, messaging_app/, etc.)
- Frontend src/ and public/ directories
- All migration files

## 🛠️ **RECOMMENDED ACTIONS**

1. **IMMEDIATELY** move `secret key` and `.env.sqlite` to secure location or delete
2. Delete all test_* and debug_* files
3. Delete documentation .md files from root
4. Delete sample data files
5. Add sensitive files to .gitignore
6. Consider setting up proper environment variable management

## ⚠️ **BEFORE DELETING**
1. Backup the entire project
2. Ensure no production dependencies on test files
3. Test the application after cleanup
4. Update .gitignore to prevent future uploads of sensitive files
