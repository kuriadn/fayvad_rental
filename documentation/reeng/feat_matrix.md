# Frontend Implementation Matrix

## 🔐 Authentication System

### Login Pages
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Staff Login | `pages/login/staff.vue` | `POST /api/auth/login/` | Card, InputText, Password, Button |
| Tenant Login | `pages/login/tenant.vue` | `POST /api/auth/tenant-login/` | Card, InputText, Button |
| Logout | `components/AppHeader.vue` | `POST /api/auth/logout/` | Button, ConfirmDialog |
| Role Detection | `middleware/auth.js` | `GET /api/auth/me/` | - |

### Navigation Structure
```
Staff Interface:
├── Dashboard (role-specific)
├── Tenants Management
├── Rooms Management  
├── Payments Management
├── Rentals Management
├── Maintenance System
├── Documents Management
├── Contracts Management
├── Reports & Analytics
└── Settings (managers only)

Tenant Interface:
├── Dashboard
├── My Profile
├── Payment History
├── Maintenance Requests
├── Documents
├── Contract View
└── Support
```

## 📊 Dashboard Components

### Staff Dashboard
| User Role | Component | API Calls | Features |
|-----------|-----------|-----------|----------|
| Manager | `pages/dashboard/manager.vue` | `GET /api/dashboard/manager/` | All metrics, reports, user management |
| Caretaker | `pages/dashboard/caretaker.vue` | `GET /api/dashboard/caretaker/` | Operational metrics, tenant/room status |
| Finance | `pages/dashboard/finance.vue` | `GET /api/dashboard/finance/` | Payment metrics, financial reports |
| Readonly | `pages/dashboard/readonly.vue` | `GET /api/dashboard/readonly/` | Read-only reports and analytics |

### Tenant Dashboard
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Account Summary | `components/tenant/AccountSummary.vue` | `GET /api/tenant/dashboard/` | Card, Tag, ProgressBar |
| Recent Payments | `components/tenant/RecentPayments.vue` | `GET /api/tenant/payments/` | DataTable, Tag |
| Maintenance Status | `components/tenant/MaintenanceStatus.vue` | `GET /api/tenant/maintenance/` | Timeline, Badge |

## 👥 Tenant Management

### Tenant List & Search
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Tenant List | `pages/tenants/index.vue` | `GET /api/tenants/` | DataTable, FilterMatchMode |
| Search/Filter | `components/tenants/TenantFilters.vue` | `GET /api/tenants/?search=&status=` | InputText, Dropdown, MultiSelect |
| Tenant Card View | `components/tenants/TenantCard.vue` | - | Card, Avatar, Tag, Button |
| Bulk Actions | `components/tenants/BulkActions.vue` | Various bulk endpoints | Toolbar, SplitButton |

### Tenant CRUD Operations
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Add Tenant | `pages/tenants/create.vue` | `POST /api/tenants/` | Dialog, InputText, Dropdown, Calendar |
| View Tenant | `pages/tenants/[id].vue` | `GET /api/tenants/{id}/` | TabView, Card, DataTable |
| Edit Tenant | `pages/tenants/[id]/edit.vue` | `PUT /api/tenants/{id}/` | InputText, Dropdown, Textarea |
| Delete Tenant | `components/tenants/DeleteConfirm.vue` | `DELETE /api/tenants/{id}/` | ConfirmDialog |

### Tenant Business Operations
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Assign to Room | `components/tenants/AssignRoom.vue` | `POST /api/tenants/{id}/assign/` | Dialog, Dropdown, Button |
| Transfer Room | `components/tenants/TransferRoom.vue` | `POST /api/tenants/{id}/transfer/` | Dialog, Dropdown, Textarea |
| Terminate Tenancy | `components/tenants/TerminateTenancy.vue` | `POST /api/tenants/{id}/terminate/` | Dialog, Calendar, Textarea |
| Update Compliance | `components/tenants/ComplianceUpdate.vue` | `PUT /api/tenants/{id}/compliance/` | Dropdown, Textarea, Button |

## 🏠 Room Management

