import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("../views/Home.vue"),
  },
  {
    path: "/connect-muse",
    name: "ConnectMuse",
    component: () => import("../views/ConnectMuse.vue"), // If you have a Vue file, use it instead
  },
  {
    path: "/muse-data",
    name: "MuseData",
    component: () => import("../views/MuseData.vue"), // If you have a Vue file, use it instead
  },
  {
    path: "/final",
    name: "Final",
    component: () => import("../views/Final.vue"), // If you have a Vue file, use it instead
  },
  {
    path: "/check-electrodes",
    name: "CheckElectrodes",
    component: () => import("../views/CheckElectrodes.vue"), // If you have a Vue file, use it instead
  },
  {
    path: "/calibration",
    name: "Calibration",
    component: () => import("../views/Calibration.vue"), // If you have a Vue file, use it instead
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
