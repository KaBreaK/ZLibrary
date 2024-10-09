<template>
  <v-card>
    <v-layout>
      <v-app-bar color="red" prominent>
        <v-app-bar-nav-icon

          @click.stop="drawer = !drawer"
        ></v-app-bar-nav-icon>

        <v-toolbar-title>AnonimowiGrajacyAlkoholicy</v-toolbar-title>
        <v-text-field label="Nazwa Gry" style="margin-top: 20px"></v-text-field>
        <font-awesome-icon :icon="['fas', 'xmark']" size="xl" style=""/>

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
            prepend-icon="mdi-account"
            title="Biblioteka Gier"
            value="liblary"
          >
            <template #prepend>
              <font-awesome-icon :icon="['fas', 'house']" size="lg" style="margin-right: 30px" />
            </template>
          </v-list-item>
          <v-list-item
              title="Ustawienia"
              @click="$router.push({ name: 'Ustawienia.vue' })"
            >
              <template #prepend>
                <font-awesome-icon :icon="['fas', 'gear']" size="lg" style="margin-right: 30px" />
              </template>
          </v-list-item>
        </v-list>
      </v-navigation-drawer>

      <v-main style="height: 100%">
        <v-card-text>
            TU TRZEBA DODAC CARDY
        </v-card-text>
      </v-main>
    </v-layout>
  </v-card>
</template>

<script>
  import {createRouter as $router} from "vue-router/dist/vue-router.esm-browser";

  export default {
    methods: {$router},
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
