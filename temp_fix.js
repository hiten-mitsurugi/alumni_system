// Temporary fix to update WebSocket handler
// This is the correct updatePostReaction function

const updatePostReaction = async (data) => {
  console.log('🔔 Updating post reaction:', data);
  
  // Find the post and update its reaction data
  const postIndex = posts.value.findIndex(p => p.id === data.post_id);
  if (postIndex !== -1) {
    console.log(`📡 WebSocket reaction update for post ${data.post_id}: ${data.action} ${data.reaction_type}`);
    
    // Only update selectedReaction if this is the current user's reaction
    if (data.user_id === authStore.user?.id) {
      if (data.action === 'removed') {
        selectedReaction.value[data.post_id] = null;
        console.log(`🧹 WebSocket: Cleared reaction state for post ${data.post_id}`);
      } else {
        selectedReaction.value[data.post_id] = data.reaction_type;
        console.log(`🎯 WebSocket: Set reaction for post ${data.post_id} to ${data.reaction_type}`);
      }
    }
    
    // Now fetch updated posts to get accurate reaction summaries from backend
    await fetchPosts();
    console.log(`🔄 WebSocket: Refreshed posts after reaction ${data.action}`);
  }
};