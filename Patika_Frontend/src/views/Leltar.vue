<!-- src/views/Leltar.vue -->
<template>
  <div class="wrap">
    <!-- Felső KPI rész -->


    <!-- A TE EREDETI ÚRLAPOD (Megmaradt változtatás nélkül) -->
    <div class="panel" style="margin-bottom: 16px">
      <div class="section-title">Új tétel felvétele</div>
      <table class="grid" style="margin-top: 6px">
                <thead>
          <tr>
            <th style="width: 15%">Vonalkód</th>
            <th style="width: 25%">Megnevezés</th>
            <th style="width: 15%">Kategória</th>
            <th style="width: 15%">Tároló / Polc</th>
            <th style="width: 15%">Lejárati idő</th>
            <th style="width: 15%">Mennyiség (db)</th> <!-- ÚJ OSZLOP -->
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><input type="text" v-model="newItem.barcode" placeholder="Minimum 6 karakter..." /></td>
            <td><input type="text" v-model="newItem.name" placeholder="Gyógyszer neve" /></td>
            <td>
              <select v-model="newItem.category">
                <option value="" disabled>Válassz kategóriát...</option>
                <option v-for="category in categories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </td>
            <td>
              <select v-model="newItem.location">
                <option value="">– válassz –</option>
                <option value="A polc">A polc</option>
                <option value="B polc">B polc</option>
                <option value="Hűtő">Hűtő</option>
                <option value="Raktár 1">Raktár 1</option>
              </select>
            </td>
            <td>
              <input type="date" v-model="newItem.expiry_date" style="width: 100%; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); background: #0b1220; color: var(--text);" />
            </td>
            <!-- ÚJ MENNYISÉG BEVITELI MEZŐ -->
            <td>
              <input type="number" v-model="newItem.quantity" min="1" style="width: 100%; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); background: #0b1220; color: var(--text);" />
            </td>
          </tr>
        </tbody>
      </table>
      <div style="display: flex; gap: 8px; margin-top: 10px; align-items: center;">
        <button class="btn success" @click="addNewItem">Hozzáadás</button>
        <button class="btn warn" @click="clearNewItem">Mezők ürítése</button>
        <span class="msg" style="margin-left: 10px; color: #22c55e; font-weight: bold;">{{ statusMessage }}</span>
      </div>
    </div>

    <!-- Alsó szekció: Keresők és Szűrők -->
    <div class="panel">
      <div class="section-title">Keresés és szűrés</div>
      <div class="filters" style="margin-bottom: 10px">
        <div class="stack" style="grid-column: span 6">
          <label>Keresés</label>
          <input type="text" v-model="searchQuery" @input="loadDataFromBackend" placeholder="Keresés név vagy vonalkód alapján..." />
        </div>
       <div class="stack" style="grid-column: span 3">
  <label>Kategória</label>
  <select v-model="filterCategory" @change="loadDataFromBackend">

    <option value="">Összes kategória</option>


    <option v-for="category in categories" :key="category" :value="category">
      {{ category }}
    </option>
  </select>
</div>
        <div class="stack" style="grid-column: span 3">
          <label>Készlet státusz</label>
          <select v-model="filterStatus" @change="loadDataFromBackend">
            <option value="">Összes státusz</option>
            <option value="in_stock">Készleten van</option>
            <option value="out_of_stock">Elfogyott (0 db)</option>
            <option value="expired">Lejárt szavatosságú</option>
          </select>
        </div>
      </div>

      <!-- Táblázat adatokkal -->
      <table class="grid" style="margin-top: 12px;">
        <thead>
          <tr>
            <th style="width: 40px;"><input type="checkbox" @change="toggleAllSelection" /></th>
            <th>Vonalkód / Sarzs</th>
            <th>Gyógyszer megnevezése</th>
            <th>Kategória</th>
            <th>Tároló</th>
            <th>Lejárati idő</th>
            <th>Mennyiség</th>
            <th style="width: 100px; text-align: center;">Részletek</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in parts" :key="item.PartId">
            <td><input type="checkbox" v-model="item.selected" /></td>
            <td>{{ item.Barcode || '–' }}</td>
            <td>{{ item.Name }}</td>
            <td>{{ item.Category }}</td>
            <td>{{ item.Location }}</td>
            <td>{{ formatDate(item.ExpiryDate) }}</td>
            <td>
              <span :class="['tag', item.Quantity > 0 ? 'green' : 'red']">
                {{ item.Quantity }} db
              </span>
            </td>
            <td style="text-align: center;">
              <!-- JAVÍTOTT LINK: Most már a valódi termékazonosítót (ProductId) küldi el a megnyitáshoz -->
              <RouterLink
                :to="'/inventory/' + item.PartId"
                class="btn primary"
                style="padding: 4px 10px; font-size: 12px; display: inline-block; text-decoration: none;"
              >
                Megnyitás
              </RouterLink>
            </td>
          </tr>
          <tr v-if="!parts || parts.length === 0">
            <td colspan="8" style="text-align: center; color: #94a3b8; padding: 20px;">
              Nem található gyógyszer a keresési feltételekkel.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import axios from 'axios'
