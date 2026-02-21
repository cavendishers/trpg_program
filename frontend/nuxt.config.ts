export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ["@pinia/nuxt"],
  css: ["~/assets/styles/main.css"],
  app: {
    head: {
      title: "AI TRPG - 克苏鲁跑团",
      link: [
        {
          rel: "stylesheet",
          href: "https://fonts.googleapis.com/css2?family=VT323&display=swap",
        },
      ],
    },
  },
  runtimeConfig: {
    public: {
      apiBase: "http://localhost:8000",
      wsBase: "ws://localhost:8000",
    },
  },
});
