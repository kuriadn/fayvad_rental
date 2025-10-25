# 🎨 Fayvad Theme CSS Integration Guide

## Overview
This guide demonstrates how the enhanced `fayvad-theme.css` integrates with the design system outlined in `ideas.md` to create a cohesive, professional property management interface.

## 🎯 Design System Integration

### **Brand Colors & Variables**
The CSS now includes comprehensive design tokens that match the ideas document:

```css
:root {
  /* Fayvad Brand Colors */
  --fayvad-gold: #C8861D;     /* Primary actions, revenue, highlights */
  --fayvad-navy: #1E3A5F;     /* Headers, navigation, primary text */
  --fayvad-blue: #4A90B8;     /* Secondary actions, occupied status */
  --fayvad-light-blue: #87CEEB; /* Subtle accents, backgrounds */
  
  /* Spacing System */
  --spacing-xs: 0.25rem;      /* 4px */
  --spacing-sm: 0.5rem;       /* 8px */
  --spacing-md: 1rem;         /* 16px */
  --spacing-lg: 1.5rem;       /* 24px */
  --spacing-xl: 2rem;         /* 32px */
  --spacing-2xl: 3rem;        /* 48px */
  
  /* Border Radius */
  --radius-sm: 0.25rem;       /* 4px */
  --radius-md: 0.5rem;        /* 8px */
  --radius-lg: 0.75rem;       /* 12px */
  --radius-xl: 1rem;          /* 16px */
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  --shadow-fayvad: 0 4px 20px rgba(200, 134, 29, 0.15);
}
```

## 🧩 Component Implementation Examples

### **1. Page Layout Structure (SUNY Orange Pattern)**

```vue
<template>
  <div class="page-container">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">{{ pageTitle }}</h1>
      <p class="page-subtitle">{{ pageSubtitle }}</p>
      <div class="page-actions">
        <Button label="Primary Action" icon="pi-plus" />
        <Button label="Secondary" class="p-button-outlined" />
      </div>
    </div>
    
    <!-- Page Content -->
    <div class="page-content">
      <!-- Your content here -->
    </div>
  </div>
</template>
```

**CSS Classes Used:**
- `.page-container` - Main page wrapper with consistent padding
- `.page-header` - Header section with bottom border
- `.page-title` - Large, bold title in Fayvad navy
- `.page-subtitle` - Secondary text in muted color
- `.page-actions` - Action buttons container

### **2. Base Card Component**

```vue
<template>
  <div class="base-card border-left-gold hover-lift">
    <div class="card-header">
      <h3>Card Title</h3>
      <div class="card-actions">
        <Button icon="pi-edit" class="p-button-text" />
        <Button icon="pi-trash" class="p-button-text p-button-danger" />
      </div>
    </div>
    
    <div class="card-content">
      <p>Card content goes here...</p>
    </div>
  </div>
</template>
```

**CSS Classes Used:**
- `.base-card` - Base card styling with consistent borders and shadows
- `.border-left-gold` - Gold accent border on the left
- `.hover-lift` - Subtle lift animation on hover
- `.card-header` - Header section with title and actions
- `.card-actions` - Action buttons container

### **3. Dashboard Metrics Grid**

```vue
<template>
  <div class="grid">
    <div class="col-12 md:col-3">
      <div class="metric-card navy-accent">
        <i class="pi pi-users metric-icon"></i>
        <div class="metric-value">{{ totalTenants }}</div>
        <div class="metric-label">Active Tenants</div>
      </div>
    </div>
    
    <div class="col-12 md:col-3">
      <div class="metric-card blue-accent">
        <i class="pi pi-home metric-icon"></i>
        <div class="metric-value">{{ availableRooms }}</div>
        <div class="metric-label">Available Rooms</div>
      </div>
    </div>
  </div>
</template>
```

**CSS Classes Used:**
- `.metric-card` - Base metric card with gradient background
- `.navy-accent` - Navy accent border
- `.blue-accent` - Blue accent border
- `.metric-icon` - Icon styling in Fayvad gold
- `.metric-value` - Large, bold metric number
- `.metric-label` - Descriptive label below metric

### **4. Quick Actions Grid**

