/**
 * Centralized utility for constructing image URLs
 * Handles absolute and relative URLs consistently across the application
 */

/**
 * Get the backend base URL from environment or auto-detect
 * @returns {string} Base URL without trailing slash
 */
export function getBackendBaseURL() {
  // Check environment variable first
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL.replace(/\/+$/, ''); // Remove trailing slash
  }
  
  // Fallback: auto-detect based on current location
  const { protocol, hostname } = window.location;
  return `${protocol}//${hostname}:8000`;
}

/**
 * Construct full image URL from relative or absolute path
 * @param {string|null|undefined} imagePath - Image path from backend
 * @param {string} fallback - Fallback image (default: '/default-avatar.png')
 * @returns {string} Full image URL or fallback
 */
export function getImageUrl(imagePath, fallback = '/default-avatar.png') {
  // Handle null, undefined, empty string, or 'null' string
  if (!imagePath || imagePath === '' || imagePath === 'null') {
    return fallback;
  }
  
  // Already absolute URL (starts with http:// or https://)
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }
  
  // Relative path - prepend backend base URL
  const baseUrl = getBackendBaseURL();
  const path = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;
  return `${baseUrl}${path}`;
}

/**
 * Get profile picture URL with fallback
 * @param {string|null|undefined} profilePicture - Profile picture path
 * @returns {string} Full profile picture URL
 */
export function getProfilePictureUrl(profilePicture) {
  return getImageUrl(profilePicture, '/default-avatar.png');
}

/**
 * Get cover photo URL with fallback
 * @param {string|null|undefined} coverPhoto - Cover photo path
 * @returns {string|null} Full cover photo URL or null if not present
 */
export function getCoverPhotoUrl(coverPhoto) {
  if (!coverPhoto || coverPhoto === '' || coverPhoto === 'null') {
    return null; // No fallback for cover photos
  }
  return getImageUrl(coverPhoto, null);
}

/**
 * Get media file URL (for posts, attachments, etc.)
 * @param {string|null|undefined} mediaPath - Media file path
 * @returns {string|null} Full media URL or null
 */
export function getMediaUrl(mediaPath) {
  if (!mediaPath || mediaPath === '' || mediaPath === 'null') {
    return null;
  }
  return getImageUrl(mediaPath, null);
}

/**
 * Construct WebSocket URL from base URL
 * @returns {string} WebSocket base URL
 */
export function getWebSocketBaseURL() {
  const baseUrl = getBackendBaseURL();
  return baseUrl.replace('http://', 'ws://').replace('https://', 'wss://');
}
