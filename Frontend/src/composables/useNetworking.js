import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import api from '@/services/api';

export function useNetworking() {
  const authStore = useAuthStore();
  
  // Reactive data
  const connections = ref([]);
  const pendingInvitations = ref([]);
  const suggestions = ref([]);
  const followers = ref([]);
  const following = ref([]);
  const loading = ref({
    connections: false,
    suggestions: false,
    invitations: false
  });

  // Stats
  const stats = computed(() => ({
    connectionsCount: connections.value.length,
    followersCount: followers.value.length,
    followingCount: following.value.length
  }));

  // Constants - No longer needed since we use api service
  // const BASE_URL = 'http://127.0.0.1:8000';

  // Helper function to format user data
  const formatUserData = (user, additionalData = {}) => ({
    id: user.id,
    name: `${user.first_name || ''} ${user.last_name || ''}`.trim(),
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    headline: user.profile?.headline || user.profile?.present_occupation || 'Alumni',
    present_address: user.present_address || user.profile?.location || user.profile?.present_address || '',
    profile_picture: user.profile_picture,
    username: user.username,
    profile: user.profile || {},
    processing: false,
    ...additionalData
  });

  // API Functions
  const fetchConnections = async () => {
    try {
      loading.value.connections = true;
      
      const response = await api.get('/auth/connections/', {
        params: { type: 'all' }
      });
      
      const data = response.data;
      
      console.log('📊 Raw connections data:', data);
      
      // Process connections (mutual followers)
      const mutualConnections = data.followers?.filter(f => 
        data.following?.some(fo => {
          const followerId = f.follower_info?.id || f.follower?.id;
          const followingId = fo.following_info?.id || fo.following?.id;
          return followingId === followerId;
        })
      ) || [];
      
      connections.value = mutualConnections.map(connection => {
        const userInfo = connection.follower_info || connection.follower || connection;
        return formatUserData(userInfo, { 
          mutualConnections: 0 // We can calculate this later if needed
        });
      });
      
      // Process followers
      followers.value = (data.followers || []).map(follower => {
        const isFollowing = data.following?.some(f => 
          f.following?.id === follower.follower?.id
        );
        
        // Use detailed follower_info if available, otherwise fallback to follower
        const userInfo = follower.follower_info || follower.follower || follower;
        return formatUserData(userInfo, { isFollowing });
      });
      
      // Process following
      following.value = (data.following || []).map(followedUser => {
        // Use detailed following_info if available, otherwise fallback to following
        const userInfo = followedUser.following_info || followedUser.following || followedUser;
        return formatUserData(userInfo);
      });
      
      // Process pending invitations (real data from backend)
      pendingInvitations.value = (data.invitations || []).map(invitation => {
        // Use detailed follower_info if available, otherwise fallback to follower
        const follower = invitation.follower_info || invitation.follower || {};
        const processedInvitation = {
          id: follower.id || invitation.id, // Use follower ID for user identification
          invitation_id: invitation.id, // Use invitation ID for API calls
          name: `${follower.first_name || ''} ${follower.last_name || ''}`.trim(),
          first_name: follower.first_name || '',
          last_name: follower.last_name || '',
          headline: follower.profile?.headline || follower.profile?.present_occupation || 'Alumni',
          present_address: follower.present_address || follower.profile?.location || follower.profile?.present_address || '',
          profile_picture: follower.profile_picture,
          username: follower.username,
          profile: follower.profile || {},
          created_at: invitation.created_at,
          processing: false
        };
        
        console.log('📨 Processed invitation:', processedInvitation);
        return processedInvitation;
      });
      
      console.log('📨 All invitations:', pendingInvitations.value);
      
      return data;
      
    } catch (error) {
      console.error('Error fetching connections:', error);
      throw new Error('Failed to load network data. Please try again.');
    } finally {
      loading.value.connections = false;
    }
  };

  const fetchSuggestions = async () => {
    try {
      loading.value.suggestions = true;
      
      const response = await api.get('/auth/suggested-connections/');
      
      suggestions.value = (response.data || []).map(suggestion => 
        formatUserData(suggestion, {
          mutualConnections: suggestion.mutual_connections || 0
        })
      );
      
      return response.data;
      
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      throw new Error('Failed to load suggestions. Please try again.');
    } finally {
      loading.value.suggestions = false;
    }
  };

  // Action functions
  const acceptInvitation = async (invitation) => {
    try {
      invitation.processing = true;
      
      console.log('🔄 Accepting invitation:', {
        invitation_id: invitation.invitation_id,
        user_id: invitation.id,
        name: invitation.name
      });
      
      // Call backend API to accept invitation
      const response = await api.post(`/invitations/${invitation.invitation_id}/accept/`);
      
      console.log('✅ Accept invitation response:', response.data);
      
      // Remove from invitations
      pendingInvitations.value = pendingInvitations.value.filter(i => i.id !== invitation.id);
      
      // Add to connections (mutual connection created)
      connections.value.push({
        ...invitation,
        processing: false
      });
      
      // Add to following (you're now following them too due to mutual connection)
      following.value.push({
        ...invitation,
        processing: false
      });
      
      // Add to followers if not already there (they were already following you)
      const existingFollower = followers.value.find(f => f.id === invitation.id);
      if (!existingFollower) {
        followers.value.push({
          ...invitation,
          processing: false,
          isFollowing: true  // Mark as following back
        });
      } else {
        // Update existing follower to show you're following back
        existingFollower.isFollowing = true;
      }
      
      return { success: true, message: response.data.message || `You are now connected with ${invitation.name}!` };
      
    } catch (error) {
      console.error('❌ Error accepting invitation:', error);
      console.error('Error response:', error.response?.data);
      throw new Error(error.response?.data?.error || 'Failed to accept invitation. Please try again.');
    } finally {
      invitation.processing = false;
    }
  };

  const ignoreInvitation = async (invitation) => {
    try {
      invitation.processing = true;
      
      // Call backend API to reject invitation (using POST method)
      const response = await api.post(`/invitations/${invitation.invitation_id}/reject/`);
      
      pendingInvitations.value = pendingInvitations.value.filter(i => i.id !== invitation.id);
      
      return { success: true, message: response.data.message || 'Invitation ignored.' };
      
    } catch (error) {
      console.error('Error ignoring invitation:', error);
      throw new Error(error.response?.data?.error || 'Failed to ignore invitation. Please try again.');
    } finally {
      invitation.processing = false;
    }
  };

  const connectToSuggestion = async (suggestion) => {
    try {
      suggestion.processing = true;
      
      await api.post(`/follow/${suggestion.id}/`);
      
      // Remove from suggestions (connection request sent)
      suggestions.value = suggestions.value.filter(s => s.id !== suggestion.id);
      
      // Note: Don't add to following yet - wait for them to accept
      // Connection will be mutual only after acceptance
      
      return { success: true, message: `Connection request sent to ${suggestion.name}!` };
      
    } catch (error) {
      console.error('Error connecting to suggestion:', error);
      throw new Error('Failed to send connection request. Please try again.');
    } finally {
      suggestion.processing = false;
    }
  };

  const removeConnection = async (connection) => {
    try {
      connection.processing = true;
      
      // Call API to disconnect (removes mutual connection)
      await api.delete(`/follow/${connection.id}/`);
      
      // Remove from connections
      connections.value = connections.value.filter(c => c.id !== connection.id);
      
      // Remove from following (no longer following them)
      following.value = following.value.filter(f => f.id !== connection.id);
      
      // Update followers list - they're no longer following you either
      followers.value = followers.value.filter(f => f.id !== connection.id);
      
      return { success: true, message: `${connection.name} has been removed from your connections.` };
      
    } catch (error) {
      console.error('Error removing connection:', error);
      throw new Error('Failed to remove connection. Please try again.');
    } finally {
      connection.processing = false;
    }
  };

  const followBack = async (follower) => {
    try {
      follower.processing = true;
      
      // Send connection request (will create mutual connection when accepted)
      await api.post(`/follow/${follower.id}/`);
      
      // Note: In LinkedIn-style, this would send a connection request
      // For immediate mutual connection, we could create a different endpoint
      // For now, keeping consistent with the invitation flow
      
      follower.isFollowing = true;
      
      return { success: true, message: `Connection request sent to ${follower.name}!` };
      
    } catch (error) {
      console.error('Error following back:', error);
      throw new Error('Failed to send connection request. Please try again.');
    } finally {
      follower.processing = false;
    }
  };

  const unfollowUser = async (user, context = 'following') => {
    try {
      user.processing = true;
      
      // Use DELETE method to unfollow
      await api.delete(`/follow/${user.id}/`);
      
      if (context === 'following') {
        following.value = following.value.filter(u => u.id !== user.id);
      } else if (context === 'followers') {
        user.isFollowing = false;
      }
      
      return { success: true, message: `You have unfollowed ${user.name}.` };
      
    } catch (error) {
      console.error('Error unfollowing user:', error);
      throw new Error('Failed to unfollow user. Please try again.');
    } finally {
      user.processing = false;
    }
  };

  // Utility functions
  const refreshAllData = async () => {
    try {
      await Promise.all([
        fetchConnections(),
        fetchSuggestions()
      ]);
      // Invitations are now loaded as part of fetchConnections()
    } catch (error) {
      console.error('Error refreshing network data:', error);
      throw new Error('Failed to refresh network data.');
    }
  };

  return {
    // Reactive data
    connections,
    pendingInvitations,
    suggestions,
    followers,
    following,
    loading,
    stats,
    
    // API functions
    fetchConnections,
    fetchSuggestions,
    refreshAllData,
    
    // Action functions
    acceptInvitation,
    ignoreInvitation,
    connectToSuggestion,
    removeConnection,
    followBack,
    unfollowUser,
    
    // Utility functions
    formatUserData
  };
}
