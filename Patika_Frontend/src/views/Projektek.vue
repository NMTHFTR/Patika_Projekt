<!-- src/views/Projektek.vue -->
<template>
  <div class="wrap">
    <!-- Felső KPI rész -->
    <div class="header">
      <div></div>
      <div class="kpis">
        <div class="kpi"><div class="big">{{ kpiAll }}</div><div class="sub">Összes projekt</div></div>
        <div class="kpi"><div class="big">{{ kpiActive }}</div><div class="sub">Aktív</div></div>
        <div class="kpi"><div class="big">{{ kpiInactive }}</div><div class="sub">Inaktív</div></div>
      </div>
    </div>

    <!-- Új projekt felvétele panel -->
    <div class="panel" style="margin-bottom: 16px">
      <div class="section-title">Új projekt felvétel</div>
      <table class="grid" style="margin-top: 6px">
        <thead>
          <tr>
            <th>Projekt neve</th>
            <th>Felelős</th>
            <th>Hely</th>
            <th>Kiadva (opcionális)</th>
            <th>Projekt azonosító (opcionális)</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><input type="text" v-model="newProject.name" placeholder="Pl. Új labor osztály" /></td>
            <td>
              <select v-model="newProject.user">
                <option value="">– válassz felelőst –</option>
                <option v-for="user in userList" :key="user" :value="user">{{ user }}</option>
              </select>
            </td>
            <td><input type="text" v-model="newProject.place" placeholder="Pl. Raktár fsz. 2" /></td>
            <td><input type="text" v-model="newProject.secUser" placeholder="Másodlagos felelős" /></td>
            <td><input type="text" v-model="newProject.code" placeholder="Pl. PRJ-2026" /></td>
          </tr>
        </tbody>
      </table>
      <div style="margin: 10px 0 0 0; display: flex; gap: 10px; align-items: center;">
        <button class="btn success" @click="addProject">Hozzáadás</button>
        <span class="msg" style="color: #22c55e;">{{ statusMessage }}</span>
      </div>
    </div>

    <!-- Keresés és szűrés -->
    <div class="panel">
      <div class="section-title">Keresés és szűrés</div>
      <div class="filters" style="margin-bottom: 10px">
        <div class="stack" style="grid-column: span 6">
          <label>Keresés</label>
          <input type="text" v-model="searchQuery" placeholder="Keresés név vagy kód alapján..." />
        </div>
      </div>

      <!-- Projektek fő táblázata (GridView kiváltása inline szerkesztéssel) -->
      <table class="grid" style="margin-top: 12px;">
        <thead>
          <tr>
            <th>Projekt név</th>
            <th>Projekt azonosító</th>
            <th>Felelős</th>
            <th>Kiadva</th>
            <th>Hely</th>
            <th style="width: 80px; text-align: center;">Aktív</th>
            <th style="width: 120px;">Műveletek</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="project in filteredProjects" :key="project.ProjectId" :class="{ 'editing': editingId === project.ProjectId }">
            <!-- NÉZET MÓD -->
            <template v-if="editingId !== project.ProjectId">
              <td>{{ project.Name }}</td>
              <td>{{ project.Code || '–' }}</td>
              <td>{{ project.User || '–' }}</td>
              <td>{{ project.SecUser || '–' }}</td>
              <td>{{ project.Place || '–' }}</td>
              <td style="text-align: center;">
                <span :class="['tag', project.IsActive ? 'green' : 'red']">
                  {{ project.IsActive ? 'Igen' : 'Nem' }}
                </span>
              </td>
              <td>
                <div class="row-actions">
                  <button class="btn primary" style="padding: 4px 8px;" @click="startEdit(project)">Szerkeszt</button>
                </div>
              </td>
            </template>

            <!-- SZERKESZTŐ MÓD (Inline) -->
            <template v-else>
              <td><input type="text" v-model="editForm.Name" /></td>
              <td><input type="text" v-model="editForm.Code" /></td>
              <td>
                <select v-model="editForm.User">
                  <option value="">– nincs –</option>
                  <option v-for="user in userList" :key="user" :value="user">{{ user }}</option>
                </select>
              </td>
              <td><input type="text" v-model="editForm.SecUser" /></td>
              <td><input type="text" v-model="editForm.Place" /></td>
              <td style="text-align: center;">
                <input type="checkbox" v-model="editForm.IsActive" />
              </td>
              <td>
                <div class="row-actions">
                  <button class="btn success" style="padding: 4px 8px;" @click="saveEdit">Mentés</button>
                  <button class="btn danger" style="padding: 4px 8px;" @click="deleteProject(project.ProjectId)">Törlés</button>
                  <button class="btn ghost" style="padding: 4px 8px; color: white;" @click="cancelEdit">X</button>
                </div>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import '../assets/projektek.css'

