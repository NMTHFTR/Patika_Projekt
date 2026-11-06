<!-- src/components/Leltar.vue -->
<template>
  <div class="wrap">
    <!-- Header KPI-okkal -->
    <div class="header">
      <div></div>
      <div class="kpis">
        <div class="kpi"><div class="big">{{ kpiAll }}</div><div class="sub">Összes tétel</div></div>
        <div class="kpi"><div class="big">{{ kpiFree }}</div><div class="sub">Szabad készlet</div></div>
        <div class="kpi"><div class="big">{{ kpiAssigned }}</div><div class="sub">Használatban</div></div>
      </div>
    </div>

    <!-- Új gyógyszer/alkatrész felvétele panel -->
    <div class="panel" style="margin-bottom: 16px">
      <div class="section-title">Új tétel felvétele</div>
      <table class="grid" style="margin-top: 6px">
        <thead>
          <tr>
            <th style="width: 25%">Vonalkód</th>
            <th style="width: 35%">Megnevezés</th>
            <th style="width: 20%">Kategória</th>
            <th style="width: 20%">Tároló / Polc</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><input type="text" v-model="newItem.barcode" placeholder="Szkennelj vagy gépelj..." /></td>
            <td><input type="text" v-model="newItem.name" placeholder="Gyógyszer vagy eszköz neve" /></td>
            <td>
              <select v-model="newItem.category">
                <option value="">– válassz –</option>
                <option value="Fájdalomcsillapító">Fájdalomcsillapító</option>
                <option value="Antibiotikum">Antibiotikum</option>
                <option value="Vitamin">Vitamin</option>
                <option value="Lázcsillapító">Lázcsillapító</option>
                <option value="Egyéb">Egyéb</option>
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
          </tr>
        </tbody>
      </table>
      <div style="display: flex; gap: 8px; margin-top: 10px;">
        <button class="btn success" @click="addNewItem">Hozzáadás</button>
        <button class="btn warn" @click="clearNewItem">Mezők ürítése</button>
        <span class="msg" style="margin-left: 10px; color: #22c55e;">{{ statusMessage }}</span>
      </div>
    </div>

    <!-- Alsó szekció: Kereső + Gyűjtőtér elrendezés -->
    <div class="grid-2">
      <!-- Bal oldal: Kereső és Lista -->
      <div class="panel">
        <div class="section-title">Keresés és szűrés</div>
        <div class="filters" style="margin-bottom: 10px">
          <div class="stack" style="grid-column: span 6">
            <label>Keresés</label>
            <input type="text" v-model="searchQuery" placeholder="Keresés név vagy vonalkód alapján..." />
          </div>
          <div class="stack" style="grid-column: span 3">
            <label>Kategória</label>
            <select v-model="filterCategory">
              <option value="">Összes</option>
              <option value="Fájdalomcsillapító">Fájdalomcsillapító</option>
              <option value="Antibiotikum">Antibiotikum</option>
              <option value="Vitamin">Vitamin</option>
            </select>
          </div>
          <div class="stack" style="grid-column: span 3">
            <label>Státusz</label>
            <select v-model="filterStatus">
              <option value="">Összes</option>
              <option value="free">Szabad</option>
              <option value="assigned">Használatban</option>
            </select>
          </div>
        </div>

        <!-- Táblázat adatokkal -->
        <table class="grid" style="margin-top: 12px;">
          <thead>
            <tr>
              <th style="width: 40px;"><input type="checkbox" @change="toggleAllSelection" /></th>
              <th>Vonalkód</th>
              <th>Megnevezés</th>
              <th>Kategória</th>
              <th>Tároló</th>
              <th>Státusz</th>
              <th>Projekt</th>
              <th style="width: 100px; text-align: center;">Részletek</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredParts" :key="item.PartId">
              <td><input type="checkbox" v-model="item.selected" /></td>
              <td>{{ item.Barcode || '(nincs)' }}</td>
              <td>{{ item.Name }}</td>
              <td>{{ item.Category }}</td>
              <td>{{ item.Location }}</td>
              <td>
                <span :class="['tag', item.ProjectName ? 'blue' : 'green']">
                  {{ item.ProjectName ? 'Haszn.' : 'Szabad' }}
                </span>
              </td>
              <td>{{ item.ProjectName || '–' }}</td>
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
          </tbody>
        </table>
      </div>

      <!-- Jobb oldal: Gyűjtőtér panel -->
      <div class="panel">
        <div class="section-title">Gyűjtőtér</div>
        <div class="stack" style="margin-bottom: 10px">
          <label>Cél Projekt / Osztály</label>
          <select v-model="selectedAssignProject">
            <option value="">Válassz ki egy osztályt...</option>
            <option value="Sebészet">Sebészet</option>
            <option value="Belgyógyászat">Belgyógyászat</option>
            <option value="Sürgősségi">Sürgősségi</option>
          </select>
        </div>
        <div style="display: flex; gap: 8px; margin-top: 12px;">
          <button class="btn success" @click="assignSelectedToProject">Hozzárendelés indítása</button>
          <button class="btn warn" @click="clearBin">Gyűjtőtér kiürítése</button>
        </div>

        <div class="bin-list">
          <div v-if="binItems.length === 0" class="muted" style="color: #94a3b8; font-size: 13px;">
            A gyűjtőtér jelenleg üres. Jelölj ki elemeket bal oldalon!
          </div>
          <div v-else class="bin-item" v-for="binItem in binItems" :key="binItem.PartId">
            <div>
              <div>{{ binItem.Name }} <span class="muted">(#{{ binItem.PartId }})</span></div>
              <div class="muted" style="font-size: 11px;">{{ binItem.Barcode }} • {{ binItem.Category }}</div>
            </div>
            <button class="btn danger" style="padding: 2px 8px;" @click="binItem.selected = false">X</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Alsó rögzített akciós sáv a kijelöltek csoportos kezelésére -->
    <div class="floating-actions" v-if="anySelected">
      <span style="color: white; align-self: center; font-size: 13px; margin-right: 10px;">
        {{ selectedCount }} tétel kijelölve:
      </span>
      <button class="btn danger" @click="deleteSelected">Kijelöltek törlése</button>
      <button class="btn warn" @click="unassignSelected">Levétel projektről</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
// Bekötjük az assets mappába kiszervezett új CSS-t
import '../assets/leltar.css'
import { RouterLink } from 'vue-router'

// Kezdő adatok gyógyszerészeti köntösben (Mock adatok)
const parts = ref([
  { PartId: 101, Barcode: '599123456', Name: 'Algoflex Forte', Category: 'Fájdalomcsillapító', Location: 'A polc', ProjectName: 'Sebészet', selected: false },
  { PartId: 102, Barcode: '599987654', Name: 'Augmentin Duo', Category: 'Antibiotikum', Location: 'Hűtő', ProjectName: '', selected: false },
  { PartId: 103, Barcode: '599555444', Name: 'C-Vitamin 1000mg', Category: 'Vitamin', Location: 'B polc', ProjectName: 'Belgyógyászat', selected: false },
  { PartId: 104, Barcode: '599333222', Name: 'Neo Citran por', Category: 'Lázcsillapító', Location: 'A polc', ProjectName: '', selected: false }
])

// Új elem űrlap reaktív állapota
const newItem = ref({ barcode: '', name: '', category: '', location: '' })
const statusMessage = ref('')

// Szűrési feltételek
const searchQuery = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const selectedAssignProject = ref('')

// KPI számítások dinamikusan az adatok alapján
const kpiAll = computed(() => parts.value.length)
const kpiFree = computed(() => parts.value.filter(p => !p.ProjectName).length)
const kpiAssigned = computed(() => parts.value.filter(p => p.ProjectName).length)

// Kereső és szűrő logika
const filteredParts = computed(() => {
  return parts.value.filter(p => {
    const matchesSearch = p.Name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          p.Barcode.includes(searchQuery.value)
    const matchesCategory = !filterCategory.value || p.Category === filterCategory.value
    const matchesStatus = !filterStatus.value || 
                          (filterStatus.value === 'free' && !p.ProjectName) || 
                          (filterStatus.value === 'assigned' && p.ProjectName)
    return matchesSearch && matchesCategory && matchesStatus
  })
})

// Gyűjtőtér elemei (amik bal oldalon ki vannak pipálva)
const binItems = computed(() => parts.value.filter(p => p.selected))
const anySelected = computed(() => binItems.value.length > 0)
const selectedCount = computed(() => binItems.value.length)

// Összes kijelölése / kijelölés megszüntetése
const toggleAllSelection = (event) => {
  filteredParts.value.forEach(p => p.selected = event.target.checked)
}

// Funkció: Új tétel felvétele
const addNewItem = () => {
  if (!newItem.value.name) {
    statusMessage.value = 'A tétel nevének kitöltése kötelező!'
    return
  }
  parts.value.push({
    PartId: Date.now(),
    Barcode: newItem.value.barcode,
    Name: newItem.value.name,
    Category: newItem.value.category || 'Egyéb',
    Location: newItem.value.location || 'Raktár 1',
    ProjectName: '',
    selected: false
  })
  statusMessage.value = 'Sikeresen hozzáadva!'
  clearNewItem()
  setTimeout(() => statusMessage.value = '', 3000)
}

const clearNewItem = () => {
  newItem.value = { barcode: '', name: '', category: '', location: '' }
}

// Funkció: Kijelöltek hozzárendelése projekthez
const assignSelectedToProject = () => {
  if (!selectedAssignProject.value) {
    alert('Kérlek válassz ki egy osztályt / projektet!')
    return
  }
  parts.value.forEach(p => {
    if (p.selected) {
      p.ProjectName = selectedAssignProject.value
      p.selected = false
    }
  })
  selectedAssignProject.value = ''
}

const clearBin = () => {
  parts.value.forEach(p => p.selected = false)
}

const deleteSelected = () => {
  if (confirm('Biztosan törölni szeretnéd a kijelölt tételeket?')) {
    parts.value = parts.value.filter(p => !p.selected)
  }
}

const unassignSelected = () => {
  parts.value.forEach(p => {
    if (p.selected) {
      p.ProjectName = ''
      p.selected = false
    }
  })
}
</script>
