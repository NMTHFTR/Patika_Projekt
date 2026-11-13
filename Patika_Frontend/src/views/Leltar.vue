<!-- src/views/Leltar.vue -->
<template>
  <div class="wrap">
    <div
      v-if="toastMessage"
      style="position: fixed; top: 24px; left: 50%; transform: translateX(-50%); background-color: #16a34a; color: white; padding: 14px 28px; border-radius: 12px; font-weight: bold; font-size: 15px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4); z-index: 10000; display: flex; align-items: center; gap: 10px;"
    >
      <span>{{ toastMessage }}</span>
    </div>

    <!-- ÚJ TÉTEL BEVÉTELEZÉSE (Módosított, legördülős űrlap) -->
    <div class="panel" style="margin-bottom: 16px">
      <div class="section-title">Új raktári tétel bevételezése</div>
      <table class="grid" style="margin-top: 6px">
        <thead>
          <tr>
            <th style="width: 25%">Kategória (Típus)</th>
            <th style="width: 35%">Gyógyszer megnevezése</th>
            <th style="width: 20%">Lejárati idő</th>
            <th style="width: 20%">Mennyiség (db)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>
              <select v-model="newItem.category" @change="newItem.name = ''" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid var(--line); background-color: var(--bg); color: var(--text);">
                <option value="" disabled>1. Válassz kategóriát...</option>
                <option v-for="category in categories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </td>
            <td>
              <select v-model="newItem.name" :disabled="!newItem.category" style="width: 100%; padding: 10px; border-radius: 8px; border: 1px solid var(--line); background-color: var(--bg); color: var(--text);">
                <option value="" disabled>2. Válassz gyógyszert...</option>
                <option v-for="prod in filteredProducts" :key="prod.name" :value="prod.name">
                  {{ prod.name }}
                </option>
              </select>
            </td>
            <td>
              <!-- :min="today" biztosítja, hogy a naptárban ne lehessen múltbéli napra kattintani -->
              <input type="date" v-model="newItem.expiry_date" :min="today" class="form-control-custom" style="width: 100%; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); color: var(--text); background-color: var(--bg);" />
            </td>
            <td>
              <input type="number" v-model="newItem.quantity" min="1" class="form-control-custom" style="width: 100%; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); color: var(--text); background-color: var(--bg);" />
            </td>
          </tr>
        </tbody>
      </table>
      <div style="display: flex; gap: 8px; margin-top: 10px; align-items: center;">
        <button class="btn success" @click="addNewItem">Bevételezés</button>
        <button class="btn warn" @click="clearNewItem">Mezők ürítése</button>
        <span class="msg" style="margin-left: 10px; font-weight: bold;" :style="{ color: isError ? '#ef4444' : '#22c55e' }">
          {{ statusMessage }}
        </span>
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
              <div style="display: inline-flex; align-items: center; gap: 8px; flex-wrap: nowrap;">
                <span :class="['tag', item.Quantity > 0 ? 'green' : 'red']">
                {{ item.Quantity }} db
              </span>
              <button
                  v-if="item.Quantity > 0"
                  @click="openSellModal(item)"
                  title="Termék eladása"
                  class="tag red" style="cursor: pointer;">
                  −
                </button>
              </div>
            </td>
            <td style="text-align: center;">
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

    <!-- Eladás Modal -->
    <div v-if="sellModal.isOpen" style="position: fixed; inset: 0; background: rgba(0, 0, 0, 0.7); display: flex; align-items: center; justify-content: center; z-index: 9999;">
      <div class="panel" style="width: 100%; max-width: 420px; padding: 24px; border-radius: 14px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);">
        <div class="section-title" style="font-size: 18px; margin-bottom: 6px;">Termék eladása</div>
        <p style="color: var(--muted); font-size: 13px; margin-bottom: 16px;">
          <strong>{{ sellModal.productName }}</strong><br />
          A rendszer automatikusan a legközelebb lejáró készletből vonja le a mennyiséget.
        </p>

        <div class="stack" style="margin-bottom: 12px;">
          <label>Nyugta száma (max. 15 karakter)</label>
          <input type="text" v-model="sellModal.receiptCode" maxlength="15" placeholder="Pl. 1046402" />
        </div>

        <div class="stack" style="margin-bottom: 16px;">
          <label>Eladott mennyiség (db)</label>
          <input type="number" v-model="sellModal.quantity" min="1" style="width: 100%; padding: 10px 12px; border-radius: 10px; border: 1px solid var(--line); color: var(--text); background-color: var(--bg);" />
        </div>

        <div v-if="sellModal.error" style="color: #ef4444; font-size: 13px; margin-bottom: 12px; font-weight: bold;">
          {{ sellModal.error }}
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 10px;">
          <button class="btn warn" @click="closeSellModal">Mégse</button>
          <button class="btn success" @click="confirmSell">Eladás rögzítése</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { RouterLink } from 'vue-router'
import axios from 'axios'
import '../assets/leltar.css'

const parts = ref([])
const kpis = ref({ ProductCnt: 0, BatchCnt: 0, StockCnt: 0, ExpiredBatchCnt: 0, OutOfStockBatchCnt: 0 })

