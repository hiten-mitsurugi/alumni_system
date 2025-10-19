// Mock dashboard service for now
// This will be replaced with actual API calls later

export const dashboardService = {
  async getDashboardOverview() {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Return mock data for now
    return {
      alerts: [
        {
          id: 1,
          priority: 'critical',
          message: '15 Pending User Approvals waiting > 7 days',
          source: 'Pending User Approval',
          actionText: 'Review Now',
          action: 'navigate',
          actionUrl: '/superadmin/pending-approvals'
        },
        {
          id: 2,
          priority: 'warning',
          message: 'Low Survey Response from BSAgri (45%)',
          source: 'Survey Management',
          actionText: 'Send Reminder',
          action: 'send_reminder',
          actionUrl: '/superadmin/survey-management'
        },
        {
          id: 3,
          priority: 'info',
          message: 'System Backup completed successfully',
          source: 'System Monitoring',
          actionText: 'View Details',
          action: 'navigate',
          actionUrl: '/superadmin/system-monitoring'
        }
      ],
      userManagement: {
        totalUsers: 1247,
        alumni: 1089,
        admins: 12,
        superAdmins: 3,
        activeUsers: 342,
        activeUsersStatus: 'good',
        newUsers: 28,
        newUsersStatus: 'excellent'
      },
      surveyManagement: {
        totalResponses: 856,
        activeSurveys: 3,
        responseRate: 68,
        responseRateStatus: 'warning',
        newResponsesWeek: 42
      },
      alumniDirectory: {
        totalAlumni: 1089,
        completeProfiles: 84,
        completeProfilesStatus: 'good',
        employmentStatus: {
          employed: 72,
          selfEmployed: 15,
          unemployed: 13
        },
        international: 18
      },
      systemMonitoring: {
        status: 'online',
        uptime: 99.8,
        storageUsed: 73,
        storageStatus: 'good',
        lastBackup: '2 hours ago',
        backupStatus: 'excellent',
        activeSessions: 45
      },
      analytics: {
        employmentRate: 87,
        employmentRateStatus: 'excellent',
        avgCompetitiveness: 4.2,
        furtherStudies: 23,
        avgIncome: 35000,
        topProgram: 'BSIT'
      },
      pendingApprovals: {
        total: 23,
        critical: 8,
        warning: 10,
        recent: 5,
        oldestDays: 18,
        approvalRate: 92
      },
      settings: {
        configStatus: 'excellent',
        securityStatus: 'good',
        emailStatus: 'excellent',
        activeAdmins: 12,
        version: 'v1.2.1'
      },
      quickStats: {
        surveyResponses: 12,
        newRegistrations: 4,
        userLogins: 87,
        reportsGenerated: 3,
        peakHour: '2:30 PM'
      },
      recentActivity: [
        {
          id: 1,
          icon: 'ClipboardList',
          iconColor: 'text-green-500',
          description: 'Juan Dela Cruz (BSIT 2023) submitted survey response',
          timestamp: '5 minutes ago'
        },
        {
          id: 2,
          icon: 'UserPlus',
          iconColor: 'text-blue-500',
          description: 'New user registration: Maria Santos (BSEd 2022)',
          timestamp: '15 minutes ago'
        },
        {
          id: 3,
          icon: 'UserCheck',
          iconColor: 'text-purple-500',
          description: 'Admin approved 5 pending users',
          timestamp: '1 hour ago'
        },
        {
          id: 4,
          icon: 'BarChart3',
          iconColor: 'text-yellow-500',
          description: 'Employment Analytics Report generated',
          timestamp: '2 hours ago'
        },
        {
          id: 5,
          icon: 'Settings',
          iconColor: 'text-gray-500',
          description: 'System backup completed successfully',
          timestamp: '3 hours ago'
        }
      ],
      programPerformance: [
        {
          id: 1,
          name: 'BSIT',
          responses: 320,
          total: 450,
          percentage: 71,
          status: 'excellent'
        },
        {
          id: 2,
          name: 'BSEd',
          responses: 210,
          total: 280,
          percentage: 75,
          status: 'excellent'
        },
        {
          id: 3,
          name: 'BSBA',
          responses: 180,
          total: 320,
          percentage: 56,
          status: 'warning'
        },
        {
          id: 4,
          name: 'BSAgri',
          responses: 140,
          total: 280,
          percentage: 50,
          status: 'warning'
        },
        {
          id: 5,
          name: 'BSCS',
          responses: 95,
          total: 180,
          percentage: 53,
          status: 'warning'
        }
      ],
      notifications: [
        {
          id: 1,
          title: 'Pending User Approvals',
          message: '15 users pending approval for over 7 days',
          read: false,
          priority: 'critical'
        },
        {
          id: 2,
          title: 'Low Response Rate',
          message: 'BSAgri survey response rate below 50%',
          read: false,
          priority: 'warning'
        },
        {
          id: 3,
          title: 'Backup Complete',
          message: 'System backup completed successfully',
          read: true,
          priority: 'info'
        }
      ],
      lastLogin: new Date(Date.now() - 2 * 60 * 60 * 1000) // 2 hours ago
    }
  },

  async handleAlert(alertId, action) {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500))
    
    console.log(`Handling alert ${alertId} with action ${action}`)
    
    // Return success response
    return {
      success: true,
      message: 'Alert action completed successfully'
    }
  },

  async getDashboardStats() {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // Return comprehensive mock statistics for the dashboard
    return {
      totalResponses: 1247,
      responseRate: 73.2,
      employmentRate: 82.5,
      competitivenessScore: 4.1,
      
      programStats: [
        { name: 'BS Computer Science', responses: 145, total: 200, percentage: 72.5 },
        { name: 'BS Information Technology', responses: 132, total: 180, percentage: 73.3 },
        { name: 'BS Agriculture', responses: 98, total: 220, percentage: 44.5 },
        { name: 'BS Education', responses: 156, total: 190, percentage: 82.1 },
        { name: 'BS Business Admin', responses: 123, total: 160, percentage: 76.9 },
        { name: 'BS Engineering', responses: 89, total: 150, percentage: 59.3 }
      ],
      
      employmentStats: {
        employed: 65.2,
        selfEmployed: 17.3,
        unemployed: 17.5,
        avgIncome: 45000,
        jobRelevance: 78.4,
        international: 23.1,
        local: 76.9
      },
      
      skillsStats: [
        { name: 'Communication Skills', rating: 4.2 },
        { name: 'Technical Competency', rating: 4.0 },
        { name: 'Problem Solving', rating: 3.8 },
        { name: 'Leadership', rating: 3.6 },
        { name: 'Teamwork', rating: 4.1 },
        { name: 'Critical Thinking', rating: 3.9 },
        { name: 'Adaptability', rating: 4.0 },
        { name: 'Digital Literacy', rating: 3.7 }
      ],
      
      programEmployment: [
        { name: 'CS', employmentRate: 89 },
        { name: 'IT', employmentRate: 85 },
        { name: 'Agri', employmentRate: 62 },
        { name: 'Educ', employmentRate: 78 },
        { name: 'BA', employmentRate: 81 }
      ],
      
      systemStats: {
        totalAlumni: 3542,
        pendingApprovals: 18,
        activeSurveys: 5,
        dataCompleteness: 87
      },
      
      furtherStudies: {
        percentage: 24.6,
        masters: 18.3,
        doctorate: 4.2,
        certificate: 2.1
      },
      
      demographics: {
        gender: {
          male: 52.3,
          female: 47.7
        },
        location: {
          philippines: 76.9,
          international: 23.1
        },
        civilStatus: {
          single: 58.4,
          married: 37.2,
          others: 4.4
        }
      }
    }
  }
}