/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App
 */

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './views/App.vue'

// Composables
import { createApp } from 'vue'

// Font Awesome imports
import { library } from '@fortawesome/fontawesome-svg-core'
import { faGear, faHouse, faXmark, faHeart } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

// Router import
import router from './router' // Importujemy nasz router

// Vue Lazyload import
import VueLazyload from 'vue-lazyload'

library.add(faGear)
library.add(faHouse)
library.add(faXmark)
library.add(faHeart)

const app = createApp(App)

// Rejestracja komponentu `font-awesome-icon` globalnie
app.component('font-awesome-icon', FontAwesomeIcon)

// Rejestracja Vuetify i innych pluginów
registerPlugins(app)

// Dodajemy router do aplikacji
app.use(router)

// Użycie VueLazyload
app.use(VueLazyload, {
  lazyComponent: true
});

// Montowanie aplikacji
app.mount('#app')
