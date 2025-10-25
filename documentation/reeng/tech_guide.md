// Nuxt Configuration
// nuxt.config.ts
export default defineNuxtConfig({
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@vueuse/nuxt'
  ],
  
  css: [
    'primevue/resources/themes/aura-light-green/theme.css',
    'primevue/resources/primevue.min.css',
    'primeicons/primeicons.css'
  ],
  
  build: {
    transpile: ['primevue']
  },
  
  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE_URL || 'http://localhost:8000/api'
    }
  }
})

// Plugin Configuration
// plugins/primevue.client.js
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(PrimeVue, { ripple: true })
  nuxtApp.vueApp.use(ToastService)
  nuxtApp.vueApp.use(ConfirmationService)
})

// API Service Layer
// composables/useApi.js
export const useApi = () => {
  const config = useRuntimeConfig()
  const { $fetch } = useNuxtApp()
  
  const api = $fetch.create({
    baseURL: config.public.apiBase,
    headers: {
      'Content-Type': 'application/json'
    },
    onRequest({ request, options }) {
      const token = useCookie('auth-token')
      if (token.value) {
        options.headers.Authorization = `Bearer ${token.value}`
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        navigateTo('/login')
      }
    }
  })
  
  return { api }
}

// Authentication Composable
// composables/useAuth.js
export const useAuth = () => {
  const user = ref(null)
  const token = useCookie('auth-token')
  const { api } = useApi()
  
  const login = async (credentials, userType = 'staff') => {
    const endpoint = userType === 'staff' ? '/auth/login/' : '/auth/tenant-login/'
    const response = await api(endpoint, {
      method: 'POST',
      body: credentials
    })
    
    if (response.success) {
      token.value = response.token
      user.value = response.user
      
      // Redirect based on user type and role
      if (userType === 'staff') {
        navigateTo('/dashboard')
      } else {
        navigateTo('/tenant/dashboard')
      }
    }
    
    return response
  }
  
  const logout = async () => {
    await api('/auth/logout/', { method: 'POST' })
    token.value = null
    user.value = null
    navigateTo('/login')
  }
  
  const checkAuth = async () => {
    if (token.value) {
      try {
        const response = await api('/auth/me/')
        user.value = response.user
        return true
      } catch {
        token.value = null
        return false
      }
    }
    return false
  }
  
  return { user, login, logout, checkAuth }
}

// Business Logic Composables
// composables/useTenants.js
export const useTenants = () => {
  const tenants = ref([])
  const loading = ref(false)
  const pagination = ref({ page: 1, limit: 20, total: 0 })
  const filters = ref({})
  const { api } = useApi()
  
  const fetchTenants = async () => {
    loading.value = true
    try {
      const params = {
        ...filters.value,
        page: pagination.value.page,
        limit: pagination.value.limit
      }
      const response = await api('/tenants/', { params })
      tenants.value = response.data
      pagination.value.total = response.total
    } finally {
      loading.value = false
    }
  }
  
  const createTenant = async (data) => {
    const response = await api('/tenants/', {
      method: 'POST',
      body: data
    })
    await fetchTenants() // Refresh list
    return response
  }
  
  const assignToRoom = async (tenantId, roomId) => {
    return await api(`/tenants/${tenantId}/assign/`, {
      method: 'POST',
      body: { room_id: roomId }
    })
  }
  
  const terminateTenancy = async (tenantId, reason, date) => {
    return await api(`/tenants/${tenantId}/terminate/`, {
      method: 'POST',
      body: { reason, date }
    })
  }
  
  return {
    tenants,
    loading,
    pagination,
    filters,
    fetchTenants,
    createTenant,
    assignToRoom,
    terminateTenancy
  }
}

// Layout Implementation
// layouts/default.vue
<template>
  <div class="min-h-screen flex">
    <AppSidebar v-if="user" :menu="menuItems" :collapsed="sidebarCollapsed" />
    
    <div class="flex-1 flex flex-col">
      <AppHeader 
        v-if="user"
        @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed"
        :user="user"
      />
      
      <main class="flex-1 p-6 bg-gray-50">
        <BreadcrumbNav />
        <slot />
      </main>
    </div>
    
    <Toast />
    <ConfirmDialog />
  </div>
