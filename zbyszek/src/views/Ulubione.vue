<template>
  <v-main>
    <v-container fluid>
      <v-row dense>
        <v-col v-for="(game, index) in games" :key="index" :cols="6">
          <!-- Skeleton loader wyświetlany, gdy dane są ładowane -->
          <v-skeleton-loader
            v-if="loading"
            type="card"
            max-width="500"
          ></v-skeleton-loader>

          <!-- Wyświetlanie karty gry po załadowaniu -->
          <v-card v-else>
            <v-img
              :src="game.image"
              class="align-end"
              gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
              height="200px"
              cover
            >
              <v-card-title class="text-white">{{ game.title }}</v-card-title>
            </v-img>

            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                color="medium-emphasis"
                icon="mdi-heart"
                size="small"
              ></v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script>
  const { ipcRenderer } = require('electron');

  export default {
    methods: {
      //async handleClickClose() {
        //try {
          //await ipcRenderer.invoke('closeapp');
        //} catch (error) {
         // console.error('Błąd podczas zamykania aplikacji:', error);
        //}
      //},
      GetGames() {
        fetch('http://localhost:8090/api/games')
          .then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
          })
          .then(data => {
            this.games = data; // Aktualizowanie danych
            this.loading = false; // Wyłączamy loader po załadowaniu danych
          })
          .catch(error => {
            console.error('Błąd podczas pobierania danych:', error);
          });
      }
    },
    data() {
      return {
        games: [],
        loading: true
      };
    },
    mounted() {
      this.GetGames(); // Pobieranie gier przy montowaniu komponentu
    }
  };
</script>
