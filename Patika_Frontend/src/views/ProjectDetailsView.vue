<!-- 1. HTML SZERKEZET -->
<template>
  <main>
    <div class="panel">

      <!-- Felső sáv: Vissza gomb és Cím -->
      <div class="product-header">
        <button class="btn ghost" @click="goBack">
          &larr; Vissza a leltárhoz
        </button>
        <div class="brand" style="color: var(--muted); font-size: 16px;">Termék adatlapja</div>
      </div>

      <!-- 12 Oszlopos Grid Felosztás -->
      <div class="grid-12">

        <!-- BAL OLDAL (5 oszlop): Kép -->
        <div class="image-box">
          <!-- Ha nincs kép, egy szürke doboz jelenik meg helyette -->
          <img v-if="product.imageUrl" :src="product.imageUrl" alt="Termék képe" class="product-image" />
          <div v-else class="no-image">Nincs feltöltött kép</div>
        </div>

        <!-- JOBB OLDAL (7 oszlop): Név, Leírás és Adatok -->
        <div class="details-box">
          <div class="section-title">Termék információk</div>

          <h1 class="product-name">{{ product.name }}</h1>

          <div style="margin-bottom: 16px;">
            <span class="tag blue">Vonalkód: {{ product.barcode }}</span>
          </div>

          <p class="product-desc">{{ product.description }}</p>

          <!-- Extra statisztikák a termékhez az eredeti dizájnnal -->
          <div class="kpis" style="margin-top: 24px;">
            <div class="kpi">Kategória<div class="big">{{ product.category }}</div>
            </div>
            <div class="kpi">Helyzet<div class="big">{{ product.location }}</div>
            </div>
            <div class="kpi">Készlet<div class="big">{{ product.stock }} db</div>
            </div>
          </div>
        </div>

      </div>

    </div>
  </main>
</template>


<!-- 2. TYPESCRIPT LOGIKA -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// Kiolvassuk az URL-ből az ID-t (vonalkódot)
const currentBarcode = ref(route.params.id as string)

// Adatszerkezet a termékhez
interface ProductDetail {
  name: string
  barcode: string
  category: string
  location: string
  stock: number
  description: string
  imageUrl: string
}

const product = ref<ProductDetail>({
  name: 'Betöltés alatt...',
  barcode: '',
  category: '',
  location: '',
  stock: 0,
  description: '',
  imageUrl: ''
})

// Visszalépés az előző oldalra
const goBack = () => {
  router.back()
}

// Oldal betöltésekor "lekérjük" az adatokat
onMounted(() => {
  // Szimulált backend válasz a currentBarcode.value alapján
  product.value = {
    name: 'Algoflex Forte Dolo 400mg filmtabletta',
    barcode: currentBarcode.value,
    category: 'Fájdalomcsillapító',
    location: 'A Raktár, 3. sor',
    stock: 45,
    description: 'Enyhe és közepesen erős fájdalom, például fejfájás, fogfájás, menstruációs fájdalom csillapítására, valamint lázcsillapításra alkalmazható gyógyszerkészítmény. Hatóanyaga az ibuprofén.',
    // Helyettesítő kép generálása a teszteléshez
    imageUrl: 'https://placehold.co/500x500/0b1220/3b82f6?text=Gyogyszer+Kepe'
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