```vue
<template>
  <div class="quick-actions">
    <div class="quick-action-card" @click="addTenant">
      <i class="pi pi-user-plus quick-action-icon"></i>
      <div class="quick-action-title">Add Tenant</div>
      <div class="quick-action-description">Register new tenant</div>
    </div>
    
    <div class="quick-action-card" @click="recordPayment">
      <i class="pi pi-credit-card quick-action-icon"></i>
      <div class="quick-action-title">Record Payment</div>
      <div class="quick-action-description">Process rent payment</div>
    </div>
  </div>
</template>
```

**CSS Classes Used:**
- `.quick-actions` - Grid container for action cards
- `.quick-action-card` - Individual action card with hover effects
- `.quick-action-icon` - Large icon in Fayvad gold
- `.quick-action-title` - Action title in navy
- `.quick-action-description` - Descriptive text in muted color

### **5. Status Tags**

```vue
<template>
  <div>
    <span class="status-available">Available</span>
    <span class="status-occupied">Occupied</span>
    <span class="status-maintenance">Maintenance</span>
    <span class="status-overdue">Overdue</span>
    <span class="status-pending">Pending</span>
  </div>
</template>
```

**CSS Classes Used:**
- `.status-available` - Green background for available status
- `.status-occupied` - Blue background for occupied status
- `.status-maintenance` - Orange background for maintenance
- `.status-overdue` - Red background for overdue status
- `.status-pending` - Yellow background for pending status

### **6. Filter Bar Component**

```vue
<template>
  <div class="filter-bar">
    <div class="filter-group">
      <label>Search:</label>
      <InputText v-model="searchTerm" placeholder="Search..." />
      
      <label>Status:</label>
      <Dropdown v-model="selectedStatus" :options="statusOptions" />
      
      <Button label="Apply Filters" icon="pi pi-filter" />
    </div>
  </div>
</template>
```

**CSS Classes Used:**
- `.filter-bar` - Filter container with light background
- `.filter-group` - Flex container for filter elements

### **7. Activity Timeline**

```vue
<template>
  <div class="activity-timeline">
    <div class="timeline-item" v-for="activity in activities" :key="activity.id">
      <div class="timeline-icon">
        <i :class="activity.icon"></i>
      </div>
      <div class="timeline-content">
        <h4>{{ activity.title }}</h4>
        <p>{{ activity.description }}</p>
        <div class="timeline-time">{{ activity.time }}</div>
      </div>
    </div>
  </div>
</template>
```

**CSS Classes Used:**
- `.activity-timeline` - Timeline container with card styling
- `.timeline-item` - Individual timeline item with flex layout
- `.timeline-icon` - Circular icon container in Fayvad gold
- `.timeline-content` - Content area with title, description, and time
- `.timeline-time` - Timestamp in muted color

### **8. Room Grid with Status**

```vue
<template>
  <div class="room-grid">
    <div 
      v-for="room in rooms" 
      :key="room.id"
      :class="['room-card', room.status]"
    >
      <div class="room-header">
        <h3>{{ room.name }}</h3>
        <span :class="`status-${room.status}`">{{ room.status }}</span>
      </div>
      <div class="room-details">
        <p>Floor: {{ room.floor }}</p>
        <p>Rent: ${{ room.rent }}/month</p>
      </div>
    </div>
  </div>
</template>
```

**CSS Classes Used:**
- `.room-grid` - Responsive grid layout for rooms
- `.room-card` - Base room card styling
- `.room-card.available` - Green accent for available rooms
- `.room-card.occupied` - Blue accent for occupied rooms
- `.room-card.maintenance` - Orange accent for maintenance rooms

### **9. Data Table with Enhanced Styling**

```vue
<template>
  <DataTable 
    :value="tenants"
    :paginator="true"
    :rows="20"
    responsiveLayout="scroll"
    selectionMode="multiple"
    v-model:selection="selectedTenants"
  >
    <Column field="name" header="Name">
      <template #body="slotProps">
        <div class="tenant-name">
          <Avatar :label="getInitials(slotProps.data.name)" />
          <span>{{ slotProps.data.name }}</span>
        </div>
      </template>
    </Column>
    
    <Column field="status" header="Status">
      <template #body="slotProps">
        <span :class="`status-${slotProps.data.status}`">
          {{ slotProps.data.status }}
        </span>
      </template>
    </Column>
  </DataTable>
</template>
```

**CSS Classes Used:**
- Enhanced PrimeVue DataTable styling with Fayvad colors
- Custom status tags for different tenant states
- Consistent spacing and typography

