export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ["@pinia/nuxt"],
  css: ["~/assets/styles/main.css"],
  app: {
    head: {
      title: "AI TRPG - 克苏鲁跑团",
      meta: [
        { name: "viewport", content: "width=device-width, initial-scale=1, viewport-fit=cover" },
      ],
      link: [
        {
          rel: "stylesheet",
          href: "https://fonts.googleapis.com/css2?family=VT323&display=swap",
        },
      ],
    },
  },
  devServer: {
    port: 29474,
    host: "0.0.0.0",
  },
  runtimeConfig: {
    public: {
      apiBase: "http://mc20.starmc.cn:25032",
      wsBase: "ws://mc20.starmc.cn:25032",
    },
  },
});
