import api from './api'

export const postsService = {
  // Post feed
  async getPosts(params = {}) {
    const response = await api.get('/posts/', { params })
    return response.data
  },

  // Get single post
  async getPost(postId) {
    const response = await api.get(`/posts/${postId}/`)
    return response.data
  },

  // Create post
  async createPost(postData) {
    const response = await api.post('/posts/create/', postData)
    return response.data
  },

  // Post reactions
  async reactToPost(postId, reactionType) {
    const response = await api.post(`/posts/${postId}/react/`, {
      reaction_type: reactionType
    })
    return response.data
  },

  async removeReaction(postId) {
    const response = await api.delete(`/posts/${postId}/react/`)
    return response.data
  },

  async getPostReactions(postId) {
    const response = await api.get(`/posts/${postId}/reactions/`)
    return response.data
  },

  // Comments
  async getComments(postId) {
    const response = await api.get(`/posts/${postId}/comments/`)
    return response.data
  },

  async addComment(postId, content, parentId = null) {
    const response = await api.post(`/posts/${postId}/comment/`, {
      content,
      parent_id: parentId
    })
    return response.data
  },

  // Share post
  async sharePost(postId, sharedText = '') {
    const response = await api.post(`/posts/${postId}/share/`, {
      shared_text: sharedText
    })
    return response.data
  },

  // Save/bookmark post
  async savePost(postId) {
    const response = await api.post(`/posts/${postId}/save/`)
    return response.data
  },

  async unsavePost(postId) {
    const response = await api.delete(`/posts/${postId}/save/`)
    return response.data
  },

  // Post management
  async deletePost(postId) {
    console.log('🗑️ Deleting post via API:', postId);
    const response = await api.delete(`/posts/posts/${postId}/delete/`)
    console.log('✅ Post delete response:', response.data);
    return response.data
  },

  async pinPost(postId) {
    const response = await api.post(`/posts/posts/${postId}/pin/`)
    return response.data
  }
}
