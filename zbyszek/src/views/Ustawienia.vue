<template>
      <v-main style="height: 100%">
        <v-card-text>
            <v-btn icon @click="LoginViaSteam">
            Steam
          </v-btn>
        </v-card-text>
      </v-main>
</template>

<script>
  import {ipcRenderer} from "electron";

  export default {
     methods: {
        async LoginViaSteam(){
          try {
            await ipcRenderer.invoke('LoginViaSteam');
            console.log("JESTEM")
          } catch (error) {
            console.error('Błąd podczas logowania przez Steam:', error);
          }
        },
      data: () => ({
        drawer: true,
        rail: true,
        group: null,
      }),
    },
  }
</script>