### **10. Floating Action Button (Mobile)**

```vue
<template>
  <button 
    v-if="showFAB"
    class="floating-action-button"
    @click="primaryAction"
    :title="actionLabel"
  >
    <i :class="actionIcon"></i>
  </button>
</template>
```

**CSS Classes Used:**
- `.floating-action-button` - Fixed position FAB with hover effects
- Responsive positioning for mobile devices

## 🎨 Utility Classes

### **Color Utilities**
```css
.text-fayvad-gold    /* Gold text color */
.text-fayvad-navy    /* Navy text color */
.text-fayvad-blue    /* Blue text color */

.bg-fayvad-gold      /* Gold background */
.bg-fayvad-navy      /* Navy background */
.bg-fayvad-blue      /* Blue background */

.border-fayvad-gold  /* Gold border */
.border-fayvad-navy  /* Navy border */
.border-fayvad-blue  /* Blue border */
```

### **Spacing Utilities**
```css
/* Use CSS variables for consistent spacing */
padding: var(--spacing-lg);    /* 24px */
margin: var(--spacing-xl);     /* 32px */
gap: var(--spacing-md);        /* 16px */
```

### **Animation Utilities**
```css
.fade-in-up          /* Fade in from bottom animation */
.hover-lift          /* Lift effect on hover */
.stagger-children    /* Staggered animation for lists */
```

## 📱 Responsive Design

The CSS includes comprehensive responsive breakpoints:

```css
/* Mobile First Approach */
@media (max-width: 768px) {
  .page-container { padding: var(--spacing-md); }
  .room-grid { grid-template-columns: 1fr; }
  .quick-actions { grid-template-columns: 1fr; }
  .page-actions { flex-direction: column; }
}
```

## 🚀 Best Practices

### **1. Consistent Spacing**
Always use the predefined spacing variables:
```css
/* ✅ Good */
padding: var(--spacing-lg);
margin-bottom: var(--spacing-xl);

/* ❌ Avoid */
padding: 24px;
margin-bottom: 32px;
```

### **2. Component Composition**
Build complex components by combining base classes:
```vue
<template>
  <div class="base-card border-left-gold hover-lift">
    <div class="card-header">
      <h3 class="page-title">Component Title</h3>
    </div>
  </div>
</template>
```

### **3. Status Consistency**
Use the predefined status classes for all status indicators:
```vue
<template>
  <!-- ✅ Consistent status styling -->
  <span class="status-available">Available</span>
  <span class="status-occupied">Occupied</span>
  
  <!-- ❌ Avoid custom status styling -->
  <span style="background: green; color: white;">Available</span>
</template>
```

### **4. Responsive Considerations**
Always test components at different breakpoints and use the responsive utilities:
```css
/* Mobile optimizations */
@media (max-width: 768px) {
  .floating-action-button {
    bottom: var(--spacing-lg);
    right: var(--spacing-lg);
  }
}
```

## 🔧 Customization

### **Adding New Status Types**
```css
.status-custom {
  background: var(--custom-color);
  color: white;
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 500;
}
```

### **Creating New Component Variants**
```css
.base-card.border-left-custom {
  border-left: 4px solid var(--custom-color);
}

.metric-card.custom-accent {
  border-left-color: var(--custom-color);
}
```

## 📚 Integration Checklist

- [ ] Import `fayvad-theme.css` in your main app file
- [ ] Use the predefined CSS variables for colors, spacing, and shadows
- [ ] Implement the page layout structure with `.page-container` and `.page-header`
- [ ] Use `.base-card` as the foundation for all card components
- [ ] Apply status classes consistently across the application
- [ ] Test responsive behavior at all breakpoints
- [ ] Use utility classes for quick styling needs
- [ ] Follow the component composition patterns shown in examples

## 🎯 Next Steps

1. **Component Library**: Create Vue components that use these CSS classes
2. **Storybook**: Set up Storybook to showcase all component variations
3. **Design Tokens**: Export CSS variables as design tokens for other tools
4. **Accessibility**: Ensure all components meet WCAG 2.1 AA standards
5. **Performance**: Optimize CSS delivery and minimize unused styles

---

This integration guide provides a solid foundation for building the Fayvad Rentals system with a professional, consistent design that follows both the Fayvad brand guidelines and SUNY Orange's information architecture patterns.
