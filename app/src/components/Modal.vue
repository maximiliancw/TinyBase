<script setup lang="ts">
/**
 * Modal Component
 *
 * Standardized modal component built on PicoCSS's dialog element.
 * Provides consistent structure and behavior across the application.
 */
import { watch, onUnmounted } from "vue";
import Icon from "./Icon.vue";

interface Props {
  /** Whether the modal is open */
  open: boolean;
  /** Optional title for the modal header */
  title?: string;
}

interface Emits {
  (e: "update:open", value: boolean): void;
  (e: "close"): void;
}

const props = withDefaults(defineProps<Props>(), {
  open: false,
  title: undefined,
});

const emit = defineEmits<Emits>();

function close() {
  emit("update:open", false);
  emit("close");
}

// Watch for ESC key to close modal
let cleanup: (() => void) | null = null;

watch(
  () => props.open,
  (isOpen) => {
    if (cleanup) {
      cleanup();
      cleanup = null;
    }

    if (isOpen) {
      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === "Escape") {
          close();
        }
      };
      document.addEventListener("keydown", handleEscape);
      cleanup = () => {
        document.removeEventListener("keydown", handleEscape);
      };
    }
  }
);

onUnmounted(() => {
  if (cleanup) {
    cleanup();
  }
});
</script>

<template>
  <dialog :open="open">
    <article>
      <header v-if="title || $slots.header">
        <button aria-label="Close" rel="prev" @click="close">
          <Icon name="X" :size="20" />
        </button>
        <h3 v-if="title && !$slots.header">{{ title }}</h3>
        <slot v-else name="header" />
      </header>

      <slot />

      <footer v-if="$slots.footer">
        <slot name="footer" />
      </footer>
    </article>
  </dialog>
</template>

<style scoped>
/* Footer button layout - consistent across all modals */
footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--tb-spacing-sm);
  margin-top: var(--tb-spacing-lg);
}

footer button {
  margin: 0;
}

/* Close button styling */
header button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--tb-spacing-xs);
  margin: 0;
  margin-left: auto;
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--tb-text-muted);
  transition: color var(--tb-transition-fast);
}

header button:hover {
  color: var(--tb-text);
}
</style>
