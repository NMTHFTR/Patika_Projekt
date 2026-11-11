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
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px;">
      
      <!-- BAL OLDAL (50%) -->
      <div class="panel">
        <div class="section-title" style="margin-bottom: 16px;">Top Kategória Darabszám</div>
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

      <!-- JOBB OLDAL (50%) -->
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
    const catResponse = await axios.get('http://localhost:8000/api/top-categories')
    topCategories.value = catResponse.data

    const kpiResponse = await axios.get('http://localhost:8000/api/kpis')
    const realKpis = kpiResponse.data

    const soldRes = await axios.get('http://localhost:8000/api/top-sold')
    topSoldProducts.value = soldRes.data

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
