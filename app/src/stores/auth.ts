/**
 * Authentication Pinia Store
 * 
 * Manages user authentication state, login/logout operations,
 * and token persistence.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../api'

export interface User {
  id: string
  email: string
  is_admin: boolean
  created_at: string
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref<string | null>(localStorage.getItem('tinybase_token'))
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const adminCreated = ref(false)
  const instanceName = ref<string>('TinyBase')

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_admin ?? false)

  // Actions
  async function login(email: string, password: string): Promise<boolean> {
    loading.value = true
    error.value = null
    adminCreated.value = false

    try {
      const response = await api.post('/api/auth/login', { email, password })
      const data = response.data

      token.value = data.token
      localStorage.setItem('tinybase_token', data.token)
      
      // Check if admin was auto-created
      if (data.admin_created) {
        adminCreated.value = true
      }

      // Fetch full user info
      await fetchUser()

      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchUser(): Promise<void> {
    if (!token.value) {
      throw new Error('No token available')
    }

    try {
      const response = await api.get('/api/auth/me')
      user.value = response.data
    } catch (err) {
      // Token might be invalid
      logout()
      throw err
    }
  }

  function logout(): void {
    token.value = null
    user.value = null
    localStorage.removeItem('tinybase_token')
  }

  function clearAdminCreated(): void {
    adminCreated.value = false
  }

  async function fetchInstanceInfo(): Promise<void> {
    try {
      const response = await api.get('/api/auth/instance-info')
      instanceName.value = response.data.instance_name
    } catch (err) {
      // Fallback to default name if fetch fails
      instanceName.value = 'TinyBase'
    }
  }

  return {
    // State
    token,
    user,
    loading,
    error,
    adminCreated,
    instanceName,
    // Getters
    isAuthenticated,
    isAdmin,
    // Actions
    login,
    fetchUser,
    logout,
    clearAdminCreated,
    fetchInstanceInfo,
  }
})

