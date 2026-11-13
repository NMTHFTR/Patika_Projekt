<template>
  <div class="panel" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0; border-bottom: none; border-radius: 14px 14px 0 0;">
    <button class="btn" @click="goBack">← Vissza a leltárhoz</button>
    <div style="font-size: 20px; font-weight: 700; color: var(--text);">Termék adatlapja</div>
  </div>

  <div class="panel" style="display: grid; grid-template-columns: 1fr 1.25fr; gap: 28px; align-items: stretch; padding: 24px; border-radius: 0 0 14px 14px;">
      

    <div style="background: #0b1020; border-radius: 12px; overflow: hidden; border: 1px solid var(--line); display: flex; align-items: center; justify-content: center;">
      <img 
        :src="product.imageUrl" 
        :alt="product.Name"
        style="width: 100%; height: 100%; object-fit: cover; display: block;" 
      />
    </div>

    <div style="display: flex; flex-direction: column; justify-content:baseline;">
      <div>
        <div class="section-title" style="margin-bottom: 6px; font-size: 14px;">TERMÉK INFORMÁCIÓK</div>
          
        <div style="color: var(--muted); font-size: 18px; text-transform: uppercase; letter-spacing: 0.5px;">
          {{ product.Brand }}
        </div>

        <h1 class="product-name" style="margin: 2px 0 12px 0; font-size: 28px; font-weight: 700;">
          {{ product.Name }}
        </h1>


      <div style="margin-bottom: 16px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
        <span style="border: 1px solid #30435f; background: rgba(59, 130, 246, 0.1); color: #93c5fd; padding: 4px 12px; border-radius: 999px; font-size: 16px;">
          Vonalkód: {{ product.Barcode }}
        </span>
        <span :style="{
          backgroundColor: product.IsPrescription ? '#ef4444' : '#22c55e',
          color: 'white',
          padding: '4px 12px',
          borderRadius: '5px',
          fontSize: '16px',
          fontWeight: 'bold'
        }">
          {{ product.IsPrescription ? 'Vényköteles (Rx)' : 'Vény nélkül kapható' }}
        </span>
      </div>

      <p class="product-desc" style="color: var(--muted); font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
        {{ product.Description }}
      </p>

      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 12px;">
        <div class="kpi" style="margin: 0; text-align: center; padding: 14px;">
          <div style="font-size: 20px; color: var(--muted); margin-bottom: 4px;">Kategória</div>
          <div class="big" style="font-size: 26px;">{{ product.Category }}</div>
        </div>
        <div class="kpi" style="margin: 0; text-align: center; padding: 14px;">
          <div style="font-size: 20px; color: var(--muted); margin-bottom: 4px;">Raktári pozíció</div>
          <div class="big" style="font-size: 26px;">{{ product.Location }}</div>
        </div>
        <div class="kpi" style="margin: 0; text-align: center; padding: 14px;">
          <div style="font-size: 20px; color: var(--muted); margin-bottom: 4px;">Készlet</div>
          <div class="big" style="font-size: 26px;">{{ product.Quantity }} db</div>
        </div>
        <div class="kpi" style="margin: 0; text-align: center; padding: 14px;">
          <div style="font-size: 20px; color: var(--muted); margin-bottom: 4px;">Lejárati idő</div>
          <div class="big" style="font-size: 26px;">{{ formatDate(product.ExpiryDate) }}</div>
        </div>
        <div class="kpi" style="margin: 0; text-align: center; padding: 14px;">
          <div style="font-size: 20px; color: var(--muted); margin-bottom: 4px;">Hatóanyag</div>
          <div class="big" style="font-size: 26px;">{{ product.ActiveIngredient }}</div>
        </div>
      </div>

        <!-- Alsó 2 széles eladási kártya -->
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px;">
        <div class="kpi" style="margin: 0; text-align: center; padding: 14px;">
          <div style="font-size: 20px; color: var(--muted); margin-bottom: 4px;">Eladva ebben a hónapban</div>
          <div class="big" style="color: #3b82f6; font-size: 26px;">{{ salesStats.MonthlySold }} db</div>
        </div>
        <div class="kpi" style="margin: 0; text-align: center; padding: 14px;">
          <div style="font-size: 20px; color: var(--muted); margin-bottom: 4px;">Összesen eladva eddig</div>
          <div class="big" style="color: #22c55e; font-size: 26px;">{{ salesStats.TotalSold }} db</div>
        </div>
      </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const currentBarcode = ref(route.params.id as string)

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
  ActiveIngredient: string
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
  Description: '',
  imageUrl: '',
  Brand: '',
  IsPrescription: false,
  ActiveIngredient: ''
})

const salesStats = ref({
  MonthlySold: 0,
  TotalSold: 0
})

const goBack = () => {
  router.back()
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '–'
  const d = new Date(dateStr)
  return d.toLocaleDateString('hu-HU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

onMounted(async () => {
  try {
    const response = await axios.get(`http://localhost:8000/api/parts/${currentBarcode.value}`)
    
    const cleanBarcode = String(response.data.Barcode || '').trim()
    const localImagePath = `/fotok/${cleanBarcode}.jpg`

    product.value = {
      ...response.data,
      imageUrl: localImagePath
    }

    if (response.data.ProductId) {
      const statsRes = await axios.get(`http://localhost:8000/api/sales-stats/${response.data.ProductId}`)
      salesStats.value = statsRes.data
    }
  } catch (error) {
    console.error("Hiba a gyógyszer részleteinek letöltésekor:", error)
    product.value.Name = "Hiba történt az adatok letöltésekor."
  }
})
</script>