### Room Overview
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Room Grid | `pages/rooms/index.vue` | `GET /api/rooms/` | DataView, Card |
| Room Status Filter | `components/rooms/StatusFilter.vue` | `GET /api/rooms/?status=` | SelectButton, Dropdown |
| Floor Plan View | `components/rooms/FloorPlan.vue` | `GET /api/rooms/` | Custom SVG + Vue |
| Occupancy Chart | `components/rooms/OccupancyChart.vue` | `GET /api/rooms/occupancy/` | Chart (Chart.js) |

### Room Operations
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Update Room Status | `components/rooms/StatusUpdate.vue` | `PUT /api/rooms/{id}/status/` | Dropdown, Button |
| Set Maintenance | `components/rooms/SetMaintenance.vue` | `POST /api/rooms/{id}/maintenance/` | Dialog, Textarea, Calendar |
| Room Details | `pages/rooms/[id].vue` | `GET /api/rooms/{id}/` | TabView, Card, Timeline |
| Rental History | `components/rooms/RentalHistory.vue` | `GET /api/rooms/{id}/rentals/` | DataTable, Timeline |

## 💰 Payment Management

### Payment List & Processing
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Payment List | `pages/payments/index.vue` | `GET /api/payments/` | DataTable, FilterMatchMode |
| Record Payment | `pages/payments/create.vue` | `POST /api/payments/` | Dialog, InputNumber, Dropdown |
| Payment Validation | `components/payments/ValidationActions.vue` | `POST /api/payments/{id}/validate/` | Button, ConfirmDialog |
| Payment Rejection | `components/payments/RejectPayment.vue` | `POST /api/payments/{id}/reject/` | Dialog, Textarea |
| Send Receipt | `components/payments/SendReceipt.vue` | `POST /api/payments/{id}/receipt/` | Button, Toast |

### Payment Analytics
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Payment Trends | `components/payments/TrendsChart.vue` | `GET /api/payments/trends/` | Chart |
| Method Statistics | `components/payments/MethodStats.vue` | `GET /api/payments/stats/` | Card, ProgressBar |
| Collection Rate | `components/payments/CollectionRate.vue` | `GET /api/payments/collection-rate/` | Knob, Card |

## 🏘️ Rental Management

### Rental Operations
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Rental List | `pages/rentals/index.vue` | `GET /api/rentals/` | DataTable, Tag |
| Create Rental | `pages/rentals/create.vue` | `POST /api/rentals/` | Steps, InputNumber, Calendar |
| Activate Rental | `components/rentals/ActivateRental.vue` | `POST /api/rentals/{id}/activate/` | Button, ConfirmDialog |
| Give Notice | `components/rentals/GiveNotice.vue` | `POST /api/rentals/{id}/notice/` | Dialog, Calendar |
| Terminate Rental | `components/rentals/TerminateRental.vue` | `POST /api/rentals/{id}/terminate/` | Dialog, Textarea |

### Rental Analytics
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Financial Summary | `components/rentals/FinancialSummary.vue` | `GET /api/rentals/{id}/finances/` | Card, ProgressBar |
| Overdue Rentals | `components/rentals/OverdueList.vue` | `GET /api/rentals/overdue/` | DataTable, Tag |
| Arrears Report | `components/rentals/ArrearsReport.vue` | `GET /api/rentals/arrears/` | DataTable, Chart |

## 🔧 Maintenance System

### Maintenance Requests
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Request List | `pages/maintenance/index.vue` | `GET /api/maintenance/` | DataTable, Tag, Rating |
| Create Request | `pages/maintenance/create.vue` | `POST /api/maintenance/` | Dialog, Dropdown, Textarea |
| Start Work | `components/maintenance/StartWork.vue` | `POST /api/maintenance/{id}/start/` | Button, Dialog |
| Complete Work | `components/maintenance/CompleteWork.vue` | `POST /api/maintenance/{id}/complete/` | Dialog, InputNumber |
| Request Details | `pages/maintenance/[id].vue` | `GET /api/maintenance/{id}/` | Card, Timeline |

### Maintenance Analytics
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Pending Requests | `components/maintenance/PendingList.vue` | `GET /api/maintenance/pending/` | DataTable, Tag |
| Trends Chart | `components/maintenance/TrendsChart.vue` | `GET /api/maintenance/trends/` | Chart |
| Cost Analysis | `components/maintenance/CostAnalysis.vue` | `GET /api/maintenance/costs/` | Card, Chart |

## 📄 Document Management