// Kezdő aspx adatok és felhasználói lista
const userList = ref([
  'Pandur Gergő G/A-S', 'Széchenyi Richárd G/A-S', 'Hódosi Gergely G/A-S',
  'Hingyi Martin G/A-S', 'Szabó Gábor G/A-S', 'Kovács Dávid G/A-S',
  'Blézer István G/A-S', 'Kámán Csilla G/A-S', 'Horváth Vivien Kata G/A-S',
  'Áder Gergely Péter G/A-S', 'Nagy András G/A-S'
])

const projects = ref([
  { ProjectId: 1, Name: 'Sebészet', Code: 'SEB-01', User: 'Pandur Gergő G/A-S', SecUser: 'Kovács Dávid G/A-S', Place: 'I. emelet A szárny', IsActive: true },
  { ProjectId: 2, Name: 'Belgyógyászat', Code: 'BEL-02', User: 'Széchenyi Richárd G/A-S', SecUser: '', Place: 'II. emelet B szárny', IsActive: true },
  { ProjectId: 3, Name: 'Sürgősségi', Code: 'SGO-03', User: 'Hódosi Gergely G/A-S', SecUser: 'Nagy András G/A-S', Place: 'Földszint mentőbejárat', IsActive: true },
  { ProjectId: 4, Name: 'Archivált Osztály', Code: 'ARC-99', User: 'Kámán Csilla G/A-S', SecUser: '', Place: 'Pince', IsActive: false }
])

// Állapotkezelők az új és a szerkesztett elemekhez
const newProject = ref({ name: '', code: '', user: '', secUser: '', place: '' })
const statusMessage = ref('')
const searchQuery = ref('')

// Szerkesztési segédváltozók
const editingId = ref(null)
const editForm = ref({ Name: '', Code: '', User: '', SecUser: '', Place: '', IsActive: true })

// KPI számítások dinamikusan
const kpiAll = computed(() => projects.value.length)
const kpiActive = computed(() => projects.value.filter(p => p.IsActive).length)
const kpiInactive = computed(() => projects.value.filter(p => !p.IsActive).length)

// Kereső szűrés név és kód alapján
const filteredProjects = computed(() => {
  return projects.value.filter(p => {
    return p.Name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
           p.Code.toLowerCase().includes(searchQuery.value.toLowerCase())
  })
})

// Funkció: Új projekt felvétele
const addProject = () => {
  if (!newProject.value.name.trim()) {
    statusMessage.value = 'Adj nevet a projektnek!'
    return
  }
  projects.value.push({
    ProjectId: Date.now(),
    Name: newProject.value.name,
    Code: newProject.value.code,
    User: newProject.value.user,
    SecUser: newProject.value.secUser,
    Place: newProject.value.place,
    IsActive: true
  })
  statusMessage.value = 'Hozzáadva.'
  newProject.value = { name: '', code: '', user: '', secUser: '', place: '' }
  setTimeout(() => statusMessage.value = '', 3000)
}

// Inline szerkesztés vezérlése
const startEdit = (project) => {
  editingId.value = project.ProjectId
  editForm.value = { ...project }
}

const cancelEdit = () => {
  editingId.value = null
}

const saveEdit = () => {
  if (!editForm.value.Name.trim()) {
    alert('A név kötelező!')
    return
  }
  const index = projects.value.findIndex(p => p.ProjectId === editingId.value)
  if (index !== -1) {
    projects.value[index] = { ...editForm.value }
  }
  editingId.value = null
  statusMessage.value = 'Mentve.'
  setTimeout(() => statusMessage.value = '', 3000)
}

// Funkció: Projekt és a hozzárendelések törlése
const deleteProject = (id) => {
  if (confirm('Biztos törlöd ezt a projektet?')) {
    projects.value = projects.value.filter(p => p.ProjectId !== id)
    editingId.value = null
    statusMessage.value = 'Törölve.'
    setTimeout(() => statusMessage.value = '', 3000)
  }
}
</script>
