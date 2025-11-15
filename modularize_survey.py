"""
Modularize SurveyManagement.vue by replacing inline modals with component tags
"""

filepath = r"c:\Users\USER\OneDrive\Desktop\Thesis\development\alumni_system\Frontend\src\views\SuperAdmin\SurveyManagement.vue"

# Read the file
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add component imports
old_imports = """import surveyService from '@/services/surveyService'
import { useThemeStore } from '@/stores/theme'
import CategoryAnalytics from '@/components/CategoryAnalytics.vue'"""

new_imports = """import surveyService from '@/services/surveyService'
import { useThemeStore } from '@/stores/theme'
import CategoryAnalytics from '@/components/CategoryAnalytics.vue'
import CategoryModal from '@/components/SurveyManagement/CategoryModal.vue'
import QuestionModal from '@/components/SurveyManagement/QuestionModal.vue'
import ExportModal from '@/components/SurveyManagement/ExportModal.vue'
import CategoryQuestionsModal from '@/components/SurveyManagement/CategoryQuestionsModal.vue'"""

content = content.replace(old_imports, new_imports)

# 2. Replace Category Modal (lines ~1340-1458)
category_modal_start = "    <!-- Modals Container -->"
category_modal_end = "    <!-- Question Modal -->"

start_idx = content.find(category_modal_start)
end_idx = content.find(category_modal_end)

if start_idx != -1 and end_idx != -1:
    category_replacement = """    <!-- Category Modal -->
    <CategoryModal
      v-if="showCategoryModal"
      :category="categoryForm.id ? categoryForm : null"
      :categories-length="categories.length"
      :is-dragging="isDragging"
      :dragged-modal="draggedModal"
      :modal-position="modalPositions.category"
      @close="showCategoryModal = false"
      @save="loadCategories"
      @start-drag="startDrag"
      @reset-position="resetModalPosition"
    />

    <!-- Question Modal -->"""
    content = content[:start_idx] + category_replacement + content[end_idx + len(category_modal_end):]
    print(f"✅ Replaced Category modal")

# 3. Replace Question Modal (find the massive form block)
question_modal_end = "    <!-- Analytics Modal -->"
start_idx = content.find("    <!-- Question Modal -->")
end_idx = content.find(question_modal_end)

if start_idx != -1 and end_idx != -1:
    question_replacement = """    <!-- Question Modal -->
    <QuestionModal
      v-if="showQuestionModal"
      :question="questionForm.id ? questionForm : null"
      :selected-category-id="selectedCategoryId"
      :categories="categories"
      :questions="questions"
      :questions-length="questions.length"
      :is-dragging="isDragging"
      :dragged-modal="draggedModal"
      :modal-position="modalPositions.question"
      @close="showQuestionModal = false"
      @save="saveQuestion"
      @start-drag="startDrag"
      @reset-position="resetModalPosition"
    />

    <!-- Analytics Modal -->"""
    content = content[:start_idx] + question_replacement + content[end_idx + len(question_modal_end):]
    print(f"✅ Replaced Question modal")

# 4. Replace Export Modal
export_modal_end = "    <!-- Category Questions Modal -->"
start_idx = content.find("    <!-- Export Modal -->")
end_idx = content.find(export_modal_end)

if start_idx != -1 and end_idx != -1:
    export_replacement = """    <!-- Export Modal -->
    <ExportModal
      v-if="showExportModal"
      :categories="categories"
      :is-dragging="isDragging"
      :dragged-modal="draggedModal"
      :modal-position="modalPositions.export"
      @close="showExportModal = false"
      @start-drag="startDrag"
      @reset-position="resetModalPosition"
    />

    <!-- Category Questions Modal -->"""
    content = content[:start_idx] + export_replacement + content[end_idx + len(export_modal_end):]
    print(f"✅ Replaced Export modal")

# 5. Replace CategoryQuestions Modal
# Find the last closing tags before </template>
catq_start = content.find("    <!-- Category Questions Modal -->")
template_end = content.find("</template>")

if catq_start != -1 and template_end != -1:
    # Find the last </div> before </template>
    catq_section = content[catq_start:template_end]
    # Count divs to find where modal ends
    catq_replacement = """    <!-- Category Questions Modal -->
    <CategoryQuestionsModal
      v-if="showCategoryQuestionsModal"
      :category="selectedCategoryForModal"
      :questions="categoryQuestions"
      :is-dragging="isDragging"
      :dragged-modal="draggedModal"
      :modal-position="modalPositions.categoryQuestions"
      @close="showCategoryQuestionsModal = false"
      @edit-question="openQuestionModal"
      @delete-question="deleteQuestion"
      @start-drag="startDrag"
      @reset-position="resetModalPosition"
    />

  </template>"""
    content = content[:catq_start] + catq_replacement
    print(f"✅ Replaced CategoryQuestions modal")

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

# Count lines
lines = content.count('\n')
print(f"\n📊 Final file has {lines} lines (originally ~2254 lines)")
print(f"✨ Saved ~{2254 - lines} lines!")
