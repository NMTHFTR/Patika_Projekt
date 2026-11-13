<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

// Űrlap adatai (vonalkód eltávolítva)
const productData = ref({
  name: '',
  category: '',
  location: ''
})

// Helyi validációs hibaüzenetek tárolója
const errors = ref({
  name: '',
  category: '',
  location: ''
})

const categories = ref<string[]>([])
const statusMessage = ref('')

onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/categories')
    categories.value = response.data
  } catch (error) {
    console.error('Hiba a kategóriák betöltésekor:', error)
  }
})

// Helyben történő ellenőrzés (Validáció)
const validateForm = () => {
  let isValid = true

  // Hibák nullázása minden mentési kísérlet előtt
  errors.value = { name: '', category: '', location: '' }

  // 1. Megnevezés: Nem lehet üres
  if (!productData.value.name.trim()) {
    errors.value.name = 'A megnevezés megadása kötelező!'
    isValid = false
  }

  // 2. Kategória: Kötelező választani
  if (!productData.value.category) {
    errors.value.category = 'Kérlek, válassz kategóriát!'
    isValid = false
  }

  // 3. Tároló: Kötelező választani
  if (!productData.value.location) {
    errors.value.location = 'Kérlek, válassz tárolót!'
    isValid = false
  }

  return isValid
}

const submitProductType = async () => {
  if (!validateForm()) {
    return
  }

  try {
    // Backend API hívás (csak a 3 megmaradt adatot küldjük)
    await axios.post('http://localhost:8000/api/product-types', productData.value)

    statusMessage.value = 'Sikeresen mentve az Azure felhőbe!'

    // Űrlap ürítése sikeres mentés után
    productData.value = { name: '', category: '', location: '' }

    setTimeout(() => {
      statusMessage.value = ''
    }, 3000)

  } catch (error) {
    console.error('Hiba a mentés során:', error)
    alert('Nem sikerült elmenteni a terméket. Nézd meg a konzolt!')
  }
}
</script>

<template>
  <div class="wrap">
    <!-- max-width megnövelve 700px-re, hogy szebben kitöltse a teret -->
    <div class="panel" style="margin-top: 16px; max-width: 700px;">
      <div class="section-title" style="margin-bottom:16px;">Új gyógyszerfajta felvitele a katalógusba</div>

      <form @submit.prevent="submitProductType" style="display: flex; flex-direction: column; gap: 15px;">

        <!-- Megnevezés -->
        <div style="display: flex; flex-direction: column; gap: 5px;">
          <label style="color: #a0aec0; font-size: 0.9rem;">Megnevezés</label>
          <input type="text" v-model="productData.name" placeholder="Pl.: Algopyrin 500 mg tabletta"
                 :style="{ padding: '12px', borderRadius: '5px', border: errors.name ? '1px solid #ef4444' : '1px solid #30435f', background: 'transparent', color: 'white' }" />
          <span v-if="errors.name" style="color: #ef4444; font-size: 0.85rem;">{{ errors.name }}</span>
        </div>

        <!-- Kategória -->
        <div style="display: flex; flex-direction: column; gap: 5px;">
          <label style="color: #a0aec0; font-size: 0.9rem;">Kategória</label>
          <select v-model="productData.category"
                  :style="{ padding: '12px', borderRadius: '5px', border: errors.category ? '1px solid #ef4444' : '1px solid #30435f', background: '#0b1120', color: 'white' }">
            <option value="" disabled>Válassz kategóriát...</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
          <span v-if="errors.category" style="color: #ef4444; font-size: 0.85rem;">{{ errors.category }}</span>
        </div>

        <!-- Tároló -->
        <div style="display: flex; flex-direction: column; gap: 5px;">
          <label style="color: #a0aec0; font-size: 0.9rem;">Tároló / Polc</label>
          <select v-model="productData.location"
                  :style="{ padding: '12px', borderRadius: '5px', border: errors.location ? '1px solid #ef4444' : '1px solid #30435f', background: '#0b1120', color: 'white' }">
            <option value="" disabled>Válassz tárolót...</option>
            <option value="A polc">A polc</option>
            <option value="B polc">B polc</option>
            <option value="Hűtő">Hűtő</option>
            <option value="Raktár 1">Raktár 1</option>
          </select>
          <span v-if="errors.location" style="color: #ef4444; font-size: 0.85rem;">{{ errors.location }}</span>
        </div>

        <!-- Mentés gomb egy kis extra paddinggal -->
        <button type="submit"
                style="margin-top: 15px; padding: 14px; background-color: #10b981; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 1rem;">
          Mentés a katalógusba
        </button>

      </form>

      <!-- Visszajelző üzenet -->
      <div v-if="statusMessage" style="margin-top: 15px; color: #10b981; font-weight: bold; text-align: center;">
        {{ statusMessage }}
      </div>

    </div>
  </div>
</template>
