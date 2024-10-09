<template>
  <v-card>
    <v-layout>
      <v-app-bar color="red" prominent>
        <v-app-bar-nav-icon
          variant="text"
          @click.stop="drawer = !drawer"
        ></v-app-bar-nav-icon>

        <v-toolbar-title>AAA</v-toolbar-title>
        <v-text-field label="CHUJJJJJJJJJ"></v-text-field>

        <v-spacer>
        </v-spacer>
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
            prepend-icon="mdi-home-city"
            title="Home"
            value="home"
          ></v-list-item>
          <v-list-item
            prepend-icon="mdi-account"
            title="My Account"
            value="account"
          ></v-list-item>
          <v-list-item
            prepend-icon="mdi-account-group-outline"
            title="Users"
            value="users"
          ></v-list-item>
        </v-list>
      </v-navigation-drawer>

      <v-main style="height: 100%">
        <v-card-text>
          CHUJJJJJJJJJJJJJJJJJJJJ
        </v-card-text>
      </v-main>
    </v-layout>
  </v-card>
</template>

<script>
  export default {
    data: () => ({
      drawer: true,
      rail: true,
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