### Document Operations
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Document List | `pages/documents/index.vue` | `GET /api/documents/` | DataTable, FileUpload |
| Upload Document | `components/documents/UploadDocument.vue` | `POST /api/documents/upload/` | FileUpload, Dialog |
| Verify Document | `components/documents/VerifyDocument.vue` | `POST /api/documents/{id}/verify/` | Button, Textarea |
| Reject Document | `components/documents/RejectDocument.vue` | `POST /api/documents/{id}/reject/` | Dialog, Textarea |
| Document Viewer | `components/documents/DocumentViewer.vue` | `GET /api/documents/{id}/` | Image, Dialog |

### Document Analytics
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Pending Verifications | `components/documents/PendingList.vue` | `GET /api/documents/pending/` | DataTable, Badge |
| Tenant Documents | `components/documents/TenantDocuments.vue` | `GET /api/documents/tenant/{id}/` | TabView, Card |

## 📋 Contract Management

### Contract Operations
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Contract List | `pages/contracts/index.vue` | `GET /api/contracts/` | DataTable, Tag |
| Generate Contract | `components/contracts/GenerateContract.vue` | `POST /api/contracts/generate/` | Dialog, Button |
| Sign Contract | `components/contracts/SignContract.vue` | `POST /api/contracts/{id}/sign/` | Dialog, Canvas (signature) |
| Download Contract | `components/contracts/DownloadContract.vue` | `GET /api/contracts/{id}/download/` | Button |
| Contract Viewer | `pages/contracts/[id].vue` | `GET /api/contracts/{id}/` | Card, Steps |

### Contract Analytics
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Pending Signatures | `components/contracts/PendingSignatures.vue` | `GET /api/contracts/pending/` | DataTable, Badge |
| Signature Status | `components/contracts/SignatureStatus.vue` | - | Steps, Badge |

## 📊 Reports & Analytics

### Dashboard Reports
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Occupancy Report | `components/reports/OccupancyReport.vue` | `GET /api/reports/occupancy/` | Card, Chart, ProgressBar |
| Revenue Report | `components/reports/RevenueReport.vue` | `GET /api/reports/revenue/` | Card, Chart |
| Collection Report | `components/reports/CollectionReport.vue` | `GET /api/reports/collection/` | DataTable, Chart |
| Maintenance Report | `components/reports/MaintenanceReport.vue` | `GET /api/reports/maintenance/` | Card, Chart |

### Export Features
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| Export Data | `components/common/ExportData.vue` | `GET /api/export/{type}/` | SplitButton, Toast |
| Report Generator | `components/reports/ReportGenerator.vue` | `POST /api/reports/generate/` | Steps, Calendar, MultiSelect |

## ⚙️ Settings & Configuration

### System Settings (Manager Only)
| Feature | Component | API Call | PrimeVue Components |
|---------|-----------|----------|-------------------|
| User Management | `pages/settings/users.vue` | `GET /api/users/` | DataTable, Dialog |
| Role Management | `pages/settings/roles.vue` | `GET /api/roles/` | DataTable, Checkbox |
| System Config | `pages/settings/config.vue` | `GET /api/config/` | InputText, InputNumber |
| Backup/Restore | `pages/settings/backup.vue` | `POST /api/backup/` | Button, FileUpload |

## 🎨 Layout & Navigation

### Main Layout Components
| Component | Purpose | PrimeVue Components |
|-----------|---------|-------------------|
| `layouts/default.vue` | Main app layout | Sidebar, Menubar, ProgressBar |
| `components/AppSidebar.vue` | Navigation menu | Menu, Divider |
| `components/AppHeader.vue` | Top navigation | Toolbar, Avatar, Badge |
| `components/AppFooter.vue` | Footer | - |
| `components/BreadcrumbNav.vue` | Breadcrumb navigation | Breadcrumb |

