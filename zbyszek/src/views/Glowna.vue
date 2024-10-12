<template>
  <v-card>
    <v-layout>
        <v-app-bar color="red" prominent>
        <v-toolbar-title>AnonimowiGrajacyAlkoholicy</v-toolbar-title>

        <v-text-field label="Nazwa Gry" style="margin-top: 20px; max-width: 600px; text-align: center"></v-text-field>

        <v-spacer></v-spacer>

          <v-btn icon @click="handleClickClose">
            <font-awesome-icon :icon="['fas', 'xmark']" size="lg" style="margin-right: 30px" />
          </v-btn>
      </v-app-bar>

      <v-navigation-drawer
        v-model="drawer"
        :rail="rail"
        permanent
        @click="rail = false"
      >
        <template v-slot:append>
          <v-btn
            icon="mdi-chevron-left"
            variant="text"
            @click.stop="rail = !rail"
          ></v-btn>
        </template>

        <v-divider></v-divider>

        <v-list density="compact" nav>
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
          </v-list-item>
        </v-list>
      </v-navigation-drawer>

      <v-main style="background: aliceblue">
        <router-view></router-view> <!-- Wyświetlanie widoków zależnych od trasy -->
      </v-main>
    </v-layout>
  </v-card>
</template>

<script>
  const { ipcRenderer } = require('electron');

  export default {
    methods: {
      async handleClickClose() {
        try {
          await ipcRenderer.invoke('closeapp');
        } catch (error) {
          console.error('Błąd podczas zamykania aplikacji:', error);
        }
      },
      async navigateTo(routeName) {
      this.$router.push({ name: routeName });
      },
      GetGames() {
      fetch('http://localhost:8090/api/games')
        .then(response => {
          if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
          }
          return response.json();
        })
        .then(data => {
          console.log('Dane z API:', data);
        })
        .catch(error => {
          console.error('Błąd podczas pobierania danych:', error);
        });
    }
  },
  data() {
    return {
      drawer: true,
      rail: true,
      games: [],
      loading: true
    };
  },
  mounted() {
    this.GetGames(); // Wywołanie pobierania gier przy montowaniu komponentu
  }
};
</script>
