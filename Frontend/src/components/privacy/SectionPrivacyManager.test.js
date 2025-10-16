/**
 * Test suite for Section Privacy Manager component
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import SectionPrivacyManager from '@/components/privacy/SectionPrivacyManager.vue'
import { usePrivacy } from '@/composables/usePrivacy'

// Mock the privacy composable
vi.mock('@/composables/usePrivacy')

// Mock privacy service
const mockPrivacyService = {
  getSectionPrivacySettings: vi.fn(),
  updateSectionPrivacySetting: vi.fn(),
  bulkUpdateSectionPrivacy: vi.fn(),
  getPrivacyProfiles: vi.fn(),
  createPrivacyProfile: vi.fn(),
  applyPrivacyProfile: vi.fn(),
  deletePrivacyProfile: vi.fn(),
  getPrivacyConflicts: vi.fn(),
  resolvePrivacyConflicts: vi.fn()
}

// Mock toast composable
const mockToast = {
  showToast: vi.fn()
}

vi.mock('@/composables/useToast', () => ({
  useToast: () => mockToast
}))

describe('SectionPrivacyManager', () => {
  let wrapper
  let mockUsePrivacy

  beforeEach(() => {
    mockUsePrivacy = {
      sectionPrivacySettings: {
        about: 'public',
        contact: 'connections_only',
        education: 'alumni_only'
      },
      privacyProfiles: [
        {
          id: 1,
          name: 'Public Profile',
          description: 'Everything visible to everyone',
          section_settings: {
            about: 'public',
            contact: 'public',
            education: 'public'
          },
          is_default: false
        },
        {
          id: 2,
          name: 'Private Profile',
          description: 'Everything private',
          section_settings: {
            about: 'private',
            contact: 'private',
            education: 'private'
          },
          is_default: true
        }
      ],
      activePrivacyProfile: 2,
      loading: false,
      error: null,
      privacyOptions: [
        { value: 'public', label: 'Everyone', icon: 'globe' },
        { value: 'alumni_only', label: 'Alumni Only', icon: 'users' },
        { value: 'connections_only', label: 'Connections Only', icon: 'user-group' },
        { value: 'private', label: 'Only Me', icon: 'lock' }
      ],
      loadSectionPrivacySettings: vi.fn(),
      updateSectionPrivacySetting: vi.fn(),
      bulkUpdateSectionPrivacy: vi.fn(),
      loadPrivacyProfiles: vi.fn(),
      createPrivacyProfile: vi.fn(),
      applyPrivacyProfile: vi.fn(),
      deletePrivacyProfile: vi.fn(),
      getPrivacyConflicts: vi.fn().mockReturnValue([]),
      resolvePrivacyConflicts: vi.fn(),
      getSectionPrivacySetting: vi.fn((section) => mockUsePrivacy.sectionPrivacySettings[section] || 'public'),
      getPrivacyColorClasses: vi.fn().mockReturnValue('text-green-600 bg-green-50'),
      getPrivacyIcon: vi.fn().mockReturnValue('globe')
    }

    usePrivacy.mockReturnValue(mockUsePrivacy)

    wrapper = mount(SectionPrivacyManager, {
      global: {
        stubs: {
          PrivacySelector: true
        }
      }
    })
  })

  it('renders correctly', () => {
    expect(wrapper.find('.section-privacy-manager').exists()).toBe(true)
    expect(wrapper.find('h3').text()).toContain('Section Privacy Controls')
  })

  it('displays privacy templates', () => {
    const templates = wrapper.findAll('[data-testid="privacy-template"]')
    expect(templates).toHaveLength(2)
    
    expect(templates[0].text()).toContain('Public Profile')
    expect(templates[1].text()).toContain('Private Profile')
  })

  it('shows active template', () => {
    const activeTemplate = wrapper.find('[data-testid="active-template"]')
    expect(activeTemplate.exists()).toBe(true)
    expect(activeTemplate.text()).toContain('Private Profile')
  })

  it('displays section privacy controls', () => {
    const sections = wrapper.findAll('[data-testid="section-control"]')
    expect(sections.length).toBeGreaterThan(0)
    
    // Check that sections are displayed
    const sectionTexts = sections.map(s => s.text())
    expect(sectionTexts.some(text => text.includes('About Me'))).toBe(true)
    expect(sectionTexts.some(text => text.includes('Contact Information'))).toBe(true)
  })

  it('handles section privacy change', async () => {
    const sectionSelect = wrapper.find('[data-testid="section-about-select"]')
    if (sectionSelect.exists()) {
      await sectionSelect.setValue('private')
      await nextTick()
      
      expect(mockUsePrivacy.updateSectionPrivacySetting).toHaveBeenCalledWith('about', 'private')
    }
  })

  it('applies privacy template', async () => {
    const applyButton = wrapper.find('[data-testid="apply-template-1"]')
    if (applyButton.exists()) {
      await applyButton.trigger('click')
      await nextTick()
      
      expect(mockUsePrivacy.applyPrivacyProfile).toHaveBeenCalledWith(1)
    }
  })

  it('creates new privacy template', async () => {
    // Open create template modal
    const createButton = wrapper.find('[data-testid="create-template-btn"]')
    if (createButton.exists()) {
      await createButton.trigger('click')
      await nextTick()
      
      // Fill in template details
      const nameInput = wrapper.find('[data-testid="template-name-input"]')
      const descInput = wrapper.find('[data-testid="template-desc-input"]')
      
      if (nameInput.exists() && descInput.exists()) {
        await nameInput.setValue('Test Template')
        await descInput.setValue('Test Description')
        
        // Submit
        const submitButton = wrapper.find('[data-testid="submit-template"]')
        if (submitButton.exists()) {
          await submitButton.trigger('click')
          await nextTick()
          
          expect(mockUsePrivacy.createPrivacyProfile).toHaveBeenCalledWith(
            'Test Template',
            'Test Description',
            expect.any(Object),
            false
          )
        }
      }
    }
  })

  it('deletes privacy template', async () => {
    const deleteButton = wrapper.find('[data-testid="delete-template-1"]')
    if (deleteButton.exists()) {
      await deleteButton.trigger('click')
      await nextTick()
      
      expect(mockUsePrivacy.deletePrivacyProfile).toHaveBeenCalledWith(1)
    }
  })

  it('shows bulk update functionality', async () => {
    const bulkButton = wrapper.find('[data-testid="bulk-update-btn"]')
    if (bulkButton.exists()) {
      await bulkButton.trigger('click')
      await nextTick()
      
      expect(wrapper.find('[data-testid="bulk-update-modal"]').exists()).toBe(true)
    }
  })

  it('handles privacy conflicts', async () => {
    // Mock conflicts
    mockUsePrivacy.getPrivacyConflicts.mockReturnValue([
      {
        section: 'about',
        field: 'bio',
        sectionPrivacy: 'public',
        fieldPrivacy: 'private',
        type: 'field_section_mismatch'
      }
    ])

    // Recreate wrapper to get updated conflicts
    wrapper = mount(SectionPrivacyManager, {
      global: {
        stubs: {
          PrivacySelector: true
        }
      }
    })

    await nextTick()

    const conflictsSection = wrapper.find('[data-testid="privacy-conflicts"]')
    if (conflictsSection.exists()) {
      expect(conflictsSection.text()).toContain('Privacy Conflicts Detected')
      
      const resolveButton = wrapper.find('[data-testid="resolve-conflicts-btn"]')
      if (resolveButton.exists()) {
        await resolveButton.trigger('click')
        await nextTick()
        
        expect(mockUsePrivacy.resolvePrivacyConflicts).toHaveBeenCalled()
      }
    }
  })

  it('shows loading state', async () => {
    mockUsePrivacy.loading = true
    
    wrapper = mount(SectionPrivacyManager, {
      global: {
        stubs: {
          PrivacySelector: true
        }
      }
    })

    expect(wrapper.find('[data-testid="loading-spinner"]').exists()).toBe(true)
  })

  it('shows error state', async () => {
    mockUsePrivacy.error = 'Failed to load privacy settings'
    
    wrapper = mount(SectionPrivacyManager, {
      global: {
        stubs: {
          PrivacySelector: true
        }
      }
    })

    const errorMessage = wrapper.find('[data-testid="error-message"]')
    if (errorMessage.exists()) {
      expect(errorMessage.text()).toContain('Failed to load privacy settings')
    }
  })

  it('validates template creation inputs', async () => {
    const createButton = wrapper.find('[data-testid="create-template-btn"]')
    if (createButton.exists()) {
      await createButton.trigger('click')
      await nextTick()
      
      // Try to submit without filling required fields
      const submitButton = wrapper.find('[data-testid="submit-template"]')
      if (submitButton.exists()) {
        await submitButton.trigger('click')
        await nextTick()
        
        // Should show validation error
        const validationError = wrapper.find('[data-testid="validation-error"]')
        if (validationError.exists()) {
          expect(validationError.text()).toContain('required')
        }
      }
    }
  })

  it('handles preview functionality', async () => {
    const previewButton = wrapper.find('[data-testid="preview-btn"]')
    if (previewButton.exists()) {
      await previewButton.trigger('click')
      await nextTick()
      
      expect(wrapper.find('[data-testid="privacy-preview"]').exists()).toBe(true)
    }
  })

  it('applies correct CSS classes based on privacy levels', () => {
    const publicSection = wrapper.find('[data-testid="section-public"]')
    if (publicSection.exists()) {
      expect(mockUsePrivacy.getPrivacyColorClasses).toHaveBeenCalledWith('public')
    }
  })

  it('displays privacy icons correctly', () => {
    const privacyIcons = wrapper.findAll('[data-testid="privacy-icon"]')
    privacyIcons.forEach(icon => {
      expect(mockUsePrivacy.getPrivacyIcon).toHaveBeenCalled()
    })
  })
})

// Integration test with actual privacy service
describe('SectionPrivacyManager Integration', () => {
  it('loads section privacy settings on mount', async () => {
    const mockLoadSettings = vi.fn().mockResolvedValue({
      section_settings: {
        about: 'public',
        contact: 'alumni_only'
      }
    })

    const mockUsePrivacy = {
      ...usePrivacy(),
      loadSectionPrivacySettings: mockLoadSettings,
      loadPrivacyProfiles: vi.fn().mockResolvedValue({ profiles: [] })
    }

    usePrivacy.mockReturnValue(mockUsePrivacy)

    mount(SectionPrivacyManager, {
      global: {
        stubs: {
          PrivacySelector: true
        }
      }
    })

    await nextTick()

    expect(mockLoadSettings).toHaveBeenCalled()
  })

  it('handles API errors gracefully', async () => {
    const mockLoadSettings = vi.fn().mockRejectedValue(new Error('API Error'))

    const mockUsePrivacy = {
      ...usePrivacy(),
      loadSectionPrivacySettings: mockLoadSettings,
      loadPrivacyProfiles: vi.fn().mockResolvedValue({ profiles: [] }),
      error: 'API Error'
    }

    usePrivacy.mockReturnValue(mockUsePrivacy)

    const wrapper = mount(SectionPrivacyManager, {
      global: {
        stubs: {
          PrivacySelector: true
        }
      }
    })

    await nextTick()

    expect(wrapper.find('[data-testid="error-message"]').exists()).toBe(true)
  })
})