</template>

<script setup>
const { user } = useAuth()
const sidebarCollapsed = ref(false)

const menuItems = computed(() => {
  if (!user.value) return []
  
  if (user.value.role === 'tenant') {
    return tenantMenu
  } else {
    return staffMenu.filter(item => 
      hasPermission(user.value.role, item.permission)
    )
  }
})
</script>

// Page Implementation Examples
// pages/tenants/index.vue
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold">Tenant Management</h1>
      <Button 
        icon="pi pi-plus" 
        label="Add Tenant"
        @click="showCreateDialog = true"
      />
    </div>
    
    <Card>
      <template #content>
        <!-- Filters -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <InputText 
            v-model="filters.search" 
            placeholder="Search tenants..."
            @input="debouncedSearch"
          />
          <Dropdown 
            v-model="filters.status"
            :options="statusOptions"
            placeholder="Status"
            @change="fetchTenants"
          />
          <Dropdown 
            v-model="filters.tenant_type"
            :options="typeOptions" 
            placeholder="Type"
            @change="fetchTenants"
          />
          <Button 
            icon="pi pi-filter-slash"
            label="Clear"
            severity="secondary"
            @click="clearFilters"
          />
        </div>
        
        <!-- Data Table -->
        <DataTable 
          v-model:selection="selectedTenants"
          :value="tenants"
          :loading="loading"
          selectionMode="multiple"
          dataKey="id"
          :paginator="true"
          :rows="pagination.limit"
          :totalRecords="pagination.total"
          :lazy="true"
          @page="onPage"
          @sort="onSort"
        >
          <Column selectionMode="multiple" />
          
          <Column field="name" header="Name" sortable>
            <template #body="{ data }">
              <div class="flex items-center gap-2">
                <Avatar :label="getInitials(data.name)" />
                <div>
                  <div class="font-medium">{{ data.name }}</div>
                  <div class="text-sm text-gray-500">{{ data.phone }}</div>
                </div>
              </div>
            </template>
          </Column>
          
          <Column field="tenant_status" header="Status" sortable>
            <template #body="{ data }">
              <Tag 
                :value="data.tenant_status"
                :severity="getStatusSeverity(data.tenant_status)"
              />
            </template>
          </Column>
          
          <Column field="current_room" header="Room">
            <template #body="{ data }">
              <span v-if="data.current_room">
                Room {{ data.current_room.number }}
              </span>
              <span v-else class="text-gray-400">No room</span>
            </template>
          </Column>
          
          <Column header="Actions">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button 
                  icon="pi pi-eye"
                  size="small"
                  severity="info"
                  @click="viewTenant(data.id)"
                />
                <Button 
                  icon="pi pi-pencil"
                  size="small"
                  @click="editTenant(data.id)"
                />
                <SplitButton 
                  :model="getActionItems(data)"
                  size="small"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
    
    <!-- Bulk Actions -->
    <Card v-if="selectedTenants.length > 0">
      <template #content>
        <div class="flex gap-4 items-center">
          <span>{{ selectedTenants.length }} tenant(s) selected</span>
          <Button 
            label="Bulk Update Status"
            @click="showBulkUpdateDialog = true"
          />
          <Button 
            label="Export Selected"
            severity="secondary"
            @click="exportSelected"
          />
        </div>
      </template>
    </Card>
    
    <!-- Dialogs -->
    <TenantCreateDialog 
      v-model:visible="showCreateDialog"
      @created="onTenantCreated"
    />
    
    <TenantBulkUpdateDialog
      v-model:visible="showBulkUpdateDialog"
      :tenants="selectedTenants"
      @updated="onBulkUpdated"
    />
  </div>
</template>

<script setup>
definePageMeta({
  middleware: 'auth',
  requiresRole: ['manager', 'caretaker']
})

