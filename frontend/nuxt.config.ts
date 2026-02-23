export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ["@pinia/nuxt"],
  css: ["~/assets/styles/main.css"],
  app: {
    head: {
      title: "AI TRPG - 克苏鲁跑团",
      meta: [
        { name: "viewport", content: "width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" },
      ],
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
