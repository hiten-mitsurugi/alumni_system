import api from '@/services/api'

/**
 * Generic CRUD operations for entity endpoints
 * @param {string} endpoint - The API endpoint (e.g., 'education', 'work-history')
 * @returns {object} CRUD operation functions
 */
export function useEntityCrud(endpoint) {
  /**
   * Create a new entity
   */
  const create = async (data) => {
    console.log(`📤 useEntityCrud: Creating ${endpoint}`, { data })
    const response = await api.post(`/auth/${endpoint}/`, data)
    console.log(`✅ useEntityCrud: Created ${endpoint} successfully`, { 
      response: response.data 
    })
    return response.data
  }

  /**
   * Update an existing entity
   */
  const update = async (id, data) => {
    console.log(`📝 useEntityCrud: Updating ${endpoint} #${id}`, { data })
    const response = await api.put(`/auth/${endpoint}/${id}/`, data)
    console.log(`✅ useEntityCrud: Updated ${endpoint} #${id} successfully`, { 
      response: response.data 
    })
    return response.data
  }

  /**
   * Delete an entity
   */
  const remove = async (id) => {
    const response = await api.delete(`/auth/${endpoint}/${id}/`)
    return response.data
  }

  return {
    create,
    update,
    remove
  }
}
