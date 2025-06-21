import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

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
    component: () => import('../views/Register.vue'),
    meta: { requiresGuest: true },
  },

  // 🛡 Super Admin Routes
  {
    path: '/super-admin',
    component: () => import('../components/layouts/SuperAdminLayout.vue'),
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
        component: () => import('../views/SuperAdmin/UserManagement.vue'),
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
        path: 'system-monitoring',
        name: 'SuperAdminSystemMonitoring',
        component: () => import('../views/SuperAdmin/SystemMonitoring.vue'),
      },
      {
        path: 'analytic-dashboard',
        name: 'SuperAdminAnalyticDashboard',
        component: () => import('../views/SuperAdmin/AnalyticDashboard.vue'),
      },
      {
        path: 'pending-user-approval',
        name: 'SuperAdminPendingUserApproval',
        component: () => import('../views/SuperAdmin/PendingUserApproval.vue'),
      },
      {
        path: 'settings',
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
        path: 'survey-management',
        name: 'AdminSurveyManagement',
        component: () => import('../views/Admin/SurveyManagementPage.vue'),
      },
      {
        path: 'notification',
        name: 'AdminNotification',
        component: () => import('../views/Admin/NotificationPage.vue'),
      },
      {
        path: 'contents',
        name: 'AdminContents',
        component: () => import('../views/Admin/ContentPage.vue'),
      },
      {
        path: 'post-approvals',
        name: 'AdminPostApprovals',
        component: () => import('../views/Admin/PostApprovalPage.vue'),
      },
      {
        path: 'pending-user-approval',
        name: 'AdminPendingUserApproval',
        component: () => import('../views/Admin/PendingUserApprovalPage.vue'),
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('../views/Admin/SettingsPage.vue'),
      },
    ],
  },

  // 🛡 Alumni Route
  {
    path: '/alumni',
    name: 'AlumniDashboard',
    component: () => import('../views/Alumni/AlumniDashboard.vue'),
    meta: { requiresAuth: true, role: 3 },
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

  // Fetch user data if token exists but no user loaded
  if (isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchUser();
    } catch {
      authStore.logout();
      return next('/login');
    }
  }

  const userRole = authStore.user?.user_type;

  // Prevent authenticated users from visiting guest-only routes
  if (to.meta.requiresGuest && isAuthenticated) {
    switch (userRole) {
      case 1: return next({ name: 'SuperAdminDashboard' });
      case 2: return next({ name: 'AdminDashboard' });
      case 3: return next({ name: 'AlumniDashboard' });
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

  next();
});

export default router;