import '../assets/leltar.css'

const parts = ref([])
const kpis = ref({ ProductCnt: 0, BatchCnt: 0, StockCnt: 0, ExpiredBatchCnt: 0, OutOfStockBatchCnt: 0 })

// Reaktív szűrők
const searchQuery = ref('')
const filterCategory = ref('')
const filterStatus = ref('')

// A TE EREDETI REAKTÍV ŰRLAP MEZŐID
const newItem = ref({ barcode: '', name: '', category: '', location: '', expiry_date: '2027-01-01', quantity: 1 })
const statusMessage = ref('')

const formatDate = (dateStr) => {
  if (!dateStr) return '–'
  const d = new Date(dateStr)
  return d.toLocaleDateString('hu-HU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}


// Keresés és szűrés bekötése az Azure-ba
const loadDataFromBackend = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/parts', {
      params: {
        search: searchQuery.value,
        category: filterCategory.value,
        status: filterStatus.value
      }
    })
    parts.value = response.data.map(p => ({ ...p, selected: false }))

    const kpiRes = await axios.get('http://localhost:8000/api/kpis')
    kpis.value = kpiRes.data
  } catch (error) {
    console.error("Hiba az adatok lekérésekor:", error)
  }
}

onMounted(() => {
  loadDataFromBackend()
  loadCategories()
})


const categories = ref([])

const toggleAllSelection = (event) => {
  parts.value.forEach(p => p.selected = event.target.checked)
}


// Ez a funkció megmarad, a backend finomítása után fogja menteni a te mezőidet is
// 2. FUNKCIÓ: Új tétel rögzítése az Azure felhőben
const addNewItem = async () => {
  // ÚJ ELLENŐRZÉSEK: Kötelező mezők és a minimum 6 karakteres vonalkód limit
  if (!newItem.value.name.trim() || !newItem.value.barcode.trim()) {
    statusMessage.value = 'A Megnevezés és a Vonalkód kitöltése kötelező!'
    return
  }
  
  if (newItem.value.barcode.trim().length < 6) {
    statusMessage.value = 'A vonalkód hossza nem lehet 6 karakternél rövidebb!'
    return
  }

  try {
    statusMessage.value = 'Mentés folyamatban...'
    
    await axios.post('http://localhost:8000/api/parts', {
      barcode: newItem.value.barcode,
      name: newItem.value.name,
      category: newItem.value.category,
      location: newItem.value.location,
      expiry_date: newItem.value.expiry_date,
      quantity: newItem.value.quantity // Átadjuk a te általad beírt darabszámot
    })

    statusMessage.value = 'Sikeresen mentve az Azure felhőbe! 🎉'
    clearNewItem()
    loadDataFromBackend()
    
    setTimeout(() => statusMessage.value = '', 4000)
  } catch (error) {
    statusMessage.value = 'Hiba történt a mentés során az Azure-ba.'
    console.error(error)
  }
}

// Az ürítésnél is állítsuk vissza az alapértelmezett dátumot
const clearNewItem = () => {
  newItem.value = { barcode: '', name: '', category: '', location: '', expiry_date: '2027-01-01', quantity: 1 }
}




const loadCategories = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/categories')
    categories.value = response.data
  } catch (error) {
    console.error('Hiba a kategóriák betöltésekor:', error)
  }
}



</script>
