<template>
  <div class="wrap">
    <div class="header">
      <div style="vertical-align: middle;">
        <div class="brand">Patika Okosraktár</div>
        <div style="display:flex;gap:10px;align-items:center; margin: 5px 0 0 0;">
          <RouterLink to="/"
            style="text-decoration:none;padding:8px 12px;border:1px solid #30435f;border-radius:10px; font-size: 1rem;">
            Főoldal</RouterLink>
          <RouterLink to="/inventory"
            style="text-decoration:none;padding:8px 12px;border:1px solid #30435f;border-radius:10px; font-size: 1rem;">
            Leltár</RouterLink>
        </div>
      </div>
    </div>

    <!-- A RouterView tölti be a menüpontokhoz tartozó tartalmat -->
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>
