<template>
  <v-card>
    <v-layout>
      <v-app-bar color="primary" prominent>
        <v-app-bar-nav-icon
          variant="text"
          @click.stop="drawer = !drawer"
        ></v-app-bar-nav-icon>

        <v-toolbar-title>AAA</v-toolbar-title>
        <v-btn variant="tonal">CHUJ</v-btn>
        <v-text-field label="Nazwa Gry"></v-text-field>

        <v-spacer>
        </v-spacer>
      </v-app-bar>

      <v-navigation-drawer
        v-model="drawer"
        :location="$vuetify.display.mobile ? 'bottom' : undefined"
        temporary
      >
        <v-list :items="items"></v-list>
      </v-navigation-drawer>

      <v-main style="height: 500px">
        <v-card-text>

        </v-card-text>
      </v-main>
    </v-layout>
  </v-card>
</template>

<script>
  export default {
    data: () => ({
      drawer: false,
      group: null,
      items: [
        {
          title: 'Gry',
          value: '',
        },
        {
          title: 'Ustawienia',
          value: 'bar',
        },
        {
          title: 'Wyloguj',
          value: 'buzz',
        },
      ],
    }),

    watch: {
      group() {
        this.drawer = false
      },
    },
  }
</script>
