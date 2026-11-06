<template>
  <main>
    <div class="panel">
      <!-- Eszközök (Gyógyszerek) KPI -->
      <div>
        <div class="section-title" style="margin-bottom:16px;">Gyógyszerek</div>
        <div class="kpis">
          <div class="kpi">Összes<div class="big">{{ stats.all }}</div>
          </div>
          <div class="kpi">Szabad készlet<div class="big">{{ stats.free }}</div>
          </div>
          <div class="kpi">Használatban<div class="big">{{ stats.assigned }}</div>
          </div>
        </div>
      </div>

      <!-- Projektek KPI -->
      <div style="margin-top: 30px;">
        <div class="section-title" style="margin-bottom:16px;">Projektek</div>
        <div class="kpis">
          <div class="kpi">Összes projekt<div class="big">{{ projects.all }}</div>
          </div>
          <div class="kpi">Aktív<div class="big">{{ projects.active }}</div>
          </div>
          <div class="kpi">Inaktív<div class="big">{{ projects.inactive }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Top Kategóriák Táblázat -->
    <div class="panel" style="margin-top: 16px;">
      <div class="section-title" style="margin-bottom:16px;">Top Kategória Darabszám</div>
      <table class="grid">
        <thead>
          <tr>
            <th>Kategória</th>
            <th>Darab</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cat in topCategories" :key="cat.name">
            <td>{{ cat.name }}</td>
            <td>{{ cat.count }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Mintaadatok a felület teszteléséhez (később a Python backendről jönnek)
const stats = ref({ all: 3200, free: 2850, assigned: 350 })
const projects = ref({ all: 15, active: 12, inactive: 3 })

const topCategories = ref([
  { name: 'Fájdalomcsillapítók', count: 850 },
  { name: 'Vitaminok és ásványi anyagok', count: 620 },
  { name: 'Antibiotikumok', count: 315 },
  { name: 'Lázcsillapítók', count: 210 }
])
</script>
