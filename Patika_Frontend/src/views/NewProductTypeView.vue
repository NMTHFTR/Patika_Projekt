<template>
  <div class="wrap">
    <div class="panel" style="margin-top: 16px;">
      <div class="section-title" style="margin-bottom:16px;">Új gyógyszerfajta felvitele a katalógusba</div>

      <!-- CSS Grid a kétoszlopos elrendezéshez (1fr 1fr = fele-fele arányban osztja a helyet) -->
      <form @submit.prevent="submitProductType" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">

        <!-- Márka -->
        <div style="display: flex; flex-direction: column; gap: 5px;">
          <label style="color: #a0aec0; font-size: 0.9rem;">Márka / Gyártó</label>
          <input type="text" v-model="productData.brand" placeholder="Pl.: Sanofi, Teva..."
                 :style="{ padding: '12px', borderRadius: '5px', border: errors.brand ? '1px solid #ef4444' : '1px solid #30435f', background: 'transparent', color: 'white' }" />
          <span v-if="errors.brand" style="color: #ef4444; font-size: 0.85rem;">{{ errors.brand }}</span>
        </div>

        <!-- Megnevezés -->
        <div style="display: flex; flex-direction: column; gap: 5px;">
          <label style="color: #a0aec0; font-size: 0.9rem;">Gyógyszer megnevezése</label>
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

        <!-- Kiadhatóság / Vénynélküliség -->
        <div style="display: flex; flex-direction: column; gap: 5px;">
          <label style="color: #a0aec0; font-size: 0.9rem;">Kiadhatóság</label>
          <select v-model="productData.prescription"
                  :style="{ padding: '12px', borderRadius: '5px', border: errors.prescription ? '1px solid #ef4444' : '1px solid #30435f', background: '#0b1120', color: 'white' }">
            <option value="" disabled>Válassz kiadhatóságot...</option>
            <option value="Vény nélkül kapható (VN)">Vény nélkül kapható (VN)</option>
            <option value="Vényköteles (V)">Vényköteles (V)</option>
          </select>
          <span v-if="errors.prescription" style="color: #ef4444; font-size: 0.85rem;">{{ errors.prescription }}</span>
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
            <option value="Páncélszekrény">Páncélszekrény</option>
            <option value="Raktár 1">Raktár 1</option>
          </select>
          <span v-if="errors.location" style="color: #ef4444; font-size: 0.85rem;">{{ errors.location }}</span>
        </div>

        <!-- Üres hely a Grid-ben, hogy a leírás egyedül uralja a következő sort -->
        <div></div>

        <!-- Leírás - MOST MÁR KÖTELEZŐ, hibaüzenettel és dinamikus kerettel -->
        <div style="display: flex; flex-direction: column; gap: 5px; grid-column: span 2;">
          <label style="color: #a0aec0; font-size: 0.9rem;">Leírás / Hatóanyag</label>
          <textarea v-model="productData.description" rows="3" placeholder="Rövid leírás a gyógyszerről és hatóanyagáról..."
                 :style="{ padding: '12px', borderRadius: '5px', border: errors.description ? '1px solid #ef4444' : '1px solid #30435f', background: 'transparent', color: 'white', resize: 'vertical' }"></textarea>
          <span v-if="errors.description" style="color: #ef4444; font-size: 0.85rem;">{{ errors.description }}</span>
        </div>

        <!-- Mentés gomb -->
        <button type="submit"
                style="grid-column: span 2; margin-top: 10px; padding: 14px; background-color: #10b981; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 1.05rem;">
          Mentés a katalógusba
        </button>

      </form>

      <!-- Visszajelző üzenet -->
      <div v-if="statusMessage" style="margin-top: 15px; color: #10b981; font-weight: bold; text-align: center; font-size: 1.1rem;">
        {{ statusMessage }}
      </div>

    </div>
  </div>
</template>



<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

// Űrlap adatai az új mezőkkel kibővítve
const productData = ref({
  brand: '',
  name: '',
  category: '',
  prescription: '',
  location: '',
  description: ''
})

// Helyi validációs hibaüzenetek tárolója (Már a leírás is szerepel benne)
const errors = ref({
  brand: '',
  name: '',
  category: '',
  prescription: '',
  location: '',
  description: ''
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

  // Hibák nullázása
  errors.value = { brand: '', name: '', category: '', prescription: '', location: '', description: '' }

  if (!productData.value.brand.trim()) {
    errors.value.brand = 'A márka / gyártó megadása kötelező!'
    isValid = false
  }

  if (!productData.value.name.trim()) {
    errors.value.name = 'A megnevezés megadása kötelező!'
    isValid = false
  }

  if (!productData.value.category) {
    errors.value.category = 'Kérlek, válassz kategóriát!'
    isValid = false
  }

  if (!productData.value.prescription) {
    errors.value.prescription = 'Kötelező megadni a kiadhatóságot!'
    isValid = false
  }

  if (!productData.value.location) {
    errors.value.location = 'Kérlek, válassz tárolót!'
    isValid = false
  }

  // ÚJ: A leírás ellenőrzése
  if (!productData.value.description.trim()) {
    errors.value.description = 'A leírás / hatóanyag megadása kötelező!'
    isValid = false
  }

  return isValid
}

const submitProductType = async () => {
  if (!validateForm()) {
    return
  }

  try {
    // Backend API hívás az összes kibővített adattal
    await axios.post('http://localhost:8000/api/product-types', productData.value)

    statusMessage.value = 'Sikeresen mentve az Azure felhőbe!'

    // Űrlap ürítése sikeres mentés után
    productData.value = { brand: '', name: '', category: '', prescription: '', location: '', description: '' }

    setTimeout(() => {
      statusMessage.value = ''
    }, 3000)

  } catch (error) {
    console.error('Hiba a mentés során:', error)
    alert('Nem sikerült elmenteni a terméket. Nézd meg a konzolt!')
  }
}
</script>
