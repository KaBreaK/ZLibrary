<template>
  <v-app>
    <div class="background-image"></div>
    <v-card>
      <v-layout>
        <!-- App Bar -->
        <v-app-bar color="purple-darken-4" prominent>
          <v-toolbar-title>AnonimowiGrajacyAlkoholicy</v-toolbar-title>

          <v-text-field
            label="Nazwa Gry"
            style="margin-top: 20px; max-width: 600px; text-align: center"
          ></v-text-field>

          <v-spacer></v-spacer>

          <v-btn icon @click="handleClickClose">
            <font-awesome-icon :icon="['fas', 'xmark']" size="lg" style="margin-right: 30px" />
          </v-btn>
        </v-app-bar>

        <!-- Navigation Drawer -->
        <v-navigation-drawer
          v-model="drawer"
          :rail="rail"
          permanent
          @click="rail = false"
        >
          <v-list density="compact" nav style="height: auto">
            <v-list-item
              prepend-icon="mdi-account"
              title="Biblioteka Gier"
              value="liblary"
              @click="$router.push({ name: 'glowna' })"
            >
              <template #prepend>
                <font-awesome-icon :icon="['fas', 'house']" size="lg" style="margin-right: 30px" />
              </template>
            </v-list-item>

            <v-list-item
              title="Ulubione"
              value="favourite"
              @click="$router.push({ name: 'ulubione' })"
            >
              <template #prepend>
                <font-awesome-icon :icon="['fas', 'heart']" size="lg" style="margin-right: 30px" />
              </template>
            </v-list-item>

            <v-list-item
              title="Ustawienia"
              value="ustawienia"
              @click="$router.push({ name: 'ustawienia' })"
            >
              <template #prepend>
                <font-awesome-icon :icon="['fas', 'gear']" size="lg" style="margin-right: 30px" />
              </template>
            </v-list-item>  <v-list-item
              title="Ustawienia"
              value="ustawienia"
              @click="$router.push({ name: 'ustawienia' })"
            >
              <template #prepend>
                <font-awesome-icon :icon="['fas', 'gear']" size="lg" style="margin-right: 30px" />
              </template>
            </v-list-item>
            <v-btn
                icon="mdi-chevron-left"
                variant="text"
                @click.stop="rail = !rail"
                style=""
              ></v-btn>
          </v-list>
        </v-navigation-drawer>

        <!-- Main Content Area -->
        <v-main>

          <!-- Router View -->
          <router-view></router-view>
        </v-main>
      </v-layout>
    </v-card>
  </v-app>
</template>

<script>
const { ipcRenderer } = require('electron');

export default {
  data() {
    return {
      drawer: true,
      rail: true
    };
  },
  methods: {
    async handleClickClose() {
      try {
        await ipcRenderer.invoke('closeapp');
      } catch (error) {
        console.error('Błąd podczas zamykania aplikacji:', error);
      }
    }
  }
};
</script>

<style scoped>
  .background-image {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1; /* Tło będzie za całą aplikacją */
    background-image: url('../galery/tlol.jpg'); /* Zmień na odpowiedni URL */
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
  }
</style>
