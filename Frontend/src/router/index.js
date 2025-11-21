import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useUiStore } from '../stores/ui';

const routes = [
  // 🔓 Public Routes
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterDynamic.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/ForgotPassword.vue'),
    meta: { requiresGuest: true },
  },
  // 🔓 Public Survey Route (for sharing with alumni)
  {
    path: '/survey/:slug',
    name: 'PublicSurvey',
    component: () => import('../views/Alumni/Survey.vue'),
    meta: { public: true },
  },
  // 🎓 Alumni Welcome/Intro (shown once after first login)
  {
    path: '/alumni-intro',
    name: 'AlumniIntro',
    component: () => import('../views/Alumni/AlumniIntro.vue'),
    meta: { requiresAuth: true, role: 3, skipIntroCheck: true },
  },

  // 🛡 Super Admin Routes
  {
    path: '/super-admin',
    component: () => import('@/components/layouts/SuperAdminLayout.vue'),
    meta: { requiresAuth: true, role: 1 },
    children: [
      {
        path: '',
        name: 'SuperAdminDashboard',
        component: () => import('../views/SuperAdmin/Dashboard.vue'),
      },
      {
        path: 'user-management',
        name: 'SuperAdminUserManagement',
        component: () => import('@/views/SuperAdmin/UserManagePage.vue'),
      },
      {
        path: 'survey-management',
        name: 'SuperAdminSurveyManagement',
        component: () => import('../views/SuperAdmin/SurveyManagement.vue'),
      },
      {
        path: 'alumni-directory',
        name: 'SuperAdminAlumniDirectory',
        component: () => import('../views/SuperAdmin/AlumniDirectory.vue'),
      },
      {
        path: 'pending-user-approval',
        name: 'SuperAdminPendingUserApproval',
        component: () => import('@/views/Admin/PendingUserApprovalPage.vue'),
      },
      {
        path: 'settings/:section?',
        name: 'SuperAdminSettings',
        component: () => import('../views/SuperAdmin/Settings.vue'),
      },
    ],
  },

  // 🛡 Admin Routes
  {
    path: '/admin',
    component: () => import('../components/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, role: 2 },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('../views/Admin/AdminDashboard.vue'),
      },
      {
        path: 'user-management',
        name: 'AdminUserManagement',
        component: () => import('../views/Admin/UserManagePage.vue'),
      },
      {
        path: 'messaging',
        name: 'AdminMessaging',
        component: () => import('../views/Alumni/Messaging.vue'),
      },
      {
        path: 'survey-management',
        name: 'AdminSurveyManagement',
        component: () => import('../views/Admin/SurveyManagementPage.vue'),
      },
      {
        path: 'survey-non-respondents',
        name: 'AdminSurveyNonRespondents',
        component: () => import('../components/admin/SurveyNonRespondents.vue'),
        meta: { title: 'Survey Non-Respondents' }
      },
      {
        path: 'contents',
        name: 'AdminContents',
        component: () => import('../views/Admin/ContentPage.vue'),
      },
      {
        path: 'post-reports',
        name: 'AdminPostReports',
        component: () => import('../views/Admin/PostReportPage.vue'),
      },
      {
        path: 'pending-user-approval',
        name: 'AdminPendingUserApproval',
        component: () => import('../views/Admin/PendingUserApprovalPage.vue'),
      },
      {
        path: 'settings/:section?',
        name: 'AdminSettings',
        component: () => import('../views/Admin/SettingsPage.vue'),
      },
    ],
  },

  // 🛡 Alumni Route
  {
    path: '/alumni',
    component: () => import('@/components/layouts/AlumniLayout.vue'),
    meta: { requiresAuth: true, role: 3 },
    children: [
      {
        path: '',
        redirect: 'home',
      },
      {
        path: 'home',
        name: 'AlumniHome',
        component: () => import('@/views/Alumni/AlumniHome.vue'),
      },
      {
        path: 'my-profile',
        name: 'AlumniMyProfile',
        component: () => import('../views/Alumni/MyProfile.vue'),
      },
      {
        path: 'profile/:userIdentifier',
        name: 'AlumniProfile',
        component: () => import('../views/Alumni/UserProfile.vue'),
      },
      {
        path: 'my-mates',
        name: 'AlumniMyMates',
        component: () => import('../views/Alumni/MyMates.vue'),
      },
      {
        path: 'network/suggestions',
        name: 'AlumniNetworkSuggestions',
        component: () => import('../views/Alumni/NetworkSuggestions.vue'),
      },
      {
        path: 'messaging',
        name: 'AlumniMessaging',
        component: () => import('../views/Alumni/Messaging.vue'),
      },
      {
        path: 'survey',
        name: 'AlumniSurvey',
        component: () => import('../views/Alumni/Survey.vue'),
      },
      {
        path: 'settings',
        name: 'AlumniSettings',
        component: () => import('../views/Alumni/Settings.vue'),
      },
      {
        path: 'debug-theme',
        name: 'AlumniDebugTheme',
        component: () => import('../components/DebugTheme.vue'),
      },
    ],
  },

  // 🔁 Default Redirect
  {
    path: '/',
    redirect: '/login',
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// ✅ Global Navigation Guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = !!authStore.token;

  // Allow public routes (like public surveys)
  if (to.meta.public) {
    return next();
  }

  // Fetch user data if token exists but no user loaded
  if (isAuthenticated && !authStore.user) {
    const ui = useUiStore();
    try {
      ui.start('Loading user...');
      await authStore.fetchUser();
    } catch {
      authStore.logout();
      return next('/login');
    } finally {
      ui.stop();
    }
  }

  const userRole = authStore.user?.user_type;

  // Prevent authenticated users from visiting guest-only routes
  if (to.meta.requiresGuest && isAuthenticated) {
    switch (userRole) {
      case 1: return next({ name: 'SuperAdminDashboard' });
      case 2: return next({ name: 'AdminDashboard' });
      case 3: {
        // Check if alumni has seen intro page
        const hasSeenIntro = localStorage.getItem('alumni_intro_seen');
        if (!hasSeenIntro) {
          return next({ name: 'AlumniIntro' });
        }
        return next({ name: 'AlumniHome' });
      }
      default: return next('/login');
    }
  }

  // Prevent guests from accessing protected routes
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login');
  }

  // Enforce role-based access
  if (to.meta.role && userRole !== to.meta.role) {
    return next('/login');
  }

  // Check if alumni user needs to see intro page (after login, before main app)
  if (isAuthenticated && userRole === 3 && !to.meta.skipIntroCheck) {
    const hasSeenIntro = localStorage.getItem('alumni_intro_seen');
    if (!hasSeenIntro && to.name !== 'AlumniIntro') {
      return next({ name: 'AlumniIntro' });
    }
  }

  next();
});

// Ensure theme persists after route navigation
router.afterEach(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark');
    document.body.classList.add('dark');
  }
});

export default router;
