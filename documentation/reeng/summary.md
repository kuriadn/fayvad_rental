# Cursor Implementation Guide

## 🎯 Project Structure to Create

```
fayvad-rentals-frontend/
├── nuxt.config.ts
├── package.json
├── app.vue
├── layouts/
│   ├── default.vue          # Staff layout
│   ├── tenant.vue           # Tenant layout  
│   └── mobile.vue           # Mobile-first layout
├── pages/
│   ├── index.vue            # Landing/redirect page
│   ├── login/
│   │   ├── staff.vue        # Staff login
│   │   └── tenant.vue       # Tenant login
│   ├── dashboard/
│   │   └── index.vue        # Role-based dashboard
│   ├── tenants/
│   │   ├── index.vue        # Tenant list
│   │   ├── create.vue       # Add tenant
│   │   └── [id].vue         # Tenant details
│   ├── rooms/
│   │   ├── index.vue        # Room overview
│   │   └── [id].vue         # Room details
│   ├── payments/
│   │   ├── index.vue        # Payment list
│   │   └── create.vue       # Record payment
│   ├── rentals/
│   │   ├── index.vue        # Rental list
│   │   └── create.vue       # Create rental
│   ├── maintenance/
│   │   ├── index.vue        # Maintenance list
│   │   └── create.vue       # Create request
│   ├── documents/
│   │   └── index.vue        # Document management
│   ├── contracts/
│   │   └── index.vue        # Contract management
│   ├── reports/
│   │   └── index.vue        # Reports dashboard
│   └── tenant/
│       ├── dashboard.vue    # Tenant dashboard
│       ├── payments.vue     # Tenant payments
│       ├── maintenance/
│       │   ├── index.vue    # Tenant maintenance
│       │   └── create.vue   # Create request
│       ├── documents.vue    # Tenant documents
│       ├── contract.vue     # View contract
│       └── profile.vue      # Tenant profile
├── components/
│   ├── common/
│   │   ├── ResponsiveDataTable.vue
│   │   ├── MobileForm.vue
│   │   ├── MetricCard.vue
│   │   └── ExportData.vue
│   ├── tenants/
│   │   ├── TenantCreateDialog.vue
│   │   ├── AssignRoom.vue
│   │   ├── TransferRoom.vue
│   │   └── TerminateTenancy.vue
│   ├── rooms/
│   │   ├── StatusFilter.vue
│   │   ├── FloorPlan.vue
│   │   └── OccupancyChart.vue
│   ├── payments/
│   │   ├── ValidationActions.vue
│   │   ├── TrendsChart.vue
│   │   └── MethodStats.vue
│   ├── maintenance/
│   │   ├── StartWork.vue
│   │   ├── CompleteWork.vue
│   │   └── PendingList.vue
│   ├── AppSidebar.vue
│   ├── AppHeader.vue
│   └── BreadcrumbNav.vue
├── composables/
│   ├── useApi.js            # API client
│   ├── useAuth.js           # Authentication
│   ├── useTenants.js        # Tenant operations
│   ├── useRooms.js          # Room operations
│   ├── usePayments.js       # Payment operations
│   ├── useRentals.js        # Rental operations
│   ├── useMaintenance.js    # Maintenance operations
│   ├── useDocuments.js      # Document operations
│   ├── useContracts.js      # Contract operations
│   ├── useDevice.js         # Device detection
│   ├── useValidation.js     # Form validation
│   └── useFormatters.js     # Data formatting
├── middleware/
│   ├── auth.js              # Staff authentication
│   └── tenant-auth.js       # Tenant authentication
├── plugins/
│   └── primevue.client.js   # PrimeVue setup
├── stores/
│   ├── auth.js              # Auth state
│   ├── tenants.js           # Tenant state
│   └── ui.js                # UI state
└── assets/
    ├── css/
    │   └── main.css         # Global styles
    └── images/
        └── logo.png
```

## 📋 Key Implementation Steps

### 1. **Initial Setup**
```bash
npx nuxi@latest init fayvad-rentals-frontend
cd fayvad-rentals-frontend
npm install primevue primeicons @nuxtjs/tailwindcss @pinia/nuxt @vueuse/nuxt
```

### 2. **Core Configuration**
- Configure `nuxt.config.ts` with PrimeVue, Tailwind, Pinia
- Set up API base URL and runtime config
- Configure PrimeVue theme and components

### 3. **Authentication Flow**
- Implement dual login (staff/tenant)
- Create auth middleware for route protection
- Set up role-based navigation

### 4. **API Integration**
- Create `useApi` composable with base configuration
- Implement business logic composables for each domain
- Set up error handling and loading states

