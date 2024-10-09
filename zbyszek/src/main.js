/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App
 */

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './views/Glowna.vue'

// Composables
import { createApp } from 'vue'

// Font Awesome imports
import { library } from '@fortawesome/fontawesome-svg-core'
import { faCoffee, faGear, faHouse, faXmark } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

// Router import
import router from './router' // Importujemy nasz router

// Dodajemy ikonę do biblioteki
library.add(faCoffee)
library.add(faGear)
library.add(faHouse)
library.add(faXmark)

const app = createApp(App)

// Rejestracja komponentu `font-awesome-icon` globalnie
app.component('font-awesome-icon', FontAwesomeIcon)

registerPlugins(app)

// Dodajemy router do aplikacji
app.use(router)

app.mount('#app')