const { 
  tenants, 
  loading, 
  pagination, 
  filters,
  fetchTenants,
  createTenant 
} = useTenants()

const selectedTenants = ref([])
const showCreateDialog = ref(false)
const showBulkUpdateDialog = ref(false)

const statusOptions = [
  { label: 'Prospective', value: 'prospective' },
  { label: 'Active', value: 'active' },
  { label: 'Former', value: 'former' }
]

const typeOptions = [
  { label: 'Student', value: 'student' },
  { label: 'Working', value: 'working' },
  { label: 'Other', value: 'other' }
]

// Lifecycle
onMounted(() => {
  fetchTenants()
})

// Methods
const debouncedSearch = useDebounceFn(() => {
  fetchTenants()
}, 500)

const clearFilters = () => {
  filters.value = {}
  fetchTenants()
}

const onPage = (event) => {
  pagination.value.page = event.page + 1
  fetchTenants()
}

const getActionItems = (tenant) => [
  {
    label: 'Assign Room',
    icon: 'pi pi-home',
    command: () => assignRoom(tenant),
    disabled: tenant.tenant_status !== 'prospective'
  },
  {
    label: 'Transfer Room', 
    icon: 'pi pi-arrow-right',
    command: () => transferRoom(tenant),
    disabled: tenant.tenant_status !== 'active'
  },
  {
    label: 'Terminate',
    icon: 'pi pi-times',
    command: () => terminateTenant(tenant),
    disabled: tenant.tenant_status !== 'active'
  }
]

const onTenantCreated = () => {
  showCreateDialog.value = false
  fetchTenants()
}
</script>

// Component Examples
// components/tenants/TenantCreateDialog.vue
<template>
  <Dialog 
    :visible="visible"
    @update:visible="$emit('update:visible', $event)"
    modal
    header="Add New Tenant"
    :style="{ width: '600px' }"
  >
    <form @submit.prevent="submitForm">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="field">
          <label class="block text-sm font-medium mb-2">Full Name *</label>
          <InputText 
            v-model="form.name"
            :class="{ 'p-invalid': errors.name }"
            placeholder="Enter full name"
          />
          <small v-if="errors.name" class="p-error">{{ errors.name }}</small>
        </div>
        
        <div class="field">
          <label class="block text-sm font-medium mb-2">Phone Number *</label>
          <InputText 
            v-model="form.phone"
            :class="{ 'p-invalid': errors.phone }"
            placeholder="0700000000"
          />
          <small v-if="errors.phone" class="p-error">{{ errors.phone }}</small>
        </div>
        
        <div class="field">
          <label class="block text-sm font-medium mb-2">Email</label>
          <InputText 
            v-model="form.email"
            type="email"
            placeholder="email@example.com"
          />
        </div>
        
        <div class="field">
          <label class="block text-sm font-medium mb-2">ID Number *</label>
          <InputText 
            v-model="form.id_number"
            :class="{ 'p-invalid': errors.id_number }"
            placeholder="12345678"
          />
          <small v-if="errors.id_number" class="p-error">{{ errors.id_number }}</small>
        </div>
        
        <div class="field">
          <label class="block text-sm font-medium mb-2">Tenant Type</label>
          <Dropdown 
            v-model="form.tenant_type"
            :options="tenantTypes"
            optionLabel="label"
            optionValue="value"
            placeholder="Select type"
          />
        </div>
        
        <div class="field">
          <label class="block text-sm font-medium mb-2">Institution/Employer</label>
          <InputText 
            v-model="form.institution_employer"
            placeholder="University/Company name"
          />
        </div>
        
        <div class="field col-span-2">
          <label class="block text-sm font-medium mb-2">Emergency Contact Name *</label>
          <InputText 
            v-model="form.emergency_contact_name"
            :class="{ 'p-invalid': errors.emergency_contact_name }"
            placeholder="Emergency contact name"
          />
          <small v-if="errors.emergency_contact_name" class="p-error">{{ errors.emergency_contact_name }}</small>
        </div>
        
        <div class="field col-span-2">
          <label class="block text-sm font-medium mb-2">Emergency Contact Phone *</label>
          <InputText 
            v-model="form.emergency_contact_phone"
            :class="{ 'p-invalid': errors.emergency_contact_phone }"
            placeholder="Emergency contact phone"
          />
          <small v-if="errors.emergency_contact_phone" class="p-error">{{ errors.emergency_contact_phone }}</small>
        </div>
      </div>
      
      <div class="flex justify-end gap-2 mt-6">
        <Button 
          label="Cancel"
          severity="secondary"
          @click="$emit('update:visible', false)"
        />
        <Button 
          label="Create Tenant"
          type="submit"
          :loading="loading"
        />
      </div>
    </form>
  </Dialog>
