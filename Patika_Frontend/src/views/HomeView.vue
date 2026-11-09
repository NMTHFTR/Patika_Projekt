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
          <tr v-for="cat in topCategories" :key="cat.Category">
            <td>{{ cat.Category }}</td>
            <td>{{ cat.Cnt }}</td>
          </tr>
        </tbody>
      </table>
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







onMounted(async () => {
  try {
    // 1. Top kategóriák lekérése a táblázathoz
    const catResponse = await axios.get('http://localhost:8000/api/top-categories')
    topCategories.value = catResponse.data

    // 2. KPI adatok lekérése a felső statisztika dobozokhoz
    // (Ugyanazt a végpontot használjuk, amit a fejlécben lévő 3 kis doboznál is)
    const kpiResponse = await axios.get('http://localhost:8000/api/kpis')
    const realKpis = kpiResponse.data

    // 3. Rákötjük a valós adatokat a régi dummy változókra:
    // GYÓGYSZEREK doboz:
    stats.value = {
      all: realKpis.ProductCnt,        // Különböző gyógyszerfajták száma
      free: realKpis.StockCnt,         // Összes fizikai doboz a raktárban
      assigned: realKpis.BatchCnt      // Raktári bejegyzések/tételek száma
    }

    // PROJEKTEK doboz (Ezt a HTML-ben majd átírhatod "Készletállapot"-ra):
    projects.value = {
      all: realKpis.StockCnt,          // Összes doboz
      active: realKpis.StockCnt - realKpis.ExpiredBatchCnt, // Jó szavatosságú dobozok
      inactive: realKpis.ExpiredBatchCnt // Lejárt dobozok
    }

    stats.value = {
      all: realKpis.ProductCnt,        // Különböző gyógyszerfajták (7)
      free: realKpis.StockCnt,         // Összes fizikai doboz (734)
      assigned: realKpis.BatchCnt      // Raktári bejegyzések (9)
    }

    // KÉSZLETÁLLAPOT doboz (A régi "Projektek"):
    projects.value = {
      // Érvényes = Összes doboz mínusz a lejártak
      all: realKpis.StockCnt - realKpis.ExpiredBatchCnt,

      // Lejárt = ExpiredBatchCnt
      active: realKpis.ExpiredBatchCnt,

      // Kifogyott = OutOfStockBatchCnt
      inactive: realKpis.OutOfStockBatchCnt
    }

  } catch (error) {
    console.error('Hiba az adatok betöltésekor:', error)
  }
})
</script>
