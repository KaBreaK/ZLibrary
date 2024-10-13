<template>
  <v-main>
    <v-container fluid>
      <v-row dense>
        <v-col v-for="(game, index) in games" :key="index" :cols="3">
          <!-- Skeleton loader wyświetlany, gdy dane są ładowane -->
          <v-skeleton-loader
            v-if="loading"
            type="card"
            max-width="500"
          ></v-skeleton-loader>

          <!-- Wyświetlanie karty gry po załadowaniu -->
          <v-card v-else>
            <v-img
              :src="game.gamephoto"
              class="align-end"
              gradient="to bottom, rgba(0,0,0,.1), rgba(0,0,0,.5)"
              height="200px"
              cover
            >
              <v-card-title class="text-white">{{ game.name }}</v-card-title>
            </v-img>

            <v-card-subtitle>
              Ostatnio grane: {{ formatLastPlayed(game.lastPlayed) }}
            </v-card-subtitle>

            <v-card-text>
              <strong>Konto:</strong> {{ game.accountName }}<br />
              <strong>Łączny czas gry:</strong> {{ game.totalPlayTime }} godzin<br />
              <v-btn color="green" size="large">ZAGRAJ</v-btn>
            </v-card-text>

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
      GetGames() {
        fetch('http://localhost:8090/api/games')
          .then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
          })
          .then(data => {
            // Przetwarzamy dane, by wyciągnąć potrzebne informacje
            this.games = data.games.map(game => {
              return {
                gamephoto: game.gamephoto,
                name: game.name,
                accountName: game.playTimePerAccount.length > 0 ? game.playTimePerAccount[0].accountName : 'Brak konta',
                lastPlayed: game.lastPlayed,
                totalPlayTime: (game.totalPlayTime / 60).toFixed(2) // Przeliczamy czas gry na godziny
              };
            });
            this.loading = false; // Wyłączamy loader po załadowaniu danych
          })
          .catch(error => {
            console.error('Błąd podczas pobierania danych:', error);
          });
      },
      formatLastPlayed(timestamp) {
        const date = new Date(timestamp * 1000);
        return date.toLocaleDateString();
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
