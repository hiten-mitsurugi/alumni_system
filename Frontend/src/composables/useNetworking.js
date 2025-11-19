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
  const formatUserData = (user, additionalData = {}) => {
    // Helper function to get full profile picture URL
    const getProfilePictureUrl = (profilePicture) => {
      if (!profilePicture) {
        return '/default-avatar.png';
      }

      if (profilePicture.startsWith('http')) {
        return profilePicture;
      }

      // Use the backend media server URL (not the API URL)
      const BASE_URL = import.meta.env.VITE_API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:8000`;
      return `${BASE_URL}${profilePicture}`;
    };

    // Ensure we have a valid user ID - this is critical for the unfollow functionality
    const userId = user?.id;
    if (!userId) {
      console.error('❌ No user ID found in user data:', user);
      return null;
    }

    return {
      id: userId,  // Make sure this is the actual user ID, not relationship ID
      name: `${user.first_name || ''} ${user.last_name || ''}`.trim(),
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      headline: user.profile?.headline || user.profile?.present_occupation || 'Alumni',
      present_address: user.present_address || user.profile?.location || user.profile?.present_address || '',
      profile_picture: getProfilePictureUrl(user.profile_picture),
      username: user.username,
      profile: user.profile || {},
      processing: false,
      ...additionalData
    };
  };

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
        // Debug: Log the raw data to see what we're getting
        console.log('🔍 Raw connection data:', connection);

        // IMPORTANT: Extract the actual user data from the response
        // The API can return different structures, so we need to check multiple possible locations
        let userInfo = connection.follower_info || connection.user || connection.follower;

        // If still no user info found, try to extract from the connection object itself
        if (!userInfo && connection.id && connection.first_name) {
          userInfo = connection;
        }

        if (!userInfo) {
          console.error('❌ No user info found in connection:', connection);
          return null;
        }

        console.log('📝 Extracted connection user info:', userInfo);

        const formattedUser = formatUserData(userInfo, {
          mutualConnections: 0 // We can calculate this later if needed
        });
        console.log('✅ Formatted connection:', formattedUser);

        return formattedUser;
      }).filter(Boolean);  // Remove any null entries

      // Process followers
      followers.value = (data.followers || []).map(follower => {
        const isFollowing = data.following?.some(f =>
          f.following?.id === follower.follower?.id
        );

        // Debug: Log the raw data to see what we're getting
        console.log('🔍 Raw follower data:', follower);

        // IMPORTANT: Extract the actual user data from the response
        // The API can return different structures, so we need to check multiple possible locations
        let userInfo = follower.follower_info || follower.user || follower.follower;

        // If still no user info found, try to extract from the follower object itself
        if (!userInfo && follower.id && follower.first_name) {
          userInfo = follower;
        }

        if (!userInfo) {
          console.error('❌ No user info found in:', follower);
          return null;
        }

        console.log('📝 Extracted user info:', userInfo);

        const formattedUser = formatUserData(userInfo, { isFollowing });
        console.log('✅ Formatted follower:', formattedUser);

        return formattedUser;
      }).filter(Boolean);  // Remove any null entries

      // Process following
      following.value = (data.following || []).map(followedUser => {
        // Debug: Log the raw data to see what we're getting
        console.log('🔍 Raw following data:', followedUser);

        // IMPORTANT: Extract the actual user data from the response
        // The API can return different structures, so we need to check multiple possible locations
        let userInfo = followedUser.following_info || followedUser.user || followedUser.following;

        // If still no user info found, try to extract from the followedUser object itself
        if (!userInfo && followedUser.id && followedUser.first_name) {
          userInfo = followedUser;
        }

        if (!userInfo) {
          console.error('❌ No user info found in:', followedUser);
          return null;
        }

        console.log('📝 Extracted user info:', userInfo);

        const formattedUser = formatUserData(userInfo);
        console.log('✅ Formatted user:', formattedUser);

        return formattedUser;
      }).filter(Boolean);  // Remove any null entries

      // Process pending invitations (real data from backend)
      pendingInvitations.value = (data.invitations || []).map(invitation => {
        console.log('🔍 Processing invitation:', invitation);

        // Use detailed follower_info if available, otherwise fallback to follower
        const follower = invitation.follower_info || invitation.user || invitation.follower || {};

        console.log('📝 Extracted follower:', follower);

        // Helper function to get full profile picture URL
        const getProfilePictureUrl = (profilePicture) => {
          if (!profilePicture) {
            return '/default-avatar.png';
          }

          if (profilePicture.startsWith('http')) {
            return profilePicture;
          }

          // Use the backend media server URL (not the API URL)
          const BASE_URL = import.meta.env.VITE_API_BASE_URL || `${window.location.protocol}//${window.location.hostname}:8000`;
          return `${BASE_URL}${profilePicture}`;
        };

        const processedInvitation = {
          id: follower.id || invitation.id, // Use follower ID for user identification
          invitation_id: invitation.id, // Use invitation ID for API calls
          name: `${follower.first_name || ''} ${follower.last_name || ''}`.trim(),
          first_name: follower.first_name || '',
          last_name: follower.last_name || '',
          headline: follower.profile?.headline || follower.profile?.present_occupation || 'Alumni',
          present_address: follower.present_address || follower.profile?.location || follower.profile?.present_address || '',
          profile_picture: getProfilePictureUrl(follower.profile_picture),
          username: follower.username,
          profile: follower.profile || {},
          created_at: invitation.created_at,
          processing: false
        };

        return processedInvitation;
      });

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
  const acceptInvitation = async (invitationId) => {
    console.log('🎯 Attempting to accept invitation ID:', invitationId);

    try {
      const response = await api.post(`/auth/invitations/${invitationId}/accept/`);
      console.log('✅ Invitation accepted successfully:', response.data);

      // Remove from pending invitations
      pendingInvitations.value = pendingInvitations.value.filter(inv =>
        inv.invitation_id !== invitationId && inv.id !== invitationId
      );

      // Refresh the connections data
      await fetchConnections();

      return response.data;
    } catch (error) {
      console.error('❌ Error accepting invitation:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      console.error('Full error object:', error);
      throw error;
    }
  };

  const ignoreInvitation = async (invitationId) => {
    console.log('🎯 Attempting to ignore invitation ID:', invitationId);

    try {
      // Call backend API to reject invitation (using DELETE method)
      const response = await api.delete(`/auth/invitations/${invitationId}/reject/`);
      console.log('✅ Invitation ignored successfully:', response.data);

      // Remove from pending invitations
      pendingInvitations.value = pendingInvitations.value.filter(inv =>
        inv.invitation_id !== invitationId && inv.id !== invitationId
      );

      return response.data;
    } catch (error) {
      console.error('❌ Error ignoring invitation:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      throw error;
    }
  };

  const connectToSuggestion = async (suggestion) => {
    try {
      suggestion.processing = true;

      await api.post(`/auth/follow/${suggestion.id}/`);

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
      await api.delete(`/auth/follow/${connection.id}/`);

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
      await api.post(`/auth/follow/${follower.id}/`);

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

      console.log('🔄 Unfollowing user - DETAILED DEBUG:', {
        user_object: user,
        user_id: user.id,
        user_name: user.name,
        user_keys: Object.keys(user),
        context: context,
        endpoint: `/auth/follow/${user.id}/`,
        full_url: `${import.meta.env.VITE_API_BASE_URL || window.location.origin.replace(window.location.port, '8000')}/api/auth/follow/${user.id}/`
      });

      // Validate user ID exists
      if (!user.id) {
        throw new Error('User ID is missing or invalid');
      }

      // Use DELETE method to unfollow
      const response = await api.delete(`/auth/follow/${user.id}/`);

      console.log('✅ Unfollow response:', response.data);

      if (context === 'following') {
        following.value = following.value.filter(u => u.id !== user.id);
      } else if (context === 'followers') {
        user.isFollowing = false;
      }

      return { success: true, message: `You have unfollowed ${user.name}.` };

    } catch (error) {
      console.error('❌ Error unfollowing user:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      console.error('Full error object:', error);
      throw new Error(`Failed to unfollow user: ${error.response?.data?.error || error.message}`);
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