### Menu Structure
```javascript
// Staff Menu Structure
const staffMenu = [
  {
    label: 'Dashboard',
    icon: 'pi pi-home',
    to: '/dashboard'
  },
  {
    label: 'Tenants',
    icon: 'pi pi-users',
    items: [
      { label: 'All Tenants', to: '/tenants' },
      { label: 'Add Tenant', to: '/tenants/create' },
      { label: 'Assignments', to: '/tenants/assignments' }
    ]
  },
  {
    label: 'Rooms',
    icon: 'pi pi-home',
    items: [
      { label: 'Room Overview', to: '/rooms' },
      { label: 'Floor Plan', to: '/rooms/floorplan' },
      { label: 'Maintenance', to: '/rooms/maintenance' }
    ]
  },
  {
    label: 'Payments',
    icon: 'pi pi-credit-card',
    items: [
      { label: 'All Payments', to: '/payments' },
      { label: 'Record Payment', to: '/payments/create' },
      { label: 'Validation Queue', to: '/payments/pending' }
    ]
  },
  {
    label: 'Rentals',
    icon: 'pi pi-file-text',
    to: '/rentals'
  },
  {
    label: 'Maintenance',
    icon: 'pi pi-cog',
    items: [
      { label: 'Requests', to: '/maintenance' },
      { label: 'Create Request', to: '/maintenance/create' },
      { label: 'Analytics', to: '/maintenance/analytics' }
    ]
  },
  {
    label: 'Documents',
    icon: 'pi pi-file',
    items: [
      { label: 'All Documents', to: '/documents' },
      { label: 'Pending Verification', to: '/documents/pending' }
    ]
  },
  {
    label: 'Contracts',
    icon: 'pi pi-bookmark',
    items: [
      { label: 'All Contracts', to: '/contracts' },
      { label: 'Pending Signatures', to: '/contracts/pending' }
    ]
  },
  {
    label: 'Reports',
    icon: 'pi pi-chart-bar',
    items: [
      { label: 'Occupancy', to: '/reports/occupancy' },
      { label: 'Revenue', to: '/reports/revenue' },
      { label: 'Collection', to: '/reports/collection' }
    ]
  }
]

// Tenant Menu Structure  
const tenantMenu = [
  {
    label: 'Dashboard',
    icon: 'pi pi-home',
    to: '/tenant/dashboard'
  },
  {
    label: 'My Profile', 
    icon: 'pi pi-user',
    to: '/tenant/profile'
  },
  {
    label: 'Payments',
    icon: 'pi pi-credit-card',
    items: [
      { label: 'Payment History', to: '/tenant/payments' },
      { label: 'Outstanding Balance', to: '/tenant/balance' }
    ]
  },
  {
    label: 'Maintenance',
    icon: 'pi pi-cog',
    items: [
      { label: 'My Requests', to: '/tenant/maintenance' },
      { label: 'Submit Request', to: '/tenant/maintenance/create' }
    ]
  },
  {
    label: 'Documents',
    icon: 'pi pi-file',
    to: '/tenant/documents'
  },
  {
    label: 'Contract',
    icon: 'pi pi-bookmark',
    to: '/tenant/contract'
  },
  {
    label: 'Support',
    icon: 'pi pi-question-circle',
    to: '/tenant/support'
  }
]
```

## 🔄 Workflows & State Management

### Key Workflows
| Workflow | Components Involved | API Sequence |
|----------|-------------------|--------------|
| Tenant Onboarding | Create → Assign Room → Generate Contract → Upload Documents | `POST /tenants/` → `POST /tenants/{id}/assign/` → `POST /contracts/generate/` → `POST /documents/upload/` |
| Payment Processing | Record → Validate → Send Receipt | `POST /payments/` → `POST /payments/{id}/validate/` → `POST /payments/{id}/receipt/` |
| Maintenance Request | Create → Assign → Start → Complete | `POST /maintenance/` → `PUT /maintenance/{id}/assign/` → `POST /maintenance/{id}/start/` → `POST /maintenance/{id}/complete/` |
| Contract Signing | Generate → Manager Sign → Tenant Sign → Activate | `POST /contracts/generate/` → `POST /contracts/{id}/sign/` → `POST /contracts/{id}/sign/` → `POST /rentals/{id}/activate/` |

### State Management with Pinia
```javascript
// stores/tenants.js
export const useTenantsStore = defineStore('tenants', () => {
  const tenants = ref([])
  const loading = ref(false)
  const filters = ref({})
  
  const fetchTenants = async () => {
    loading.value = true
    const { data } = await $fetch('/api/tenants/', { params: filters.value })
    tenants.value = data
    loading.value = false
  }
  
  return { tenants, loading, filters, fetchTenants }
})
```