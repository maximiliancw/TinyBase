<script setup lang="ts">
/**
 * Login View
 * 
 * Authentication page for admin users.
 * Uses semantic HTML elements following PicoCSS conventions.
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
  try {
    const response = await api.get('/api/auth/setup-status')
    needsSetup.value = response.data.needs_setup
  } catch {
    // Ignore errors, just don't show the setup message
  } finally {
    checkingSetup.value = false
  }
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
  <!-- Login layout: full viewport, centered -->
  <div class="login-layout">
    <!-- Article is Pico's card element -->
    <article data-animate="fade-in">
      <h1>🔐 TinyBase</h1>
      <p class="text-muted text-center mb-3">
        Admin Dashboard
      </p>
      
      <!-- First-time setup notice -->
      <div v-if="needsSetup && !checkingSetup" class="setup-notice mb-3">
        <strong>👋 Welcome!</strong>
        <p>No users exist yet. Enter your email and password to create the first admin account.</p>
      </div>
      
      <!-- Form elements are auto-styled by Pico -->
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
        
        <small v-if="errorMessage" class="text-error">
          {{ errorMessage }}
        </small>
        
        <!-- Pico handles aria-busy loading state automatically -->
        <button
          type="submit"
          :aria-busy="authStore.loading"
          :disabled="authStore.loading"
        >
          {{ authStore.loading ? '' : (needsSetup ? 'Create Admin & Sign In' : 'Sign In') }}
        </button>
      </form>
    </article>
  </div>
</template>

<style scoped>
.setup-notice {
  background: rgba(99, 179, 237, 0.15);
  border: 1px solid var(--tb-info);
  border-radius: var(--tb-radius);
  padding: var(--tb-spacing-md);
  text-align: center;
}

.setup-notice strong {
  color: var(--tb-info);
}

.setup-notice p {
  margin: var(--tb-spacing-xs) 0 0 0;
  font-size: 0.875rem;
  opacity: 0.9;
}
</style>
