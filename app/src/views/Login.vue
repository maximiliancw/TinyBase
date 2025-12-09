<script setup lang="ts">
/**
 * Login View
 * 
 * Premium authentication page with ambient effects and smooth interactions.
 */
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { api } from '../api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const needsSetup = ref(false)
const checkingSetup = ref(true)

onMounted(async () => {
  // Fetch instance name and setup status in parallel
  await Promise.all([
    authStore.fetchInstanceInfo(),
    api.get('/api/auth/setup-status')
      .then(response => { needsSetup.value = response.data.needs_setup })
      .catch(() => { /* Ignore errors */ })
  ])
  checkingSetup.value = false
})

async function handleLogin() {
  errorMessage.value = ''
  
  const success = await authStore.login(email.value, password.value)
  
  if (success) {
    // Redirect to intended destination or dashboard
    const redirect = route.query.redirect as string || '/'
    router.push(redirect)
  } else {
    errorMessage.value = authStore.error || 'Login failed'
  }
}
</script>

<template>
  <div class="login-layout">
    <!-- Login Card -->
    <article data-animate="fade-in">
      <!-- Logo -->
      <div class="login-logo">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
            <line x1="12" y1="22.08" x2="12" y2="12"/>
          </svg>
        </div>
        <h1>{{ authStore.instanceName }}</h1>
        <p>Admin Dashboard</p>
      </div>
      
      <!-- First-time setup notice -->
      <div v-if="needsSetup && !checkingSetup" class="setup-notice">
        <div class="setup-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
          </svg>
        </div>
        <div class="setup-content">
          <strong>Welcome!</strong>
          <p>No users exist yet. Enter your credentials to create the first admin account.</p>
        </div>
      </div>
      
      <!-- Login Form -->
      <form @submit.prevent="handleLogin">
        <label for="email">
          Email
          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="admin@example.com"
            required
            autocomplete="email"
          />
        </label>
        
        <label for="password">
          Password
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="••••••••"
            required
            autocomplete="current-password"
          />
        </label>
        
        <!-- Error message -->
        <div v-if="errorMessage" class="error-message">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {{ errorMessage }}
        </div>
        
        <button
          type="submit"
          class="login-button"
          :aria-busy="authStore.loading"
          :disabled="authStore.loading"
        >
          {{ authStore.loading ? '' : (needsSetup ? 'Create Admin & Sign In' : 'Sign In') }}
        </button>
      </form>
      
      <!-- Footer -->
      <div class="login-footer">
        <small>Powered by TinyBase</small>
      </div>
    </article>
  </div>
</template>

<style scoped>
/* Logo area */
.login-logo {
  text-align: center;
  margin-bottom: var(--tb-spacing-xl);
}

.logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 3.5rem;
  height: 3.5rem;
  background: var(--tb-gradient-primary);
  border-radius: var(--tb-radius-lg);
  box-shadow: 
    var(--tb-btn-primary-shadow-hover),
    var(--tb-shadow-glow);
  margin-bottom: var(--tb-spacing-md);
}

.logo-icon svg {
  width: 1.75rem;
  height: 1.75rem;
  color: white;
}

.login-logo h1 {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 var(--tb-spacing-xs) 0;
  background: var(--tb-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-logo p {
  margin: 0;
  color: var(--tb-text-muted);
  font-size: 0.9375rem;
}

/* Setup notice */
.setup-notice {
  display: flex;
  align-items: flex-start;
  gap: var(--tb-spacing-md);
  background: var(--tb-info-bg);
  border: 1px solid var(--tb-info-bg);
  border-radius: var(--tb-radius);
  padding: var(--tb-spacing-md);
  margin-bottom: var(--tb-spacing-xl);
}

.setup-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  background: var(--tb-info-bg);
  border-radius: var(--tb-radius);
  flex-shrink: 0;
}

.setup-icon svg {
  width: 1.125rem;
  height: 1.125rem;
  color: var(--tb-info);
}

.setup-content strong {
  display: block;
  color: var(--tb-info);
  font-size: 0.875rem;
  margin-bottom: var(--tb-spacing-xs);
}

.setup-content p {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--tb-text-secondary);
  line-height: 1.5;
}

/* Form styling */
form {
  display: flex;
  flex-direction: column;
  gap: var(--tb-spacing-md);
}

form label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--tb-text-secondary);
}

/* Error message */
.error-message {
  display: flex;
  align-items: center;
  gap: var(--tb-spacing-sm);
  padding: var(--tb-spacing-sm) var(--tb-spacing-md);
  background: var(--tb-error-bg);
  border: 1px solid var(--tb-error-bg);
  border-radius: var(--tb-radius);
  color: var(--tb-error);
  font-size: 0.8125rem;
}

.error-message svg {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

/* Login button */
.login-button {
  margin-top: var(--tb-spacing-sm);
  padding: 0.875rem var(--tb-spacing-lg);
  font-size: 0.9375rem;
  font-weight: 600;
}

/* Footer */
.login-footer {
  margin-top: var(--tb-spacing-xl);
  padding-top: var(--tb-spacing-lg);
  border-top: 1px solid var(--tb-border-subtle);
  text-align: center;
}

.login-footer small {
  color: var(--tb-text-muted);
  font-size: 0.75rem;
}
</style>
