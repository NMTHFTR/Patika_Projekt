<!-- 1. HTML SZERKEZET -->
<template>
  <main>
    <div class="panel">

      <!-- Felső sáv: Vissza gomb és Cím -->
      <div class="product-header">
        <button class="btn ghost" @click="goBack">
          &larr; Vissza a leltárhoz
        </button>
        <div class="brand" style="color: var(--muted); font-size: 20px;">Termék adatlapja</div>
      </div>

      <!-- 12 Oszlopos Grid Felosztás -->
      <div class="grid-12">

        <!-- BAL OLDAL (5 oszlop): Kép -->
        <div class="image-box">
          <!-- Ha nincs kép, egy szürke doboz jelenik meg helyette -->
         <img
            v-if="product.Barcode"
            :src="`/fotok/${product.Barcode}.jpg`"
            alt="Termék képe"
            class="product-image"
          />
          <div v-else class="no-image">Nincs feltöltött kép</div>
        </div>

        <!-- JOBB OLDAL (7 oszlop): Név, Leírás és Adatok -->
        <div class="details-box">
          <div class="section-title">Termék információk</div>

          <div style="color: var(--muted); font-size: 20px; text-transform: uppercase; letter-spacing: 1px;">
            {{ product.Brand }}
          </div>

          <h1 class="product-name">{{ product.Name }}</h1>



          <div style="margin-bottom: 16px;">
            <span class="tag blue", style="font-size: 14px;">Vonalkód: {{ product.Barcode }}</span>
            <span :style="{
              backgroundColor: product.IsPrescription ? '#ef4444' : '#22c55e',
              color: 'white',
              padding: '4px 8px',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: 'bold'
            }">
              {{ product.IsPrescription ? 'Vényköteles (Rx)' : 'Vény nélkül kapható' }}
            </span>
          </div>

          <p class="product-desc">{{ product.Description }}</p>

          <!-- Extra statisztikák a termékhez az eredeti dizájnnal -->
          <div class="kpis" style="margin-top: 24px;">
            <div class="kpi">Kategória<div class="big">{{ product.Category }}</div>
            </div>
            <div class="kpi">Tároló<div class="big">{{ product.Location }}</div>
            </div>
            <div class="kpi">Készlet<div class="big">{{ product.Quantity }} db</div>
            </div>
            <div class="kpi">Lejárati idő<div class="big">{{ formatDate(product.ExpiryDate) }}</div>
            </div>
          </div>
        </div>

      </div>

    </div>
  </main>
</template>


<!-- 2. TYPESCRIPT LOGIKA -->
<!-- 2. TYPESCRIPT LOGIKA -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

// Kiolvassuk az URL-ből az ID-t (vonalkódot / sarzsot)
const currentBarcode = ref(route.params.id as string)

// Adatszerkezet a termékhez (igazítva az inv.py get_parts_by_ids formátumához)
interface ProductDetail {
  PartId: string
  Barcode: string
  Name: string
  Category: string
  Location: string
  ExpiryDate: string
  ProductId: number
  Quantity: number
  Description: string
  imageUrl: string
  Brand: string
  IsPrescription: boolean
}

const product = ref<ProductDetail>({
  PartId: '',
  Barcode: '',
  Name: 'Betöltés alatt...',
  Category: '',
  Location: '',
  ExpiryDate: '',
  ProductId: 0,
  Quantity: 0,
  Description: 'A termék leírása hamarosan elérhető a központi adatbázisból.',
  imageUrl: '',
  Brand: '',
  IsPrescription: false
})

// Visszalépés az előző oldalra
const goBack = () => {
  router.back()
}

// Dátum formázó segédfüggvény
const formatDate = (dateStr: string) => {
  if (!dateStr) return '–'
  const d = new Date(dateStr)
  // Visszaadjuk a szép magyar formátumot: ÉÉÉÉ. MM. DD.
  return d.toLocaleDateString('hu-HU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// Oldal betöltésekor ténylegesen lekérjük az adatokat az Azure felhőből
onMounted(async () => {
  try {
    const response = await axios.get(`http://localhost:8000/api/parts/${currentBarcode.value}`)

    // Feltöltjük az interfészt a Pythonból kapott adatokkal
    product.value = {
      ...response.data,
      // JAVÍTOTT LINK (Hozzáadva a / perjel, hogy betöltsön a tesztkép)
      imageUrl: 'https://placehold.co' + encodeURIComponent(response.data.Name || 'Gyogyszer')
    }
  } catch (error) {
    console.error("Hiba a gyógyszer részleteinek letöltésekor:", error)
    product.value.Name = "Hiba történt az adatok letöltésekor."
  }
})
</script>



<!-- 3. CSS (Csak erre a komponensre ható dizájn) -->
<style scoped>
/* Fejléc a vissza gombbal */
.product-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--line);
  padding-bottom: 16px;
  margin-bottom: 24px;
}

/* 12 Oszlopos Rács */
.grid-12 {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
}

/* Kép konténer (5 oszlop) */
.image-box {
  grid-column: span 5;
  background-color: #0b1220;
  border: 1px solid var(--line);
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  overflow: hidden;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* Kitölti a dobozt anélkül, hogy torzulna */
}

.no-image {
  color: var(--muted);
  font-size: 14px;
}

/* Részletek konténer (7 oszlop) */
.details-box {
  grid-column: span 7;
  display: flex;
  flex-direction: column;
}

.product-name {
  margin: 0 0 8px 0;
  font-size: clamp(20px, 3vw, 28px);
  color: #ffffff;
}

.product-desc {
  font-size: 15px;
  color: var(--text);
  line-height: 1.6;
  margin: 0;
}

/* Reszponzivitás: Mobilon a 12 oszlopos grid egymás alá törik (12-12) */
@media (max-width: 980px) {

  .image-box,
  .details-box {
    grid-column: span 12;
  }
}
</style>
