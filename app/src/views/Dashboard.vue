<script setup lang="ts">
/**
 * Dashboard View
 * 
 * Overview page showing key metrics and quick links.
 * Uses semantic HTML elements following PicoCSS conventions.
 */
import { onMounted, ref } from 'vue'
import { useCollectionsStore } from '../stores/collections'
import { useFunctionsStore } from '../stores/functions'
import { useAuthStore } from '../stores/auth'

const collectionsStore = useCollectionsStore()
const functionsStore = useFunctionsStore()
const authStore = useAuthStore()

const stats = ref({
  collections: 0,
  functions: 0,
  recentCalls: 0,
  activeSchedules: 0,
})

const showAdminCreatedNotice = ref(authStore.adminCreated)

onMounted(async () => {
  // Clear the flag after showing
  if (authStore.adminCreated) {
    authStore.clearAdminCreated()
  }
  
  await collectionsStore.fetchCollections()
  await functionsStore.fetchFunctions()
  
  stats.value.collections = collectionsStore.collections.length
  stats.value.functions = functionsStore.functions.length
  
  if (authStore.isAdmin) {
    const callsResult = await functionsStore.fetchFunctionCalls({ limit: 1 })
    stats.value.recentCalls = callsResult.total
    
    await functionsStore.fetchSchedules()
    stats.value.activeSchedules = functionsStore.schedules.filter(s => s.is_active).length
  }
})

function dismissNotice() {
  showAdminCreatedNotice.value = false
}
</script>

<template>
  <div data-animate="fade-in">
    <!-- Admin Created Notice -->
    <article v-if="showAdminCreatedNotice" data-status="success" class="notice mb-3">
      <div class="notice-content">
        <strong>🎉 Admin account created!</strong>
        <p>No users existed, so an admin account was automatically created with your credentials.</p>
      </div>
      <button class="secondary small" @click="dismissNotice">Dismiss</button>
    </article>
    
    <header class="page-header">
      <h1>Dashboard</h1>
      <p>Welcome to TinyBase Admin</p>
    </header>
    
    <!-- Stats Grid - uses article for cards (Pico's card element) -->
    <div class="stats-grid">
      <article class="stat-card">
        <p>{{ stats.collections }}</p>
        <p>Collections</p>
      </article>
      <article class="stat-card">
        <p>{{ stats.functions }}</p>
        <p>Functions</p>
      </article>
      <article v-if="authStore.isAdmin" class="stat-card">
        <p>{{ stats.activeSchedules }}</p>
        <p>Active Schedules</p>
      </article>
      <article v-if="authStore.isAdmin" class="stat-card">
        <p>{{ stats.recentCalls }}</p>
        <p>Total Function Calls</p>
      </article>
    </div>
    
    <!-- Quick Actions Card -->
    <article>
      <header>
        <h3>Quick Actions</h3>
      </header>
      <div role="group">
        <router-link to="/collections" role="button" class="secondary">
          <span aria-hidden="true">📁</span> View Collections
        </router-link>
        <router-link to="/functions" role="button" class="secondary">
          <span aria-hidden="true">⚡</span> View Functions
        </router-link>
        <router-link v-if="authStore.isAdmin" to="/users" role="button" class="secondary">
          <span aria-hidden="true">👥</span> Manage Users
        </router-link>
      </div>
    </article>
    
    <!-- Recent Collections Card -->
    <article>
      <header>
        <h3>Recent Collections</h3>
        <router-link to="/collections" role="button" class="secondary small">
          View All
        </router-link>
      </header>
      
      <div v-if="collectionsStore.collections.length === 0" data-empty data-empty-icon="📁">
        <p>No collections yet</p>
        <router-link to="/collections" role="button" class="small mt-2">
          Create Collection
        </router-link>
      </div>
      
      <table v-else>
        <thead>
          <tr>
            <th>Name</th>
            <th>Label</th>
            <th>Fields</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="collection in collectionsStore.collections.slice(0, 5)" :key="collection.id">
            <td>
              <router-link :to="`/collections/${collection.name}`">
                {{ collection.name }}
              </router-link>
            </td>
            <td>{{ collection.label }}</td>
            <td>{{ collection.schema?.fields?.length || 0 }}</td>
          </tr>
        </tbody>
      </table>
    </article>
  </div>
</template>
