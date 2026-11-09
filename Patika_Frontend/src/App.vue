<template>
  <!-- EZ A NYITÓ TAG HIÁNYZOTT: -->
  <div class="wrap">

    <div class="header" style="display: flex; justify-content: space-between; align-items: center; width: 100%;">

      <!-- BAL OLDAL: Cím és gombok -->
      <div>
        <div class="brand">Patika Okosraktár</div>
        <div style="display:flex; gap:10px; align-items:center; margin: 5px 0 0 0;">
          <RouterLink to="/"
            style="text-decoration:none; padding:8px 12px; border:1px solid #30435f; border-radius:10px; font-size: 1rem;">
            Főoldal
          </RouterLink>
          <RouterLink to="/inventory"
            style="text-decoration:none; padding:8px 12px; border:1px solid #30435f; border-radius:10px; font-size: 1rem;">
            Leltár
          </RouterLink>
        </div>
      </div>

      <!-- JOBB OLDAL: KPI Számlálók -->
      <div class="kpis" style="display: flex; gap: 15px; align-items: center;">
        <div class="kpi"><div class="big">{{ kpis.StockCnt || 0 }}</div><div class="sub">Összes doboz</div></div>
        <div class="kpi"><div class="big">{{ kpis.ExpiredBatchCnt || 0 }}</div><div class="sub">Lejárt tételek</div></div>
        <div class="kpi"><div class="big">{{ kpis.OutOfStockBatchCnt || 0 }}</div><div class="sub">Hiánycikk</div></div>
      </div>

    </div>

    <!-- A RouterView tölti be a menüpontokhoz tartozó tartalmat -->
    <RouterView />

  <!-- Most már van mihez tartoznia ennek a záró tagnek -->
  </div>
</template>

<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { ref, onMounted } from 'vue'
import axios from 'axios'


// A KPI adatok tárolója, alapértelmezett 0-s értékekkel
const kpis = ref({
  StockCnt: 0,
  ExpiredBatchCnt: 0,
  OutOfStockBatchCnt: 0
})

onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/kpis')
    kpis.value = response.data
  } catch (error) {
    console.error('Hiba a KPI-k betöltésekor:', error)
  }
})
</script>