### 5. **Component Development Priority**

**Phase 1: Core Infrastructure**
1. Layout components (sidebar, header, navigation)
2. Authentication pages and flow
3. Dashboard with basic metrics
4. Common components (DataTable, forms, cards)

**Phase 2: Staff Features**
1. Tenant management (CRUD operations)
2. Room management and status updates
3. Payment processing and validation
4. Basic reporting

**Phase 3: Tenant Portal**
1. Tenant dashboard and profile
2. Payment history view
3. Maintenance request submission
4. Document and contract access

**Phase 4: Advanced Features**
1. Real-time updates and notifications
2. Advanced analytics and reporting
3. Mobile optimizations
4. PWA features

## 🔧 Key Technical Patterns

### **API Calls Pattern**
```javascript
// In composables
const { api } = useApi()
const response = await api('/tenants/', { 
  method: 'POST', 
  body: data 
})
```

### **Form Handling Pattern**
```javascript
// Validation + submission
const { validateForm } = useValidation()
const errors = validateForm(form.value, rules)
if (Object.keys(errors).length === 0) {
  await submitForm()
}
```

### **Mobile-First Pattern**
```javascript
// Responsive components
const { isMobile } = useDevice()
// Show cards on mobile, table on desktop
```

### **State Management Pattern**
```javascript
// Business logic in composables
const { 
  tenants, 
  loading, 
  fetchTenants, 
  createTenant 
} = useTenants()
```

## 🎨 UI/UX Guidelines

### **Design System**
- **Primary Color**: Blue (#3B82F6)
- **Success**: Green (#10B981) 
- **Warning**: Yellow (#F59E0B)
- **Error**: Red (#EF4444)
- **Gray Scale**: Tailwind grays

### **Component Standards**
- Use PrimeVue components as base
- Extend with Tailwind classes for styling
- Mobile-first responsive design
- Consistent spacing (4px grid)

### **Navigation Standards**
- **Staff**: Sidebar navigation with collapsible menu
- **Tenant**: Bottom navigation on mobile, sidebar on desktop
- **Breadcrumbs**: On all internal pages
- **Back buttons**: On mobile detail pages

## 🔄 Business Logic Mapping

### **Complete API Coverage**
| Frontend Feature | Backend API | Method |
|------------------|-------------|--------|
| Login | `/api/auth/login/` | POST |
| Get Tenants | `/api/tenants/` | GET |
| Create Tenant | `/api/tenants/` | POST |
| Assign Room | `/api/tenants/{id}/assign/` | POST |
| Record Payment | `/api/payments/` | POST |
| Validate Payment | `/api/payments/{id}/validate/` | POST |
| Create Maintenance | `/api/maintenance/` | POST |
| Upload Document | `/api/documents/upload/` | POST |
| Generate Contract | `/api/contracts/generate/` | POST |
| Dashboard Data | `/api/dashboard/` | GET |

### **Workflow Implementation**
1. **Tenant Onboarding**: Create → Assign Room → Upload Docs → Generate Contract
2. **Payment Processing**: Record → Validate → Send Receipt
3. **Maintenance**: Create Request → Assign → Complete → Update Room Status
4. **Contract Signing**: Generate → Manager Sign → Tenant Sign → Activate Rental

## 📱 Mobile Optimization

### **Responsive Breakpoints**
- **Mobile**: < 768px (stack layouts, bottom nav, simplified forms)
- **Tablet**: 768px - 1024px (hybrid layouts, side nav)
- **Desktop**: > 1024px (full sidebar, data tables)

### **Mobile-Specific Features**
- Bottom navigation for tenant portal
- Swipe gestures for cards
- Pull-to-refresh on lists
- Touch-friendly button sizes (44px min)
- Simplified forms with better mobile inputs

## 🚀 Performance Optimization

### **Code Splitting**
- Lazy load routes and components
- Split vendor bundles
- Dynamic imports for heavy components

### **Caching Strategy**
- API response caching (SWR pattern)
- Image optimization and lazy loading
- Static asset caching

### **PWA Features**
- Service worker for offline support
- App-like experience on mobile
- Push notifications for updates

---

## ✅ Success Criteria

1. **Complete feature parity** with existing Odoo system
2. **Mobile-first responsive design** that works on all devices
3. **Role-based access** with proper authentication
4. **Real-time updates** and smooth user experience
5. **Production-ready performance** and optimization

**This implementation matrix provides Cursor with everything needed to build a complete, modern frontend that fully utilizes the Django FBS backend while maintaining simplicity and avoiding over-engineering.**