</template>

<script setup>
const props = defineProps(['visible'])
const emit = defineEmits(['update:visible', 'created'])

const { createTenant } = useTenants()
const { validateForm } = useValidation()

const form = ref({
  name: '',
  phone: '',
  email: '',
  id_number: '',
  tenant_type: 'student',
  institution_employer: '',
  emergency_contact_name: '',
  emergency_contact_phone: ''
})

const errors = ref({})
const loading = ref(false)

const tenantTypes = [
  { label: 'Student', value: 'student' },
  { label: 'Working Professional', value: 'working' },
  { label: 'Other', value: 'other' }
]

const validationRules = {
  name: { required: true, min: 2 },
  phone: { required: true, pattern: /^[0-9]{10}$/ },
  id_number: { required: true, min: 6 },
  emergency_contact_name: { required: true },
  emergency_contact_phone: { required: true, pattern: /^[0-9]{10}$/ }
}

const submitForm = async () => {
  errors.value = validateForm(form.value, validationRules)
  
  if (Object.keys(errors.value).length === 0) {
    loading.value = true
    try {
      await createTenant(form.value)
      emit('created')
      resetForm()
    } catch (error) {
      // Handle API errors
    } finally {
      loading.value = false
    }
  }
}

const resetForm = () => {
  form.value = {
    name: '',
    phone: '',
    email: '',
    id_number: '',
    tenant_type: 'student',
    institution_employer: '',
    emergency_contact_name: '',
    emergency_contact_phone: ''
  }
  errors.value = {}
}
</script>

// Dashboard Implementation
// pages/dashboard/index.vue
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold">Dashboard</h1>
      <div class="flex gap-2">
        <Button 
          icon="pi pi-refresh"
          label="Refresh"
          severity="secondary"
          @click="refreshData"
        />
        <Dropdown 
          v-model="selectedPeriod"
          :options="periodOptions"
          @change="onPeriodChange"
        />
      </div>
    </div>
    
    <!-- Metrics Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        title="Total Rooms"
        :value="dashboardData.total_rooms"
        icon="pi pi-home"
        color="blue"
      />
      <MetricCard
        title="Occupied Rooms"
        :value="dashboardData.occupied_rooms"
        icon="pi pi-users"
        color="green"
        :percentage="occupancyRate"
      />
      <MetricCard
        title="Monthly Revenue"
        :value="formatCurrency(dashboardData.monthly_revenue)"
        icon="pi pi-credit-card"
        color="purple"
      />
      <MetricCard
        title="Collection Rate"
        :value="`${dashboardData.collection_rate}%`"
        icon="pi pi-chart-line"
        color="orange"
      />
    </div>
    
    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <template #title>Occupancy Trend</template>
        <template #content>
          <Chart 
            type="line"
            :data="occupancyChartData"
            :options="chartOptions"
          />
        </template>
      </Card>
      
      <Card>
        <template #title>Revenue Breakdown</template>
        <template #content>
          <Chart 
            type="doughnut"
            :data="revenueChartData"
            :options="doughnutOptions"
          />
        </template>
      </Card>
    </div>
    
    <!-- Recent Activities -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <template #title>Recent Payments</template>
        <template #content>
          <DataTable 
            :value="recentPayments"
            :paginator="false"
          >
            <Column field="tenant_name" header="Tenant" />
            <Column field="amount" header="Amount">
              <template #body="{ data }">
                {{ formatCurrency(data.amount) }}
              </template>
            </Column>
            <Column field="payment_date" header="Date">
              <template #body="{ data }">
                {{ formatDate(data.payment_date) }}
              </template>
            </Column>
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag 
                  :value="data.is_validated ? 'Validated' : 'Pending'"
                  :severity="data.is_validated ? 'success' : 'warning'"
                />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
      
      <Card>
        <template #title>Maintenance Requests</template>
        <template #content>
          <DataTable 
            :value="maintenanceRequests"
            :paginator="false"
          >
            <Column field="room_number" header="Room" />
            <Column field="issue_type" header="Issue" />
            <Column field="urgency" header="Priority">
              <template #body="{ data }">
                <Tag 
                  :value="data.urgency"
                  :severity="getUrgencySeverity(data.urgency)"
                />
              </template>
            </Column>
            <Column field="status" header="Status" />
          </DataTable>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  middleware: 'auth'
})

