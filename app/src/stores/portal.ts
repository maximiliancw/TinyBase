/**
 * Portal Store
 *
 * Manages portal configuration (instance name, logo, colors)
 * and applies them to the UI.
 */

import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { api } from "../api";

interface PortalConfig {
  instance_name: string;
  logo_url: string | null;
  primary_color: string | null;
  background_color: string | null;
  registration_enabled: boolean;
}

export const usePortalStore = defineStore("portal", () => {
  const config = ref<PortalConfig>({
    instance_name: "TinyBase",
    logo_url: null,
    primary_color: null,
    background_color: null,
    registration_enabled: true,
  });

  const loading = ref(false);
  const error = ref<string | null>(null);

  // Computed styles based on config
  const styles = computed(() => {
    const style: Record<string, string> = {};
    if (config.value.background_color) {
      style["--pico-background-color"] = config.value.background_color;
    }
    if (config.value.primary_color) {
      style["--pico-primary"] = config.value.primary_color;
      style["--pico-primary-background"] = config.value.primary_color;
      style["--pico-primary-underline"] = config.value.primary_color;
    }
    return style;
  });

  async function fetchConfig() {
    loading.value = true;
    error.value = null;

    try {
      const response = await api.get("/api/auth/portal-config");
      config.value = response.data;
    } catch (err: any) {
      error.value =
        err.response?.data?.detail || "Failed to load portal configuration";
      console.error("Failed to fetch portal config:", err);
    } finally {
      loading.value = false;
    }
  }

  return {
    config,
    loading,
    error,
    styles,
    fetchConfig,
  };
});