const searchQuery = ref('')
const filterCategory = ref('')
const filterStatus = ref('')

// A mai dátum kiszámítása az alapértelmezett értékhez és a minimumhoz (ÉÉÉÉ-HH-NN)
const today = new Date().toISOString().split('T')[0]

// A módosított űrlap adatai
const newItem = ref({ category: '', name: '', expiry_date: today, quantity: 1 })
const statusMessage = ref('')
const isError = ref(false)

// A katalógusból betöltött összes gyógyszertípus
const productTypes = ref([])
const categories = ref([])

// Automatikusan szűri a gyógyszereket a kiválasztott kategória alapján
const filteredProducts = computed(() => {
  if (!newItem.value.category) return []
  return productTypes.value.filter(p => p.category === newItem.value.category)
})

const formatDate = (dateStr) => {
  if (!dateStr) return '–'
  const d = new Date(dateStr)
  return d.toLocaleDateString('hu-HU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

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
    window.dispatchEvent(new Event('kpis-updated'))
  } catch (error) {
    console.error("Hiba az adatok lekérésekor:", error)
  }
}

const loadCategories = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/categories')
    categories.value = response.data
  } catch (error) {
    console.error('Hiba a kategóriák betöltésekor:', error)
  }
}

// ÚJ: A katalógusban lévő gyógyszerek betöltése a legördülőhöz
const loadProductTypes = async () => {
  try {
    // Ezt a végpontot majd be kell kötni a backendben (visszaadja a katalógus elemeit)
    const response = await axios.get('http://localhost:8000/api/product-types')
    productTypes.value = response.data
  } catch (error) {
    console.error('Hiba a terméktípusok betöltésekor:', error)
  }
}

onMounted(() => {
  loadDataFromBackend()
  loadCategories()
  loadProductTypes() // Betöltjük a katalógust
})

const toggleAllSelection = (event) => {
  parts.value.forEach(p => p.selected = event.target.checked)
}

const addNewItem = async () => {
  isError.value = false

  // 1. Kötelező mezők ellenőrzése
  if (!newItem.value.category || !newItem.value.name || !newItem.value.expiry_date || !newItem.value.quantity) {
    isError.value = true
    statusMessage.value = 'Minden mező kiválasztása és kitöltése kötelező!'
    return
  }

  // 2. Dátum ellenőrzése (nem lehet régebbi a mainál)
  if (newItem.value.expiry_date < today) {
    isError.value = true
    statusMessage.value = 'A lejárati idő nem lehet a mai napnál régebbi!'
    return
  }

  // 3. Mennyiség ellenőrzése
  if (newItem.value.quantity < 1) {
    isError.value = true
    statusMessage.value = 'A mennyiségnek legalább 1-nek kell lennie!'
    return
  }

  try {
    statusMessage.value = 'Mentés folyamatban...'
    isError.value = false

    await axios.post('http://localhost:8000/api/parts', {
      name: newItem.value.name,
      category: newItem.value.category,
      expiry_date: newItem.value.expiry_date,
      quantity: newItem.value.quantity
    })

    statusMessage.value = 'Sikeresen bevételezve a raktárba!'
    clearNewItem()
    await loadDataFromBackend()
    window.dispatchEvent(new Event('kpis-updated'))

    setTimeout(() => statusMessage.value = '', 5000)
  } catch (error) {
    isError.value = true
    statusMessage.value = 'Hiba történt a mentés során az Azure-ba.'
    console.error(error)
  }
}

const clearNewItem = () => {
  newItem.value = { category: '', name: '', expiry_date: today, quantity: 1 }
  statusMessage.value = ''
  isError.value = false
}

const sellModal = ref({
  isOpen: false,
  productId: null,
  productName: '',
  receiptCode: '',
  quantity: 1,
  error: ''
})

const openSellModal = (item) => {
  sellModal.value = {
    isOpen: true,
    productId: item.ProductId,
    productName: item.Name,
    receiptCode: '',
    quantity: 1,
    error: ''
  }
}

const closeSellModal = () => {
  sellModal.value.isOpen = false
}

const toastMessage = ref('')
let toastTimer = null

const showToast = (msg) => {
  toastMessage.value = msg
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
  }, 5000)
}

const confirmSell = async () => {
  if (!sellModal.value.receiptCode.trim()) {
    sellModal.value.error = 'A nyugta számának megadása kötelező!'
    return
  }
  if (sellModal.value.quantity < 1) {
    sellModal.value.error = 'Legalább 1 darabot kell megadni!'
    return
  }

  try {
    sellModal.value.error = ''
    const res = await axios.post('http://localhost:8000/api/sell', {
      product_id: sellModal.value.productId,
      receipt_code: sellModal.value.receiptCode,
      quantity: sellModal.value.quantity
    })

    closeSellModal()
    await loadDataFromBackend()
    window.dispatchEvent(new Event('kpis-updated'))
    showToast(res.data.message || 'Sikeres eladás rögzítve!')
  } catch (err) {
    sellModal.value.error = err.response?.data?.error || 'Hiba történt az eladás során.'
  }
}
</script>
