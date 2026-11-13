<template>
  <main>
    <div class="panel">
      <!-- Eszközök (Gyógyszerek) KPI -->
      <div>
        <div class="section-title" style="margin-bottom:16px;">Gyógyszerek</div>
        <div class="kpis">
          <div class="kpi">Különböző gyógyszerfajták<div class="big">{{ stats.all }}</div>
          </div>
          <div class="kpi">Összes fizikai doboz<div class="big">{{ stats.free }}</div>
          </div>
          <div class="kpi">Raktári bejegyzések<div class="big">{{ stats.assigned }}</div>
          </div>
        </div>
      </div>


      <div style="margin-top: 30px;">
        <div class="section-title" style="margin-bottom:16px;">Készletállapot</div>
        <div class="kpis">
          <div class="kpi">Érvényes szavatosságú doboz<div class="big">{{ projects.all }}</div>
          </div>
          <div class="kpi">Lejárt tételek (Selejt)<div class="big">{{ projects.active }}</div>
          </div>
          <div class="kpi">Kifogyott termékek (Hiánycikk)<div class="big">{{ projects.inactive }}</div>
          </div>
        </div>
      </div>
    </div>

        <!-- Kétoszlopos fele-fele elrendezés -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 16px; margin-top: 16px;">
      
      <div class="panel">
        <div class="section-title" style="margin-bottom: 16px;">Top Kategória Darabszám</div>
        <table class="grid">
          <thead>
            <tr>
              <th>Kategória</th>
              <th style="text-align: right;">Darab</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cat in topCategories" :key="cat.Category">
              <td>{{ cat.Category }}</td>
              <td style="text-align: right; font-weight: bold;">{{ cat.Cnt }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="panel">
        <div class="section-title" style="margin-bottom: 16px;">Legtöbbet Eladott Termékek</div>
        <table class="grid">
          <thead>
            <tr>
              <th>Termék megnevezése</th>
              <th style="text-align: right;">Eladott darab</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in topSoldProducts" :key="index">
              <td>{{ item.Name }}</td>
              <td style="text-align: right; font-weight: bold;">{{ item.TotalSold }} db</td>
            </tr>
            <tr v-if="!topSoldProducts || topSoldProducts.length === 0">
              <td colspan="2" style="text-align: center; color: var(--muted); padding: 16px;">
                Még nincs rögzített eladás az adatbázisban.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </main>
</template>

<script setup lang="ts">
// 1. BE KELL IMPORTÁLNI AZ ONMOUNTED-ET ÉS AZ AXIOS-T!
import { ref, onMounted } from 'vue'
import axios from 'axios'

// Ezek most már nem dummy adatok, hanem a valós értékek tárolói lesznek:
const stats = ref({ all: 0, free: 0, assigned: 0 })
const projects = ref({ all: 0, active: 0, inactive: 0 })

const topCategories = ref<any[]>([])


const topSoldProducts = ref<any[]>([])


onMounted(async () => {
  try {
    // Párhuzamosítjuk a 3 kérést, így nem várják meg egymást
    const [catResponse, kpiResponse, soldRes] = await Promise.all([
      axios.get('http://localhost:8000/api/top-categories'),
      axios.get('http://localhost:8000/api/kpis'),
      axios.get('http://localhost:8000/api/top-sold')
    ])

    topCategories.value = catResponse.data
    topSoldProducts.value = soldRes.data
    const realKpis = kpiResponse.data

    stats.value = {
      all: realKpis.ProductCnt,
      free: realKpis.StockCnt,
      assigned: realKpis.BatchCnt
    }

    projects.value = {
      all: realKpis.StockCnt - realKpis.ExpiredBatchCnt,
      active: realKpis.ExpiredBatchCnt,
      inactive: realKpis.OutOfStockBatchCnt
    }
  } catch (error) {
    console.error('Hiba az adatok betöltésekor:', error)
  }
})



</script>
