# Copilot Instructions for This Project

## System Analysis
This system is a modular alumni management and social platform. It includes:
- Django backend with apps for authentication, posts, messaging, surveys, and alumni directory
- Vue.js frontend with modular components for alumni, admin, posting, messaging, registration, and layouts
- Features: user registration, profile management, posting, commenting, messaging, admin controls, directory management, and dynamic survey integration
- Strict separation of frontend and backend logic

## Coding Instructions for Copilot
1. **Modularization**
   - All code must be modularized. If a file or module exceeds 400 lines, split it into smaller files, modules, or components.
   - For backend (Django/Python), each class (model, view, serializer, etc.) should be defined in its own file whenever possible, similar to the structure in `auth_app`. This makes debugging and maintenance easier.
   - Use clear, descriptive names for new modules/components or class files.

2. **Variable Naming**
   - Do not change existing variable names when making changes or refactoring.
   - Preserve naming conventions and context for all variables and functions.

3. **Change Management**
   - Before making any change, analyze thoroughly:
     - The user's request and intent
     - The code and files affected
     - The impact on related features, functions, and UI/styles
   - Do not affect any features, functions, UI, or styles that are not related to the requested change, in both frontend and backend.
   - Only add what is necessary for the requested change, as a professional expert programmer would.

4. **Best Practices**
   - Use clean, readable, and maintainable code.
   - Follow project conventions for both backend (Django/Python) and frontend (Vue.js/JavaScript).
   - Document new modules/components with concise comments.
   - Prefer composition and separation of concerns.

5. **General Guidance**
   - Treat every change as if you are a professional expert programmer.
   - Always review the context and dependencies before editing.
   - If a change requires new files, create them in the appropriate module or folder.
   - If a change would exceed 400 lines in a file, split the logic into multiple files.

## Additional Instructions

6. **Tailwind and CSS Management**
   - Tailwind CSS is the primary styling framework.
   - If a component has additional scoped CSS, move those styles into a separate CSS file within the component's css folder (e.g., `src/components/css/`).
   - All custom CSS must be placed in the appropriate component css folder, not inside the `.vue` file.
   - Avoid mixing inline styles and scoped CSS in the same file; prefer Tailwind classes and external CSS files for custom styles.

7. **Script Setup Modularization**
   - For Vue components using `<script setup>`, modularize the JavaScript logic as needed.
   - Prefer splitting logic so each function is in its own file (per composable/utility), similar to the backend 'one class per file' rule. This is more professional and maintainable.
   - If the script section becomes large or complex, split logic into composables, utility files, or modules in the appropriate folder (e.g., `src/components/composables/`, `src/components/utils/`).
   - Ensure modularization is correct and maintains functionality, readability, and separation of concerns.

8. **Theme and Component Organization**
   - The theme color for the project is white and green. Use these colors for UI elements and styling.
   - Organize components by feature: each feature should have its own folder in `src/components/`.
   - Do not create redundant or duplicate files. If a file exists and can be reused, use it instead of creating a new one.
   - Do not remove files; if there is a bug, fix it in the existing file. Do not suggest removal or duplication (e.g., do not create `RegisterDynamicClean.vue` if `RegisterDynamic.vue` exists—fix the original).

9. **Realtime and Technology Considerations**
   - Always consider using Redis and WebSocket for realtime features if necessary. Prioritize realtime updates and communication where appropriate.

10. **Prompting and Reporting**
   - Do not give one-by-one instructions. Auto-prompt yourself with a summary list of what to do and what to prompt, not step-by-step instructions.
   - Always provide a summary of actions and compliance when reporting or making changes.
   - Do NOT create a todo list or summary markdown file after refactoring or making changes. If you need the user to take action or check something, provide all prompts in a single, consolidated list—not one by one. For example, if multiple checks or confirmations are needed, present them together as a single list for efficiency.

---

*These instructions are mandatory for all Copilot-assisted code generation and editing in this project.*