const { user } = useAuth()
const { api } = useApi()

const dashboardData = ref({})
const recentPayments = ref([])
const maintenanceRequests = ref([])
const selectedPeriod = ref('month')
const loading = ref(false)

const periodOptions = [
  { label: 'Last 7 Days', value: 'week' },
  { label: 'Last 30 Days', value: 'month' },
  { label: 'Last 90 Days', value: 'quarter' }
]

const occupancyRate = computed(() => {
  if (!dashboardData.value.total_rooms) return 0
  return Math.round((dashboardData.value.occupied_rooms / dashboardData.value.total_rooms) * 100)
})

// Fetch dashboard data based on user role
const fetchDashboardData = async () => {
  loading.value = true
  try {
    const endpoint = `/dashboard/${user.value.role}/`
    const response = await api(endpoint, {
      params: { period: selectedPeriod.value }
    })
    
    dashboardData.value = response.metrics
    recentPayments.value = response.recent_payments || []
    maintenanceRequests.value = response.maintenance_requests || []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})

const refreshData = () => {
  fetchDashboardData()
}

const onPeriodChange = () => {
  fetchDashboardData()
}
</script>

// Middleware Implementation
// middleware/auth.js
export default defineNuxtRouteMiddleware(async (to) => {
  const { user, checkAuth } = useAuth()
  
  if (!await checkAuth()) {
    return navigateTo('/login')
  }
  
  // Check role-based access
  if (to.meta.requiresRole) {
    const userRole = user.value?.role
    const requiredRoles = Array.isArray(to.meta.requiresRole) 
      ? to.meta.requiresRole 
      : [to.meta.requiresRole]
    
    if (!requiredRoles.includes(userRole)) {
      throw createError({
        statusCode: 403,
        statusMessage: 'Access Denied'
      })
    }
  }
})

