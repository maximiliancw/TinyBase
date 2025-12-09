<script setup lang="ts">
/**
 * Users View
 * 
 * Manage user accounts (admin only).
 * Uses semantic HTML elements following PicoCSS conventions.
 */
import { onMounted, ref } from 'vue'
import { useUsersStore } from '../stores/users'

const usersStore = useUsersStore()

const showCreateModal = ref(false)
const newUser = ref({
  email: '',
  password: '',
  is_admin: false,
})

onMounted(async () => {
  await usersStore.fetchUsers()
})

async function handleCreate() {
  const result = await usersStore.createUser(newUser.value)
  if (result) {
    showCreateModal.value = false
    newUser.value = { email: '', password: '', is_admin: false }
  }
}

async function handleToggleAdmin(userId: string, currentStatus: boolean) {
  await usersStore.updateUser(userId, { is_admin: !currentStatus })
}

async function handleDelete(userId: string) {
  if (confirm('Are you sure you want to delete this user?')) {
    await usersStore.deleteUser(userId)
  }
}
</script>

<template>
  <div data-animate="fade-in">
    <header class="page-header">
      <hgroup>
        <h1>Users</h1>
        <p>Manage user accounts</p>
      </hgroup>
      <button @click="showCreateModal = true">
        + New User
      </button>
    </header>
    
    <!-- Loading State -->
    <article v-if="usersStore.loading" aria-busy="true">
      Loading users...
    </article>
    
    <!-- Users Table -->
    <article v-else>
      <table>
        <thead>
          <tr>
            <th>Email</th>
            <th>Role</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in usersStore.users" :key="user.id">
            <td>{{ user.email }}</td>
            <td>
              <mark :data-status="user.is_admin ? 'info' : 'neutral'">
                {{ user.is_admin ? 'Admin' : 'User' }}
              </mark>
            </td>
            <td><small class="text-muted">{{ new Date(user.created_at).toLocaleDateString() }}</small></td>
            <td>
              <div role="group">
                <button
                  class="small secondary"
                  @click="handleToggleAdmin(user.id, user.is_admin)"
                >
                  {{ user.is_admin ? 'Remove Admin' : 'Make Admin' }}
                </button>
                <button class="small contrast" @click="handleDelete(user.id)">
                  Delete
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </article>
    
    <!-- Create User Modal - using Pico's dialog element -->
    <dialog :open="showCreateModal">
      <article>
        <header>
          <button aria-label="Close" rel="prev" @click="showCreateModal = false"></button>
          <h3>Create User</h3>
        </header>
        
        <form @submit.prevent="handleCreate">
          <label for="email">
            Email
            <input
              id="email"
              v-model="newUser.email"
              type="email"
              required
            />
          </label>
          
          <label for="password">
            Password
            <input
              id="password"
              v-model="newUser.password"
              type="password"
              minlength="8"
              required
            />
          </label>
          
          <label>
            <input type="checkbox" v-model="newUser.is_admin" role="switch" />
            Admin privileges
          </label>
          
          <small v-if="usersStore.error" class="text-error">
            {{ usersStore.error }}
          </small>
          
          <footer>
            <button type="button" class="secondary" @click="showCreateModal = false">
              Cancel
            </button>
            <button type="submit" :aria-busy="usersStore.loading" :disabled="usersStore.loading">
              {{ usersStore.loading ? '' : 'Create User' }}
            </button>
          </footer>
        </form>
      </article>
    </dialog>
  </div>
</template>

<style scoped>
/* Page header layout */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-header hgroup {
  margin: 0;
}

.page-header hgroup h1 {
  margin-bottom: var(--tb-spacing-xs);
}

.page-header hgroup p {
  margin: 0;
  color: var(--pico-muted-color);
}

/* Dialog footer buttons */
dialog article footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--tb-spacing-sm);
}
</style>
