import type { AuraApi, JarvisApi } from "./index";

declare global {
  interface Window {
    aura: AuraApi;
    jarvis: JarvisApi;
  }
}