// Tenant Portal Implementation
// pages/tenant/dashboard.vue
<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold">Welcome, {{ user.name }}</h1>
        <p class="text-gray-600">Room {{ tenantData.current_room?.number }}</p>
      </div>
      <Button 
        icon="pi pi-refresh"
        label="Refresh"
        severity="secondary"
        @click="refreshData"
      />
    </div>
    
    <!-- Account Summary -->
    <Card>
      <template #title>Account Summary</template>
      <template #content>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="text-center">
            <div class="text-2xl font-bold" :class="balanceColor">
              {{ formatCurrency(Math.abs(tenantData.account_balance || 0)) }}
            </div>
            <div class="text-sm text-gray-600">
              {{ tenantData.account_balance >= 0 ? 'Credit Balance' : 'Amount Owing' }}
            </div>
          </div>
          
          <div class="text-center">
            <div class="text-2xl font-bold text-blue-600">
              {{ formatCurrency(tenantData.monthly_rent || 0) }}
            </div>
            <div class="text-sm text-gray-600">Monthly Rent</div>
          </div>
          
          <div class="text-center">
            <div class="text-2xl font-bold text-green-600">
              {{ tenantData.next_due_date ? formatDate(tenantData.next_due_date) : 'N/A' }}
            </div>
            <div class="text-sm text-gray-600">Next Due Date</div>
          </div>
        </div>
      </template>
    </Card>
    
    <!-- Quick Actions -->
    <Card>
      <template #title>Quick Actions</template>
      <template #content>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Button 
            icon="pi pi-credit-card"
            label="View Payments"
            class="p-button-outlined"
            @click="navigateTo('/tenant/payments')"
          />
          <Button 
            icon="pi pi-cog"
            label="Report Issue"
            class="p-button-outlined"
            @click="navigateTo('/tenant/maintenance/create')"
          />
          <Button 
            icon="pi pi-file"
            label="My Documents"
            class="p-button-outlined"
            @click="navigateTo('/tenant/documents')"
          />
          <Button 
            icon="pi pi-bookmark"
            label="View Contract"
            class="p-button-outlined"
            @click="navigateTo('/tenant/contract')"
          />
        </div>
      </template>
    </Card>
    
    <!-- Recent Payments -->
    <Card>
      <template #title>Recent Payments</template>
      <template #content>
        <DataTable 
          :value="recentPayments"
          :paginator="false"
        >
          <template #empty>
            <div class="text-center py-8">
              <i class="pi pi-credit-card text-4xl text-gray-300 mb-4"></i>
              <p class="text-gray-500">No payments recorded yet</p>
            </div>
          </template>
          
          <Column field="name" header="Receipt No." />
          <Column field="amount" header="Amount">
            <template #body="{ data }">
              {{ formatCurrency(data.amount) }}
            </template>
          </Column>
          <Column field="payment_date" header="Date">
            <template #body="{ data }">
              {{ formatDate(data.payment_date) }}
            </template>
          </Column>
          <Column field="payment_method" header="Method" />
          <Column field="is_validated" header="Status">
            <template #body="{ data }">
              <Tag 
                :value="data.is_validated ? 'Validated' : 'Pending'"
                :severity="data.is_validated ? 'success' : 'warning'"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup>
definePageMeta({
  layout: 'tenant',
  middleware: 'tenant-auth'
})

const { user } = useAuth()
const { api } = useApi()

const tenantData = ref({})
const recentPayments = ref([])

const balanceColor = computed(() => {
  const balance = tenantData.value.account_balance || 0
  return balance >= 0 ? 'text-green-600' : 'text-red-600'
})

const fetchTenantData = async () => {
  try {
    const response = await api('/tenant/dashboard/')
    tenantData.value = response.tenant
    recentPayments.value = response.recent_payments
  } catch (error) {
    console.error('Failed to fetch tenant data:', error)
  }
}

onMounted(() => {
  fetchTenantData()
})

const refreshData = () => {
  fetchTenantData()
}
</script>

// Utility Composables
// composables/useValidation.js
export const useValidation = () => {
  const validateForm = (form, rules) => {
    const errors = {}
    
    Object.keys(rules).forEach(field => {
      const value = form[field]
      const rule = rules[field]
      
      if (rule.required && (!value || value.toString().trim() === '')) {
        errors[field] = `${field} is required`
        return
      }
      
      if (value && rule.min && value.length < rule.min) {
        errors[field] = `${field} must be at least ${rule.min} characters`
        return
      }
      
      if (value && rule.pattern && !rule.pattern.test(value)) {
        errors[field] = `${field} format is invalid`
        return
      }
    })
    
    return errors
  }
  
  return { validateForm }
}

// composables/useFormatters.js
export const useFormatters = () => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
    }).format(amount)
  }
  
  const formatDate = (date) => {
    return new Intl.DateTimeFormat('en-KE').format(new Date(date))
  }
  
  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase()
  }
  
  return { formatCurrency, formatDate, getInitials }
}