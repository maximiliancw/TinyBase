<script setup lang="ts">
/**
 * Main App Component
 *
 * Provides the main layout with sidebar navigation and router outlet.
 * Uses semantic HTML elements following PicoCSS conventions.
 */
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "./stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const showSidebar = computed(() => {
  return (
    authStore.isAuthenticated && router.currentRoute.value.name !== "login"
  );
});

function handleLogout() {
  authStore.logout();
  router.push("/login");
}
</script>

<template>
  <div id="app-root" :class="{ 'has-sidebar': showSidebar }">
    <!-- Sidebar Navigation - uses semantic <aside> and <nav> -->
    <aside v-if="showSidebar" class="sidebar">
      <header>
        <h1>TinyBase</h1>
      </header>

      <nav aria-label="Main navigation">
        <section>
          <small>Admin</small>
          <ul>
            <li>
              <router-link to="/">
                <span aria-hidden="true">📊</span> Dashboard
              </router-link>
            </li>
            <li>
              <router-link to="/settings">
                <span aria-hidden="true">⚙️</span> Settings
              </router-link>
            </li>
          </ul>
        </section>

        <section>
          <small>Database</small>
          <ul>
            <li>
              <router-link to="/users">
                <span aria-hidden="true">👥</span> Users
              </router-link>
            </li>
            <li>
              <router-link to="/collections">
                <span aria-hidden="true">📁</span> Collections
              </router-link>
            </li>
          </ul>
        </section>

        <section v-if="authStore.isAdmin">
          <small>Functions</small>
          <ul>
            <li>
              <router-link to="/functions">
                <span aria-hidden="true">⚡</span> Overview
              </router-link>
            </li>
            <li>
              <router-link to="/schedules">
                <span aria-hidden="true">🕐</span> Schedules
              </router-link>
            </li>
            <li>
              <router-link to="/function-calls">
                <span aria-hidden="true">📋</span> Function Calls
              </router-link>
            </li>
          </ul>
        </section>

        <section>
          <ul>
            <li>
              <a href="#" @click.prevent="handleLogout">
                <span aria-hidden="true">🚪</span> Logout
              </a>
            </li>
          </ul>
        </section>
      </nav>

      <footer v-if="authStore.user">
        <small class="text-muted">
          Logged in as<br />
          <strong>{{ authStore.user.email }}</strong>
          <mark v-if="authStore.isAdmin" data-status="info">Admin</mark>
        </small>
      </footer>
    </aside>

    <!-- Main Content Area -->
    <main>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Sidebar footer positioning */
aside.sidebar {
  display: flex;
  flex-direction: column;
}

aside.sidebar > footer {
  margin-top: auto;
  padding: var(--tb-spacing-md);
}

aside.sidebar > footer mark {
  margin-left: var(--tb-spacing-xs);
}
</style>
